from ApiManager.models import TestCaseInfo, ModuleInfo
from httprunner.cli import main_ate

'''通过test id组装case 供其他方法调用'''


def run_by_single(id):
    testcases_list = []
    obj = TestCaseInfo.objects.get(id=id)
    module = obj.belong_module_id
    include = obj.include
    request = obj.request

    # do not have include
    if include == '' or include is None:
        testcases_list.append(eval(request))
        return testcases_list

    else:
        config_test = include.split('>')
        for name in config_test:
            include_request = TestCaseInfo.objects.get(name__exact=name,
                                                       belong_module=ModuleInfo.objects.get(id=module)).request
            testcases_list.append(eval(include_request))
        testcases_list.append(eval(request))
        return testcases_list


'''单个模块组装所有test'''


def run_by_module(id):
    testcases_lists = []
    obj = ModuleInfo.objects.get(id=id)
    test_index_list = TestCaseInfo.objects.filter(belong_module=obj, type__exact=1).values_list('id')
    for index in test_index_list:
        testcases_lists.append(run_by_single(index[0]))
    return testcases_lists


'''test批量组装'''


def run_by_batch(test_list):
    testcases_lists = []
    for index in test_list:
        form_test = index.split('=')
        id = int(form_test[1])
        if 'test' in form_test[0]:
            testcases_lists.append(run_by_single(id))
        elif 'module' in form_test[0]:
            testcases_lists.extend(run_by_module(id))
    return testcases_lists


'''运行并返回报告'''


def get_result(test_lists):
    results = {'testResult': []}
    for index in range(len(test_lists)):
        result = main_ate(test_lists[index], 'test')
        if index == 0:
            results['beginTime'] = result.pop('beginTime')
        results['testName'] = result.pop('testName')
        results['testSkip'] = results.pop('testSkip', 0) + result.pop('testSkip')
        results['testError'] = results.pop('testError', 0) + result.pop('testError')
        results['testPass'] = results.pop('testPass', 0) + result.pop('testPass')  # 持续时间不对，bug待修复
        results['totalTime'] = (str)((int)(results.pop('totalTime', '0').replace('s', '')) + (int)(
            result.pop('totalTime').replace('s', ''))) + 's'
        results['testAll'] = results.pop('testAll', 0) + result.pop('testAll')
        for value in result.pop('testResult'):
            results['testResult'].append(value)
        results['testFail'] = results.pop('testFail', 0) + result.pop('testFail')
    return results
