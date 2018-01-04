from django.core.exceptions import ValidationError
from django.db import DataError
from django.http import HttpResponse

from ApiManager.models import ProjectInfo, ModuleInfo


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

def add_module_data(**kwargs):
    if ProjectInfo.objects.all().count() < 1:
        return HttpResponse('请先添加项目！')
    else:
        try:
            if True:
                belong_project = ProjectInfo.objects.get_pro_name(kwargs.pop('belong_project'), type = False)
                ModuleInfo.objects.insert_module(kwargs.pop('module_name'), belong_project , kwargs.pop('test_user'),
                                                 kwargs.pop('lifting_time'), kwargs.pop('simple_desc'), kwargs.pop('other_desc'))
            else:
                return '该模块已在项目中存在，请重新编辑'
        except DataError:
            return '字段长度超长，请重新编辑'
        except ValidationError:
            return '提测时间格式非法，请使用 YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] 格式'
    return 'ok'


def add_case_data(**kwargs):
    pass

