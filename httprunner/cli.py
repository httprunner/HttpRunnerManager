import logging
import multiprocessing
import os
import sys
from collections import OrderedDict

from httprunner import exception
from httprunner.task import TaskSuite
from pyunitreport import HTMLTestRunner


def main_ate(testset_paths, name):
    # """ API test: parse command line options and run commands.
    # """
    # parser = argparse.ArgumentParser(
    #     description='HTTP test runner, not just about api test and load test.')
    # parser.add_argument(
    #     '-V', '--version', dest='version', action='store_true',
    #     help="show version")
    # parser.add_argument(
    #     'testset_paths', nargs='*',
    #     help="testset file path")
    # parser.add_argument(
    #     '--log-level', default='INFO',
    #     help="Specify logging level, default is INFO.")
    # parser.add_argument(
    #     '--report-name',
    #     help="Specify report name, default is generated time.")
    # parser.add_argument(
    #     '--failfast', action='store_true', default=False,
    #     help="Stop the test run on the first error or failure.")
    # parser.add_argument(
    #     '--startproject',
    #     help="Specify new project name.")
    #
    # args = parser.parse_args()
    #
    # if args.version:
    #     print("HttpRunner version: {}".format(ate_version))
    #     print("PyUnitReport version: {}".format(pyu_version))
    #     exit(0)

    log_level = getattr(logging, 'INFO')
    logging.basicConfig(level=log_level)

    # project_name = args.startproject
    # if project_name:
    #     project_path = os.path.join(os.getcwd(), project_name)
    #     create_scaffold(project_path)
    #     exit(0)

    report_name = name
    # if report_name and len(args.testset_paths) > 1:
    #     report_name = None
    #     logging.warning("More than one testset paths specified, \
    #                     report name is ignored, use generated time instead.")

    results = {}
    success = True

    for testset_path in testset_paths:
        try:
            task_suite = TaskSuite(testset_path)
        except exception.TestcaseNotFound:
            success = False
            continue

        output_folder_name = os.path.dirname(os.path.abspath(__file__))
        kwargs = {
            "output": output_folder_name,
            "report_name": report_name,
            "failfast": False
        }
        result = HTMLTestRunner(**kwargs).run(task_suite)

        if len(result.successes) != result.testsRun:
            success = False
        results = OrderedDict({
            "total": result.testsRun,
            "successes": len(result.successes),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped),
            "success": success,
            "html_reports": result.reports[1],
            "reports": result.reports[0]
        })

        # for task in task_suite.tasks:
        #     task.print_output()

    return results

def main_locust():
    """ Performance test with locust: parse command line options and run commands.
    """
    logging.basicConfig(level="INFO")

    try:
        from httprunner import locusts
    except ImportError:
        msg = "Locust is not installed, install first and try again.\n"
        msg += "install command: pip install locustio"
        logging.info(msg)
        exit(1)

    sys.argv[0] = 'locust'
    if len(sys.argv) == 1:
        sys.argv.extend(["-h"])

    if sys.argv[1] in ["-h", "--help", "-V", "--version"]:
        locusts.main()
        sys.exit(0)

    try:
        testcase_index = sys.argv.index('-f') + 1
        assert testcase_index < len(sys.argv)
    except (ValueError, AssertionError):
        logging.error("Testcase file is not specified, exit.")
        sys.exit(1)

    testcase_file_path = sys.argv[testcase_index]
    sys.argv[testcase_index] = locusts.parse_locustfile(testcase_file_path)

    if "--cpu-cores" in sys.argv:
        """ locusts -f locustfile.py --cpu-cores 4
        """
        if "--no-web" in sys.argv:
            logging.error("conflict parameter args: --cpu-cores & --no-web. \nexit.")
            sys.exit(1)

        cpu_cores_index = sys.argv.index('--cpu-cores')

        cpu_cores_num_index = cpu_cores_index + 1

        if cpu_cores_num_index >= len(sys.argv):
            """ do not specify cpu cores explicitly
                locusts -f locustfile.py --cpu-cores
            """
            cpu_cores_num_value = multiprocessing.cpu_count()
            logging.warning("cpu cores number not specified, use {} by default.".format(cpu_cores_num_value))
        else:
            try:
                """ locusts -f locustfile.py --cpu-cores 4 """
                cpu_cores_num_value = int(sys.argv[cpu_cores_num_index])
                sys.argv.pop(cpu_cores_num_index)
            except ValueError:
                """ locusts -f locustfile.py --cpu-cores -P 8888 """
                cpu_cores_num_value = multiprocessing.cpu_count()
                logging.warning("cpu cores number not specified, use {} by default.".format(cpu_cores_num_value))

        sys.argv.pop(cpu_cores_index)
        locusts.run_locusts_on_cpu_cores(sys.argv, cpu_cores_num_value)
    else:
        locusts.main()
