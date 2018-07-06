HttpRunnerManager
=================

Design Philosophy
-----------------

基于HttpRunner的接口自动化测试平台: `HttpRunner`_, `djcelery`_ and `Django`_. HttpRunner手册: http://cn.httprunner.org/

Key Features
------------

- 项目管理：新增项目、列表展示及相关操作，支持用例批量上传(标准化的HttpRunner json和yaml用例脚本)
- 模块管理：为项目新增模块，用例和配置都归属于module，module和project支持同步和异步方式
- 用例管理：分为添加config与test子功能，config定义全部变量和request等相关信息 request可以为公共参数和请求头，也可定义全部变量
- 场景管理：可以动态加载可引用的用例，跨项目、跨模快，依赖用例列表支持拖拽排序和删除
- 运行方式：可单个test，单个module，单个project，也可选择多个批量运行，支持自定义测试计划，运行时可以灵活选择配置和环境，
- 分布执行：单个用例和批量执行结果会直接在前端展示，模块和项目执行可选择为同步或者异步方式，
- 环境管理：可添加运行环境，运行用例时可以一键切换环境
- 报告查看：所有异步执行的用例均可在线查看报告，可自主命名，为空默认时间戳保存，
- 定时任务：可设置定时任务，遵循crontab表达式，可在线开启、关闭，完毕后支持邮件通知
- 持续集成：jenkins对接，开发中。。。

本地开发环境部署
--------
1. 安装mysql数据库服务端(推荐5.7+),并设置为utf-8编码，创建相应HttpRunner数据库，设置好相应用户名、密码，启动mysql

2. 修改:HttpRunnerManager/HttpRunnerManager/settings.py里DATABASES字典和邮件发送账号相关配置
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

    EMAIL_SEND_USERNAME = 'username@163.com'  # 定时任务报告发送邮箱，支持163,qq,sina,企业qq邮箱等，注意需要开通smtp服务
    EMAIL_SEND_PASSWORD = 'password'     # 邮箱密码
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
        CELERYD_CONCURRENCY = 10  # celery worker的并发数 也是命令行-c指定的数目 根据服务器配置实际更改 默认10
        CELERYD_MAX_TASKS_PER_CHILD = 100  # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，默认100
    ```

5. 命令行窗口执行pip install -r requirements.txt 安装工程所依赖的库文件

6. 命令行窗口切换到HttpRunnerManager目录 生成数据库迁移脚本,并生成表结构
    ```bash
        python manage.py makemigrations ApiManager #生成数据迁移脚本
        python manage.py migrate  #应用到db生成数据表
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
        python manage.py celery -A HttpRunnerManager worker --loglevel=info  #启动worker
        python manage.py celery beat --loglevel=info #启动定时任务监听器
        celery flower #启动任务监控后台
    ```

10. 访问：http://localhost:5555/dashboard 即可查看任务列表和状态

11. 浏览器输入：http://127.0.0.1:8000/api/register/  注册用户，开始尽情享用平台吧

12. 浏览器输入http://127.0.0.1:8000/admin/  输入步骤6设置的用户名、密码，登录后台运维管理系统，可后台管理数据

### 生产环境uwsgi+nginx部署参考：https://www.jianshu.com/p/d6f9138fab7b

新手入门手册
-----------
1、首先需要注册一个新用户,注册成功后会自动跳转到登录页面，正常登录即可访问页面
![注册页面](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/register_01.jpg)<br>
![登录页面](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/login_01.jpg)<br>

2、登陆后默认跳转到首页，左侧为菜单栏，上排有快捷操作按钮，当前只简单的做了项目，模块，用例，配置的统计
![首页](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/index_01.jpg)<br>
<br>
3、首先应该先添加一个项目，用例都是以项目为维度进行管理, 注意简要描述和其他信息可以为空, 添加成功后会自动重定向到项目列表
![新增项目](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_project_01.png)<br>
<br>
4、支持对项目进行二次编辑,也可以进行筛选等,项目列表页面可以选择单个项目运行，也可以批量运行，注意：删除操作会强制删除该项目下所有数据，请谨慎操作
![项目列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/project_list_01.jpg)<br>
<br>
5、当前项目可以新增模块了，之后用例或者配置都会归属模块下，必须指定模块所属的项目,模块列表与项目列表类似，故不赘述
![新增模块](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_module_01.jpg)<br>
<br>
6、新增用例，遵循HtttpRuunner脚本规范，可以跨项目，跨模块引用用例，支持拖拽排序，动态添加和删减，极大地方便了场景组织, HttpRunner用例编写很灵活，建议规范下编写方式
![新增用例01](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_01.jpg)<br>
<br>
![新增用例02](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_02.jpg)<br>
<br>
![新增用例03](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_03.jpg)<br>
<br>
![新增用例04](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_case_04.jpg)<br>
<br>
7、新增配置，可定义全局变量，全局hook，公共请求参数和公共headers,一般可用于测试环境，验证环境切换配置，具体用法参考HttpRunner手册
![新增配置](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_config_01.jpg)<br>
<br>
8、支持添加项目级别定时任务，模块集合的定时任务，遵循crontab表达式, 模块列表为空默认为整个项目，定时任务支持选择环境和配置
![添加任务](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/add_tasks_01.jpg)<br>
9、定时任务列表可以对任务进行开启或者关闭、删除，不支持二次更改
![任务列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/tasks_list_01.jpg)<br>
<br>
10、用例列表运行用例可以选择单个，批量运行，鼠标悬浮到用例名称后会自动展开依赖的用例，方便预览，鼠标悬浮到对应左边序列栏会自动收缩,只能同步运行
![用例列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/test_list_01.jpg)<br>
<br>
11、项目和模块列表可以选择单个，或者批量运行，可以选择运行环境，配置等，支持同步、异步选择，异步支持自定义报告名称，默认时间戳命名
![模块列表](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/module_list_01.jpg)<br>
<br>
12、异步运行的用例还有定时任务生成的报告均会存储在数据库，可以在线点击查看，当前不提供下载功能
![报告持久化](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/report_list_01.jpg)<br>
<br>
13、高大上的报告(基于extentreports实现), 可以一键翻转主题哦
![最终报告01](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/reports_01.jpg)<br>
<br>
![最终报告02](https://github.com/HttpRunner/HttpRunnerManager/blob/master/images/reports_02.jpg)<br>



###  其他
MockServer：https://github.com/yinquanwang/MockServer

因时间限制，平台可能还有很多潜在的bug，使用中如遇到问题，欢迎issue,
如果任何疑问好好的建议欢迎github提issue, 或者可以直接加群(628448476)，反馈会比较快








