# 视频行为分析系统v3 后台管理

### 安装
| 程序         | 版本               |
| ---------- |------------------|
| python     | 3.8+             |
| 依赖库      | requirements.txt |

### 启动
~~~
//启动后台管理服务
python manage.py runserver 0.0.0.0:9991

//管理员用户
admin/admin888

~~~

### Windows打包过程

~~~

// 根据 manage.spec 文件 打包后台服务
pyinstaller manage.spec

//打包启动工具
pyinstaller -i logo.ico -F  VideoAnalyzer.py

~~~



### linux 创建python虚拟环境
~~~

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 更新虚拟环境的pip版本
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 在虚拟环境中安装依赖库
python -m pip install -r requirements-linux.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

~~~

### windows 创建python虚拟环境
~~~
# 创建虚拟环境
python -m venv venv

# 切换到虚拟环境
venv\Scripts\activate

# 更新虚拟环境的pip版本
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 在虚拟环境中安装依赖库
python -m pip install -r requirements-windows.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

~~~

