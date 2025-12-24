import asyncio
from backend.scrapers.google_shopping import GoogleShoppingScraper

async def test_scraper():
    print("Testando Google Shopping Scraper...")
    scraper = GoogleShoppingScraper()
    results = await scraper.search("iphone 13")
    
    print("-" * 50)
    for p in results:
        print(f"🛍️ {p['store']}")
        print(f"📱 {p['title']}")
        print(f"💰 R$ {p['price']}")
        print(f"🔗 {p['link'][:50]}...") # Link curto
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(test_scraper())
