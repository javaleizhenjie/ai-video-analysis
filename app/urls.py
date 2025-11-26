from django.urls import path
from .views import web
from .views import api
from .views import Algorithm
from .views import ControlView
from .views import AlarmView
from .views import StreamView



app_name = 'app'

urlpatterns = [
    path('', web.web_index),
    path('profile', web.web_profile),
    path('login', web.web_login),
    path('logout', web.web_logout),
    # 视频流功能
    path('stream/online', StreamView.online),
    path('stream/openIndex', StreamView.api_openIndex), #3.52新增，适配集群管理平台
    path('stream/index', StreamView.index),
    path('stream/add', StreamView.add),
    path('stream/edit', StreamView.edit),
    path('stream/openDel', StreamView.api_openDel),#3.52新增，适配集群管理平台
    path('stream/openAddStreamProxy', StreamView.api_openAddStreamProxy),#3.52新增，适配集群管理平台
    path('stream/openDelStreamProxy', StreamView.api_openDelStreamProxy),#3.52新增，适配集群管理平台
    path('stream/openAddStreamPusherProxy', StreamView.api_openAddStreamPusherProxy),#3.52新增，适配集群管理平台
    path('stream/player', StreamView.player),
    path('stream/getOnline', StreamView.api_getOnline),
    path('stream/getAllStartForward', StreamView.api_getAllStartForward),
    path('stream/getAllUpdateForwardState', StreamView.api_getAllUpdateForwardState),

    path('alarms', AlarmView.index),
    path('alarm/openAdd', AlarmView.api_openAdd),
    # 算法
    path('algorithm/index', Algorithm.index),
    path('algorithm/add', Algorithm.add),
    path('algorithm/edit', Algorithm.edit),
    path('algorithm/openDel', Algorithm.api_openDel),
    # 布控
    path('controls', ControlView.index),
    path('control/openIndex', ControlView.api_openIndex),#3.52新增，适配集群管理平台
    path('control/add', ControlView.add),
    path('control/edit', ControlView.edit),
    path('control/openStartControl', ControlView.api_openStartControl),#3.52新增，适配集群管理平台
    path('control/openStopControl', ControlView.api_openStopControl),#3.52新增，适配集群管理平台
    path('control/openDel', ControlView.api_openDel),#3.52新增，适配集群管理平台
    path('open/discover', api.api_discover),#3.52新增，适配集群管理平台
    path('open/getAllStreamData', api.api_getAllStreamData),#3.52新增，适配集群管理平台
    path('open/getAllAlgroithmFlowData', api.api_getAllAlgroithmFlowData),#3.52新增，适配集群管理平台
    path('open/getAllCoreProcessData', api.api_getAllCoreProcessData),#3.52新增，适配集群管理平台
    path('open/getAllCoreProcessData2', api.api_getAllCoreProcessData2),#3.52新增，适配集群管理平台

    path('api/postHandleAlarm', api.api_postHandleAlarm),

    path('api/postAddControl', api.api_postAddControl),
    path('api/postEditControl', api.api_postEditControl),


    path('api/getIndex', api.api_getIndex),
]