import logging
import re
from utils.error import LoliconAPIEmptyError, PixivNoSizeError

from avilla.builtins.elements import PlainText, Image
from avilla.execution.message import MessageSend
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship
from pathlib import Path
from functools import wraps

from utils.pixiv import Pixiv
from utils.sql import add_new, update_time
from utils.lolicon import get_img

async def member_send_time(sender_name, sender_id):
    result = await add_new(sender_id)
    if result:
        logging.info(f"{sender_name}({sender_id})记录成功")
    else:
        logging.info(f"{sender_name}({sender_id})已记录")
        await update_time(sender_id)

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
            await rs.exec(MessageSend([PlainText("当前任务过多，请稍后再试")]))
            return
        limit.append(1)
        await rs.exec(MessageSend([PlainText("指令已收到，请稍后")]))
        limit.append(1)
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


async def lolicon_imgs(rs: Relationship,params: str):
    '''Get image from Lolicon API'''
    if len(limit) > 5:
            await rs.exec(MessageSend([PlainText("当前任务过多，请稍后再试")]))
            return
    limit.append(1)
    if "或" in params:
        params = params.replace("或", "|")
    if "和" in params:
        params = params.replace("和", "&tag=")
    try:
        res = await get_img(params)
        pid, title, name = res[0], res[1], res[3]
        message = MessageChain.create([PlainText(f"你要的色图: PID{pid}\n标题: {title}\n")])
        img = Image.fromLocalFile(Path(f"imgs/lolicon/{name}"))
        new_message = MessageChain.create([img])
        message.plus(new_message)
    except LoliconAPIEmptyError:
        message = MessageChain.create([PlainText("无此tag")])
    await rs.exec(MessageSend(message))
    limit.pop()
