from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
import asyncio
import time

from graia.application.message.elements.internal import Plain, Image, At, Json
from graia.application.friend import Friend
from graia.application.group import Group, Member

from GetConfig import GetConfig, GetMahConfig

try:
    mah_config = GetMahConfig()
    print("获取mah配置成功")
    config = GetConfig()
    print("获取机器人配置成功")
except FileNotFoundError:
    print("配置文件未找到:请确保文件与mirai在同一目录")
    exit()

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host=f"http://localhost:{mah_config['port']}", 
        authKey=mah_config["authKey"], # 填入 authKey
        account=config["Robot"], # 你的机器人的 qq 号
        websocket=True 
    )
)

async def group_permission(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain):
# 获取群权限
    user = str(member.permission)[11:]
    #发言者权限
    bot = str(group.accountPerm)[11:]
    #机器人权限
    try:
        perm = config[str(member.id)]
    except KeyError:
        perm = "User"
    await app.sendGroupMessage(group,MessageChain.create([
        Plain("您的权限为:"), Plain(user), Plain("\n"),
        Plain("机器人的权限为:"), Plain(bot), Plain("\n"),
        Plain("您对机器人的权限为:"), Plain(perm)
    ]))
    
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
    elif user == 'MemberPerm.Administrator' or user == 'MemberPerm.Owner' and beMute != 1274911913:
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



@bcc.receiver("FriendMessage")
async def friend_test_function(app: GraiaMiraiApplication, friend: Friend):
    await app.sendFriendMessage(friend, MessageChain.create([
        Plain("Hello, World!")
    ]))
        

#入群欢迎
@bcc.receiver("MemberJoinEvent")
async def group_welocme(app: GraiaMiraiApplication, group: Group, member: Member):
    await app.sendGroupMessage(group,MessageChain.create([
        Plain(f"欢迎{member.name}({member.id})入群")
    ]))
    if group.id == 960879609 or group.id in config["DebugGroup"]:
        await app.sendGroupMessage(group,MessageChain.create([
            Image.fromLocalFile(config["image"]["YY_yyds"])
        ]))
                

#测试功能 仅测试群
@bcc.receiver("GroupMessage")
async def group_test_function(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain):
    if group.id in config["DebugGroup"]:
        msg = message.asDisplay()
        if msg == "/test":
            await app.sendGroupMessage(group,MessageChain.create([
                Plain("Hello,World")
            ]))
        elif msg == "/testAt":
            await app.sendGroupMessage(group,MessageChain.create([
                Plain("Hello"), At(member.id)
            ]))
        elif message.asDisplay() == "/list":
            get = str(await app.groupList())
            await app.sendGroupMessage(group,MessageChain.create([
                Plain(get)
            ]))
        elif msg == "/WelcomeTest":
            await group_welocme(app,group,member)
    

#Main 全群(在设置中)通用
@bcc.receiver("GroupMessage")
async def group_message_listener(app: GraiaMiraiApplication, group: Group, member: Member, message: MessageChain):
    if group.id in config["group"]:
        msg = message.asDisplay()
        if msg.startswith("/mute"):
            await group_mute(app,group,member,message)
        if msg == "信息":
            await group_peission(app,group,member,message)

    
app.launch_blocking()

