import psutil
import os
import time
import logging
import json
import threading
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

LOGFILE_TIMEFMT = "%Y-%m-%d_%H%M%S"
LOGFILE_WHEN = 'd'
LOGFILE_BACKUPCOUNT = 7

class App():
    def __init__(self, process_name, process_start_path):
        self.__process_name = process_name  # 例 MediaServer
        self.__process_start_path = process_start_path  # 例 D:\\bin\\MediaServer -c D:\\bin\\config.json


    def get_info(self):

        info = {
            "process": self.__process_name,
            "started": None,
            "status": None,
            "pid": None,
            "state": False
        }
        try:
            for pid in psutil.pids():
                process = psutil.Process(pid)

                process_name_lower = process.name().lower()
                __process_name_lower = self.__process_name.lower()

                if process_name_lower.startswith(__process_name_lower):

                    info["status"] = process.status()
                    info["pid"] = pid
                    timeArray = time.localtime(int(process.create_time()))
                    dateStr = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    info["started"] = dateStr
                    info["state"] = True
        except Exception as e:
            info["error"] = str(e)

        return info

    def __start_process(self):
        logger.info("start process_name=%s,process_start_path=%s" % (self.__process_name, self.__process_start_path))
        state = False
        try:
            res = os.popen(self.__process_start_path)
            res.read()
            state = True
        except Exception as e:
            logger.error("start %s error: %s" % (self.__process_name, str(e)))

        return state

    def __kill_process(self):

        for pid in psutil.pids():
            try:
                process = psutil.Process(pid)
                # print(u"进程名 %-20s  内存利用率 %-18s 进程状态 %-10s 创建时间 %-10s "
                #       % (p.name(), p.memory_percent(), p.status(), p.create_time()))

                process_name_lower = process.name().lower()
                __process_name_lower = self.__process_name.lower()

                if process_name_lower.startswith(__process_name_lower):
                    try:
                        process.kill()
                    except Exception as e:
                        logger.error("__kill_process error：%s" % (str(e)))

            except Exception as e:
                logger.error("__kill_process error：%s" % (str(e)))

        return True

    def start(self):

        self.__kill_process()
        self.__start_process()
class VideoAnalyzer():
    def __init__(self,adminPort):
        self.__adminPort = adminPort
    def run(self):

        ts = []
        self.__apps = []

        app = App("MediaServer","MediaServer\\MediaServer.exe -c MediaServer\\config.ini")
        t = threading.Thread(target=app.start)
        ts.append(t)
        self.__apps.append(app)

        app = App("manage","Admin\\manage.exe runserver 0.0.0.0:%s --noreload"%str(self.__adminPort))
        t = threading.Thread(target=app.start)
        ts.append(t)
        self.__apps.append(app)

        app = App("Analyzer","Analyzer\\Analyzer.exe -f config.json")
        t = threading.Thread(target=app.start)
        ts.append(t)
        self.__apps.append(app)

        t = threading.Thread(target=self.__recordLog)
        ts.append(t)

        for t in ts:
            t.start()
        for t in ts:
            t.join()
    def __recordLog(self):

        recordLog_count = 0
        while True:
            time.sleep(30)

            recordLog_count += 1
            for app in self.__apps:
                info = app.get_info()
                info_str = str(info)
                logger.info("recordLog_count=%d,info=%s"%(recordLog_count,info_str))



def getLogger(logDir, is_show_console=False):
    if not os.path.exists(logDir):
        os.makedirs(logDir)

    fileName = os.path.join(logDir, "%s.log" % (datetime.now().strftime(LOGFILE_TIMEFMT)))
    level = logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(name)s %(lineno)s %(levelname)s %(message)s')

    # 最基础
    # fileHandler = logging.FileHandler(fileName, encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
    # fileHandler.setLevel(level)
    # fileHandler.setFormatter(formatter)
    # logger.addHandler(fileHandler)

    # 时间滚动切分
    # when:备份的时间单位，backupCount:备份保存的时间长度
    timedRotatingFileHandler = TimedRotatingFileHandler(fileName,
                                    when=LOGFILE_WHEN,
                                    backupCount=LOGFILE_BACKUPCOUNT,
                                    encoding='utf-8')

    timedRotatingFileHandler.setLevel(level)
    timedRotatingFileHandler.setFormatter(formatter)
    logger.addHandler(timedRotatingFileHandler)

    # 控制台打印
    if is_show_console:
        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(level)
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)

    return logger
if __name__ == '__main__':
    """
    
    // 根据 manage.spec 文件，打包程序
    pyinstaller manage.spec

    # 打包成可执行文件

    pyinstaller -F  VideoAnalyzer.py

    """

    logger = getLogger(logDir="log", is_show_console=True)
    logger.info("视频行为分析系统v%s built on 2025/09/25" % "3.52")
    logger.info("作者：北小菜，微信：bilibili_bxc，QQ：1402990689")

    try:
        filename = "config.json"
        if not os.path.exists(filename):
            raise Exception("启动配置文件config.json不存在!")
        f = open(filename, 'r', encoding='gbk')
        content = f.read()
        config_data = json.loads(content)

        f.close()
        logger.info(str(config_data))
        adminPort = int(config_data.get("adminPort")) #int

        videoAnalyzer = VideoAnalyzer(adminPort)
        videoAnalyzer.run()

    except Exception as e:
        logger.error(str(e))






