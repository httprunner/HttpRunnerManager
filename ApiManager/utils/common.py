import logging

from ApiManager.models import ModuleInfo
from ApiManager.utils.operation import add_project_data, add_module_data, add_case_data, add_config_data, \
    add_register_data

logger = logging.getLogger('HttpRunnerManager')


def type_change(type, value):
    try:
        if type == 'string':
            value = str(value)
        elif type == 'float':
            value = float(value)
        elif type == 'int':
            value = int(value)
        else:
            value = bool(value)
    except ValueError:
        logger.error('{type}转换失败，默认转换为str类型'.format(type=type))
    return value


def key_value_list(key, **kwargs):
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        lists = []
        test = kwargs.pop('test')
        for value in test:
            if value.get('key') != '' and value.get('value') != '':
                if key == 'validate':
                    value['check'] = value.pop('key')
                    value['expected'] = type_change(value.pop('type'), value.pop('value'))
                elif key == 'extract':
                    value[value.pop('key')] = value.pop('value')
                elif key == 'variables':
                    value[value.pop('key')] = type_change(value.pop('type'), value.pop('value'))
                lists.append(value)
        return lists


def key_value_dict(key, **kwargs):
    if not isinstance(kwargs, dict) or not kwargs:
        return None
    else:
        dicts = {}
        test = kwargs.pop('test')
        for value in test:
            if value.get('key') != '' and value.get('value') != '':
                if key == 'headers':
                    value[value.pop('key')] = value.pop('value')
                elif key == 'data':
                    value[value.pop('key')] = type_change(value.pop('type'), value.pop('value'))
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
        if not test.get('validate'):
            return '至少需要一个结果校验！'

        name = test.pop('name')
        test.setdefault('name', name.pop('case_name'))

        test.setdefault('case_info', name)

        validate = test.pop('validate')
        test.setdefault('validate', key_value_list('validate', **validate))

        extract = test.pop('extract')
        if extract:
            test.setdefault('extract', key_value_list('extract', **extract))

        request_data = test.get('request').pop('request_data')
        data_type = test.get('request').pop('type')
        if request_data and data_type:
            if data_type == 'json':
                test.get('request').setdefault(data_type, request_data)
            else:
                test.get('request').setdefault(data_type, key_value_dict('data', **request_data))

        headers = test.get('request').pop('headers')
        if headers:
            test.get('request').setdefault('headers', key_value_dict('headers', **headers))

        variables = test.pop('variables')
        if variables:
            test.setdefault('variables', key_value_list('variables', **variables))

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
                config.get('request').setdefault(data_type, key_value_dict('data', **request_data))

        headers = config.get('request').pop('headers')
        if headers:
            config.get('request').setdefault('headers', key_value_dict('headers', **headers))

        variables = config.pop('variables')
        if variables:
            config.setdefault('variables', key_value_list('variables', **variables))

        kwargs.setdefault('config', config)
        return add_config_data(type, **kwargs)


'''查询session'''


def set_filter_session(request):
    request.session['user'] = request.POST.get('user', '')
    request.session['name'] = request.POST.get('name', '')
    request.session['belong_project'] = request.POST.get('belong_project', '')
    request.session['belong_module'] = request.POST.get('belong_module', '')

    filter_query = {'user': request.session['user'], 'name': request.session['name'],
                    'belong_project': request.session['belong_project'],
                    'belong_module': request.session['belong_module']}

    return filter_query


'''ajax异步提示'''


def get_ajax_msg(msg, success):
    return success if msg is 'ok' else msg


'''注册信息逻辑判断'''


def register_info_logic(**kwargs):
    return add_register_data(**kwargs)
