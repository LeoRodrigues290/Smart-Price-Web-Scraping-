from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base import BaseScraper
import asyncio

class MagazineLuizaScraper(BaseScraper):
    async def search(self, query: str) -> list:
        print(f"🔎 Iniciando busca no Magazine Luiza (Playwright) para: {query}")
        
        # URL de busca do Magalu
        url = f"https://www.magazineluiza.com.br/busca/{query}/"
        products = []

        async with async_playwright() as p:
            # Stealth Args: Tenta esconder que é um robô
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certifcate-errors',
                    '--ignore-certifcate-errors-spki-list',
                    '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'
                ]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 800}
            )
            page = await context.new_page()
            
            # Script extra para mascarar o webdriver
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)

            try:
                # OTIMIZAÇÃO: Timeout reduzido para 15s
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                try:
                    await page.click("button:has-text('Cookies')", timeout=2000)
                except Exception:
                    pass # Não há problema se o botão de cookies não aparecer
                
                # Scroll para garantir carregamento de lazy load
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2) # Espera renderizar

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                # ESTRATÉGIA HEURÍSTICA (Robustez contra mudança de CSS)
                # 1. Acha todos os preços (R$)
                # 2. Sobe na árvore DOM para achar o card do produto
                
                import re
                prices_elements = soup.find_all(string=re.compile(r'R\$\s?[\d\.,]+'))
                
                seen_links = set()
                
                for price_elem in prices_elements:
                    if len(products) >= 20: break
                    
                    try:
                        # Sobe até 5 níveis para achar um container que tenha Link e Titulo
                        parent = price_elem.parent
                        card = None
                        
                        for _ in range(5):
                            if not parent: break
                            # Um card de produto deve ter um Link (a) e uma Imagem (img)
                            if parent.find("a", href=True) and parent.find("img"):
                                card = parent
                                if len(str(card)) > 5000: # Evita pegar o body inteiro
                                    card = None
                                    continue
                                break
                            parent = parent.parent
                        
                        if not card: continue
                        
                        # Extração de dados do Card encontrado
                        
                        # Link
                        link = ""
                        link_tag = card.find("a", href=True)
                        if link_tag:
                            link = link_tag['href']
                            if not link.startswith("http"):
                                link = f"https://www.magazineluiza.com.br{link}"
                        
                        if not link or link in seen_links: continue
                        seen_links.add(link)
                        
                        # Título
                        title = ""
                        title_tag = card.find(["h2", "h3", "h4"])
                        if title_tag:
                            title = title_tag.text.strip()
                        else:
                            # Tenta texto do link ou imagem alt
                            if link_tag: title = link_tag.get_text(" ", strip=True)
                        
                        if not title:
                            img = card.find("img")
                            if img: title = img.get("alt") or ""
                            
                        # Preço (já temos a string, limpa ela)
                        price = 0.0
                        p_match = re.search(r'R\$\s?([\d\.,]+)', str(price_elem))
                        if p_match:
                            p_clean = p_match.group(1).replace('.', '').replace(',', '.')
                            try:
                                price = float(p_clean)
                            except: pass
                        
                        # Imagem
                        image = ""
                        img_tag = card.find("img")
                        if img_tag:
                             image = img_tag.get("src") or img_tag.get("data-src") or ""
                             
                        if title and price > 0:
                             products.append({
                                "title": title,
                                "price": price,
                                "currency": "BRL",
                                "link": link,
                                "image": image,
                                "store": "Magazine Luiza"
                            })
                            
                    except Exception as e:
                        continue
                
                print(f"✅ Encontrados {len(products)} produtos no Magalu via heurística.")
                
                if not products:
                     print("⚠️ Nenhum produto encontrado no Magalu.")
                     # NUNCA retornar mocks

            except Exception as e:
                print(f"❌ Erro no Playwright Magalu: {e}")
            finally:
                await browser.close()
                
        return products
