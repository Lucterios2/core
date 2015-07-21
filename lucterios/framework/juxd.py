# -*- coding: utf-8 -*-
'''Django Test Suite runner that also writes out JUnit-compatible XML

Based on the junitxml plugin from the unittest2 plugin experiments:
https://bitbucket.org/jpellerin/unittest2, unittest2.plugins.junitxml
'''
from __future__ import unicode_literals
import time
from xml.etree import ElementTree as ET

from django.conf import settings
from django.test.runner import DiscoverRunner
from unittest.runner import TextTestRunner, TextTestResult

class JUXDTestResult(TextTestResult):
    def startTest(self, test):
        self.case_start_time = time.time()  # pylint: disable=attribute-defined-outside-init
        super(JUXDTestResult, self).startTest(test)

    def addSuccess(self, test):
        self._make_testcase_element(test)
        super(JUXDTestResult, self).addSuccess(test)

    def addFailure(self, test, err):
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'failure')
        self._add_tb_to_test(test, test_result, err)
        super(JUXDTestResult, self).addFailure(test, err)

    def addError(self, test, err):
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'error')
        self._add_tb_to_test(test, test_result, err)
        super(JUXDTestResult, self).addError(test, err)

    def addUnexpectedSuccess(self, test):
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'skipped')
        test_result.set('message', 'Test Skipped: Unexpected Success')
        super(JUXDTestResult, self).addUnexpectedSuccess(test)

    def addSkip(self, test, reason):
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'skipped')
        test_result.set('message', 'Test Skipped: %s' % reason)
        super(JUXDTestResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        testcase = self._make_testcase_element(test)
        test_result = ET.SubElement(testcase, 'skipped')
        self._add_tb_to_test(test, test_result, err)
        super(JUXDTestResult, self).addExpectedFailure(test, err)

    def startTestRun(self):
        self.tree = ET.Element('testsuite')  # pylint: disable=attribute-defined-outside-init
        self.run_start_time = time.time()  # pylint: disable=attribute-defined-outside-init
        super(JUXDTestResult, self).startTestRun()

    def stopTestRun(self):
        run_time_taken = time.time() - self.run_start_time
        self.tree.set('name', 'Django Project Tests')
        self.tree.set('errors', str(len(self.errors)))
        self.tree.set('failures', str(len(self.failures)))
        self.tree.set('skips', str(len(self.skipped)))
        self.tree.set('tests', str(self.testsRun))
        self.tree.set('time', "%.3f" % run_time_taken)

        output = ET.ElementTree(self.tree)
        output.write(settings.JUXD_FILENAME, encoding="utf-8")
        super(JUXDTestResult, self).stopTestRun()

    def _make_testcase_element(self, test):
        time_taken = time.time() - self.case_start_time
        classname = ('%s.%s' % (test.__module__, test.__class__.__name__)).split('.')
        testcase = ET.SubElement(self.tree, 'testcase')
        testcase.set('time', "%.6f" % time_taken)
        testcase.set('classname', '.'.join(classname))
        testcase.set('name', test._testMethodName)  # pylint: disable=protected-access
        return testcase

    def _add_tb_to_test(self, test, test_result, err):
        '''Add a traceback to the test result element'''
        exc_class, exc_value, _ = err
        tb_str = self._exc_info_to_string(err, test)
        test_result.set('type', '%s.%s' % (exc_class.__module__, exc_class.__name__))
        test_result.set('message', str(exc_value))
        test_result.text = tb_str

class JUXDTestRunner(TextTestRunner):
    resultclass = JUXDTestResult

class JUXDTestSuiteRunner(DiscoverRunner):
    test_runner = JUXDTestRunner

class XMLTestResult(JUXDTestResult):

    def stopTestRun(self):
        run_time_taken = time.time() - self.run_start_time
        self.tree.set('name', 'Lucterios Functionnal Tests')
        self.tree.set('errors', str(len(self.errors)))
        self.tree.set('failures', str(len(self.failures)))
        self.tree.set('skips', str(len(self.skipped)))
        self.tree.set('tests', str(self.testsRun))
        self.tree.set('time', "%.3f" % run_time_taken)

        output = ET.ElementTree(self.tree)
        output.write("results.xml", encoding="utf-8")
        super(JUXDTestResult, self).stopTestRun()  # pylint: disable=bad-super-call

class XMLTestRunner(TextTestRunner):
    resultclass = XMLTestResult
