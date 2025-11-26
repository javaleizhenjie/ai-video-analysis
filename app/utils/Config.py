import json
import os
from framework.settings import BASE_DIR
class Config:
    def __init__(self):

        BASE_DIR_PARENT_DIR = os.path.dirname(BASE_DIR) # 根目录的父级目录
        filepath = os.path.join(BASE_DIR_PARENT_DIR, "config.json")
        print("Config.__init__",os.path.abspath(__file__))
        print("Config.__init__,filepath=%s"%filepath)

        f = open(filepath, 'r', encoding='gbk')
        content = f.read()
        config_data = json.loads(content)
        f.close()

        print("Config.__init__",config_data)

        self.code = config_data.get("code") #v3.52新增
        self.name = config_data.get("name") #v3.52新增
        self.describe = config_data.get("describe") #v3.52新增
        self.host = config_data.get("host")
        self.adminPort =config_data.get("adminPort")
        self.analyzerPort =config_data.get("analyzerPort")
        self.mediaHttpPort =config_data.get("mediaHttpPort")
        self.mediaRtspPort =config_data.get("mediaRtspPort")
        self.adminHost = "http://"+self.host +":"+ str(self.adminPort)         # http://127.0.0.1:9991
        self.analyzerHost = "http://"+self.host +":"+ str(self.analyzerPort)   # http://127.0.0.1:9993
        self.mediaHttpHost = "http://"+self.host +":"+ str(self.mediaHttpPort) # http://127.0.0.1:9992
        self.mediaWsHost = "ws://"+self.host +":"+ str(self.mediaHttpPort)     # http://127.0.0.1:9992
        self.mediaRtspHost = "rtsp://"+self.host +":"+ str(self.mediaRtspPort) # http://127.0.0.1:9994
        self.mediaSecret = config_data.get("mediaSecret")
        self.uploadDir = config_data.get("uploadDir")
        self.modelDir = config_data.get("modelDir")
        self.saveAlarmType = int(config_data.get("saveAlarmType",1))
        self.saveAlarmUrl = config_data.get("saveAlarmUrl", "").strip()  # v3.52新增，上传报警数据到xcnvs服务器

        self.uploadAlarmDir = os.path.join(self.uploadDir,"alarm")
        self.uploadDir_www = "/static/upload/"


    def __del__(self):
        pass

    def show(self):
        pass


