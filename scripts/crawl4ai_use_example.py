import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://ieeexplore.ieee.org/abstract/document/9716741/",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())