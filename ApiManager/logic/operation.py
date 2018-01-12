from django.core.exceptions import ValidationError
from django.db import DataError

from ApiManager.models import ProjectInfo, ModuleInfo, TestCaseInfo

'''项目数据落地'''


def add_project_data(type, **kwargs):
    project_opt = ProjectInfo.objects
    try:
        if type:
            if project_opt.get_pro_name(kwargs.get('project_name')) < 1:
                project_opt.insert_project(kwargs.pop('project_name'), kwargs.pop('responsible_name'),
                                           kwargs.pop('test_user'), kwargs.pop('dev_user'), kwargs.pop('publish_app'),
                                           kwargs.pop('simple_desc'), kwargs.pop('other_desc'))
            else:
                return '该项目已存在，请重新编辑'
        else:
            project_opt.update_project(kwargs.pop('project_name'), kwargs.pop('responsible_name'),
                                       kwargs.pop('test_user'), kwargs.pop('dev_user'), kwargs.pop('publish_app'),
                                       kwargs.pop('simple_desc'), kwargs.pop('other_desc'))

    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'


'''改变状态'''


def change_status(Model, type='pro', **kwargs):
    name = kwargs.pop('name')

    obj = Model.objects.get(pro_name=name)
    if type == 'module':
        obj = Model.objects.get(module_name=name)
    elif type == 'test':
        obj = Model.objects.get(name=name)

    obj.status = kwargs.pop('status')
    obj.save()
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
    case_info = kwargs.get('test').get('case_info')
    try:
        if TestCaseInfo.objects.get_case_name(kwargs.get('test').get('name'), case_info.get('module')) < 1:
            belong_module = ModuleInfo.objects.get_module_name(case_info.get('module'), type=False)
            TestCaseInfo.objects.insert_case(belong_module, **kwargs)
        else:
            return '用例或配置已存在，请重新编辑'
    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'


'''配置数据落地'''


def add_config_data(**kwargs):
    config_info = kwargs.get('config').get('config_info')
    try:
        if TestCaseInfo.objects.get_case_name(kwargs.get('config').get('name'), config_info.get('config_module')) < 1:
            belong_module = ModuleInfo.objects.get_module_name(config_info.get('config_module'), type=False)
            TestCaseInfo.objects.insert_config(belong_module, **kwargs)
        else:
            return '用例或配置已存在，请重新编辑'
    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'
