import asyncio
from pathlib import Path
from typing import NoReturn
import aiohttp
import aiofiles
import logging
import re

try:
    from .error import *
except ImportError:
    from error import *
    

logging.basicConfig(level=logging.INFO, format="%(asctime)s : %(message)s")

async def _get_data(params) -> dict:
    if not params:
        params = ""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.lolicon.app/setu/v2{params}") as rep:
            res = await rep.json()
            return res

async def _parser(res: dict) -> list:
    if res["error"]:
        raise LoliconAPIError
    rec_name = re.compile(r".*/(.*)$")
    try:
        pid = res["data"][0]["pid"]
        title = res["data"][0]["title"]
        url = res["data"][0]["urls"]["original"]
        name = name = re.search(rec_name, url).group(1)
    except IndexError:
        raise LoliconAPIEmptyError
    return [pid, title, url, name]

async def _download(url, name, force) -> NoReturn:
    file = Path(f"imgs/pixiv/{name}")
    if file.exists() and not force:
        logging.info(f"{name}已存在")
        return
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as rep:
                content = await rep.read()
        if not force:
            async with aiofiles.open(f"imgs/lolicon/{name}", "ab") as f:
                await f.write(content)
        else:
            async with aiofiles.open(f"imgs/lolicon/{name}", "wb") as f:
                await f.write(content)
        logging.info(f"{name}下载完毕")

async def get_img(params: str, force):
    if params:
        params = "?tag=" + params
    res = await _get_data(params)
    rep = await _parser(res)
    url = rep[2]
    name = rep[3]
    await _download(url, name, force)
    return rep

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_img("bucz"))