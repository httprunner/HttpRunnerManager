from ApiManager.utils.operation import add_project_data, add_module_data, add_case_data, add_config_data, \
    add_register_data, bulk_import_data
from ApiManager.models import ModuleInfo
import yaml

'''前端test信息转字典'''


def key_value_dict(mode=3, **kwargs):
    if not kwargs:
        return None
    sorted_kwargs = sorted(kwargs.items())
    kwargs.clear()
    if mode == 3:
        half_index = len(sorted_kwargs) // 3

        for value in range(half_index):
            key = sorted_kwargs[value][1]
            data_type = sorted_kwargs[value + 2 * half_index][1]
            value = sorted_kwargs[half_index + value][1]
            if key != '' and value != '':
                try:
                    if data_type == 'string':
                        value = str(value)
                    elif data_type == 'float':
                        value = float(value)
                    elif data_type == 'int':
                        value = int(value)
                    else:
                        value = bool(value)
                except ValueError:  # 如果类型转换失败，默认字符串保存
                    pass
            if key != '' and value != '':
                kwargs.setdefault(key, value)
    else:
        half_index = len(sorted_kwargs) // 2

        for value in range(half_index):
            key = sorted_kwargs[value][1]
            value = sorted_kwargs[half_index + value][1]
            if key != '' and value != '':
                kwargs.setdefault(key, value)

    return kwargs


'''前端test信息转列表'''


def key_value_list(mode=4, **kwargs):
    if not kwargs:
        return None
    sorted_kwargs = sorted(kwargs.items())
    lists = []
    if mode == 4:
        half_index = len(sorted_kwargs) // 4
        for value in range(half_index):
            check = sorted_kwargs[value][1]
            expected = sorted_kwargs[value + half_index][1]
            comparator = sorted_kwargs[value + 2 * half_index][1]
            data_type = sorted_kwargs[value + 3 * half_index][1]
            if check != '' and expected != '':
                try:
                    if data_type == 'string':
                        expected = str(expected)
                    elif data_type == 'float':
                        expected = float(expected)
                    elif data_type == 'int':
                        expected = int(expected)
                    else:
                        expected = bool(expected)
                except ValueError:  # 如果类型转换失败，默认字符串保存
                    pass

                lists.append({'check': check, 'comparator': comparator, 'expected': expected})
    elif mode == 3:
        half_index = len(sorted_kwargs) // 3
        for value in range(half_index):
            key = sorted_kwargs[value][1]
            data_type = sorted_kwargs[value + 2 * half_index][1]
            value = sorted_kwargs[half_index + value][1]
            if key != '' and value != '':
                try:
                    if data_type == 'string':
                        value = str(value)
                    elif data_type == 'float':
                        value = float(value)
                    elif data_type == 'int':
                        value = int(value)
                    else:
                        value = bool(value)
                except ValueError:  # 如果类型转换失败，默认字符串保存
                    pass
                lists.append({key: value})
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
    if kwargs.get('lifting_time') is '':
        return '提测时间不能为空'
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
        test.setdefault('validate', key_value_list(**validate))

        extract = test.pop('extract')
        if extract:
            test.setdefault('extract', key_value_list(mode=2, **extract))

        request_data = test.get('request').pop('request_data')
        date_type = test.get('request').pop('type')
        if request_data and date_type:
            test.get('request').setdefault(date_type, key_value_dict(**request_data))

        headers = test.get('request').pop('headers')
        if headers:
            test.get('request').setdefault('headers', key_value_dict(mode=2, **headers))

        variables = test.pop('variables')
        if variables:
            test.setdefault('variables', key_value_list(mode=3, **variables))

        setup = test.pop('setup')
        if setup:
            test.setdefault('setup', key_value_list(mode=2, **setup))

        teardown = test.pop('teardown')
        if teardown:
            test.setdefault('teardown', key_value_list(mode=2, **teardown))

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
            config.get('request').setdefault(data_type, key_value_dict(**request_data))

        headers = config.get('request').pop('headers')
        if headers:
            config.get('request').setdefault('headers', key_value_dict(mode=2, **headers))

        variables = config.pop('variables')
        if variables:
            config.setdefault('variables', key_value_list(mode=3, **variables))

        kwargs.setdefault('config', config)
        return add_config_data(type, **kwargs)


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


'''注册信息逻辑判断'''


def register_info_logic(**kwargs):
    return add_register_data(**kwargs)


'''上传yml文件内容转列表'''


def yml_parser(file_path):
    with open(file_path, 'r') as f:
        s = yaml.load(f)
    data = {'case_info': s}
    bulk_import_data(**data)
    return s
