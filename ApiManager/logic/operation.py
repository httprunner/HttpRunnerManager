from django.core.exceptions import ValidationError
from django.db import DataError

from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo

'''项目数据落地'''


def add_project_data(**kwargs):
    project_opt = ProjectInfo.objects
    try:
        if project_opt.get_pro_name(kwargs.get('project_name')) < 1:
            project_opt.insert_project(kwargs.pop('project_name'), kwargs.pop('responsible_name'),
                                       kwargs.pop('test_user'), kwargs.pop('dev_user'), kwargs.pop('publish_app'),
                                       kwargs.pop('simple_desc'), kwargs.pop('other_desc'))
        else:
            return '该项目已存在，请重新编辑'
    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'


'''模块数据落地'''


def add_module_data(**kwargs):
    try:
        if ModuleInfo.objects.get_module_name(kwargs.get('module_name')) < 1:
            belong_project = ProjectInfo.objects.get_pro_name(kwargs.pop('belong_project'), type=False)
            ModuleInfo.objects.insert_module(kwargs.pop('module_name'), belong_project, kwargs.pop('test_user'),
                                             kwargs.pop('lifting_time'), kwargs.pop('simple_desc'),
                                             kwargs.pop('other_desc'))
        else:
            return '该模块已在项目中存在，请重新编辑'
    except DataError:
        return '字段长度超长，请重新编辑'
    except ValidationError:
        return '提测时间格式非法'
    return 'ok'


'''用例数据落地'''


def add_case_data(**kwargs):
    name = kwargs.get('name')
    try:
        if TestCaseInfo.objects.get_case_name(name.get('case_name'), name.get('module')) < 1:
            belong_module = ModuleInfo.objects.get_module_name(name.get('module'), type=False)
            TestCaseInfo.objects.insert_case(belong_module, **kwargs)
        else:
            return '用例已存在，请重新编辑'
    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'
