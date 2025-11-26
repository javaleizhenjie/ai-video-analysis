from app.views.ViewsBase import *
from app.utils.OSSystem import OSSystem
import shutil

def api_discover(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == 'GET':
        # params = f_parseGetParams(request)
        osSystem = OSSystem()
        info = {
            "system_name": osSystem.getSystemName(),
            "machine_node": osSystem.getMachineNode(),
            "project_ua": PROJECT_UA,
            "project_version": PROJECT_VERSION,
            "project_flag": PROJECT_FLAG,
            "project_built": PROJECT_BUILT,
            "project_start_timestamp": PROJECT_ADMIN_START_TIMESTAMP,
            "code":g_config.code,
            "name":g_config.name,
            "describe":g_config.describe,
            "host":g_config.host
        }

        ret = True
        msg = "success"
    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    return f_responseJson(res)
def api_getAllStreamData(request):
    data = g_djangoSql.select("select code,nickname from av_stream order by id desc")
    res = {
        "code": 1000,
        "msg": "success",
        "data": data
    }
    return f_responseJson(res)

def api_getAllAlgroithmFlowData(request):
    data = g_djangoSql.select("select code,name from av_algorithm order by id desc")

    res = {
        "code": 1000,
        "msg": "success",
        "data": data
    }
    return f_responseJson(res)
def api_getAllCoreProcessData(request):
    ret = False
    msg = "未知错误"
    data = []
    info = {}

    if request.method == "GET":
        print("OpenView.getAllCoreProcessData()")
        info["processNum"] = 0
        info["processMode"] = 0
        ret = True
        msg = "success"

    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "data": data,
        "info": info
    }
    print("OpenView.getAllCoreProcessData() res:%s" % str(res))

    return f_responseJson(res)
def api_getAllCoreProcessData2(request):
    ret = False
    msg = "未知错误"
    info = {}

    if request.method == "GET":

        print("OpenView.getAllCoreProcessData2()")
        streamSet = set()  # 数据库中所有布控code的set
        controlCount = 0
        atDBControls = g_djangoSql.select("select code,stream_app,stream_name from av_control where state=1")
        for atDBControl in atDBControls:
            app_name = "%s_%s" % (atDBControl["stream_app"], atDBControl["stream_name"])
            streamSet.add(app_name)
            controlCount += 1

        info["processNum"] = 0
        info["processMode"] = 0
        info["controlCount"] = controlCount
        info["streamCount"] = len(streamSet)

        ret = True
        msg = "success"

    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "info": info
    }
    print("OpenView.getAllCoreProcessData2() res:%s" % str(res))

    return f_responseJson(res)



def api_getIndex(request):
    # highcharts 例子 https://www.highcharts.com.cn/demo/highcharts/dynamic-update
    code = 0
    msg = "error"
    os_info = {}

    try:

        osSystem = OSSystem()
        os_info = osSystem.getOSInfo()
        code = 1000
        msg = "success"

    except Exception as e:
        msg = str(e)

    res = {
        "code": code,
        "msg": msg,
        "os_info": os_info
    }
    return f_responseJson(res)


def api_postAddControl(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        try:
            controlCode = params.get("controlCode")
            algorithmCode = params.get("algorithmCode")
            objectCode = params.get("objectCode")
            polygon = params.get("polygon")
            pushStream = True if '1' == params.get("pushStream") else False
            minInterval = int(params.get("minInterval"))
            classThresh = float(params.get("classThresh"))
            overlapThresh = float(params.get("overlapThresh"))
            remark = params.get("remark")

            streamApp = params.get("streamApp")
            streamName = params.get("streamName")
            streamVideo = params.get("streamVideo")
            streamAudio = params.get("streamAudio")

            if controlCode and algorithmCode and streamApp and streamName and streamVideo:

                __save_state = False
                __save_msg = "error"

                control = None
                try:
                    control = Control.objects.get(code=controlCode)
                except:
                    pass

                if control:
                    # 编辑更新
                    control.stream_app = streamApp
                    control.stream_name = streamName
                    control.stream_video = streamVideo
                    control.stream_audio = streamAudio

                    control.algorithm_code = algorithmCode
                    control.object_code = objectCode
                    control.polygon = polygon
                    control.min_interval = minInterval
                    control.class_thresh = classThresh
                    control.overlap_thresh = overlapThresh
                    control.remark = remark
                    control.push_stream = pushStream
                    control.last_update_time = datetime.now()
                    control.save()

                    if control.id:
                        __save_state = True
                        __save_msg = "更新布控成功(a)"
                    else:
                        __save_msg = "更新布控失败(a)"

                else:
                    # 新增
                    control = Control()
                    control.user_id = getUser(request).get("id")
                    control.sort = 0
                    control.code = controlCode

                    control.stream_app = streamApp
                    control.stream_name = streamName
                    control.stream_video = streamVideo
                    control.stream_audio = streamAudio

                    control.algorithm_code = algorithmCode
                    control.object_code = objectCode
                    control.polygon = polygon
                    control.min_interval = minInterval
                    control.class_thresh = classThresh
                    control.overlap_thresh = overlapThresh
                    control.remark = remark

                    control.push_stream = pushStream
                    control.push_stream_app = g_zlm.default_push_stream_app
                    control.push_stream_name = controlCode

                    control.create_time = datetime.now()
                    control.last_update_time = datetime.now()

                    control.save()

                    if control.id:
                        __save_state = True
                        __save_msg = "添加布控成功"
                    else:
                        __save_msg = "添加布控失败"

                if __save_state:
                    code = 1000
                msg = __save_msg
            else:
                msg = "布控请求参数不完整！"
        except Exception as e:
            msg = "布控请求参数存在错误: %s" % str(e)
    else:
        msg = "请求方法不合法！"

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)


def api_postEditControl(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        try:
            controlCode = params.get("controlCode")
            algorithmCode = params.get("algorithmCode")
            objectCode = params.get("objectCode")
            polygon = params.get("polygon")
            pushStream = True if '1' == params.get("pushStream") else False
            minInterval = int(params.get("minInterval"))
            classThresh = float(params.get("classThresh"))
            overlapThresh = float(params.get("overlapThresh"))
            remark = params.get("remark")

            if controlCode and algorithmCode and objectCode:
                try:
                    control = Control.objects.get(code=controlCode)

                    control.algorithm_code = algorithmCode
                    control.object_code = objectCode
                    control.polygon = polygon
                    control.min_interval = minInterval
                    control.class_thresh = classThresh
                    control.overlap_thresh = overlapThresh
                    control.remark = remark
                    control.push_stream = pushStream

                    control.last_update_time = datetime.now()
                    control.save()

                    if control.id:
                        code = 1000
                        msg = "更新布控成功"
                    else:
                        msg = "更新布控失败"

                except Exception as e:
                    msg = "更新布控数据失败：" + str(e)
            else:
                msg = "更新布控请求参数不完整！"
        except Exception as e:
            msg = "布控请求参数存在错误: %s" % str(e)
    else:
        msg = "请求方法不合法！"

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)


def api_postHandleAlarm(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = f_parsePostParams(request)

        alarm_ids_str = params.get("alarm_ids_str")
        handle = params.get("handle")
        if "read" == handle:
            sql = "update av_alarm set state=1 where id in (%s)" % alarm_ids_str
            if g_djangoSql.execute(sql=sql):
                msg = "已读操作成功"
                code = 1000
            else:
                msg = "已读操作失败"

        elif "delete" == handle:

            alarm_ids = alarm_ids_str.split(",")
            handle_success_count = 0
            handle_error_count = 0
            for alarm_id in alarm_ids:
                if f_removeAlarmAndStorage(alarm_id):
                    handle_success_count += 1
                else:
                    handle_error_count += 1

            msg = "删除成功%d条，删除失败%d条" % (handle_success_count, handle_error_count)
            code = 1000
        else:
            msg = "不支持的处理类型"

    else:
        msg = "请求方法不支持"
    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)

