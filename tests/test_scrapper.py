import asyncio
from app.scraper import scrape_promptior


async def test():
    results = await scrape_promptior()
    for item in results:
        print(f"URL: {item['url']}")
        print(f"Contenido: {item['content'][:200]}...")

asyncio.run(test())
