import logging
import multiprocessing
import sys

from BeautifulReport import BeautifulReport
from httprunner import exception
from httprunner.task import TaskSuite


def main_ate(testset_path, report_name):
    logging.basicConfig(level='INFO')
    task_suite = None
    try:
        task_suite = TaskSuite(testset_path)
    except exception.TestcaseNotFound:
        logging.error('TestCase not Fund')

    result = BeautifulReport(task_suite)
    return result.report(description='Test Report')



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
