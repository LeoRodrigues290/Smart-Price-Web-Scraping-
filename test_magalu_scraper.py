import asyncio
from backend.scrapers.magazineluiza import MagazineLuizaScraper

async def test_scraper():
    scraper = MagazineLuizaScraper()
    results = await scraper.search("iphone 13")
    
    print("-" * 50)
    for p in results:
        print(f"🛍️ {p['store']}")
        print(f"📱 {p['title']}")
        print(f"💰 R$ {p['price']}")
        print(f"🔗 {p['link']}")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(test_scraper())
