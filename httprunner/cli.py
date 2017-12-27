import logging
import sys

from pyunitreport import HTMLTestRunner

from httprunner import exception
from httprunner.task import TaskSuite



def main_ate(*args):
    log_level = getattr(logging, 'DEBUG')
    logging.basicConfig(level=log_level)
    report_name = 'TestReport'
    success = True

    for testset_path in args:
        try:
            task_suite = TaskSuite(testset_path)
        except exception.TestcaseNotFound:
            success = False
            continue

    output_folder_name = 'D:\\PasTest\\'
    kwargs = {
        "output": output_folder_name,
        "report_name": report_name,
        "failfast": False
    }

    result = HTMLTestRunner(**kwargs).run(task_suite)

    if len(result.successes) != result.testsRun:
        success = False


    return success


def main_locust():
    """ Performance test with locust: parse command line options and run commands.
    """
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

    if "--full-speed" in sys.argv:

        if "--no-web" in sys.argv:
            logging.warning("conflict parameter args: --full-speed --no-web. \nexit.")
            sys.exit(1)

        locusts.run_locusts_at_full_speed(sys.argv)
    else:
        locusts.main()
