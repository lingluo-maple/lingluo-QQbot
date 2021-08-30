import asyncio
import logging
import aiofiles
import sys
import yaml

def get_mah_config():
    '''for mirai-api-http'''
    path = sys.path[0] + "/config/net.mamoe.mirai-api-http/setting.yml"
    with open(path,encoding="utf-8") as f:
        file = f.read()
        mah_config = yaml.load(file,Loader=yaml.FullLoader)
    return mah_config

def get_config():
    path = sys.path[0] + "/bot_conf.yml"
    with open(path,encoding="utf-8") as f:
        file = f.read()
        config = yaml.load(file,Loader=yaml.FullLoader)
    return config

async def save_config(config):
    config_text = yaml.dump(config)
    logging.info("配置保存成功")
    async with aiofiles.open("bot_conf.yml", "w") as f:
        await f.write(config_text)

async def main():
    a = 0
    while a < 99999999999:
        a += 1

if __name__ == "__main__":
    config = get_config()
    print(config)
    print(config["Group"])
    print(config["Group"]["962618214"])
    print(config["Group"]["962618214"]["global"])
    test = config["test"]
    if test:
        config["test"] = False
    else:
        config["test"] = True
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        exit()
    finally:
        asyncio.run(save_config(config))
        loop.close()