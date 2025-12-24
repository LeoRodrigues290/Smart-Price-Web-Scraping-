from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base import BaseScraper
import asyncio

class MercadoLivreScraper(BaseScraper):
    async def search(self, query: str) -> list:
        print(f"🔎 Iniciando busca no Mercado Livre (Playwright) para: {query}")
        
        url = f"https://lista.mercadolivre.com.br/{query.replace(' ', '-')}"
        products = []

        async with async_playwright() as p:
            # Launch browser
            # Headless = True para prod, mas False ajuda a debuggar se precisar
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                # Navega até a página
                # wait_until='domcontentloaded' é mais rápido que 'networkidle'
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                # Espera pelo container principal de resultados
                # Tenta dois seletores comuns do ML
                try:
                    await page.wait_for_selector(".ui-search-layout", timeout=5000)
                except:
                    # Se falhar o primeiro, tenta ver se já carregou ou é outro layout
                    pass

                # Pega o HTML renderizado
                content = await page.content()
                
                # Agora usa o scraper do BS4 que já tínhamos, mas com o HTML completo!
                soup = BeautifulSoup(content, "html.parser")
                
                # Lógica de extração idêntica à anterior
                items = soup.find_all("li", class_="ui-search-layout__item")
                if not items:
                     items = soup.find_all("div", class_="ui-search-result__wrapper")

                # Debug: Screenshot
                await page.screenshot(path="debug_ml.png")
                title_page = await page.title()
                print(f"Debug: Título da página: {title_page}")

                for item in items:
                    try:
                        title_tag = item.find("h2", class_="ui-search-item__title")
                        if not title_tag:
                            title_tag = item.find("a", class_="ui-search-item__group__element")
                        title = title_tag.text.strip() if title_tag else "Sem Título"
                        
                        link_tag = item.find("a", class_="ui-search-link")
                        link = link_tag["href"] if link_tag else ""
                        
                        img_tag = item.find("img")
                        image = img_tag.get("data-src") or img_tag.get("src") if img_tag else ""
                        
                        price_fraction = item.find("span", class_="andes-money-amount__fraction")
                        price = 0.0
                        if price_fraction:
                            price_text = price_fraction.text.replace(".", "").replace(",", ".")
                            price = float(price_text)

                        products.append({
                            "title": title,
                            "price": price,
                            "currency": "BRL",
                            "link": link,
                            "image": image,
                            "store": "Mercado Livre"
                        })
                    except:
                        continue
                
                print(f"✅ Encontrados {len(products)} produtos via Playwright.")
                
                # --- FALLBACK SE BLOQUEADO ---
                if not products:
                    print("⚠️ Nenhum produto encontrado. Ativando MOCK DATA para não travar o projeto.")
                    products = [
                        {"title": f"MOCK: {query} Modelo X", "price": 1000.0, "currency": "BRL", "link": "#", "image": "https://http2.mlstatic.com/D_NQ_NP_793699-MLA48807865243_012022-O.webp", "store": "Mercado Livre (Mock)"},
                        {"title": f"MOCK: {query} Pro", "price": 2500.0, "currency": "BRL", "link": "#", "image": "https://http2.mlstatic.com/D_NQ_NP_793699-MLA48807865243_012022-O.webp", "store": "Mercado Livre (Mock)"},
                    ]
                # -----------------------------

            except Exception as e:
                print(f"❌ Erro no Playwright: {e}")

            except Exception as e:
                print(f"❌ Erro no Playwright: {e}")
            finally:
                await browser.close()
                
        return products
