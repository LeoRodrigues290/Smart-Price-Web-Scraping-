from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base import BaseScraper
import re

class MercadoLivreScraper(BaseScraper):
    async def search(self, query: str) -> list:
        print(f"🔎 Iniciando busca no Mercado Livre (Playwright Heurístico) para: {query}")
        
        url = f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}"
        products = []

        async with async_playwright() as p:
            # Stealth Args
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            try:
                # OTIMIZAÇÃO: Timeout reduzido para 15s
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                try:
                    await page.click("button:has-text('Aceitar cookies')", timeout=2000)
                except: pass

                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/3)")
                
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                # HEURÍSTICA: Acha preços (R$) e sobe para achar o Card
                price_elements = soup.find_all(string=re.compile(r'R\$\s?[\d\.,]+'))
                if not price_elements:
                     # Mercado Livre as vezes usa <span class="andes-money-amount__fraction">2.500</span> sem o R$ no texto direto
                     # Mas geralmente tem o simbolo em outro span.
                     # Vamos tentar achar o container padrão também se a heurística de texto falhar
                     pass

                seen_links = set()
                
                # 1. Tentativa Heurística por Preço
                for p_elem in price_elements:
                    if len(products) >= 15: break
                    try:
                        parent = p_elem.parent
                        card = None
                        for _ in range(6):
                            if not parent: break
                            if parent.find("a", href=True) and parent.find("img"):
                                card = parent
                                if len(str(card)) > 8000: # muito grande
                                    card = None
                                    continue
                                break
                            parent = parent.parent
                        
                        if card:
                            self._extract_from_card(card, products, seen_links)
                    except: continue

                # 2. Tentativa por Seletores Clássicos (Fallback)
                if len(products) < 5:
                    items = soup.find_all("li", class_="ui-search-layout__item")
                    for item in items:
                         self._extract_from_card(item, products, seen_links)

                print(f"✅ Encontrados {len(products)} produtos via Playwright ML.")
                
            except Exception as e:
                print(f"❌ Erro no Playwright ML: {e}")
            finally:
                await browser.close()
        
        if not products:
            print("⚠️ Nenhum produto encontrado na API do Mercado Livre.")
            # NUNCA retornar mocks
            # products = [] 

        return products

    def _extract_from_card(self, card, products, seen_links):
        try:
            link_tag = card.find("a", href=True)
            if not link_tag: return
            
            link = link_tag['href']
            if link in seen_links: return
            seen_links.add(link)
            
            title = link_tag.get("title") or link_tag.text.strip()
            if not title:
                t_tag = card.find(["h2", "h3"])
                if t_tag: title = t_tag.text.strip()
            
            # Imagem
            img = card.find("img")
            image = ""
            if img:
                image = img.get("data-src") or img.get("src") or ""
            
            # Preço
            price = 0.0
            # Tenta achar estrutura de preço do ML
            price_fraction = card.find("span", class_="andes-money-amount__fraction")
            if price_fraction:
                 p_text = price_fraction.text.replace('.', '').replace(',', '.')
                 price = float(p_text)
            else:
                # Regex no texto todo do card
                match = re.search(r'R\$\s?([\d\.,]+)', card.get_text(" ", strip=True))
                if match:
                    p_clean = match.group(1).replace('.', '').replace(',', '.')
                    try: price = float(p_clean)
                    except: pass
            
            if title and price > 0:
                products.append({
                    "title": title,
                    "price": price,
                    "currency": "BRL",
                    "link": link,
                    "image": image,
                    "store": "Mercado Livre"
                })
        except: pass
