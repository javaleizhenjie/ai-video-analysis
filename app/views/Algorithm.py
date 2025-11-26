from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render,redirect
import os
import time
from app.utils.Utils import buildPageLabels, gen_random_code_s

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
        if page_size < 1:
            page_size = 1
    except:
        page_size = 10

    skip = (page - 1) * page_size
    sql_data = "select * from av_algorithm order by id desc limit %d offset %d " % (page_size, skip)
    sql_data_num = "select count(id) as count from av_algorithm "

    count = g_djangoSql.select(sql_data_num)
    count = int(count[0]["count"])

    if count > 0:
        data = g_djangoSql.select(sql_data)

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
    return render(request, 'app/algorithm/index.html', context)
def add(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)

        handle = params.get("handle")

        code = params.get("code", "").strip()
        name = params.get("name", "").strip()
        api_url = params.get("api_url", "").strip()
        object_str = params.get("object_str", "").strip()
        remark = params.get("remark", "").strip()
        try:
            if handle != "add":
                raise Exception("request parameters are incorrect")
            if code == "":
                raise Exception("code cannot be empty")
            if name == "":
                raise Exception("name cannot be empty")
            if api_url != "":
                object_str = "api"

            obj = AlgorithmModel.objects.filter(code=code).first()
            if obj:
                raise Exception("algorithm code already exist")

            objects_array = object_str.split(",")
            object_count = len(objects_array)

            obj = AlgorithmModel()
            obj.sort = 0
            obj.code = code
            obj.name = name
            obj.api_url = api_url
            obj.object_count = object_count
            obj.object_str = object_str
            obj.remark = remark
            obj.state = 0
            obj.save()

            __msg = "添加成功"
            __ret = True

        except Exception as e:
            __msg = str(e)

        if __ret:
            redirect_url = "/algorithm/index"
        else:
            redirect_url = "/algorithm/add"

        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})
    else:

        context = {
        }
        context["handle"] = "add"

        context["obj"] = {
            "sort": 0
        }

        return render(request, 'app/algorithm/add.html', context)
def edit(request):
    if "POST" == request.method:
        __ret = False
        __msg = "未知错误"

        params = f_parsePostParams(request)

        handle = params.get("handle")

        code = params.get("code", "").strip()
        name = params.get("name", "").strip()
        api_url = params.get("api_url", "").strip()
        object_str = params.get("object_str", "").strip()
        remark = params.get("remark", "").strip()
        try:
            if handle != "edit":
                raise Exception("request parameters are incorrect")
            if code == "":
                raise Exception("code cannot be empty")
            if name == "":
                raise Exception("name cannot be empty")
            if api_url != "":
                object_str = "api"


            objects_array = object_str.split(",")
            object_count = len(objects_array)

            obj = AlgorithmModel.objects.filter(code=code)
            if len(obj) > 0:
                obj = obj[0]

                obj.name = name
                obj.api_url = api_url
                obj.object_count = object_count
                obj.object_str = object_str
                obj.remark = remark
                obj.save()

                __msg = "编辑成功"
                __ret = True
            else:
                __msg = "the data does not exist"
        except Exception as e:
            __msg = str(e)

        if __ret:
            redirect_url = "/algorithm/index"
        else:
            redirect_url = "/algorithm/edit?code=" + code

        return render(request, 'app/message.html',
                      {"msg": __msg, "is_success": __ret, "redirect_url": redirect_url})

    else:
        context = {
        }
        params = f_parseGetParams(request)
        code = params.get("code")
        if code:
            obj = AlgorithmModel.objects.filter(code=code)
            if len(obj) > 0:
                obj = obj[0]
                context["handle"] = "edit"
                context["obj"] = obj
                return render(request, 'app/algorithm/add.html', context)
            else:
                return render(request, 'app/message.html',
                              {"msg": "该节点不存在", "is_success": False, "redirect_url": "/algorithm/index"})
        else:
            return redirect("/algorithm/index")
def api_openDel(request):
    ret = False
    msg = "未知错误"
    if request.method == 'POST':
        params = f_parsePostParams(request)
        code = params.get("code")
        controls = Control.objects.filter(algorithm_code=code)

        if len(controls) == 0:
            obj = AlgorithmModel.objects.filter(code=code)
            if len(obj) > 0:
                obj = obj[0]
                if obj.delete():
                    ret = True
                    msg = "success"
                else:
                    msg = "failed to delete model"
            else:
                msg = "the data does not exist"
        else:
            msg = "有%d条布控在使用该算法，无法删除"%len(controls)

    else:
        msg = "request method not supported"

    res = {
        "code": 1000 if ret else 0,
        "msg": msg
    }
    return f_responseJson(res)


