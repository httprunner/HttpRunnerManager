

def key_value_dict(**kwargs):
    sorted_kwargs = sorted(kwargs.items())
    kwargs.clear()
    half_index = len(sorted_kwargs) // 2

    for value in range(half_index):
        key = sorted_kwargs[value][1]
        value = sorted_kwargs[half_index + value][1]
        if key != '' and value != '':
            kwargs.setdefault(key, value)

    return kwargs


def key_value_list(name='false', **kwargs):
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

    return lists


def load_case(path):
    parsed_request = {}
    request = {}
    testcase_lists = []

    for value in path:
        if value is not {}:
            key_name = str(value.keys())
            if 'keyvariables' in key_name:
                parsed_request.setdefault('variables', key_value_list(**value))
            elif 'keyheader' in key_name:
                parsed_request.setdefault('headers', key_value_dict(**value))
            elif 'keydata' in key_name:
                parsed_request.setdefault('data', key_value_dict(**value))
            elif 'keyextract' in key_name:
                parsed_request.setdefault('extract', key_value_list(**value))
            elif 'keyvalidate' in key_name:
                parsed_request.setdefault('validate', key_value_list(name='true', **value))
            elif 'case_name' in key_name:
                parsed_request['name'] = value.pop('case_name')
            elif 'DataType' in key_name:
                parsed_request['data_type'] = value.pop('DataType')
            elif 'method' in key_name:
                request['method'] = value.pop('method')
            elif 'url' in key_name:
                request['url'] = value.pop('url')

    if 'data' in parsed_request.keys():
        data_type = parsed_request.pop('data_type')
        request.setdefault(data_type, parsed_request.pop('data'))

    parsed_request.setdefault('request', request)
    testcase_lists.append({'test':parsed_request})
    return testcase_lists

def module_info_logic(**kwargs):
    if kwargs.get('module_name') is '':
        return '模块名称不能为空'
    if kwargs.get('belong_project') is '':
        return '所属项目不能为空'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    if kwargs.get('lifting_time') is '':
        return '提测时间不能为空'
    return 'ok'


def project_info_logic(**kwargs):
    if kwargs.get('project_name') is '':
        return '项目名称不能为空'
    if kwargs.get('responsible_name') is '':
        return '负责人不能为空'
    if kwargs.get('test_user') is '':
        return '测试人员不能为空'
    if kwargs.get('dev_user') is '':
        return '开发人员不能为空'
    return 'ok'