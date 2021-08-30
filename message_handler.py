import asyncio
import logging
import os
import re
from pathlib import Path

from avilla.builtins.elements import Image, PlainText
from avilla.builtins.profile import GroupProfile
from avilla.execution.message import MessageSend
from avilla.execution.request import RequestApprove, RequestDeny
from avilla.execution.fetch import FetchMember, FetchMembers
from avilla.group import Group
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship
from sqlalchemy import exc

from utils.error import LoliconAPIEmptyError, PixivNoSizeError
from utils.ImgSearch import saucenao
from utils.lolicon import get_img
from utils.pixiv import Pixiv
from utils.sql import add_new, update_time


async def member_send_time(sender_name, sender_id):
    result = await add_new(sender_id)
    if result:
        logging.info(f"{sender_name}({sender_id})记录成功")
    else:
        logging.info(f"{sender_name}({sender_id})已记录")
        await update_time(sender_id)

# async def event_handling(rs: Relationship, msg):
#     try:
#         request_id = re.search("([0-9]*)", msg).group(1)
#     except AttributeError:
#         message = MessageChain.create([PlainText("未找到事件id")])
#     try:
#         mode = re.search("event (.*?) [0-9]*", msg).group(1)
#     except AttributeError:
#         message = MessageChain.create([PlainText("未找到事件处理方式")])
#     if mode == "accept":
#         await rs.exec(RequestApprove(request_id))
#         message = MessageChain.create([PlainText("{request_id}已接受")])
#     elif mode == "refuse" or mode == "deny":
#         await rs.exec(RequestDeny(request_id))
#         message = MessageChain.create([PlainText("{request_id}已拒绝")])
#     else:
#         message = MessageChain.create([PlainText("输入accept接受, 输入refuse或deny拒绝")])
#     await rs.exec(MessageSend(message))

async def get_members(rs: Relationship):
    result = await rs.exec(FetchMembers(rs.ctx.profile.group))
    for member in result:
        logging.info(member)
        qq = member.id

async def rm_file(msg: str):
    params = msg.split()
    path = params[1]
    name = params[2]
    os.system(f"rm ./imgs/{path/name}*")
    logging.info("删除文件成功")

async def send_message(rs:Relationship, msg: str):
    params = msg.split()
    group = msg[1]
    text = params[2]
    message = MessageChain.create([PlainText(text)])
    await rs.exec(MessageSend(message), Group(group, GroupProfile()))


limit = []

async def pixiv_request(rs: Relationship, msg: str):
    global limit
    '''
    Pixiv search function
    search the image by pixiv id
    '''
    pid = re.search("pixiv *([0-9]*)", msg).group(1)
    size = re.search("pixiv *[0-9]* *(.*)", msg).group(1)
    if not size:
        size = "regular"

    if not pid:
        send_message = MessageChain.create([PlainText("指令识别错误，语法：pixiv [pid] <size>")])
    else:
        if len(limit) > 5:
            await rs.exec(MessageSend(MessageChain.create([PlainText("当前任务过多，请稍后再试")])))
            return

        limit.append(1)
        await rs.exec(MessageSend(MessageChain.create([PlainText("指令已收到，请稍后")])))
        pixiv = Pixiv()
        urls = await pixiv.get_img(pid, size)
        if not urls:
            send_message = MessageChain.create([PlainText(f"PID: {pid}不存在")])
        else:
            try:
                img_names = await pixiv.download_img(urls)
                send_message = MessageChain.create([PlainText(pid)])
                for img_name in img_names:
                    img = Image.fromLocalFile(Path(f"imgs/pixiv/{img_name}"))
                    new_message = MessageChain.create([img])
                    send_message.plus(new_message)
            except PixivNoSizeError:
                send_message = MessageChain.create([PlainText(f"没有{size}尺寸的图")])
    logging.info(send_message)
    await rs.exec(MessageSend(send_message))
    limit.pop()


async def lolicon_imgs(rs: Relationship, params: str, force: bool):
    """Get image from Lolicon API"""
    if len(limit) > 5:
        await rs.exec(MessageSend(MessageChain.create([PlainText("当前任务过多，请稍后再试")])))
        return
    limit.append(1)
    if "或" in params:
        params = params.replace("或", "|")
    if "和" in params:
        params = params.replace("和", "&tag=")
    try:
        res = await get_img(params, force)
        pid, title, name = res[0], res[1], res[3]
        message = MessageChain.create([PlainText(f"你要的色图: PID{pid}\n标题: {title}\n")])
        img = Image.fromLocalFile(Path(f"imgs/lolicon/{name}"))
        new_message = MessageChain.create([img])
        message.plus(new_message)
    except LoliconAPIEmptyError:
        message = MessageChain.create([PlainText("无此tag")])
    await rs.exec(MessageSend(message))
    limit.pop()


async def image_search(rs: Relationship, message: MessageChain):
    try:
        img = message.get_first(Image)
    except IndexError:
        return
    url = img.provider.url
    result = await saucenao(url)
    await rs.exec(MessageSend(MessageChain.create([PlainText(f'''搜图结果：
    标题：{result[0]},
    url: {result[1]} 
    pid: {result[2]}
    相似度: {result[3]}''')]
                                                  )))

async def menus(rs: Relationship):
    message = MessageChain.create([PlainText('''目前功能: 
    1.loliconAPI调用: 来点(xx)色图 cmd: lolicon
    2.pixiv爬取: pixiv [pid] <size> cmd: pixiv
    3.以图搜图: 测试中''')])
    await rs.exec(MessageSend(message))


async def bot_help(rs: Relationship, cmd: str):
    if not cmd:
        message = MessageChain.create([
            PlainText("指令语法：\n关键词 + 参数\n方括号[]内为必须参数, 尖括号内为可选参数"),
            PlainText("示例：pixiv 11111111 original中 pixiv为关键词 11111111, original为参数")
        ])
    elif cmd == "pixiv":
        message = MessageChain.create([PlainText("指令：pixiv \n 语法： pixiv [pid] <size> \nsize默认值为regular")])
    elif cmd == "lolicon" or cmd == "来点色图":
        message = MessageChain.create([PlainText("指令：LoliconAPI\n语法：来点(.*)色图\n.*内为p站标签")])
    else:
        message = MessageChain.create([PlainText("本指令语法： help <cmd>")])
    await rs.exec(MessageSend(message))
