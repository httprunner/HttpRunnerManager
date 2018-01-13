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
            if kwargs.get('project_name') != project_opt.get_pro_name('',
                                            type=False, id = kwargs.get('index')) and project_opt.get_pro_name(
                kwargs.get('project_name')) > 0:
                return '该项目已存在， 请重新命名'
            project_opt.update_project(kwargs.pop('index'), kwargs.pop('project_name'), kwargs.pop('responsible_name'),
                                       kwargs.pop('test_user'), kwargs.pop('dev_user'), kwargs.pop('publish_app'),
                                       kwargs.pop('simple_desc'), kwargs.pop('other_desc'))


    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'


'''模块数据落地'''


def add_module_data(type, **kwargs):
    module_opt = ModuleInfo.objects
    belong_project = kwargs.pop('belong_project')
    try:
        if type:
            if module_opt.filter(belong_project__pro_name__exact = belong_project)\
                            .filter(module_name__exact = kwargs.get('module_name')).count() < 1:
                belong_project = ProjectInfo.objects.get_pro_name(belong_project, type=False)
                module_opt.insert_module(kwargs.pop('module_name'), belong_project, kwargs.pop('test_user'),
                                                 kwargs.pop('lifting_time'), kwargs.pop('simple_desc'),
                                                 kwargs.pop('other_desc'))
            else:
                return '该模块已在项目中存在，请重新编辑'
        else:
            if kwargs.get('module_name') != module_opt.get_module_name('',type = False, id = kwargs.get('index')) \
                    and module_opt.filter(belong_project__pro_name__exact = belong_project)\
                            .filter(module_name__exact = kwargs.get('module_name')).count() > 0:
                return '该模块已存在，请重新命名'
            module_opt.update_module(kwargs.pop('index'), kwargs.pop('module_name'), kwargs.get('test_user'), kwargs.pop('lifting_time'),
                                     kwargs.pop('simple_desc'), kwargs.pop('other_desc'))

    except DataError:
        return '字段长度超长，请重新编辑'
    except ValidationError:
        return '提测时间格式非法'
    return 'ok'


'''用例数据落地'''


def add_case_data(**kwargs):
    case_info = kwargs.get('test').get('case_info')
    case_opt = TestCaseInfo.objects
    try:
        if case_opt.get_case_name(kwargs.get('test').get('name'), case_info.get('module'), case_info.get('project')) < 1:
            belong_module = ModuleInfo.objects.get_module_name(case_info.get('module'), type=False, project=case_info.get('project'))
            case_opt.insert_case(belong_module, **kwargs)
        else:
            return '用例或配置已存在，请重新编辑'
    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'


'''配置数据落地'''


def add_config_data(**kwargs):
    case_opt = TestCaseInfo.objects
    config_info = kwargs.get('config').get('config_info')
    try:
        if case_opt.get_case_name(kwargs.get('config').get('name'), config_info.get('config_module'), config_info.get('project')) < 1:
            belong_module = ModuleInfo.objects.get_module_name(config_info.get('config_module'), type=False, project=config_info.get('project'))
            case_opt.insert_config(belong_module, **kwargs)
        else:
            return '用例或配置已存在，请重新编辑'
    except DataError:
        return '字段长度超长，请重新编辑'
    return 'ok'



'''改变状态'''


def change_status(Model, **kwargs):
    name = kwargs.pop('name')
    obj = Model.objects.get(id=name)
    obj.status = kwargs.pop('status')
    obj.save()
    return 'ok'