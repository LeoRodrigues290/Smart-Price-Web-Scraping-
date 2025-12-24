from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base import BaseScraper
import re
import asyncio

class BingShoppingScraper(BaseScraper):
    async def search(self, query: str) -> list:
        print(f"🔎 Iniciando busca no Bing Shopping para: {query}")
        
        # URL do Bing Shopping
        url = f"https://www.bing.com/shop?q={query}"
        products = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'
                ]
            )
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(2)
                
                # Bing as vezes pede clique em "Shopping" se cair na busca geral
                # Mas a URL /shop deve ir direto.
                
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                # Seletores do Bing Shopping
                # Geralmente: .br-item (Grid Item)
                items = soup.select(".br-item, .br-standard-item, li.br-item")
                
                print(f"🔧 Bing encontrou {len(items)} itens via seletor.")
                
                if not items:
                    # Tenta heurística se falhar seletor
                     await page.screenshot(path="debug_bing.png")
                     
                # ESTRATÉGIA HEURÍSTICA DE TÍTULO
                # Bing as vezes retorna classes genéricas ou o título está em atributos aria-label.
                # A lógica abaixo tenta várias fontes para garantir um título legível.
                for item in items:
                    try:
                        # 1. Tentativa Direta (Seletores CSS conhecidos)
                        title = ""
                        title_tag = item.select_one(".br-tit, .br-title, .br-standard-title, .pd-title")
                        if title_tag:
                            title = title_tag.text.strip()
                        
                        # 2. Heurística de Texto Mais Longo (Fallback)
                        # Se não achou título, pega todos os textos do card e assume que o
                        # texto mais longo (que não seja preço) é o título.
                        if not title or title == "Imagem do Produto":
                            # Pega todos os textos do item
                            texts = item.get_text(separator="|", strip=True).split("|")
                            # Filtra textos curtos e o preço
                            candidates = [t for t in texts if len(t) > 10 and "R$" not in t]
                            if candidates:
                                # O título geralmente é o texto mais longo
                                title = max(candidates, key=len)
                        
                        if not title: title = "Sem Título"
                        
                        # Remove sufixos sujos se houver
                        if "..." in title: title = title.split("...")[0] + "..."

                        # Link
                        link = ""

                        # Link
                        link = ""
                        link_tag = item.find("a", href=True)
                        if link_tag:
                            link = link_tag['href']
                            if link.startswith("/"):
                                link = f"https://www.bing.com{link}"
                        
                        # Preço (.br-price)
                        price = 0.0
                        price_tag = item.select_one(".br-price, .br-standard-price")
                        p_text = ""
                        if price_tag:
                            p_text = price_tag.text
                        else:
                            p_text = item.get_text()
                            
                        # Limpa R$ 1.200,00
                        match = re.search(r'R\$\s?([\d\.,]+)', p_text)
                        if match:
                             p_clean = match.group(1).replace('.', '').replace(',', '.')
                             try: price = float(p_clean)
                             except: pass
                        
                        # Imagem
                        image = ""
                        img_tag = item.find("img")
                        if img_tag:
                            image = img_tag.get("src") or img_tag.get("data-src") or ""
                            # Bing as vezes usa imagens pequenas base64, tentar pegar URL limpa se possivel
                        
                        # Loja
                        store = "Bing Shopping"
                        seller_tag = item.select_one(".br-seller, .br-standard-seller")
                        if seller_tag:
                            store = seller_tag.text.strip()

                        if title and price > 0:
                            products.append({
                                "title": title,
                                "price": price,
                                "currency": "BRL",
                                "link": link,
                                "image": image,
                                "store": store
                            })
                    except: continue

                print(f"✅ Bing retornou {len(products)} produtos.")

            except Exception as e:
                print(f"❌ Erro no Bing Scraper: {e}")
            finally:
                await browser.close()
                
        return products
