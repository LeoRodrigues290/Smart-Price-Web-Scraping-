import requests
from bs4 import BeautifulSoup
from .base import BaseScraper
import re

class MercadoLivreScraper(BaseScraper):
    def search(self, query: str) -> list:
        print(f"🔎 Iniciando busca na API do Mercado Livre para: {query}")
        
        # Usando a API oficial pública (muito mais robusta que HTML scraping)
        # Doc: https://developers.mercadolibre.com.ar/en_US/item-search-items
        url = f"https://api.mercadolibre.com/sites/MLB/search"
        params = {"q": query, "limit": 10}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            products = []
            
            for item in results:
                try:
                    # Tenta pegar imagem em alta resolução, se não tiver usa thumbnail
                    image = item.get("thumbnail", "")
                    # Tenta melhorar a resolução da thumb
                    if image:
                        image = image.replace("-I.jpg", "-V.jpg")

                    products.append({
                        "title": item.get("title"),
                        "price": float(item.get("price", 0)),
                        "currency": item.get("currency_id", "BRL"),
                        "link": item.get("permalink"),
                        "image": image,
                        "store": "Mercado Livre"
                    })
                except Exception as e:
                    print(f"Erro ao processar item da API: {e}")
                    continue
            
            print(f"✅ Encontrados {len(products)} produtos via API.")
            return products

        except requests.exceptions.RequestException as e:
            print(f"❌ Erro na requisição API ML: {e}")
            return []
