import sys
import time
from unittest import TextTestRunner

from .result import HtmlTestResult

UTF8 = "UTF-8"


class HTMLTestRunner(TextTestRunner):
    """" A test runner class that output the results. """

    def __init__(self, output, report_name=None, verbosity=2, stream=sys.stderr,
                 descriptions=True, failfast=False, buffer=False,
                 report_title=None, template=None, resultclass=None):
        self.verbosity = verbosity
        self.output = output
        self.report_name = report_name
        self.encoding = UTF8

        TextTestRunner.__init__(self, stream, descriptions, verbosity,
                                failfast=failfast, buffer=buffer)

        if resultclass is None:
            self.resultclass = HtmlTestResult
        else:
            self.resultclass = resultclass

        self.report_title = report_title or "Test Reports"
        self.template = template

    def _make_result(self):
        """ Create a TestResult object which will be used to store
        information about the executed tests. """
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def run(self, test):
        """ Runs the given testcase or testsuite. """
        result = self._make_result()
        result.failfast = self.failfast
        result.buffer = self.buffer

        self.stream.writeln()
        self.stream.writeln("Running tests... ")
        self.stream.writeln(result.separator2)

        self.startTime = time.time()
        if getattr(result, 'startTestRun', None):
            result.startTestRun()

        try:
            test(result)
        finally:
            if getattr(result, 'stopTestRun', None):
                result.stopTestRun()

        stopTime = time.time()
        self.timeTaken = "%.3fs" % (stopTime - self.startTime)

        result.printErrors()
        self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %s" %
                            (run, run != 1 and "s" or "", self.timeTaken))
        self.stream.writeln()

        expectedFails = len(result.expectedFailures)
        unexpectedSuccesses = len(result.unexpectedSuccesses)
        skipped = len(result.skipped)

        infos = []
        if not result.wasSuccessful():
            self.stream.writeln("FAILED")
            failed, errors = map(len, (result.failures, result.errors))
            if failed:
                infos.append("Failures={0}".format(failed))
            if errors:
                infos.append("Errors={0}".format(errors))
        else:
            self.stream.writeln("OK")

        if skipped:
            infos.append("Skipped={}".format(skipped))
        if expectedFails:
            infos.append("expected failures={}".format(expectedFails))
        if unexpectedSuccesses:
            infos.append("unexpected successes={}".format(unexpectedSuccesses))

        if infos:
            self.stream.writeln(" ({})".format(", ".join(infos)))
        else:
            self.stream.writeln("\n")

        reports_path_list = result.generate_reports(self)
        result.reports = reports_path_list

        return result
