from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render, redirect
from app.utils.Utils import buildPageLabels, gen_random_code_s

def online(request):
    context = {
        
    }
    # data = Camera.objects.all().order_by("-sort")
    return render(request, 'app/stream/web_stream_online.html', context)


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
    sql_data = "select * from av_stream order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from av_stream "

    count = g_djangoSql.select(sql_data_num)

    if len(count) > 0:
        count = int(count[0]["count"])
        data = g_djangoSql.select(sql_data)
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
    return render(request, 'app/stream/web_stream_index.html', context)


def api_openIndex(request):

    params = f_parseGetParams(request)
    data = []

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
    sql_data = "select * from av_stream order by id desc limit %d,%d " % (
        skip, page_size)
    sql_data_num = "select count(id) as count from av_stream "

    count = g_djangoSql.select(sql_data_num)

    if len(count) > 0:
        count = int(count[0]["count"])

        __data = g_djangoSql.select(sql_data)
        for d in __data:
            d["camera_device_id"] = d["nickname"]
            d["pull_stream_type"] = 1
            d["pull_stream_ip"] = ""
            d["is_audio"] = 0
            d["last_update_time"] = d["last_update_time"].strftime("%Y/%m/%d %H:%M:%S")
            data.append([d])
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

    res = {
        "code": 1000,
        "msg": "success",
        "data": data,
        "pageData": pageData,
        "extra": {
            "audioTypes": g_audio_types,
            "pullStreamTypes": g_pull_stream_types
        }
    }
    return f_responseJson(res)


def add(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)
        handle = params.get("handle")
        code = params.get("code")
        pull_stream_url = params.get("pull_stream_url", "").strip()
        nickname = params.get("nickname").strip()
        remark = params.get("remark", "").strip()

        if "add" == handle and code and pull_stream_url.lower().startswith("rtsp") and nickname:
            try:
                user_id = getUser(request).get("id")
            except:
                user_id = 0

            obj = Stream()
            obj.user_id = user_id
            obj.sort = 0
            obj.code = params.get("code").strip()
            obj.app = params.get("app").strip()
            obj.name = params.get("name").strip()
            obj.pull_stream_url = pull_stream_url
            obj.pull_stream_type = 0
            obj.nickname = nickname
            obj.remark = remark
            obj.forward_state = 0  # 默认未开启转发
            obj.create_time = datetime.now()
            obj.last_update_time = datetime.now()
            obj.state = 0
            obj.save()
            __msg = "添加成功"
            __ret = True

        else:
            __msg = "请求参数格式错误"
        if __ret:
            redirect_url = "/stream/index"
        else:
            redirect_url = "/stream/add"
        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})
    else:
        context = {
            
        }

        code = gen_random_code_s(prefix="cam")
        app = "live"
        name = code
        context["handle"] = "add"
        context["obj"] = {
            "code": code,
            "app": app,
            "name": name,
            "rtspUrl": g_zlm.get_rtspUrl(app, name),
            "hlsUrl": g_zlm.get_hlsUrl(app, name),
            "httpMp4Url": g_zlm.get_httpMp4Url(app, name),
            "wsMp4Url": g_zlm.get_wsMp4Url(app, name),

        }
        context["data"] = g_djangoSql.select("select * from av_stream order by id desc")

        return render(request, 'app/stream/web_stream_add.html', context)


def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)
        handle = params.get("handle")
        code = params.get("code")
        pull_stream_url = params.get("pull_stream_url", "").strip()
        nickname = params.get("nickname", None)
        remark = params.get("remark", "").strip()

        if "edit" == handle and code and pull_stream_url.lower().startswith("rtsp") and nickname:
            obj = Stream.objects.get(code=code)
            if obj.pull_stream_url != pull_stream_url:
                # 如果 拉流地址更换了，需要停止转发代理
                g_zlm.delStreamProxy(app=obj.app, name=obj.name)
                obj.forward_state = 0
            obj.pull_stream_url = pull_stream_url
            obj.nickname = nickname.strip()
            obj.remark = remark
            obj.last_update_time = datetime.now()
            obj.save()
            # 编辑完成后，需要取消转发代理，避免视频源被更换

            __msg = "编辑成功"
            __ret = True

        else:
            __msg = "请求参数格式错误"
        if __ret:
            redirect_url = "/stream/index"
        else:
            redirect_url = "/stream/edit?code=" + code

        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})
    else:
        context = {
            
        }
        params = f_parseGetParams(request)
        code = params.get("code")

        __is_edit_page = False
        if code:
            data = g_djangoSql.select("select * from av_stream order by id desc")
            obj = None
            for d in data:
                if code == d["code"]:
                    obj = d
                    break
            if obj:
                obj["rtspUrl"] = g_zlm.get_rtspUrl(obj["app"], obj["name"])
                obj["hlsUrl"] = g_zlm.get_hlsUrl(obj["app"], obj["name"])
                obj["wsMp4Url"] = g_zlm.get_wsMp4Url(obj["app"], obj["name"])
                obj["httpMp4Url"] = g_zlm.get_httpMp4Url(obj["app"], obj["name"])

                context["handle"] = "edit"
                context["obj"] = obj
                context["data"] = data
                __is_edit_page = True

        if __is_edit_page:
            return render(request, 'app/stream/web_stream_add.html', context)
        else:
            return redirect("/stream/index")
            # return render(request, 'app/message.html',{"msg": "请通过摄像头管理进入", "is_success": False, "redirect_url": "/stream/index"})

def player(request):
    context = {
    }
    params = f_parseGetParams(request)
    app = params.get("app", None)
    name = params.get("name", None)

    if app and name:
        stream = GetStream(app=app, name=name)
        context["stream"] = stream
        context["is_exist_stream"] = 1
    else:
        context["is_exist_stream"] = 0

    return render(request, 'app/stream/player.html', context)



def api_getOnline(request):
    # 获取在线流
    code = 0
    msg = "未知错误"
    mediaServerState = False
    data = []

    try:
        mediaServerState, data = __getAllOnlineStream(is_filter_analyzer=True)

        code = 1000
        msg = "success"
    except Exception as e:
        log = "流媒体服务异常：" + str(e)
        msg = log

    top_msg = ""
    if not mediaServerState:
        top_msg = "流媒体服务未运行"

    res = {
        "code": code,
        "msg": msg,
        "top_msg": top_msg,
        "data": data
    }
    return f_responseJson(res)

def __getAllOnlineStream(is_filter_analyzer=False):
    data = []
    online_data = g_zlm.getMediaList()
    mediaServerState = g_zlm.mediaServerState
    if mediaServerState:

        db_streams = readAllStreamData()
        db_stream_dict = {}  # 数据库
        for db_stream in db_streams:
            app_name = "{app}_{name}".format(app=db_stream["app"], name=db_stream["name"])
            db_stream_dict[app_name] = db_stream

        for online_stream in online_data:
            app = online_stream["app"]
            name = online_stream["name"]

            if app == "live":
                app_name = "{app}_{name}".format(app=app, name=name)
                db_stream = db_stream_dict.get(app_name, None)  # 数据库查到的数据
                if db_stream:
                    online_stream["source_type"] = 1  # 来自数据库
                    online_stream["source"] = db_stream
                    online_stream["source_nickname"] = db_stream["nickname"]
                else:
                    online_stream["source_type"] = 0  # 来自推流
                    online_stream["source_nickname"] = "{app}/{name}".format(app=app, name=name)
                data.append(online_stream)
            else:
                # print(is_filter_analyzer,app,g_zlm.default_push_stream_app)

                if is_filter_analyzer and app == g_zlm.default_push_stream_app:
                    # 筛选算法流的同时，app也必须是算法流分类
                    app_name = "{app}_{name}".format(app=app, name=name)
                    db_stream = db_stream_dict.get(app_name, None)  # 数据库查到的数据
                    if db_stream:
                        online_stream["source_type"] = 1  # 来自数据库
                        online_stream["source"] = db_stream
                        online_stream["source_nickname"] = db_stream["nickname"]
                    else:
                        online_stream["source_type"] = 0  # 来自推流
                        online_stream["source_nickname"] = "{app}/{name}".format(app=app, name=name)
                    data.append(online_stream)

    return mediaServerState, data

def api_getAllStartForward(request):
    code = 0
    msg = "未知错误"
    if request.method == 'GET':
        __ret, __msg = AllStreamStartForward()
        msg = __msg
        if __ret:
            code = 1000
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)


def api_getAllUpdateForwardState(request):
    code = 0
    msg = "未知错误"
    # 全部更新转发状态
    try:
        online_data = g_zlm.getMediaList()
        online_dict = {}
        mediaServerState = g_zlm.mediaServerState
        if not mediaServerState:
            # 流媒体服务不在线，全部更新下线状态
            g_djangoSql.execute("update av_stream set forward_state=0")
        else:
            for d in online_data:
                app_name = "{app}_{name}".format(app=d["app"], name=d["name"])
                online_dict[app_name] = d

            stream_data = g_djangoSql.select("select * from av_stream order by id desc")
            stream_data_set = set()
            for stream_d in stream_data:
                app_name = "{app}_{name}".format(app=stream_d["app"], name=stream_d["name"])
                stream_data_set.add(app_name)
                if online_dict.get(app_name):
                    g_djangoSql.execute("update av_stream set forward_state=1 where id=%d" % int(stream_d["id"]))
                else:
                    g_djangoSql.execute("update av_stream set forward_state=0 where id=%d" % int(stream_d["id"]))

            online_not_in_db_data = set(online_dict.keys()).difference(stream_data_set)
            # online_not_in_db_data = list(online_not_in_db_data)  # 在线但不来自于数据库的视频流

        code = 1000
        msg = "刷新状态成功"
    except Exception as e:
        msg = "刷新状态失败：" + str(e)

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)

def api_openDel(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        handle = params.get("handle","one")  # one：删除一个视频流，all：删除全部视频流
        stream_code = params.get("code")
        try:
            if handle == "one":
                stream = Stream.objects.filter(code=stream_code)
                if len(stream) > 0:
                    stream = stream[0]
                    g_zlm.delStreamProxy(app=stream.app, name=stream.name)
                    if stream.delete():
                        code = 1000
                        msg = "删除成功"
                    else:
                        msg = "删除失败！"
                else:
                    msg = "该视频流不存在"
            elif handle == "all":
                success_count = 0
                error_count = 0
                streams = Stream.objects.all()
                for stream in streams:
                    g_zlm.delStreamProxy(app=stream.app, name=stream.name)
                    if stream.delete():
                        code = 1000
                        msg = "删除成功"
                    else:
                        msg = "删除失败！"
                    msg = "成功%d条，失败%d条" % (success_count, error_count)

                    if success_count > 0:
                        ret = True

                else:
                    msg = "删除失败！"
            else:
                msg = "request parameters are incorrect"
        except Exception as e:
            msg = str(e)
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)


def api_openAddStreamProxy(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        stream_code = params.get("code")
        try:
            stream = Stream.objects.get(code=stream_code)
            if stream.forward_state == 1:
                code = 1000
                msg = "开启转发已经成功"
            else:
                __media_ret = g_zlm.addStreamProxy(app=stream.app, name=stream.name,
                                                     origin_url=stream.pull_stream_url)
                if __media_ret:
                    stream.forward_state = 1
                    stream.save()
                    code = 1000
                    msg = "开启转发成功"
                else:
                    msg = "开启转发失败！"

        except Exception as e:
            msg = "openAddStreamProxy() error:" + str(e)
    else:
        msg = "请求方法不支持"

    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)
def api_openDelStreamProxy(request):
    code = 0
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        stream_code = params.get("code")
        try:
            stream = Stream.objects.get(code=stream_code)

            __media_ret = g_zlm.delStreamProxy(app=stream.app, name=stream.name)
            stream.forward_state = 0
            stream.save()
            code = 1000
            msg = "停止转发成功"

        except Exception as e:
            msg = "openDelStreamProxy() error:" + str(e)
    else:
        msg = "请求方法不支持"
    res = {
        "code": code,
        "msg": msg
    }
    return f_responseJson(res)

def api_openAddStreamPusherProxy(request):
    # （v3.502新增）开启转推代理
    ret = False
    msg = "未知错误"
    key = "" # 转推key
    if request.method == 'POST':
        params = f_parsePostParams(request)
        print("StreamView.openAddStreamPusherProxy() params:%s" % str(params))
        stream_app = params.get("stream_app", "").strip()
        stream_name = params.get("stream_name", "").strip()
        dst_stream_app = params.get("dst_stream_app", "").strip()
        dst_stream_name = params.get("dst_stream_name", "").strip()
        dst_host = params.get("dst_host", "").strip()
        dst_rtsp_port = int(params.get("dst_rtsp_port",554))
        dst_http_port = int(params.get("dst_http_port",80))
        dst_secret = params.get("dst_secret", "").strip()

        try:

            __key, __msg = g_zlm.addStreamPusherProxy(app=stream_app,
                                                               name=stream_name,
                                                               schema="rtsp",
                                                               dst_url="rtsp://%s:%d/%s/%s" % (dst_host, dst_rtsp_port,dst_stream_app, dst_stream_name))
            print("StreamView.openAddStreamPusherProxy() key=%s,msg=%s" % (__key,__msg))

            if __key:
                ret = True
                msg = "success"
                key = __key
            else:
                raise Exception(__msg)
        except Exception as e:
            msg = str(e)

    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg,
        "key": key
    }
    print("StreamView.openAddStreamPusherProxy() res:%s" % str(res))
    return f_responseJson(res)