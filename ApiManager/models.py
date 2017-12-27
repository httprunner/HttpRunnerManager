from django.db import models

# Create your models here.
from ApiManager.managers import UserTypeManager, UserInfoManager

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






