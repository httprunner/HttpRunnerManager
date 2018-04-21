from ApiManager.models import TestCaseInfo, ModuleInfo, ProjectInfo
# from httprunner.cli import main_ate

'''通过test id组装case 供其他方法调用'''


def run_by_single(id):
    testcase_list = []
    obj = TestCaseInfo.objects.get(id=id, status=1)
    module = obj.belong_module_id
    include = obj.include
    request = obj.request

    # do not have include
    if include == '' or include is None:
        testcase_list.append(eval(request))
        return testcase_list

    else:
        config_test = include.split('>')
        for name in config_test:
            include_request = TestCaseInfo.objects.get(name__exact=name,
                                                       belong_module=ModuleInfo.objects.get(id=module),
                                                       status=1).request
            testcase_list.append(eval(include_request))
        testcase_list.append(eval(request))
        return testcase_list


'''单个模块组装所有test'''


def run_by_module(id):
    testcase_lists = []
    obj = ModuleInfo.objects.get(id=id, status=1)
    test_index_list = TestCaseInfo.objects.filter(belong_module=obj, type=1, status=1).values_list('id')
    for index in test_index_list:
        testcase_lists.append(run_by_single(index[0]))
    return testcase_lists


'''单个项目组装所有test'''


def run_by_project(id):
    testcase_lists = []
    obj = ProjectInfo.objects.get(id=id, status=1)
    module_index_list = ModuleInfo.objects.filter(belong_project=obj, status=1).values_list('id')
    for index in module_index_list:
        module_id = index[0]
        testcase_lists.extend(run_by_module(module_id))
    return testcase_lists


'''test批量组装'''


def run_by_batch(test_list):
    testcase_lists = []
    for index in test_list:
        form_test = index.split('=')
        id = form_test[1]
        if 'test' in form_test[0]:
            testcase_lists.append(run_by_single(id))
        elif 'module' in form_test[0]:
            testcase_lists.extend(run_by_module(id))
        elif 'project' in form_test[0]:
            testcase_lists.extend(run_by_project(id))
    return testcase_lists


'''运行并返回报告'''


def get_result(test_lists):
    summary = {
        "success": True,
        "stat": {
            'testsRun': 0,
            'successes': 0,
            'failures': 0,
            'errors': 0,
            'skipped': 0,
            'expectedFailures': 0,
            'unexpectedSuccesses': 0
        },
        "platform": {},
        "time": {
            'start_at': '',
            'duration': 0.0,
        },
        "records": [],
    }
    for index in range(len(test_lists)):
        result = main_ate(test_lists[index])

        if index == 0:
            summary["time"]["start_at"] = result["time"].pop("start_at")

        if "html_report_name" in result.keys():
            summary["html_report_name"] = result.pop("html_report_name")

        summary["success"] = summary.pop("success") and result.pop("success")

        for key, value in result["stat"].items():
            summary["stat"][key] = summary["stat"].get(key) + value

        summary["platform"] = result.pop("platform")

        summary["time"]["duration"] = summary["time"].pop("duration") + result["time"]["duration"]

        summary["records"].extend(result.pop("records"))

    return summary
