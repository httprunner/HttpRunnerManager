from django.db import models

# Create your models here.
from ApiManager.managers import UserTypeManager, UserInfoManager, ProjectInfoManager, ModuleInfoManager

'''
用户类型表
'''
class UserType(models.Model):
    class Meta:
        db_table = 'UserType'
    user_type_id = models.IntegerField(primary_key=True,db_column='user_type_id')
    type_name = models.CharField(max_length=20)
    type_desc = models.CharField(max_length=50)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    objects = UserTypeManager()
'''
用户信息表
'''
class UserInfo(models.Model):
    class Meta:
        db_table = 'UserInfo'
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.EmailField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    status = models.IntegerField(default=1)
    user_type = models.ForeignKey(UserType,db_column='user_type', on_delete=models.CASCADE)
    objects = UserInfoManager()

'''项目信息表'''
class ProjectInfo(models.Model):
    class Meta:
        db_table = 'ProjectInfo'
    project_id = models.IntegerField(primary_key=True, db_column='project_id')
    pro_name = models.CharField(max_length=50)
    responsible_name = models.CharField(max_length=20)
    test_user = models.CharField(max_length=100)
    dev_user = models.CharField(max_length=100)
    publish_app = models.CharField(max_length=60)
    simple_desc = models.CharField(max_length=100, null=True)
    other_desc = models.CharField(max_length=100, null=True)
    status = models.IntegerField(default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    objects = ProjectInfoManager()


class ModuleInfo(models.Model):
    class Meta:
        db_table = 'ModuleInfo'
    module_name = models.CharField(max_length=100)
    belong_project = models.ForeignKey(ProjectInfo,db_column='belong_project', on_delete=models.CASCADE)
    test_user = models.CharField(max_length=50)
    lifting_time = models.DateTimeField()
    simple_desc = models.CharField(max_length=100, null=True)
    other_desc = models.CharField(max_length=100, null=True)
    status = models.IntegerField(default=1)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    objects = ModuleInfoManager()








