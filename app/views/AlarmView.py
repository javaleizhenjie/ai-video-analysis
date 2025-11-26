import requests
from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from app.utils.Common import buildPageLabels


def index(request):
    context = {
    }
    data = []

    params = f_parseGetParams(request)

    page = params.get('p', 1)
    page_size = params.get('ps', 10)
    try:
        page = int(page)
    except:
        page = 1

    try:
        page_size = int(page_size)
        if page_size > 20 or page_size < 10:
            page_size = 10
    except:
        page_size = 10

    skip = (page - 1) * page_size
    sql_data = "select * from av_alarm order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from av_alarm "

    count = g_djangoSql.select(sql_data_num)
    unread_count = 0
    if len(count) > 0:
        count = int(count[0]["count"])
        __data = g_djangoSql.select(sql_data)
        for i in __data:
            data.append({
                # "imageUrl":"http://127.0.0.1:9001/static/images/media.jpg",
                # "videoUrl":"http://127.0.0.1:9001/static/alarms/c4bb4965648175-1697194397420.mp4",
                "id": i["id"],
                "imageUrl": g_config.uploadDir_www + i["image_path"],
                "videoUrl": g_config.uploadDir_www + i["video_path"],
                "desc": i["desc"],
                "create_time": i["create_time"],
                "state": i["state"]
            })
        unread_count = g_djangoSql.select("select count(id) as count from av_alarm where state=0")
        if len(unread_count) > 0:
            unread_count = int(unread_count[0]["count"])
        else:
            unread_count = 0
    else:
        count = 0

    page_num = int(count / page_size)  # 总页数
    if count % page_size > 0:
        page_num += 1
    pageLabels = buildPageLabels(page=page, page_num=page_num)
    pageData = {
        "page": page,
        "page_size": page_size,
        "page_num": page_num,
        "count": count,
        "pageLabels": pageLabels
    }

    context["data"] = data
    context["pageData"] = pageData
    top_msg = ""
    if unread_count > 0:
        top_msg = "未读报警数据%d条" % unread_count

    context["top_msg"] = top_msg

    return render(request, 'app/alarm/index.html', context)
def api_openAdd(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        print("AlarmView.openAdd() params:",params)
        control_code = params.get("control_code")
        desc = params.get("desc")
        video_path = params.get("video_path")
        image_path = params.get("image_path")
        try:
            now_date = datetime.now()
            def __saveDb():
                alarm = Alarm()
                alarm.sort = 0
                alarm.control_code = control_code
                alarm.desc = desc
                alarm.video_path = video_path
                alarm.image_path = image_path
                alarm.create_time = now_date
                alarm.state = 0
                alarm.save()
            def __uploadServer():
                print("__uploadServer() start")
                __ret = False
                __msg = "未知错误"

                control = Control.objects.filter(code=control_code).first()
                stream = Stream.objects.filter(app=control.stream_app,name=control.stream_name).first()
                if stream:
                    stream_app = stream.app
                    stream_name = stream.name
                    stream_code = stream.code
                    stream_nickname = stream.nickname
                else:
                    stream_app = control.stream_app
                    stream_name = control.stream_name
                    stream_code = control.stream_name
                    stream_nickname = control.stream_name

                algorithm = g_djangoSql.select("select * from av_algorithm where code='%s' limit 1"%control.algorithm_code)
                if len(algorithm) > 0:
                    algorithm = algorithm[0]
                    flowCode = algorithm["code"]
                    flowName = algorithm["name"]
                else:
                    flowCode = control.algorithm_code
                    flowName = control.algorithm_code

                interface_video_array = []
                interface_video_count = 1
                interface_image_array = []
                interface_image_count = 1

                if interface_video_count > 0:
                    video_path_abs = os.path.join(g_config.uploadDir, video_path)
                    if os.path.exists(video_path_abs):
                        __base64Str = f_calcuFileBase64Str(video_path_abs)
                        interface_video_array.append({
                            "index": 0,
                            "videoPath": video_path,
                            "videoUrl": g_config.uploadDir_www + video_path,
                            "base64Str": __base64Str
                        })
                if interface_image_count > 0:
                    image_path_abs = os.path.join(g_config.uploadDir, image_path)
                    if os.path.exists(image_path_abs):
                        __base64Str = f_calcuFileBase64Str(image_path_abs)
                        interface_image_array.append({
                            "index": 0,
                            "imagePath": image_path,
                            "imageUrl": g_config.uploadDir_www + image_path,
                            "base64Str": __base64Str
                        })

                alarm_interface_data = {
                    "nodeCode": g_config.code,
                    "streamNickname": stream_nickname,
                    "streamDeviceId": stream_nickname,  # v.641新增，摄像头分组编号
                    "streamApp": stream_app,
                    "streamName": stream_name,
                    "streamCode": stream_code,
                    "controlCode": control_code,
                    "flowCode": flowCode,
                    "flowName": flowName,
                    "flowMode": 1,
                    "drawType": 1, # 画框:1 不画框:0
                    "flag": now_date.strftime('%Y%m%d%H%M%S'),
                    "desc": desc,
                    "videoCount": interface_video_count,
                    "videoArray": interface_video_array,
                    "imageCount": interface_image_count,
                    "imageArray": interface_image_array,
                    "imageDetects": []
                }

                data_json = json.dumps(alarm_interface_data)
                headers = {
                    "User-Agent": PROJECT_UA,
                    "Content-Type": "application/json;"
                }
                res = requests.post(url=g_config.saveAlarmUrl,
                                    headers=headers,
                                    data=data_json,
                                    timeout=60)
                if res.status_code == 200:
                    __ret = True
                    __msg = "发送http成功：%s" % (res.content.decode("utf-8"))
                else:
                    __msg = "发送http失败：status=%d,%s" % (res.status_code, res.content.decode("utf-8"))

                print("__uploadServer() ",__ret,__msg)

            if g_config.saveAlarmType == 1:
                __saveDb()
            elif g_config.saveAlarmType == 2:
                __uploadServer()
            elif g_config.saveAlarmType == 3:
                __uploadServer()
                __saveDb()
            else:
                raise Exception("保存报警类型不支持")

            msg = "success"
            code = 1000
        except Exception as e:
            msg = str(e)
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    print("AlarmView.openAdd() res:", res)

    return f_responseJson(res)