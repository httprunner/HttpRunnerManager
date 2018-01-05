import json

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from ApiManager.forms import username_validate, password_validate, email_validate
from ApiManager.logic.common import module_info_logic, project_info_logic, case_info_logic
from ApiManager.models import UserInfo, UserType, ProjectInfo
from httprunner.cli import main_ate

# Create your views here.

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
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))
        msg = project_info_logic(**project_info)

        if msg is 'ok':
            return HttpResponse('项目添加成功')
        else:
            return HttpResponse(msg)
    elif request.method == 'GET':
        return render_to_response('add_project.html')


'''添加模块'''


def add_module(request):
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        msg = module_info_logic(**module_info)

        if msg is 'ok':
            return HttpResponse('模块添加成功')
        else:
            return HttpResponse(msg)

    elif request.method == 'GET':

        return render_to_response('add_module.html', {'data': ProjectInfo.objects.all().values('pro_name')})

'''
添加用例
'''
def add_case(request):
    project = ProjectInfo.objects.all().values('pro_name').order_by('-create_time')

    if request.is_ajax():
        testcase_lists = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(**testcase_lists)
        if msg is 'ok':
            return HttpResponse('用例添加成功')
        else:
            return HttpResponse(msg)
    elif request.method == 'GET':
        return render_to_response('add_case.html', {'project': project})

'''添加配置'''


def add_config(request):
    project = ProjectInfo.objects.all().values('pro_name').order_by('-create_time')

    if request.is_ajax():
        testconfig_lists = json.loads(request.body.decode('utf-8'))

    elif request.method == 'GET':
        return render_to_response('add_config.html', {'project': project})

'''运行用例'''
def run_test(request):
    if request.is_ajax():
        testcase_lists = json.loads(request.body.decode('utf-8'))

        if main_ate(testcase_lists):
            return HttpResponse('ok')
        else:
            return HttpResponse('fail')



'''添加接口'''


def add_api(request):
    return render_to_response('add_api.html')


'''测试代码'''


def test_get(request):
    if request.method == 'GET':
        if request.GET.get('username') == 'lcc':
            return HttpResponse(json.dumps({'status': 'ok'}))
        else:
            return HttpResponse('illegal')
    elif request.method == 'POST':

        if request.POST.get('username') == 'lcc' and request.POST.get('password') == 'lcc':
            a = {'login': 'success'}
            return HttpResponse(json.dumps(a))
        elif json.loads(request.body.decode('utf-8')).get('username') == 'yinquanwang':
            return HttpResponse('this is a json post request')
        else:
            return HttpResponse('this is a post request')
