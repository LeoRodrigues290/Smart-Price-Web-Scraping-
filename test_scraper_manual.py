import asyncio
from backend.scrapers.mercadolivre import MercadoLivreScraper

async def test_scraper():
    scraper = MercadoLivreScraper()
    results = await scraper.search("iphone 13")
    
    print("-" * 50)
    for p in results[:3]:
        print(f"📱 {p['title']}")
        print(f"💰 R$ {p['price']}")
        print(f"🔗 {p['link']}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(test_scraper())
