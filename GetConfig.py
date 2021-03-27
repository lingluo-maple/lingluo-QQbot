import sys
import yaml

def GetMahConfig():
    path = sys.path[0] + "/config/net.mamoe.mirai-api-http/setting.yml"
    with open(path) as f:
        file = f.read()
        mah_config = yaml.load(file,Loader=yaml.FullLoader)
    return mah_config

def GetConfig():
    path = sys.path[0] + "/config.yml"
    with open(path) as f:
        file = f.read()
        config = yaml.load(file,Loader=yaml.FullLoader)
    return config

if __name__ == "__main__":
    config = GetConfig()
    print(config)
    print(type(config))
    for i in config:
        print(i)
        print(config[i])
        print(type(i))
        
        