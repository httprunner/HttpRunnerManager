import logging

from djcelery.models import PeriodicTask

from ApiManager.models import ModuleInfo
from ApiManager.utils.operation import add_project_data, add_module_data, add_case_data, add_config_data, \
    add_register_data
from ApiManager.utils.task_opt import create_task

logger = logging.getLogger('HttpRunnerManager')


def type_change(type, value):
    try:
        if type == 'string':
            value = str(value)
        elif type == 'float':
            value = float(value)
        elif type == 'int':
            value = int(value)
    except ValueError:
        logger.error('{value}转换{type}失败'.format(value=value, type=type))
        return 'error'
    if type == 'boolean':
        if value == 'False':
            value = False
        elif value == 'True':
            value = True
        else:
            return 'error'
    return value


def key_value_list(keyword, **kwargs):
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        lists = []
        test = kwargs.pop('test')
        for value in test:
            try:
                key = value.pop('key')
                val = value.pop('value')
                type = value.pop('type')
            except KeyError:
                pass
            tips = '{keyword}: {val}格式错误,不是{type}类型'.format(keyword=keyword, val=val, type=type)
            if key != '' and val != '':
                if keyword == 'validate':
                    value['check'] = key
                    msg = type_change(type, val)
                    if msg == 'error':
                        return tips
                    value['expected'] = msg
                elif keyword == 'extract':
                    value[key] = val
                elif keyword == 'variables':
                    msg = type_change(type, val)
                    if msg == 'error':
                        return tips
                    value[key] = msg
                elif keyword == 'parameters':
                    try:
                        value[key] = eval(val)
                    except Exception:
                        logging.error('{val}->eval 异常'.format(val=val))
                        return '{keyword}: {val}格式错误'.format(keyword=keyword, val=val)

                lists.append(value)
        return lists


def key_value_dict(keyword, **kwargs):
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        dicts = {}
        test = kwargs.pop('test')
        for value in test:
            try:
                key = value.pop('key')
                val = value.pop('value')
                type = value.pop('type')
            except KeyError:
                pass

            if key != '' and val != '':
                if keyword == 'headers':
                    value[key] = val
                elif keyword == 'data':
                    msg = type_change(type, val)
                    if msg == 'error':
                        return '{keyword}: {val}格式错误,不是{type}类型'.format(keyword=keyword, val=val, type=type)
                    value[key] = msg
                dicts.update(value)
        return dicts


'''动态加载模块'''


def load_modules(**kwargs):
    belong_project = kwargs.get('name').get('project')
    module_info = list(ModuleInfo.objects.get_module_info(belong_project))
    string = ''
    for value in module_info:
        string = string + value + 'replaceFlag'

    return string[:len(string) - 11]


'''模块信息逻辑及落地'''


def module_info_logic(type=True, **kwargs):
    if kwargs.get('module_name') is '':
        return '模块名称不能为空'
    if kwargs.get('belong_project') is '':
        return '请先添加项目'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    return add_module_data(type, **kwargs)


'''项目信息逻辑及落地'''


def project_info_logic(type=True, **kwargs):
    if kwargs.get('project_name') is '':
        return '项目名称不能为空'
    if kwargs.get('responsible_name') is '':
        return '负责人不能为空'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    if kwargs.get('dev_user') is '':
        return '开发人员不能为空'
    if kwargs.get('publish_app') is '':
        return '发布应用不能为空'

    return add_project_data(type, **kwargs)


'''用例信息逻辑及落地'''


def case_info_logic(type=True, **kwargs):
    test = kwargs.pop('test')
    '''
        动态展示模块
    '''
    if 'request' not in test.keys():
        return load_modules(**test)
    else:
        logging.info('用例原始信息: {kwargs}'.format(kwargs=kwargs))
        if test.get('name').get('case_name') is '':
            return '用例名称不可为空'
        if test.get('name').get('project') is None or test.get('name').get('project') is '':
            return '请先添加项目'
        if test.get('name').get('module') is None or test.get('name').get('module') is '':
            return '请先添加模块'
        if test.get('name').get('author') is '':
            return '创建者不能为空'
        if test.get('request').get('url') is '':
            return '接口地址不能为空'

        name = test.pop('name')
        test.setdefault('name', name.pop('case_name'))

        test.setdefault('case_info', name)

        validate = test.pop('validate')
        if validate:
            validate_list = key_value_list('validate', **validate)
            if not isinstance(validate_list, list):
                return validate_list
            test.setdefault('validate', validate_list)

        extract = test.pop('extract')
        if extract:
            test.setdefault('extract', key_value_list('extract', **extract))

        request_data = test.get('request').pop('request_data')
        data_type = test.get('request').pop('type')
        if request_data and data_type:
            if data_type == 'json':
                test.get('request').setdefault(data_type, request_data)
            else:
                data_dict = key_value_dict('data', **request_data)
                if not isinstance(data_dict, dict):
                    return data_dict
                test.get('request').setdefault(data_type, data_dict)

        headers = test.get('request').pop('headers')
        if headers:
            test.get('request').setdefault('headers', key_value_dict('headers', **headers))

        variables = test.pop('variables')
        if variables:
            variables_list = key_value_list('variables', **variables)
            if not isinstance(variables_list, list):
                return variables_list
            test.setdefault('variables', variables_list)

        parameters = test.pop('parameters')
        if parameters:
            params_list = key_value_list('parameters', **parameters)
            if not isinstance(params_list, list):
                return params_list
            test.setdefault('parameters', params_list)

        kwargs.setdefault('test', test)
        return add_case_data(type, **kwargs)


'''模块信息逻辑及落地'''


def config_info_logic(type=True, **kwargs):
    config = kwargs.pop('config')
    '''
        动态展示模块
    '''
    if 'request' not in config.keys():
        return load_modules(**config)
    else:
        logging.debug('配置原始信息: {kwargs}'.format(kwargs=kwargs))
        if config.get('name').get('config_name') is '':
            return '配置名称不可为空'
        if config.get('name').get('project') is None or config.get('name').get('project') is '':
            return '请先添加项目'
        if config.get('name').get('config_module') is None or config.get('name').get('config_module') is '':
            return '请先添加模块'
        if config.get('name').get('config_author') is '':
            return '创建者不能为空'

        name = config.pop('name')
        config.setdefault('name', name.pop('config_name'))

        config.setdefault('config_info', name)

        request_data = config.get('request').pop('request_data')
        data_type = config.get('request').pop('type')
        if request_data and data_type:
            if data_type == 'json':
                config.get('request').setdefault(data_type, request_data)
            else:
                data_dict = key_value_dict('data', **request_data)
                if not isinstance(data_dict, dict):
                    return data_dict
                config.get('request').setdefault(data_type, data_dict)

        headers = config.get('request').pop('headers')
        if headers:
            config.get('request').setdefault('headers', key_value_dict('headers', **headers))

        variables = config.pop('variables')
        if variables:
            variables_list = key_value_list('variables', **variables)
            if not isinstance(variables_list, list):
                return variables_list
            config.setdefault('variables', variables_list)

        parameters = config.pop('parameters')
        if parameters:
            params_list = key_value_list('parameters', **parameters)
            if not isinstance(params_list, list):
                return params_list
            config.setdefault('parameters', params_list)
        kwargs.setdefault('config', config)
        return add_config_data(type, **kwargs)


def task_logic(**kwargs):
    if kwargs.get('name') is '':
        return '任务名称不可为空'
    elif kwargs.get('project') is '':
        return '请选择一个项目'
    elif kwargs.get('crontab_time') is '':
        return '定时配置不可为空'
    elif kwargs.get('module') is '':
        kwargs.pop('module')
    try:
        crontab_time = kwargs.pop('crontab_time').split(' ')
        if len(crontab_time) > 5:
            return '定时配置参数格式不正确'
        crontab = {
            'day_of_week': crontab_time[-1],
            'month_of_year': crontab_time[3],  # 月份
            'day_of_month': crontab_time[2],  # 日期
            'hour': crontab_time[1],  # 小时
            'minute': crontab_time[0],  # 分钟
        }
    except Exception:
        return '定时配置参数格式不正确'
    if PeriodicTask.objects.filter(name__exact=kwargs.get('name')).count() > 0:
        return '任务名称重复，请重新命名'
    desc = " ".join(str(i) for i in crontab_time)
    name = kwargs.pop('name')
    if 'module' in kwargs.keys():
        return create_task(name, 'ApiManager.tasks.module_hrun', kwargs, crontab, desc)
    else:
        return create_task(name, 'ApiManager.tasks.project_hrun', kwargs, crontab, desc)


'''查询session'''


def set_filter_session(request):
    request.session['user'] = request.POST.get('user', '')
    request.session['name'] = request.POST.get('name', '')
    request.session['belong_project'] = request.POST.get('belong_project', '')
    request.session['belong_module'] = request.POST.get('belong_module', '')
    request.session['report_name'] = request.POST.get('report_name', '')

    filter_query = {'user': request.session['user'], 'name': request.session['name'],
                    'belong_project': request.session['belong_project'],
                    'belong_module': request.session['belong_module'], 'report_name': request.session['report_name']}

    return filter_query


'''ajax异步提示'''


def get_ajax_msg(msg, success):
    return success if msg is 'ok' else msg


'''注册信息逻辑判断'''


def register_info_logic(**kwargs):
    return add_register_data(**kwargs)
