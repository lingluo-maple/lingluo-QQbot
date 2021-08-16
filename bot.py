import asyncio
import logging
import re

from aiohttp.client import ClientSession
from avilla import Avilla
from avilla.builtins.elements import PlainText, Image
from avilla.event.message import MessageEvent
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.network.clients.aiohttp import AiohttpWebsocketClient
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
from avilla.onebot.protocol import OnebotProtocol
from avilla.relationship import Relationship
from graia.broadcast import Broadcast
from pathlib import Path
from yarl import URL

from GetConfig import get_config
from utils.pixiv import Pixiv
from utils.sql import add_new, update_time, query
from message_handler import *

logging.basicConfig(
    format="%(asctime)s - [%(levelname)s]: %(message)s",
    level=logging.INFO,
)

try:
    config = get_config()
    logging.info("获取机器人配置成功")
except FileNotFoundError:
    logging.error("配置文件未找到")
    mode = input("输入y/Y继续，输入其他退出")
    if mode != "y" or mode != "Y":
        exit()
    else:
        logging.warning("程序将继续运行")

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
session = ClientSession(loop=loop)
avilla = Avilla(
    broadcast,
    OnebotProtocol,
    {"ws": AiohttpWebsocketClient(session)},
    {
        OnebotProtocol:
        OnebotConfig(
            access_token="avilla-test",
            bot_id=config["bot_qq"],
            communications={
                "ws":
                WebsocketCommunication(api_root=URL("ws://127.0.0.1:6700/"))
            },
        )
    },
)

@broadcast.receiver(MessageEvent)
async def global_message_handler(rs: Relationship, message: MessageChain):
    '''全局消息处理函数'''
    msg = message.as_display()
    sender_name = rs.ctx.profile.name
    sender_id = rs.ctx.id
    group_id = rs.ctx.profile.group.id
    group_name = rs.ctx.profile.group.profile.name
    logging.info(f"{group_name}({group_id})-{sender_name}({sender_id}): {msg}")
    if sender_id == "1274911913":
        await event_receiver_test(rs, msg)
    if msg.startswith("pixiv"):
        await pixiv_request(rs, msg)
    if "来点" in msg and "色图" in msg:
        params = re.search("来点(.*)色图", msg)
        if params:
            params = params.group(1)
        await lolicon_imgs(rs, params)
    # if group_id == "792068440":
    #     await member_send_time(sender_name, sender_id)
    # if (group_id == "792068440" or group_id == "962618214") and sender_id == "1274911913" and msg == "query":
    #     result = await query()
    #     await rs.exec(MessageSend([PlainText(result)]))

async def member_send_time(sender_name, sender_id):
    result = await add_new(sender_id)
    if result:
        logging.info(f"{sender_name}({sender_id})记录成功")
    else:
        logging.info(f"{sender_name}({sender_id})已记录")
        await update_time(sender_id)

async def event_receiver_test(rs: Relationship, msg: str):
    "Test function"
    if msg == "test":
        await rs.exec(MessageSend([PlainText('Hello, World!')]))

try:
    loop.run_until_complete(avilla.launch())
    loop.run_forever()
except KeyboardInterrupt:
    exit()
finally:
    loop.close()
