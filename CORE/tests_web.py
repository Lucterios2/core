# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from unittest.suite import BaseTestSuite
import time

class QUnitCase(object):

    def __init__(self, test):
        self.module_name = test.find_elements_by_xpath('strong/span[@class="module-name"]')[0].text
        self.test_name = test.find_elements_by_xpath('strong/span[@class="test-name"]')[0].text

        self.nb_failed = int(test.find_elements_by_xpath('strong/b[@class="counts"]/b[@class="failed"]')[0].text)
        self.runtime = float(test.find_elements_by_xpath('span[@class="runtime"]')[0].text.replace(" ms", ""))
        self.failure = ''
        if self.nb_failed > 0:
            for item in test.find_elements_by_xpath('ol/li'):
                self.failure += item.find_elements_by_xpath('span[@class="test-message"]')[0].text + ":\n"
                for fail_item in item.find_elements_by_xpath('table/tbody/tr'):
                    self.failure += "--- " + fail_item.find_elements_by_xpath('th')[0].text + " ---\n"
                    self.failure += fail_item.find_elements_by_xpath('td/pre')[0].text + "\n"
                self.failure += "\n"
        self._testMethodName = '.'.join((self.module_name, self.test_name))  # pylint: disable=invalid-name

    __hash__ = None

    def shortDescription(self):
        # pylint: disable=invalid-name,no-self-use
        return None

    def run(self, result):
        # pylint: disable=protected-access
        def my_exc_info_to_string(err, _):
            return err[2]
        old_exc_info = result._exc_info_to_string
        result._exc_info_to_string = my_exc_info_to_string
        try:

            result.startTest(self)
            if hasattr(result, "case_start_time"):
                setattr(result, "case_start_time", time.time() - self.runtime / 1000)
            if self.nb_failed == 0:
                result.addSuccess(self)
            else:
                result.addError(self, (AssertionError, "QUnit error", self.failure))
            result.stopTest(self)
        finally:
            result._exc_info_to_string = old_exc_info

class QUnitWeb(BaseTestSuite):

    def __init__(self, testurl):
        BaseTestSuite.__init__(self)
        try:
            from selenium import webdriver
            self.driver_class = webdriver.Firefox
        except ImportError:
            self.driver_class = None
        self.driver = None
        self.testurl = testurl

    def is_el_present(self):
        from selenium.common.exceptions import NoSuchElementException
        try:
            sel = self.driver.find_element_by_id('qunit-testresult')
            return 'completed' in sel.text
        except NoSuchElementException:
            return False

    def wait_for_el(self):
        from selenium.webdriver.support.wait import WebDriverWait
        from selenium.common.exceptions import TimeoutException
        try:
            waiter = WebDriverWait(self.driver, 20)
            waiter.until(lambda driver: self.is_el_present())
        except TimeoutException:
            raise Exception('Never saw element qunit-testresult')

    def run(self, result):
        if self.driver_class is not None:
            self.driver = self.driver_class()
            try:
                self.driver.get(self.testurl)
                self.wait_for_el()
                tests = self.driver.find_elements_by_xpath('//ol[@id="qunit-tests"]/li')

                for test in tests:
                    unit = QUnitCase(test)
                    unit.run(result)
            finally:
                self.driver.quit()

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)
