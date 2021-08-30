import asyncio
import logging
import signal

from aiohttp.client import ClientSession
from avilla import Avilla
from avilla.builtins.elements import PlainText
from avilla.builtins.profile import FriendProfile, MemberProfile
from avilla.entity import Entity
from avilla.event.message import MessageEvent
from avilla.event.request import FriendAddRequest, GroupJoinRequest
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.network.clients.aiohttp import AiohttpWebsocketClient
from avilla.onebot.config import OnebotConfig, WebsocketCommunication
from avilla.onebot.protocol import OnebotProtocol
from avilla.relationship import Relationship
from graia.broadcast import Broadcast
from yarl import URL

from utils.sql import query
from config import get_config, save_config
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
    """全局消息处理函数"""
    msg = message.as_display()
    profile = rs.ctx.profile
    if isinstance(profile, FriendProfile):
        # 私聊
        name = rs.ctx.profile.name
        qq = rs.ctx.id
        logging.info(f"收到内{name}({qq})的消息: {msg}")
        # if msg.startswith("event") and qq == "1274911913":
        #     await event_handling(rs, msg)
        if msg.startswith("pixiv"):
            await pixiv_request(rs, msg)
        if "来点" in msg and ("色图" in msg or "涩图" in msg):
            params = re.search("来点(.*)的?色|涩图", msg)
            if params:
                params = params.group(1)
            await lolicon_imgs(rs, params)
        if "以图搜图" in msg:
            await image_search(rs, message)
        return
        
    if isinstance(profile, MemberProfile):
        # 群聊
        sender_name = rs.ctx.profile.name
        sender_id = rs.ctx.id
        group_id = rs.ctx.profile.group.id
        group_name = rs.ctx.profile.group.profile.name
        permission = rs.ctx.profile.role
        logging.info(f"收到{group_name}({group_id})内{sender_name}({sender_id})的消息: {msg}")
        if msg.startswith("send") and sender_id == "1274911913":
            logging.info("收到消息")
            await send_message(rs, msg)
        try:
            global_control = config["Group"][group_id]["global"]
        except KeyError:
            config["Group"][group_id] = {"global": False}
            config["Group"][group_id]["name"] = group_name
            global_control = False
        if (sender_id == "1274911913" or permission > 0) and msg == "bot on" and global_control is False:
            config["Group"][group_id]["global"] = True
            await rs.exec(MessageSend(MessageChain.create([PlainText("开启成功")])))
        
        if sender_id == "1274911913" and msg == "member_list":
            await get_members(rs)

        if global_control:
            # test
            if (sender_id == "1274911913" or permission > 0) and msg == "test":
                await rs.exec(MessageSend(MessageChain.create([PlainText('Hello, World!')])))
            # 开关
            if (sender_id == "1274911913" or permission > 0) and msg == "bot off":
                config["Group"][group_id]["global"] = False
                await rs.exec(MessageSend(MessageChain.create([PlainText("关闭成功")])))
            # 请求
            # if msg.startswith("event") and (permission > 0 or sender_id == "1274911913"):
            #     await event_handling(rs, msg)
            # functions
            if msg.startswith("pixiv"):
                await pixiv_request(rs, msg)
            if "来点" in msg and ("色图" in msg or "涩图" in msg):
                params = re.search("来点(.*)的?色|涩图", msg)
                if params:
                    params = params.group(1)
                if "-f" or "--force" in msg:
                    force = True
                else:
                    force = False
                await lolicon_imgs(rs, params, force)
            if "菜单" in msg:
                await menus(rs)
            if "help" in msg:
                try:
                    cmd = re.search("help [-]*?(.*)", msg).group(1)
                except AttributeError:
                    cmd = ""
                await bot_help(rs, cmd)
            if "以图搜图" in msg:
                await image_search(rs, message)
            if group_id == "792068440":
                await member_send_time(sender_name, sender_id)
            if sender_id == "1274911913" and msg == "query":
                result = await query()
                await rs.exec(MessageSend([PlainText(result)]))
        return


@broadcast.receiver(FriendAddRequest)
async def friend_request(rs: Relationship, event: FriendAddRequest):
    name = event.ctx.profile.name
    qq = event.ctx.id
    msg = event.comment
    id = event.request_id
    message=MessageChain.create([PlainText(f"收到{name}({qq})的好友请求, 请求id:{id}\n请求信息:{msg}")])
    await rs.exec(MessageSend(message), target=Entity("1274911913", profile=FriendProfile(name="", remark="")))
    

@broadcast.receiver(GroupJoinRequest)
async def friend_request(rs: Relationship, event: GroupJoinRequest):
    group_id = event.group.id
    group_name = event.group.profile.name
    try:
        global_control = config["Group"][group_id]["global"]
    except KeyError:
        config["Group"][group_id] = {"global": False}
        config["Group"][group_id]["name"] = group_name
        global_control = False
    if global_control:
        name = event.ctx.profile.name
        qq = event.ctx.id
        msg = event.comment
        id = event.request_id
        message  =MessageChain.create([PlainText(f"收到{name}({qq})的入群请求, 请求id:{id}\n请求信息:{msg}")])
        logging.info(message)
        await rs.exec(MessageSend(message), target=event.group)


def sigintHandler(signum, frame):
    logging.info("进程结束中")
    asyncio.run(save_config(config))
    logging.info("配置保存完成")
    loop.close()
    exit()


try:
    signal.signal(signal.SIGTERM, sigintHandler)
    loop.run_until_complete(avilla.launch())
    loop.run_forever()
except KeyboardInterrupt:
    exit()
finally:
    asyncio.run(save_config(config))
    loop.close()
