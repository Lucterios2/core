'''
Created on 13 avr. 2015

@author: ubuntu
'''
import unittest

from shutil import rmtree
from os import makedirs
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from unittest.runner import TextTestRunner
from juxd import JUXDTestResult
from os.path import join
import os, sys
from importlib import reload, import_module # pylint: disable=redefined-builtin,no-name-in-module

class Reloader(object):

    def __init__(self, name):
        self.before_list = list(sys.modules.keys())
        self.module = import_module(name)
        self.after_list = list(sys.modules.keys())

    def reload(self):
        mod_list = list(set(self.after_list) - set(self.before_list))
        for mod_name in mod_list:
            reload(sys.modules[mod_name])

class BaseTest(unittest.TestCase):

    reloader = Reloader('lucterios.install.lucterios_admin')

    def setUp(self):
        self.reloader.reload()
        self.path_dir = "test"
        rmtree(self.path_dir, True)
        makedirs(self.path_dir)
        self.luct_glo = self.reloader.module.LucteriosGlobal(self.path_dir)

    def tearDown(self):
        rmtree(self.path_dir, True)

class TestAdmin(BaseTest):

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_a", self.path_dir)
        inst.add()
        self.assertEqual(["inst_a"], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_a", self.path_dir)
        inst.read()
        self.assertEqual("sqlite", inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        self.assertEqual(["inst_a"], self.luct_glo.listing())

    def test_add_modif(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_b", self.path_dir)
        inst.add()
        self.assertEqual(["inst_b"], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_b", self.path_dir)
        inst.set_database("sqlite")
        inst.appli_name = "lucterios.standard"
        inst.modules = ('lucterios.dummy',)
        inst.modif()

        inst = self.reloader.module.LucteriosInstance("inst_b", self.path_dir)
        inst.read()
        self.assertEqual("sqlite", inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual(('lucterios.dummy',), inst.modules)

        inst = self.reloader.module.LucteriosInstance("inst_b", self.path_dir)
        inst.refresh()

    def test_add_del(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_c", self.path_dir)
        inst.add()
        self.assertEqual(["inst_c"], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_d", self.path_dir)
        inst.add()
        list_res = self.luct_glo.listing()
        list_res.sort()
        self.assertEqual(["inst_c", "inst_d"], list_res)

        inst = self.reloader.module.LucteriosInstance("inst_c", self.path_dir)
        inst.delete()
        self.assertEqual(["inst_d"], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_d", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_extra(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_e", self.path_dir)
        inst.set_extra("DEBUG=True,ALLOWED_HOSTS=[localhost]")
        inst.add()
        self.assertEqual(["inst_e"], self.luct_glo.listing())

        # print(open(self.path_dir + '/inst_a/settings.py', 'r').readlines())

        inst = self.reloader.module.LucteriosInstance("inst_e", self.path_dir)
        inst.read()
        self.assertEqual({'DEBUG':True, 'ALLOWED_HOSTS':['localhost']}, inst.extra)

    def test_archive(self):
        inst = self.reloader.module.LucteriosInstance("inst_e", self.path_dir)
        inst.add()
        path_usr = join(self.path_dir, 'inst_e', 'usr', 'foo')
        makedirs(path_usr)
        with open(join(path_usr, 'myfile'), mode='w+') as myfile:
            myfile.write('boooo!!')

        inst.filename = join(self.path_dir, "inst_e.arc")
        self.assertEqual(True, inst.archive())

        import tarfile
        list_file = []
        with tarfile.open(inst.filename, "r:gz") as tar:
            for tarinfo in tar:
                list_file.append(tarinfo.name)
        list_file.sort()
        self.assertEqual(['dump.json', 'usr', 'usr/foo', 'usr/foo/myfile'], list_file)

#         inst = LucteriosInstance("inst_b", self.path_dir)
#         inst.add()
#         inst.filename = join(self.path_dir,"inst_a.arc")
#         self.assertEqual(True, inst.restore())

class TestAdminMySQL(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        self.data = {'dbname':'testv2', 'username':'myuser', 'passwd':'123456', 'server':'localhost'}
        for cmd in ("CREATE DATABASE %(dbname)s", \
                    "GRANT all ON %(dbname)s.* TO %(username)s@'%(server)s' IDENTIFIED BY '%(passwd)s'", \
                    "GRANT all ON %(dbname)s.* TO %(username)s@'127.0.0.1' IDENTIFIED BY '%(passwd)s'"):
            complete_cmd = 'echo "%s;" | mysql -u root -pabc123' % (cmd % self.data)
            os.system(complete_cmd)

    def tearDown(self):
        os.system('echo "DROP DATABASE %(dbname)s;" | mysql -u root -pabc123' % self.data)
        BaseTest.tearDown(self)

    def run_mysql_cmd(self, cmd):
        mysqlres = join(self.path_dir, 'out.txt')
        complete_cmd = 'echo "%s;" | mysql -u root -pabc123 > %s' % (cmd % self.data, mysqlres)
        os.system(complete_cmd)
        with open(mysqlres, 'r') as res_file:
            for line in res_file.readlines():
                yield line.strip()

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_mysql", self.path_dir)
        inst.set_database("mysql:name=testv2,user=myuser,password=123456,host=localhost")
        inst.add()
        self.assertEqual(["inst_mysql"], self.luct_glo.listing())

        inst = self.reloader.module.LucteriosInstance("inst_mysql", self.path_dir)
        inst.read()
        self.assertEqual("mysql:host=localhost,name=testv2,password=123456,user=myuser", inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        waiting_table = ['CORE_label', 'CORE_parameter', 'CORE_printmodel', 'auth_group', 'auth_group_permissions', \
                         'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions', \
                         'django_admin_log', 'django_content_type', 'django_migrations', 'django_session']
        waiting_table.sort()
        table_list = list(self.run_mysql_cmd("use testv2;show tables;"))
        if "Tables_in_testv2" in table_list:

            table_list.remove("Tables_in_testv2")
        table_list.sort()
        self.assertEqual(waiting_table, table_list)

        inst = self.reloader.module.LucteriosInstance("inst_mysql", self.path_dir)
        inst.clear()
        table_list = list(self.run_mysql_cmd("use testv2;show tables;"))
        self.assertEqual([], table_list)

        inst = self.reloader.module.LucteriosInstance("inst_mysql", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

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
    if sys.argv[1] == "TestAdmin":
        suite.addTest(loader.loadTestsFromTestCase(TestAdmin))
    if sys.argv[1] == "TestAdminMySQL":
        suite.addTest(loader.loadTestsFromTestCase(TestAdminMySQL))
    XMLTestRunner(verbosity=1).run(suite)
