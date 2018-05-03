from django.core.exceptions import ObjectDoesNotExist

from ApiManager.models import TestCaseInfo, ModuleInfo, ProjectInfo

'''通过test id组装case 供其他方法调用'''


def run_by_single(index, base_url):
    testcase_dict = {
        'name': 'testset description',
        'config': {
            'name': 'base_url config',
            'request': {
                'base_url': base_url,
            }
        },
        'api': {},
        'testcases': []
    }
    obj = TestCaseInfo.objects.get(id=index)
    include = obj.include
    request = eval(obj.request).pop('test')

    if include == '':
        testcase_dict['testcases'].append(request)
        return testcase_dict

    else:
        module = obj.belong_module_id
        test_set = include.split('>')
        for name in test_set:
            try:
                include_request = eval(
                    TestCaseInfo.objects.get(name__exact=name, belong_module=ModuleInfo.objects.get(id=module)).request)
            except ObjectDoesNotExist:
                return testcase_dict
            if 'config' in include_request.keys():
                include_request.get('config').get('request').setdefault('base_url', base_url)
                testcase_dict['config'] = include_request.pop('config')
            else:
                testcase_dict['testcases'].append(include_request.pop('test'))
        testcase_dict['testcases'].append(request)
        return testcase_dict


'''test批量组装'''


def run_by_batch(test_list, base_url, type=None):
    testcase_lists = []
    if type == 'project':
        for value in test_list.values():
            testcase_lists.extend(run_by_project(value, base_url))
    elif type == 'module':
        for value in test_list.values():
            testcase_lists.extend(run_by_module(value, base_url))
    else:

        for index in range(len(test_list) - 1):
            form_test = test_list[index].split('=')
            index = form_test[1]
            testcase_lists.append(run_by_single(index, base_url))
    return testcase_lists


def run_by_module(id, base_url):
    testcase_lists = []
    obj = ModuleInfo.objects.get(id=id)
    test_index_list = TestCaseInfo.objects.filter(belong_module=obj, type=1).values_list('id')
    for index in test_index_list:
        testcase_lists.append(run_by_single(index[0], base_url))
    return testcase_lists


def run_by_project(id, base_url):
    testcase_lists = []
    obj = ProjectInfo.objects.get(id=id)
    module_index_list = ModuleInfo.objects.filter(belong_project=obj).values_list('id')
    for index in module_index_list:
        module_id = index[0]
        testcase_lists.extend(run_by_module(module_id, base_url))
    return testcase_lists
