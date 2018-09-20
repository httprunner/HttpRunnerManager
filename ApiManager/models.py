from django.db import models

from ApiManager.managers import UserTypeManager, UserInfoManager, ProjectInfoManager, ModuleInfoManager, \
    TestCaseInfoManager, EnvInfoManager


# Create your models here.


class BaseTable(models.Model):
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        abstract = True
        verbose_name = "公共字段表"
        db_table = 'BaseTable'


class UserType(BaseTable):
    class Meta:
        verbose_name = '用户类型'
        db_table = 'UserType'

    type_name = models.CharField(max_length=20)
    type_desc = models.CharField(max_length=50)
    objects = UserTypeManager()


class UserInfo(BaseTable):
    class Meta:
        verbose_name = '用户信息'
        db_table = 'UserInfo'

    username = models.CharField('用户名', max_length=20, unique=True, null=False)
    password = models.CharField('密码', max_length=20, null=False)
    email = models.EmailField('邮箱', null=False, unique=True)
    status = models.IntegerField('有效/无效', default=1)
    # user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    objects = UserInfoManager()


class ProjectInfo(BaseTable):
    class Meta:
        verbose_name = '项目信息'
        db_table = 'ProjectInfo'

    project_name = models.CharField('项目名称', max_length=50, unique=True, null=False)
    responsible_name = models.CharField('负责人', max_length=20, null=False)
    test_user = models.CharField('测试人员', max_length=100, null=False)
    dev_user = models.CharField('开发人员', max_length=100, null=False)
    publish_app = models.CharField('发布应用', max_length=100, null=False)
    simple_desc = models.CharField('简要描述', max_length=100, null=True)
    other_desc = models.CharField('其他信息', max_length=100, null=True)
    objects = ProjectInfoManager()


class ModuleInfo(BaseTable):
    class Meta:
        verbose_name = '模块信息'
        db_table = 'ModuleInfo'

    module_name = models.CharField('模块名称', max_length=50, null=False)
    belong_project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
    test_user = models.CharField('测试负责人', max_length=50, null=False)
    simple_desc = models.CharField('简要描述', max_length=100, null=True)
    other_desc = models.CharField('其他信息', max_length=100, null=True)
    objects = ModuleInfoManager()


class TestCaseInfo(BaseTable):
    class Meta:
        verbose_name = '用例信息'
        db_table = 'TestCaseInfo'

    type = models.IntegerField('test/config', default=1)
    name = models.CharField('用例/配置名称', max_length=50, null=False)
    belong_project = models.CharField('所属项目', max_length=50, null=False)
    belong_module = models.ForeignKey(ModuleInfo, on_delete=models.CASCADE)
    include = models.CharField('前置config/test', max_length=1024, null=True)
    author = models.CharField('编写人员', max_length=20, null=False)
    request = models.TextField('请求信息', null=False)

    objects = TestCaseInfoManager()


class TestReports(BaseTable):
    class Meta:
        verbose_name = "测试报告"
        db_table = 'TestReports'

    report_name = models.CharField(max_length=40, null=False)
    start_at = models.CharField(max_length=40, null=True)
    status = models.BooleanField()
    testsRun = models.IntegerField()
    successes = models.IntegerField()
    reports = models.TextField()


class EnvInfo(BaseTable):
    class Meta:
        verbose_name = '环境管理'
        db_table = 'EnvInfo'

    env_name = models.CharField(max_length=40, null=False, unique=True)
    base_url = models.CharField(max_length=40, null=False)
    simple_desc = models.CharField(max_length=50, null=False)
    objects = EnvInfoManager()


class DebugTalk(BaseTable):
    class Meta:
        verbose_name = '驱动py文件'
        db_table = 'DebugTalk'

    belong_project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
    debugtalk = models.TextField(null=True, default='#debugtalk.py')


class TestSuite(BaseTable):
    class Meta:
        verbose_name = '用例集合'
        db_table = 'TestSuite'

    belong_project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
    suite_name = models.CharField(max_length=100, null=False)
    include = models.TextField(null=False)
