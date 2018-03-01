import re

'''
用户名正则匹配验证
'''


def username_validate(value):
    if value == '':
        return '用户名不能为空'
    else:
        username = re.compile(r'^[a-z0-9_-]{3,16}$')
        if not username.match(value):
            return '用户名格式错误'
        else:
            return 'ok'


'''
密码格式匹配
'''


def password_validate(value):
    if value == '':
        return '密码不能为空'
    else:
        password = re.compile(r'^[a-z0-9_-]{6,18}$')
        if not password.match(value):
            return '密码格式错误'
        return 'ok'


'''
邮箱格式验证
'''


def email_validate(value):
    if value == '':
        return '邮箱不能为空'
    else:
        email = re.compile(r'^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$')
        if not email.match(value):
            return '邮箱格式错误'
        return 'ok'
