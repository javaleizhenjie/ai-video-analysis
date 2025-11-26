import json
import os
import time
from datetime import datetime
import base64
import shutil
from app.utils.ZLMediaKit import ZLMediaKit
from app.utils.Analyzer import Analyzer
from app.utils.DjangoSql import DjangoSql
from app.utils.Config import Config
from app.models import *
from django.http import HttpResponse
from framework.settings import PROJECT_UA,PROJECT_FLAG,PROJECT_VERSION,PROJECT_BUILT,PROJECT_ADMIN_START_TIMESTAMP


g_config = Config()
g_zlm = ZLMediaKit(config=g_config)
g_analyzer = Analyzer(g_config.analyzerHost)
g_djangoSql = DjangoSql()
g_session_key_user = "user"
g_pull_stream_types = [
    {
        "id": 1,
        "name": "RTSP"
    },
    {
        "id": 2,
        "name": "RTMP"
    },
    {
        "id": 3,
        "name": "FLV"
    },
    {
        "id": 4,
        "name": "HLS"
    },
    {
        "id": 21,
        "name": "GB28181"
    },
    {
        "id": 31,
        "name": "cRTSP"
    },
    {
        "id": 32,
        "name": "cRTMP"
    }
]
g_audio_types = [
    {
        "type": 0,
        "name": "静音",
    },
    {
        "type": 1,
        "name": "原始音频",
    }
]

def getUser(request):
    user = request.session.get(g_session_key_user)
    return user

def GetStream(app, name):
    __mediaInfo = g_zlm.getMediaInfo(app=app, name=name)
    is_online = 0
    video_codec_name = ""
    video_width = 0
    video_height = 0
    if __mediaInfo.get("ret"):
        is_online = 1
        video_codec_name = __mediaInfo.get("video_codec_name")  # 视频编码格式
        video_width = __mediaInfo.get("video_width")
        video_height = __mediaInfo.get("video_height")

    stream = {
        "is_online": is_online,
        # "code": code,
        "app": app,
        "name": name,
        # "produce_speed": produce_speed,
        # "video": video_str,
        "video_codec_name": video_codec_name,
        "video_width": video_width,
        "video_height": video_height,
        # "audio": audio_str,
        # "originUrl": d.get("originUrl"),  # 推流地址
        # "originType": d.get("originType"),  # 推流地址采用的推流协议类型
        # "originTypeStr": d.get("originTypeStr"),  # 推流地址采用的推流协议类型（字符串）
        # "clients": d.get("totalReaderCount"),  # 客户端总数量
        # "schemas_clients": schemas_clients,
        # "videoUrl": g_zlm.get_wsMp4Url(app, name),
        "wsHost": g_zlm.get_wsHost(),
        "wsMp4Url": g_zlm.get_wsMp4Url(app, name),
        "wsFlvUrl": g_zlm.get_wsFlvUrl(app, name),
        "httpMp4Url": g_zlm.get_httpMp4Url(app, name),
        "httpFlvUrl": g_zlm.get_httpFlvUrl(app, name),
        "rtspUrl": g_zlm.get_rtspUrl(app, name)
    }
    return stream

def readAllStreamData():
    data = g_djangoSql.select("select * from av_stream order by id desc")
    return data

def AllStreamStartForward():
    __ret = False
    __msg = "未知错误"

    try:
        online_data = g_zlm.getMediaList()
        online_dict = {}
        mediaServerState = g_zlm.mediaServerState
        if not mediaServerState:
            # 流媒体服务不在线，全部更新下线状态
            g_djangoSql.execute("update av_stream set forward_state=0")
            __msg = "流媒体服务不在线，无法开启转发！"
        else:
            for d in online_data:
                app_name = "{app}_{name}".format(app=d["app"], name=d["name"])
                online_dict[app_name] = d
            streams = Stream.objects.all()

            successCount = 0
            errorCount = 0
            for stream in streams:
                stream_app_name = "{app}_{name}".format(app=stream.app, name=stream.name)
                if online_dict.get(stream_app_name):  # 当前流已经在线，不用再次请求转发
                    successCount += 1
                else:
                    __media_ret = g_zlm.addStreamProxy(app=stream.app,
                                                         name=stream.name,
                                                         origin_url=stream.pull_stream_url)
                    if __media_ret:
                        stream.forward_state = 1
                        stream.save()
                        successCount += 1
                    else:
                        errorCount += 1

            if successCount > 0:
                __ret = True
            __msg = "转发成功%d条,转发失败%d条" % (successCount, errorCount)

    except Exception as e:
        __msg = "开启转发失败：" + str(e)

    return __ret, __msg

def f_parseGetParams(request):
    params = {}
    for k in request.GET:
        params.__setitem__(k, request.GET.get(k))

    return params


def f_parsePostParams(request):
    params = {}
    for k in request.POST:
        params.__setitem__(k, request.POST.get(k))

    # 接收json方式上传的参数
    if not params:
        params = request.body.decode('utf-8')
        params = json.loads(params)

    return params


def f_responseJson(res):
    def json_dumps_default(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError

    return HttpResponse(json.dumps(res, default=json_dumps_default), content_type="application/json")

def f_removeAlarmAndStorage(alarm_id):
    # 删除报警视频对应的数据库数据以及文件数据
    try:
        print("f_removeAlarmAndStorage()",alarm_id)

        alarm = Alarm.objects.get(id=alarm_id)
        image_path = alarm.image_path
        video_path = alarm.video_path
        alarm.delete()

        if image_path.startswith('alarm/'):
            image_path_abs = os.path.join(g_config.uploadDir, image_path)

            if os.path.exists(image_path_abs):
                image_path_dir = os.path.dirname(image_path_abs)
                shutil.rmtree(image_path_dir)
        else:
            raise Exception("image_path should start with 'alarm'")

        return True
    except Exception as e:
        print("f_removeAlarmAndStorage() error: %s" % str(e))

    return False

def f_calcuFileBase64Str(filepath):
    __base64Str = "encode error"
    try:
        if os.path.exists(filepath):
            f = open(filepath, 'rb')
            f_byte = f.read()
            f.close()
            __base64Str = base64.b64encode(f_byte)
            __base64Str = __base64Str.decode("utf-8")  # str类型
        else:
            raise Exception("filepath not found")
    except Exception as e:
        print("f_calcuFileBase64Str error filepath:%s, e:%s" % (str(filepath),str(e)))
    return __base64Str