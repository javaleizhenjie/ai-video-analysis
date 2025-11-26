from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render,redirect
from app.utils.Utils import gen_random_code_s,buildPageLabels

def index(request):
    context = {
    }

    return render(request, 'app/control/index.html', context)
def api_openIndex(request):
    data = []
    pageData = {}

    params = f_parseGetParams(request)
    page = params.get('p', 1)
    page_size = params.get('ps', 10)
    search_text = str(params.get('search_text', "")).strip()  # v4.638新增

    try:
        page = int(page)
    except:
        page = 1
    try:
        page_size = int(page_size)
        if page_size < 1:
            page_size = 1
    except:
        page_size = 10

    __online_streams_dict = {}  # 在线的视频流
    __online_controls_dict = {}  # 在线的布控数据

    __streams = g_zlm.getMediaList()
    mediaServerState = g_zlm.mediaServerState
    for d in __streams:
        if d.get("is_online"):
            __online_streams_dict[d.get("an")] = d

    ananyServerState = False
    if mediaServerState:
        __state, __msg, __controls = g_analyzer.controls()
        ananyServerState = g_analyzer.analyzerServerState
        for d in __controls:
            __online_controls_dict[d.get("code")] = d

    db_streams = g_djangoSql.select("select * from av_stream")
    db_stream_dict = {}
    for d in db_streams:
        app_name = "%s_%s" % (d["app"], d["name"])
        db_stream_dict[app_name] = d

    algorithms_dict = {}
    algorithms_data = g_djangoSql.select("select * from av_algorithm order by id desc")
    for d in algorithms_data:
        algorithms_dict[d.get("code")] = d

    atDBControls = g_djangoSql.select("select * from av_control order by id desc")
    atDBControlCodeSet = set()  # 数据库中所有布控code的set

    for atDBControl in atDBControls:
        atDBControlCodeSet.add(atDBControl.get("code"))

        app_name = "%s_%s" % (atDBControl["stream_app"], atDBControl["stream_name"])
        atDBControl["create_time"] = atDBControl["create_time"].strftime("%Y-%m-%d %H:%M")
        d_stream = db_stream_dict.get(app_name)
        if d_stream:
            atDBControl["stream_nickname"] = d_stream["nickname"]
        else:
            atDBControl["stream_nickname"] = atDBControl["stream_name"]

        if __online_streams_dict.get(app_name):
            atDBControl["stream_active"] = 1  # 当前视频流在线
        else:
            atDBControl["stream_active"] = 0  # 当前视频流不在线


        algorithm = algorithms_dict.get(atDBControl["algorithm_code"])
        if algorithm:
            atDBControl["flow_nickname"] = algorithm["name"]
            atDBControl["flow_code"] = algorithm["code"]
            atDBControl["flow_deploy_process_index"] = 0
            atDBControl["flow_max_concurrency"] = 0
            atDBControl["flow_concurrency_unit_length"] = 0
        else:
            atDBControl["flow_nickname"] = 0


        atDBControl["last_update_time"] = atDBControl["last_update_time"].strftime("%Y/%m/%d %H:%M:%S")
        atDBControl["checkFps"] = "0"
        __online_control = __online_controls_dict.get(atDBControl["code"])

        if __online_control:
            atDBControl["cur_state"] = 1  # 布控中
            atDBControl["checkFps"] = "%.2f" % float(__online_control.get("checkFps"))
        else:
            if 0 == int(atDBControl.get("state")):
                atDBControl["cur_state"] = 0  # 未布控
            else:
                atDBControl["cur_state"] = 5  # 布控中断

        if atDBControl.get("state") != atDBControl.get("cur_state"):
            # 数据表中的布控状态和最新布控状态不一致，需要更新至最新状态
            update_state_sql = "update av_control set state=%d where id=%d " % (
                atDBControl.get("cur_state"), atDBControl.get("id"))
            g_djangoSql.execute(update_state_sql)

        data.append([atDBControl])
    count = len(data)

    for code, control in __online_controls_dict.items():
        if code not in atDBControlCodeSet:
            # 布控数据在运行中，但却不存在本地数据表中，该数据为失控数据，需要关闭其运行状态
            print("api_getControls() 当前布控数据还在运行在，但却不存在本地数据表中，已启动停止布控", code, control)
            g_analyzer.control_cancel(code=code)

    if mediaServerState and ananyServerState:
        top_msg = "<span style='color:green;font-size:14px;'>流媒体运行中，视频分析器运行中</span>"
    elif mediaServerState and not ananyServerState:
        top_msg = "<span style='color:green;font-size:14px;'>流媒体运行中</span> <span style='color:red;font-size:14px;'>视频分析器未运行<span>"
    else:
        top_msg = "<span style='color:red;font-size:14px;'>流媒体未运行，视频分析器未运行<span>"

    page_num = int(count / page_size)  # 总页数
    if count % page_size > 0:
        page_num += 1

    pageData = {
        "page": page,
        "page_size": page_size,
        "page_num": page_num,
        "count": count,
        "pageLabels": buildPageLabels(page=page, page_num=page_num)
    }
    res = {
        "code": 1000,
        "msg": "success",
        "top_msg": top_msg,
        "data": data,
        "pageData": pageData
    }
    return f_responseJson(res)


def add(request):
    context = {
    }

    streams = g_zlm.getMediaList()


    context["streams"] = streams
    context["algorithms"] = g_djangoSql.select("select * from av_algorithm order by id desc")
    context["handle"] = "add"

    context["control"] = {
        "code": gen_random_code_s("control"),
        "min_interval": 180,
        "class_thresh": 0.5,
        "overlap_thresh": 0.5,
        "push_stream": True
    }

    return render(request, 'app/control/add.html', context)


def edit(request):
    context = {
    }
    params = f_parseGetParams(request)

    code = params.get("code")
    try:
        control = Control.objects.get(code=code)
        algorithm = AlgorithmModel.objects.filter(code=control.algorithm_code)
        if len(algorithm) > 0:
            algorithm = algorithm[0]
            old_object_data = algorithm.object_str.split(",")
        else:
            old_object_data = []

        context["algorithms"] = g_djangoSql.select("select * from av_algorithm order by id desc")

        context["old_object_data"] = old_object_data
        context["handle"] = "edit"
        context["control"] = control
        context["control_stream_flvUrl"] = g_zlm.get_wsMp4Url(control.stream_app, control.stream_name)

    except Exception as e:
        print("ControlView.edit() error", e)

        return render(request, 'app/message.html',
                      {"msg": "请通过布控管理进入", "is_success": False, "redirect_url": "/controls"})

    return render(request, 'app/control/add.html', context)

def api_openStartControl(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = f_parsePostParams(request)

        controlCode = params.get("code")

        if controlCode:

            try:
                control = Control.objects.get(code=controlCode)
                stream = Stream.objects.filter(app=control.stream_app,name=control.stream_name).first()
                if stream:
                    streamApp = control.stream_app
                    streamName = control.stream_name
                    streamCode = stream.code
                else:
                    streamApp = control.stream_app
                    streamName = control.stream_name
                    streamCode = streamName

                algorithm = AlgorithmModel.objects.filter(code=control.algorithm_code).first()
                if algorithm:
                    __state, __msg = g_analyzer.control_add(
                        code=controlCode,
                        algorithmCode=control.algorithm_code,
                        streamCode=streamCode,
                        streamApp=streamApp,
                        streamName=streamName,
                        streamUrl=g_zlm.get_rtspUrl(control.stream_app, control.stream_name),  # 拉流地址
                        pushStream=control.push_stream,
                        pushStreamUrl=g_zlm.get_rtspUrl(control.push_stream_app, control.push_stream_name),  # 推流地址
                        api_url=algorithm.api_url,
                        object_str=algorithm.object_str,
                        objectCode=control.object_code,
                        recognitionRegion=control.polygon,
                        minInterval=control.min_interval,
                        classThresh=control.class_thresh,
                        overlapThresh=control.overlap_thresh
                    )

                    msg = __msg
                    if __state:
                        control = Control.objects.get(code=controlCode)
                        control.state = 1
                        control.save()
                        code = 1000
                        msg = "布控成功"
                else:
                    msg = "该布控算法不存在"

            except Exception as e:
                msg = str(e)
                print("ControlView.api_openStartControl() error", e)

        else:
            msg = "请求参数不合法"
    else:
        msg = "请求方法不支持"
    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)

def api_openStopControl(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = f_parsePostParams(request)

        controlCode = params.get("code")
        if controlCode:
            control = None
            try:
                control = Control.objects.get(code=controlCode)
            except:
                pass

            if control:
                __state, __msg = g_analyzer.control_cancel(
                    code=controlCode
                )

                if __state:
                    control = Control.objects.get(code=controlCode)
                    control.state = 0
                    control.save()
                    msg = "取消布控成功"
                    code = 1000
                else:
                    msg = __msg
            else:
                msg = "布控数据不能存在！"

        else:
            msg = "请求参数不合法"
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)

def api_openDel(request):
    code = 0
    msg = "error"

    if request.method == 'POST':
        params = f_parsePostParams(request)
        try:
            controlCode = params.get("code")

            if controlCode:
                try:
                    control = Control.objects.get(code=controlCode)
                    g_analyzer.control_cancel(code=controlCode)  # 取消布控

                    if control.delete():
                        alarm_data = g_djangoSql.select(
                            "select id from av_alarm where control_code='%s' order by id asc" % controlCode)
                        for alarm in alarm_data:
                            alarm_id = alarm["id"]
                            f_removeAlarmAndStorage(alarm_id=alarm_id)
                        code = 1000
                        msg = "删除成功"
                    else:
                        msg = "删除失败"

                except Exception as e:
                    msg = "更新布控数据失败：" + str(e)
            else:
                msg = "删除布控请求参数不完整！"
        except Exception as e:
            msg = "删除布控请求参数存在错误: %s" % str(e)
    else:
        msg = "请求方法不合法！"

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)

