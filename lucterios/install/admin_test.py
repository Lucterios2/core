'''
Created on 13 avr. 2015

@author: ubuntu
'''
import unittest

from lucterios.install.lucterios_admin import LucteriosGlobal, LucteriosInstance
from shutil import rmtree
from os import makedirs
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from unittest.runner import TextTestRunner
from juxd import JUXDTestResult

class TestAdmin(unittest.TestCase):

    def setUp(self):
        self.path_dir = "test"
        rmtree(self.path_dir, True)
        makedirs(self.path_dir)
        self.luct_glo = LucteriosGlobal(self.path_dir)

    def tearDown(self):
        rmtree(self.path_dir, True)

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.add()
        self.assertEqual(["inst_a"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.read()
        self.assertEqual("sqlite", inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        self.assertEqual(["inst_a"], self.luct_glo.listing())

    def test_add_modif(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.add()
        self.assertEqual(["inst_a"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.database = "sqlite"
        inst.appli_name = "lucterios.standard"
        inst.modules = ('lucterios.dummy',)
        inst.modif()

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.read()
        self.assertEqual("sqlite", inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual(('lucterios.dummy',), inst.modules)

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.refresh()

    def test_add_del(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.add()
        self.assertEqual(["inst_a"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.add()
        self.assertEqual(["inst_b", "inst_a"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.delete()
        self.assertEqual(["inst_b"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_extra(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.set_extra("DEBUG=True,ALLOWED_HOSTS=[localhost]")
        inst.add()
        self.assertEqual(["inst_a"], self.luct_glo.listing())

        # print(open(self.path_dir + '/inst_a/settings.py', 'r').readlines())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.read()
        self.assertEqual({'DEBUG':True, 'ALLOWED_HOSTS':['localhost']}, inst.extra)

class XMLTestResult(JUXDTestResult):

    def stopTestRun(self):
        from xml.etree import ElementTree as ET
        import time
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

if __name__ == "__main__":
    suite = TestSuite()  # pylint: disable=invalid-name
    loader = TestLoader()  # pylint: disable=invalid-name
    suite.addTest(loader.loadTestsFromTestCase(TestAdmin))
    XMLTestRunner(verbosity=1).run(suite)
