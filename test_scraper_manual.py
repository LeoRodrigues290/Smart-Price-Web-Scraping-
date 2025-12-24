from backend.scrapers.mercadolivre import MercadoLivreScraper

def test_scraper():
    scraper = MercadoLivreScraper()
    results = scraper.search("iphone 13")
    
    print("-" * 50)
    for p in results[:3]:
        print(f"📱 {p['title']}")
        print(f"💰 R$ {p['price']}")
        print(f"🔗 {p['link']}")
        print("-" * 20)

if __name__ == "__main__":
    test_scraper()
