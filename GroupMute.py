from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import asyncio

from graia.application.message.elements.internal import Plain, At
from graia.application.group import Group, Member

async def group_mute(app: GraiaMiraiApplication,group,member,message):
    user = str(member.permission)
    if user == 'MemberPerm.Member':
    #发言者权限为成员
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("你的权限不足")
        ]))
        return False
    bot = str(group.accountPerm)
    if bot == 'MemberPerm.Member':
    #机器人权限为成员
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("机器人权限不足")
        ]))
        return False
    try:
        beMute = message.get(At)[0].target
    except IndexError:
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("参数错误,请输入要禁言的人")
        ]))
        return False
    try:
        muteTime = int(message.asDisplay()[5:])
    except ValueError:
        await app.sendGroupMessage(group,MessageChain.create([
            Plain("参数错误,请设置禁言时间(单位:秒)")
        ]))
        return False
    if beMute == config["host"]:
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
    elif user == 'MemberPerm.Administrator' or user == 'MemberPerm.Owner' and beMute != config["Host"]:
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
