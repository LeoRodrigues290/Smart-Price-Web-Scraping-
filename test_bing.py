import asyncio
from backend.scrapers.bing_shopping import BingShoppingScraper

async def test_scraper():
    print("Testando Bing Shopping Scraper...")
    scraper = BingShoppingScraper()
    results = await scraper.search("iphone 13")
    
    print("-" * 50)
    for p in results:
        print(f"🛍️ {p['store']}")
        print(f"📱 {p['title']}")
        print(f"💰 R$ {p['price']}")
        print(f"🔗 {p['link'][:50]}...")
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(test_scraper())
