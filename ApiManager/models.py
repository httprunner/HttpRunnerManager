from django.db import models

# Create your models here.
from ApiManager.managers import UserTypeManager, UserInfoManager, ProjectInfoManager, ModuleInfoManager, \
    TestCaseInfoManager


class BaseTable(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

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

    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.EmailField()
    status = models.IntegerField(default=1)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE)
    objects = UserInfoManager()


class ProjectInfo(BaseTable):
    class Meta:
        verbose_name = '项目信息'
        db_table = 'ProjectInfo'

    pro_name = models.CharField(max_length=50)
    responsible_name = models.CharField(max_length=20)
    test_user = models.CharField(max_length=100)
    dev_user = models.CharField(max_length=100)
    publish_app = models.CharField(max_length=60)
    simple_desc = models.CharField(max_length=100, null=True)
    other_desc = models.CharField(max_length=100, null=True)
    status = models.IntegerField(default=1)
    objects = ProjectInfoManager()


class ModuleInfo(BaseTable):
    class Meta:
        verbose_name = '模块信息'
        db_table = 'ModuleInfo'

    module_name = models.CharField(max_length=50)
    belong_project = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
    test_user = models.CharField(max_length=50)
    lifting_time = models.DateTimeField()
    simple_desc = models.CharField(max_length=100, null=True)
    other_desc = models.CharField(max_length=100, null=True)
    status = models.IntegerField(default=1)
    objects = ModuleInfoManager()


class TestCaseInfo(BaseTable):
    class Meta:
        verbose_name = '用例信息'
        db_table = 'TestCaseInfo'

    type = models.IntegerField(default=1)
    name = models.CharField(max_length=50)
    belong_project = models.CharField(max_length=50)
    belong_module = models.ForeignKey(ModuleInfo, on_delete=models.CASCADE)
    include = models.CharField(max_length=200, null=True)
    author = models.CharField(max_length=20)
    request = models.TextField()
    status = models.IntegerField(default=1)
    objects = TestCaseInfoManager()


class TestReports(BaseTable):
    class Meta:
        verbose_name = "测试报告"
        db_table = 'TestReports'

    name = models.CharField(max_length=50)
    belong_project = models.CharField(max_length=50)
    belong_module = models.CharField(max_length=50)
    reports = models.TextField()
    status = models.IntegerField(default=1)
