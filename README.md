# HttpRunnerManager


Design Philosophy
-----------------
基于HttpRunner的接口自动化测试平台: `Django`_, `Bootstrap`_ and `Python`.目前不支持HttpRunner api功能
注意：目前前端页面还未开发用例运行入口，后台开发完毕，待时间宽松点一定及时更新！
请更改HttpRunnerManager/settings.py DATABASES相关配置(NAME,USER,PASSWORD,HOST,PORT)，推荐mysql 5.7+
Key Features


- 项目管理模块：新增项目，列表展示及相关操作
- 模块管理：为项目新增模块，子模块用module1>module2方式
- 接口管理：待开发
- 用例管理：分为添加config与test子功能，config定义全部变量和base_url，request等相关信息
- test为用例，业务组织方式：在include输入框中以 config>case1>case2...或者case1>case2
- 报告管理：运行完后前端显示，也可运行完后选择打开
- mock服务：待开发
- 任务调度：待开发
- 运行方式：可单个test，单个module，单个project，也可选择多个批量运行


