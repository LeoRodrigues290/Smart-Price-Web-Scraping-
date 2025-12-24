import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import random

class GoogleShoppingScraper:
    def __init__(self):
        self.base_url = "https://www.google.com/search"

    async def search(self, query: str) -> list:
        print(f"🔎 Iniciando busca no Google Shopping para: {query}")
        
        # tbm=shop ativa a aba Shopping
        url = f"{self.base_url}?q={query}&tbm=shop&hl=pt-BR&gl=br"
        products = []

        async with async_playwright() as p:
            # Stealth Args
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-infobars',
                    '--window-position=0,0',
                    '--ignore-certificate-errors',
                    '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"'
                ]
            )
            context = await browser.new_context(
                 viewport={'width': 1366, 'height': 768},
                 user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # Evasão simples
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            try:
                # ESTRATÉGIA HUMANA: Home -> Busca -> Aba Shopping
                print("📍 Acessando Google Home...")
                await page.goto("https://www.google.com.br", wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(1)

                # Tenta lidar com popup de consentimento (Antes de continuar...)
                try:
                    consent_button = page.get_by_text("Aceitar tudo", exact=False).or_(page.get_by_role("button", name="Aceitar tudo")).or_(page.get_by_role("button", name="Concordo"))
                    if await consent_button.count() > 0:
                        print("🍪 Aceitando cookies/consentimento...")
                        await consent_button.first.click()
                        await asyncio.sleep(1)
                except:
                    pass

                # Digita a busca
                print(f"⌨️ Digitando busca: {query}")
                await page.fill('textarea[name="q"]', query) # Google mudou input para textarea recentemente
                await asyncio.sleep(0.5)
                await page.keyboard.press("Enter")
                
                # Espera resultados carregarem (Timeout maior e seletor generico)
                try:
                    await page.wait_for_load_state("networkidle", timeout=15000)
                except:
                    print("⚠️ Timeout esperando networkidle, tentando seguir...")

                # Debug: Screenshot após busca
                # await page.screenshot(path="debug_after_search.png")
                
                # Clica na aba Shopping
                print("🛒 Procurando aba Shopping...")
                # Tenta achar o link 'Shopping'
                # Variações: "Shopping", "Compras"
                shopping_tab = page.get_by_text("Shopping", exact=True).or_(page.get_by_text("Compras", exact=True))
                
                if await shopping_tab.count() > 0:
                     await shopping_tab.first.click()
                     print("✅ Clicou na aba Shopping.")
                else:
                     # Tenta via URL direto se falhar o clique (Fallback)
                     print("⚠️ Aba Shopping não encontrada, indo via URL direto...")
                     await page.goto(f"https://www.google.com/search?q={query}&tbm=shop", wait_until="domcontentloaded")

                await page.wait_for_load_state("domcontentloaded", timeout=20000)
                await asyncio.sleep(2)
                
                # Scroll para carregar itens
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
                await asyncio.sleep(1)
                
                # DEBUG: Log Page Title (ajuda a saber se caiu em captcha)
                page_title = await page.title()
                print(f"📄 Título da página: {page_title}")
                if "Robô" in page_title or "Robot" in page_title:
                     print("🚫 Google detectou robô!")
                
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                items = []
                
                # ESTRATÉGIA HEURÍSTICA (Baseada em Padrão Visual)
                # 1. Encontra todos elementos que contêm preço (R$ ...)
                # 2. Sobe para achar um container 'Card' que tenha Link e Imagem
                
                import re
                price_elements = soup.find_all(string=re.compile(r"R\$\s?[\d\.,]+"))
                
                unique_products = {} # Usar dict para deduplicar pelo Link
                
                for p_elem in price_elements:
                    try:
                        # Começa do elemento de preço e sobe na árvore até achar um container coerente
                        # (Máximo 5 níveis para cima)
                        parent = p_elem.parent
                        card_candidate = None
                        
                        for _ in range(5):
                            if not parent: break
                            # Regra: Tem que ter Link (a) e Imagem (img) dentro deste pai
                            if parent.find("a", href=True) and parent.find("img"):
                                card_candidate = parent
                                # Se o container for muito grande (body, main), ignora
                                if len(str(card_candidate)) > 5000: # Heurística de tamanho
                                    card_candidate = None
                                    continue
                                break
                            parent = parent.parent
                        
                        if card_candidate:
                            # Extração
                            # Título: Link TEXTO ou h3/h4
                            title = ""
                            title_tag = card_candidate.find(["h3", "h4"])
                            if title_tag:
                                title = title_tag.text.strip()
                            else:
                                # Pega texto do link principal
                                link_tag = card_candidate.find("a", href=True)
                                if link_tag:
                                    title = link_tag.get_text(" ", strip=True)
                            
                            # Link
                            link = ""
                            link_tag = card_candidate.find("a", href=True)
                            if link_tag:
                                link = link_tag['href']
                                # Google Redirect Clean
                                if link.startswith("/url?q="):
                                    link = link.split("/url?q=")[1].split("&")[0]
                                elif link.startswith("/"):
                                    link = f"https://www.google.com{link}"

                            # Preço - já temos do p_elem, mas vamos limpar
                            price = 0.0
                            p_str_match = re.search(r'R\$\s?([\d\.,]+)', str(p_elem))
                            if p_str_match:
                                p_clean = p_str_match.group(1).replace('.', '').replace(',', '.')
                                try:
                                    price = float(p_clean)
                                except: pass
                            
                            # Imagem
                            image = ""
                            img_tag = card_candidate.find("img")
                            if img_tag:
                                image = img_tag.get("src") or img_tag.get("data-src") or ""

                            # Store
                            store = "Google Shopping"
                            # Tenta achar nome da loja (geralmente texto curto no final)
                            # Simples: Pega todo texto e tenta achar algo que não seja título ou preço
                            # (Difícil, vamos deixar genérico por enquanto ou 'Google Offer')

                            if title and price > 0 and link not in unique_products:
                                unique_products[link] = {
                                    "title": title,
                                    "price": price,
                                    "currency": "BRL",
                                    "link": link,
                                    "image": image,
                                    "store": store
                                }
                    except Exception as e:
                        continue
                
                products = list(unique_products.values())
                print(f"🔧 Heurística encontrou {len(products)} produtos candidatos.")

                if not products:
                    print("⚠️ Nenhum item encontrado via Heurística. Salvando screenshot e HTML.")
                    await page.screenshot(path="debug_google_heuristic.png")
                    with open("debug_google.html", "w", encoding="utf-8") as f:
                        f.write(soup.prettify())
                    print("📄 HTML salvo em debug_google.html")
                        
                print(f"✅ Google retornou {len(products)} produtos.")
                
            except Exception as e:
                print(f"❌ Erro no Google Scraper: {e}")
            finally:
                await browser.close()
                
        return products
