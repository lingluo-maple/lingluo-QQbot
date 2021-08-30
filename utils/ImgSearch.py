import asyncio

from PicImageSearch import AsyncSauceNAO, NetWork

async def saucenao(url):
    async with NetWork() as client:
        api_key = "9c228b996e490b32381fcbedde134d7d954f89bb"
        saucenao = AsyncSauceNAO(client=client, api_key=api_key)
        res = await saucenao.search(url)
        raw = res.raw[0]
        title = raw.title
        url = raw.url
        pid = raw.pixiv_id
        similarity = raw.similarity
        return [title, url, pid, similarity]
