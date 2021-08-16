import asyncio
import logging
import re
from pathlib import Path

import aiofiles
import aiohttp

from utils.error import PixivNoSizeError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s :%(message)s")

class Pixiv():
    def __init__(self) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
             (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        }
        self.dns = {
            "m.pixiv.net": "210.140.131.219",
            "pixiv.net": "210.140.131.223",
            "www.pixiv.net": "210.140.131.223",
        }
    
    async def get_index(self):
        headers = self.headers
        headers["host"] = "www.pixiv.net"
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{self.dns['www.pixiv.net']}", headers=headers, ssl=False) as res:
                result = await res.text()
                with open("index.html","a", encoding="utf8") as f:
                    f.write(result)
                logging.info("获取成功")

    async def get_img(self, pid, size: str) -> list:
        '''
        获取Pixiv某pid下的所有原图链接

        Args:
            pid (str): 需要获取的pid
            size (str): 获取图片的尺寸

        Return:
            result (list): 获取到的所有图片的链接
        '''
        url = f"https://{self.dns['www.pixiv.net']}/ajax/illust/{pid}/pages?lang=zh"
        headers = self.headers
        headers["host"] = "www.pixiv.net"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, ssl=False) as rep:
                    json = await rep.json()
                    result = await self._parser(json, size)
                    if not result:
                        logging.warning(f"{pid}不存在")
                    else:
                        logging.info(f"PID: {pid} 获取成功")
                    return result
        except asyncio.TimeoutError:
            logging.warning("pixiv获取超时")
            return

    async def download_img(self, img_url_list: list) -> list:
        headers = self.headers
        # rec_host = re.compile(r"https://(.*?)/")
        rec_address = re.compile(r"https://.*?/(.*)")
        rec_name = re.compile(r".*/(.*)$")
        names = []
        for img_url in img_url_list:
            # host = re.search(rec_host, img_url).group(1)
            address = re.search(rec_address, img_url).group(1)
            name = re.search(rec_name, img_url).group(1)
            file = Path(f"imgs/pixiv/{name}")
            if file.exists():
                logging.info(f"{name}已存在")
                names.append(name)
                continue
            headers["host"] = "i.pixiv.cat"
            # headers["Referer"] = "https://www.pixiv.net"
            logging.info(f"正在下载{name}, {img_url}")
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://i.pixiv.cat/{address}", headers=headers, ssl=False) as rep:
                        content = await rep.read()
                        logging.debug(f"headers:{headers}")
            except asyncio.TimeoutError:
                logging.warning("图片下载超时")
                return
            async with aiofiles.open(f"imgs/pixiv/{name}","ab") as f:
                await f.write(content)
            names.append(name)
        logging.info("全部下载完成")
        return names
    
    async def _parser(self, res: dict,size: str) -> list:
        if res["error"]:
            return
        body = res["body"]
        urls = []
        for i in body:
            try:
                url = i["urls"][size]
                urls.append(url)
            except KeyError:
                logging.error("没有该尺寸的图")
                raise PixivNoSizeError
        return urls
