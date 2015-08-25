# -*- coding: utf-8 -*-
'''Django Test Suite runner that also writes out JUnit-compatible XML

Based on the junitxml plugin from the unittest2 plugin experiments:
https://bitbucket.org/jpellerin/unittest2, unittest2.plugins.junitxml
'''
from __future__ import unicode_literals

from django.conf import settings
from django.test.runner import DiscoverRunner
from unittest.runner import TextTestRunner, TextTestResult
from django.core.exceptions import ImproperlyConfigured


class JUXDTestResult(TextTestResult):

    def __init__(self, stream, descriptions, verbosity):
        TextTestResult.__init__(self, stream, descriptions, verbosity)
        try:
            self.xml_filename = settings.JUXD_FILENAME
        except ImproperlyConfigured:
            self.xml_filename = "results.xml"

    def startTest(self, test):
        import time
        self.case_start_time = time.time(
        )
        super(JUXDTestResult, self).startTest(test)

    def addSuccess(self, test):
        self._make_testcase_element(test)
        super(JUXDTestResult, self).addSuccess(test)

    def addFailure(self, test, err):
        from xml.etree import ElementTree as ET
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'failure')
        self._add_tb_to_test(test, test_result, err)
        super(JUXDTestResult, self).addFailure(test, err)

    def addError(self, test, err):
        from xml.etree import ElementTree as ET
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'error')
        self._add_tb_to_test(test, test_result, err)
        super(JUXDTestResult, self).addError(test, err)

    def addUnexpectedSuccess(self, test):
        from xml.etree import ElementTree as ET
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'skipped')
        test_result.set('message', 'Test Skipped: Unexpected Success')
        super(JUXDTestResult, self).addUnexpectedSuccess(test)

    def addSkip(self, test, reason):
        from xml.etree import ElementTree as ET
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'skipped')
        test_result.set('message', 'Test Skipped: %s' % reason)
        super(JUXDTestResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        from xml.etree import ElementTree as ET
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'skipped')
        self._add_tb_to_test(test, test_result, err)
        super(JUXDTestResult, self).addExpectedFailure(test, err)

    def startTestRun(self):
        import time
        from xml.etree import ElementTree as ET
        self.tree = ET.Element(
            'testsuite')
        self.run_start_time = time.time(
        )
        super(JUXDTestResult, self).startTestRun()

    def stopTestRun(self):
        import time
        from xml.etree import ElementTree as ET
        run_time_taken = time.time() - self.run_start_time
        self.tree.set('name', 'Django Project Tests')
        self.tree.set('errors', str(len(self.errors)))
        self.tree.set('failures', str(len(self.failures)))
        self.tree.set('skips', str(len(self.skipped)))
        self.tree.set('tests', str(self.testsRun))
        self.tree.set('time', "%.3f" % run_time_taken)

        output = ET.ElementTree(self.tree)
        output.write(self.xml_filename, encoding="utf-8")

    def _make_testcase_element(self, test):
        import time
        from xml.etree import ElementTree as ET
        time_taken = time.time() - self.case_start_time
        classname = ('%s.%s' %
                     (test.__module__, test.__class__.__name__)).split('.')
        testcase = ET.SubElement(self.tree, 'testcase')
        testcase.set('time', "%.6f" % time_taken)
        testcase.set('classname', '.'.join(classname))
        testcase.set(
            'name', test._testMethodName)
        return testcase

    def _add_tb_to_test(self, test, test_result, err):
        '''Add a traceback to the test result element'''
        exc_class, exc_value, _ = err
        tb_str = self._exc_info_to_string(err, test)
        test_result.set('type', '%s.%s' %
                        (exc_class.__module__, exc_class.__name__))
        test_result.set('message', str(exc_value))
        test_result.text = tb_str


class JUXDTestRunner(TextTestRunner):
    resultclass = JUXDTestResult


class JUXDTestSuiteRunner(DiscoverRunner):
    test_runner = JUXDTestRunner
