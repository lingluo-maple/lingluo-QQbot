import asyncio
import re

from graia.application import GraiaMiraiApplication, Session
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import At, Plain
from graia.broadcast import Broadcast


async def group_mute(app: GraiaMiraiApplication,group,member,message, config):
    "/mute @sb sometime"
    #获取机器人权限
    msg = message.asDisplay()
    # 更新后asDisplay可以获取到AT的QQ号
    bot = str(group.accountPerm)
    if bot == 'MemberPerm.Member':
    #机器人权限为成员
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("机器人权限不足")
        ]))
        return False
    # 获取被禁言者QQ号
    try:
        beMute = int(re.search(r"-n ([0-9]*)",msg).group(1))
        await app.sendGroupMessage(group,MessageChain.create([
            Plain(str(beMute))
        ]))
    except IndexError:
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("参数错误,请输入要禁言的人")
        ]))
        return False
    # 获取禁言时间
    try:
        muteTime = int(re.search(r"-t ([0-9]*)",msg).group(1))
        await app.sendGroupMessage(group,MessageChain.create([
            Plain(str(muteTime))
        ]))
    except ValueError:
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("参数错误,请设置禁言时间(单位:秒)")
        ]))
        return False
    if beMute == config["Host"]:
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("禁言失败，请选择其他人")
        ]))
    elif beMute == config["Robot"]:
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("禁言失败，机器人不可以禁言自己")
        ]))
    elif muteTime <= 0 or muteTime >= 2592000:
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("参数错误，禁言时间应大于0小于259200")
        ]))
    elif config["Permission"][member.id]  and beMute != config["Host"]:
    #发言者权限为管理员或群主
        try:
            await app.mute(group,beMute,muteTime)
        except PermissionError:
            await app.sendGroupMessage(group,MessageChain.create([
                Plain("权限错误")
            ]))
            return False
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("已禁言"), Plain(beMute), Plain("\n时间:"), Plain(muteTime), Plain("(秒)")
        ]))
