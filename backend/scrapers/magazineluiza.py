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
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                
                # Tenta esperar por um seletor de produto genérico
                # Magalu costuma usar data-testid ou classes específicas
                try:
                    await page.wait_for_selector('[data-testid="product-card-container"]', timeout=8000)
                except:
                    # Se falhar, segue o baile e tenta parsear o que tiver
                    print("⚠️ Timeout esperando seletor específico do Magalu, tentando parsear HTML direto...")
                    pass

                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                # Seletores do Magalu (Podem mudar, então tentar alguns padrões)
                # Padrão atual: data-testid="product-card-container"
                items = soup.find_all("div", attrs={"data-testid": "product-card-container"})
                
                # Se não achar, tenta fallback para classes comuns antiga
                if not items:
                     items = soup.select('li > a[href*="/p/"]') # Seletor genérico de lista de produtos

                for item in items:
                    try:
                        # Título
                        title_tag = item.find("h2", attrs={"data-testid": "product-title"})
                        if not title_tag:
                            title_tag = item.find("h2")
                        title = title_tag.text.strip() if title_tag else "Sem Título"
                        
                        # Link
                        # O container as vezes é o próprio link ou tem um link dentro
                        link = ""
                        if item.name == "a":
                             link = item["href"]
                        else:
                             link_tag = item.find("a", attrs={"data-testid": "product-card-container"}) 
                             if not link_tag:
                                 link_tag = item.find("a")
                             link = link_tag["href"] if link_tag else ""
                        
                        # Magalu usa links relativos as vezes
                        if link and not link.startswith("http"):
                            link = f"https://www.magazineluiza.com.br{link}"
                        
                        # Imagem
                        img_tag = item.find("img", attrs={"data-testid": "product-image"})
                        if not img_tag:
                            img_tag = item.find("img")
                        image = img_tag.get("src") or img_tag.get("data-src") if img_tag else ""
                        
                        # Preço
                        price_tag = item.find("p", attrs={"data-testid": "price-value"})
                        if not price_tag:
                            # Tenta padrão antigo
                             price_tag = item.find("span", text=lambda t: t and "R$" in t)

                        price = 0.0
                        if price_tag:
                            price_text = price_tag.text.replace("R$", "").replace(".", "").replace(",", ".").strip()
                            # Limpeza extra para casos como "à vista"
                            price_text = price_text.split(" ")[0] 
                            try:
                                price = float(price_text)
                            except:
                                pass

                        # Só adiciona se tiver título e preço válido
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
                        # print(f"Erro parser item Magalu: {e}")
                        continue
                
                print(f"✅ Encontrados {len(products)} produtos no Magalu.")
                
                # Mock Fallback se bloqueado (igual ao ML)
                if not products:
                     print("⚠️ Nenhum produto encontrado no Magalu. Ativando Mock.")
                     products = [
                        {"title": f"MOCK Magalu: {query} Super", "price": 2400.0, "currency": "BRL", "link": "#", "image": "https://img.freepik.com/fotos-gratis/sacolas-de-compras-coloridas_23-2147652053.jpg", "store": "Magazine Luiza (Mock)"},
                     ]

            except Exception as e:
                print(f"❌ Erro no Playwright Magalu: {e}")
            finally:
                await browser.close()
                
        return products
