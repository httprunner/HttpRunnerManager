# HttpRunnerManager


Design Philosophy
-----------------
基于HttpRunner的接口自动化测试平台: `Django`_, `Bootstrap`_ and `Python`.目前不支持HttpRunner api功能
请更改HttpRunnerManager/settings.py DATABASES相关配置(NAME,USER,PASSWORD,HOST,PORT)，推荐mysql 5.7+
部署后打开网址：http://localhost:8000/api/index (注意，端口号是由自己定义！)
-----------------
Key Features

- 项目管理模块：新增项目，列表展示及相关操作
- 模块管理：为项目新增模块，子模块用module1>module2方式
- 用例管理：分为添加config与test子功能，config定义全部变量和base_url，request等相关信息
- test为用例，业务组织方式：在include输入框中以 config>case1>case2...或者case1>case2
- 报告管理：单个运行会前端显示，批量的运行后可以选在打开
- mock服务：待开发
- 任务调度：待开发
- 运行方式：可单个test，单个module，单个project，也可选择多个批量运行


