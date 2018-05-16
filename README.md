HttpRunnerManager
=================

Design Philosophy
-----------------

基于HttpRunner的接口自动化测试平台: `Requests`_, `celery`_ and `Django`_. HttpRunner手册: http://cn.httprunner.org/

Key Features
------------

- 项目管理：新增项目，列表展示及相关操作
- 模块管理：为项目新增模块，用例和配置都归属于module
- 用例管理：分为添加config与test子功能，config定义全部变量和request等相关信息 request可以为公共参数和请求头，也可定义全部变量
- 场景管理：可以动态添加用例，跨项目跨模块，支持拖拽排序
- 报告管理：单个运行会前端显示，批量的运行后可以在线查看
- 运行方式：可单个test，单个module，单个project，也可选择多个批量运行，运行时可以灵活选择配置和环境，其中配置支持跨项目
- 分布执行：单个用例和批量执行结果会直接在前端展示，模块和项目执行可选择为同步异步方式
- 环境管理：可添加运行环境，运行用例时可以一键切换环境
- 报告查看：所有异步执行的用例均可在线查看报告，可自主命名，为空默认时间戳保存
- 定时任务：可设置定时任务，遵循crontab表达式，可在线开启、关闭

本地开发环境部署
---------------
1. 安装mysql数据库服务端(推荐5.7+),并设置为utf-8编码，创建相应HttpRunner数据库，设置好相应用户名、密码，启动mysql

2. 修改:HttpRunnerManager/HttpRunnerManager/settings.py里DATABASES字典相关配置
   ```python
        DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'HttpRunner',  # 新建数据库名
            'USER': 'root',  # 数据库登录名
            'PASSWORD': 'lcc123456',  # 数据库登录密码
            'HOST': '127.0.0.1',  # 数据库所在服务器ip地址
            'PORT': '3306',  # 监听端口 默认3306即可
        }
}
}
    ```
3. 安装rabbitmq消息中间件，启动服务，访问：http://host:15672/#/ host即为你部署rabbitmq的服务器ip地址
   username：guest、Password：guest, 成功登陆即可
    ```bash
        service rabbitmq-server start
    ```

4. 修改:HttpRunnerManager/HttpRunnerManager/settings.py里worker相关配置
    ```python
        djcelery.setup_loader()
        CELERY_ENABLE_UTC = True
        CELERY_TIMEZONE = 'Asia/Shanghai'
        BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672//'  # 127.0.0.1即为rabbitmq-server所在服务器ip地址
        CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
        CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
        CELERY_ACCEPT_CONTENT = ['application/json']
        CELERY_TASK_SERIALIZER = 'json'
        CELERY_RESULT_SERIALIZER = 'json'

        CELERY_TASK_RESULT_EXPIRES = 7200  # celery任务执行结果的超时时间，
        CELERYD_CONCURRENCY = 25  # celery worker的并发数 也是命令行-c指定的数目 根据服务器配置实际更改 一般25即可
        CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，比如200
    ```

5. 命令行窗口执行pip install -r requirements.txt 安装工程所依赖的库文件

6. 命令行窗口切换到HttpRunnerManager目录 生成数据库迁移脚本,并生成表结构
    ```bash
        python manage.py makemigrations ApiManager
        python manage.py makemigrations
    ```

7. 创建超级用户，用户后台管理数据库，并按提示输入相应用户名，密码，邮箱。 如不需用，可跳过此步骤
    ```bash
        python manage.py createsuperuser
    ```

8. 启动服务,
    ```bash
        python manage.py runserver 0.0.0.0:8000
    ```

9. 启动worker, 如果选择同步执行并确保不会使用到定时任务，那么此步骤可忽略
    ```bash
        python manage.py celery -A HttpRunnerManager worker --loglevel=info
        python manage.py celery beat --loglevel=info
        celery flower
    ```

10. 访问：http://localhost:5555/dashboard 即可查看任务列表和状态

11. 浏览器输入：http://127.0.0.1:8000/api/register/  注册用户，开始尽情享用平台吧

12. 浏览器输入http://127.0.0.1:8000/admin/  输入步骤6设置的用户名、密码，登录后台运维管理系统，可后台管理数据

新手入门手册
-----------
1、首先需要注意一个新用户
![注册页面](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/register01.png)<br>
<br>


