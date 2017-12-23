import json

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

# Create your views here.
from ApiManager.forms import username_validate, password_validate, email_validate
from ApiManager.models import UserInfo, UserType

'''用户注册'''


def register(request):
    error_msg = {'error': ''}
    if request.method == 'POST':
        username = request.POST.get('username', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        re_password = request.POST.get('ensurepwd', None)
        request.session['username'] = username
        request.session['email'] = email
        if username_validate(username) == 'ok':
            if password_validate(password) == 'ok':
                if re_password == '':
                    error_msg['error'] = '确认密码不能为空'
                elif re_password != password:
                    error_msg['error'] = '确认密码必须和密码保持一致'
                else:
                    if not email_validate(email) == 'ok':
                        error_msg['error'] = email_validate(email)
                    else:
                        # 后台校验通过，进行数据库重复校验逻辑
                        if UserInfo.objects.filter(username__exact=username).count() > 0 or \
                                        UserInfo.objects.filter(email__exact=email).count() > 0:
                            error_msg['error'] = '用户名或邮箱已被其他用户注册'
                        else:
                            del request.session['username']  # 删掉session
                            del request.session['email']

                            obj = UserType.objects.get_objects(1)  # 普通用户
                            UserInfo.objects.insert_user(username, password, email, obj)
                            return redirect('/api/login/')
            else:
                error_msg['error'] = password_validate(password)
        else:
            error_msg['error'] = username_validate(username)

    return render_to_response('register.html', {'error_msg': error_msg,
                                                'username': request.session.get('username', ''),
                                                'email': request.session.get('email', '')})


'''登录'''


def login(request):
    error_msg = {'error': ''}
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        if UserInfo.objects.query_user(username, password) == 1:
            return redirect('/api/index/')
        else:
            error_msg['error'] = '用户名或密码错误'

    return render_to_response('login.html', {'error_msg': error_msg})


'''首页'''


def index(request):
    return render_to_response('index.html')


'''添加项目'''


def add_project(request):
    return render_to_response('add_project.html')


'''添加模块'''


def add_module(request):
    return render_to_response('add_module.html')


'''添加配置'''


def add_config(request):
    return render_to_response('add_config.html')


'''添加用例'''


def add_case(request):
    if request.method == 'POST':
        test = json.loads(request.body.decode('utf-8'))
        for value in test:
            print(sorted(value.items()))
        return HttpResponse('用例添加成功')
    return render_to_response('add_case.html')


'''添加接口'''


def add_api(request):
    return render_to_response('add_api.html')
