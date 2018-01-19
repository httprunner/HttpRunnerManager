from ApiManager.models import TestCaseInfo, ModuleInfo

'''运行单一yaml'''


def run_by_single(id):
    testcases_list = []
    testcases_lists = []
    obj = TestCaseInfo.objects.get(id=id)
    module = obj.belong_module_id
    include = obj.include
    request = obj.request

    # do not have include
    if include == '' or include is None:
        testcases_list.append(eval(request))
        testcases_lists.append(testcases_list)
        return testcases_lists

    else:
        config_test = include.split('>')
        for name in config_test:
            include_request = TestCaseInfo.objects.get(name__exact=name,
                                                       belong_module=ModuleInfo.objects.get(id=module)).request
            testcases_list.append(eval(include_request))
        testcases_list.append(eval(request))
        testcases_lists.append(testcases_list)
        return testcases_lists
