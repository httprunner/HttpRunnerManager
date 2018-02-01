from ApiManager.models import TestCaseInfo, ModuleInfo

'''运行单一yaml'''


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


def run_by_batch(test_list):
    testcases_lists = []
    for index in test_list:
        index = int(index.split('=')[1])
        testcases_lists.append(run_by_single(index))
    return testcases_lists


