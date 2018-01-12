from django.http import HttpResponse

from ApiManager.logic.operation import add_project_data, add_module_data, add_case_data, add_config_data
from ApiManager.models import ModuleInfo

'''前端test信息转字典'''


def key_value_dict(**kwargs):
    if not kwargs:
        return None
    sorted_kwargs = sorted(kwargs.items())
    kwargs.clear()
    half_index = len(sorted_kwargs) // 2

    for value in range(half_index):
        key = sorted_kwargs[value][1]
        value = sorted_kwargs[half_index + value][1]
        if key != '' and value != '':
            kwargs.setdefault(key, value)

    return kwargs


'''前端test信息转列表'''


def key_value_list(name='false', **kwargs):
    if not kwargs:
        return None
    sorted_kwargs = sorted(kwargs.items())
    lists = []
    if name == 'true':
        half_index = len(sorted_kwargs) // 3
        for value in range(half_index):
            check = sorted_kwargs[value][1]
            expected = sorted_kwargs[value + half_index][1]
            comparator = sorted_kwargs[value + 2 * half_index][1]
            if check != '' and expected != '':
                lists.append({'check': check, 'comparator': comparator, 'expected': expected})
    else:
        half_index = len(sorted_kwargs) // 2

        for value in range(half_index):
            key = sorted_kwargs[value][1]
            value = sorted_kwargs[half_index + value][1]
            if key != '' and value != '':
                lists.append({key: value})
    if not lists:
        return None
    return lists


def load_case(**kwargs):
    pass


'''动态加载模块'''


def load_modules(**kwargs):
    belong_project = kwargs.get('name').get('project')
    module_info = list(ModuleInfo.objects.get_module_info(belong_project))
    string = ''
    for value in module_info:
        string = string + value + 'replaceFlag'

    return string[:len(string) - 11]


'''模块信息逻辑及落地'''


def module_info_logic(**kwargs):
    if kwargs.get('module_name') is '':
        return '模块名称不能为空'
    if kwargs.get('belong_project') is '':
        return '请先添加项目'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    if kwargs.get('lifting_time') is '':
        return '提测时间不能为空'
    return add_module_data(**kwargs)


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


def case_info_logic(**kwargs):
    test = kwargs.pop('test')
    '''
        动态展示模块
    '''
    if 'request' not in test.keys():
        return load_modules(**test)
    else:
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
        test.setdefault('validate', key_value_list(name='true', **validate))

        extract = test.pop('extract')
        test.setdefault('extract', key_value_list(**extract))

        request_data = test.get('request').pop('request_data')
        test.get('request').setdefault(test.get('request').pop('type'), key_value_dict(**request_data))

        headers = test.get('request').pop('headers')
        test.get('request').setdefault('headers', key_value_dict(**headers))

        variables = test.pop('variables')
        test.setdefault('variables', key_value_list(**variables))

        setUp = test.pop('setUp')
        test.setdefault('setUp', key_value_list(**setUp))

        tearDown = test.pop('tearDown')
        test.setdefault('tearDown', key_value_list(**tearDown))

        kwargs.setdefault('test', test)
        return add_case_data(**kwargs)


'''模块信息逻辑及落地'''


def config_info_logic(**kwargs):
    config = kwargs.pop('config')
    '''
        动态展示模块
    '''
    if 'request' not in config.keys():
        return load_modules(**config)
    else:
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
        config.get('request').setdefault(config.get('request').pop('type'), key_value_dict(**request_data))

        headers = config.get('request').pop('headers')
        config.get('request').setdefault('headers', key_value_dict(**headers))

        variables = config.pop('variables')
        config.setdefault('variables', key_value_list(**variables))

        kwargs.setdefault('config', config)
        return add_config_data(**kwargs)


'''查询session'''


def set_filter_session(request):
    filter_query = {'filter': '1', 'user': '', 'name': ''}
    if request.method == 'POST':
        request.session['filter'] = request.POST.get('filter')
        request.session['user'] = request.POST.get('user')
        request.session['name'] = request.POST.get('name')
        try:
            filter_query = {'filter': request.session['filter'], 'user': request.session['user'],
                            'name': request.session['name']}
        except KeyError:
            pass

    return filter_query


'''ajax异步提示'''


def get_ajax_msg(msg, success):
    if msg is 'ok':
        return success
    else:
        return msg
