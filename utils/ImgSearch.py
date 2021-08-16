import asyncio

from PicImageSearch import AsyncSauceNAO, NetWork

async def main():
    async with NetWork() as client:
        saucenao = AsyncSauceNAO(client=client)
        raw = await saucenao.search("https://raw.githubusercontent.com/lingluo-maple/lingluo-maple.github.io/master/images/thumb/thumb_1.webp")
        print(raw)

asyncio.run(main())