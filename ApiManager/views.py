import json

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from ApiManager.forms import username_validate, password_validate, email_validate
from ApiManager.logic.common import module_info_logic, project_info_logic, case_info_logic, config_info_logic, \
    set_filter_session, get_ajax_msg
from ApiManager.logic.operation import change_status
from ApiManager.logic.pagination import get_pager_info
from ApiManager.models import UserInfo, UserType, ProjectInfo, ModuleInfo, TestCaseInfo
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
                            UserInfo.objects.insert_user(
                                username, password, email, obj)
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
        return HttpResponse(get_ajax_msg(msg, '项目添加成功'))

    elif request.method == 'GET':
        return render_to_response('add_project.html')


'''添加模块'''


def add_module(request):
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))
        msg = module_info_logic(**module_info)
        return HttpResponse(get_ajax_msg(msg, '模块添加成功'))

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
        return HttpResponse(get_ajax_msg(msg, '用例添加成功'))
    elif request.method == 'GET':
        return render_to_response('add_case.html', {'project': project})


'''添加配置'''


def add_config(request):
    project = ProjectInfo.objects.all().values('pro_name').order_by('-create_time')

    if request.is_ajax():
        testconfig_lists = json.loads(request.body.decode('utf-8'))

        msg = config_info_logic(**testconfig_lists)
        return HttpResponse(get_ajax_msg(msg, '配置添加成功'))

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


'''项目列表'''


def project_list(request, id):
    if request.is_ajax():
        project_info = json.loads(request.body.decode('utf-8'))

        if 'status' in project_info.keys():
            msg = change_status(ProjectInfo, **project_info)
            return HttpResponse(get_ajax_msg(msg, '项目状态已更改！'))
        else:
            msg = project_info_logic(type=False, **project_info)
            return HttpResponse(get_ajax_msg(msg, '项目信息更新成功'))
    else:
        filter_query = set_filter_session(request)
        pro_list = get_pager_info(
            ProjectInfo, filter_query, '/api/project_list/', id)
        return render_to_response('project_list.html',
                                  {'project': pro_list[1], 'page_list': pro_list[0], 'info': filter_query})


'''模块列表'''


def module_list(request, id):
    if request.is_ajax():
        module_info = json.loads(request.body.decode('utf-8'))

        if 'status' in module_info.keys():
            msg = change_status(ModuleInfo, **module_info)
            return HttpResponse(get_ajax_msg(msg, '模块状态已更改！'))
        else:
            msg = module_info_logic(type=False, **module_info)
            return HttpResponse(get_ajax_msg(msg, '模块信息更新成功'))
    else:
        filter_query = set_filter_session(request)
        module_list = get_pager_info(
            ModuleInfo, filter_query, '/api/module_list/', id)
        return render_to_response('module_list.html',
                                  {'module': module_list[1], 'page_list': module_list[0], 'info': filter_query})


'''配置或用例列表'''


def test_list(request, id):
    filter_query = set_filter_session(request)
    test_list = get_pager_info(
        TestCaseInfo, filter_query, '/api/test_list/', id)
    return render_to_response('test_list.html', {'test': test_list[1], 'page_list': test_list[0], 'info': filter_query})


'''用例编辑'''


def edit_case(request, id):
    if request.is_ajax():
        testcase_lists = json.loads(request.body.decode('utf-8'))
        msg = case_info_logic(**testcase_lists, type=False)
        return HttpResponse(get_ajax_msg(msg, '用例更新成功'))

    elif request.method == 'GET':
        test_info = TestCaseInfo.objects.get_case_by_id(int(id))
        request = eval(test_info[0].request)
        return render_to_response('edit_case.html', {'info': test_info[0], 'request': request['test']})


'''配置编辑'''


def edit_config(request, id):
    if request.is_ajax():
        testconfig_lists = json.loads(request.body.decode('utf-8'))
        msg = config_info_logic(type=False, **testconfig_lists)
        return HttpResponse(get_ajax_msg(msg, '配置更新成功'))

    elif request.method == 'GET':
        test_info = TestCaseInfo.objects.get_case_by_id(int(id))
        request = eval(test_info[0].request)
        return render_to_response('edit_config.html', {'info': test_info[0], 'request': request['config']})


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
