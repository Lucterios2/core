# -*- coding: utf-8 -*-
'''
Unit test classes to admin and migration tools

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

import unittest

from shutil import rmtree
from os import makedirs
from unittest.suite import TestSuite
from unittest.loader import TestLoader
from unittest.runner import TextTestRunner
from juxd import JUXDTestResult
from os.path import join, dirname, isfile, isdir
import os
from lucterios.install.lucterios_migration import MigrateFromV1
from lucterios.install.lucterios_admin import LucteriosGlobal, LucteriosInstance

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.path_dir = join(dirname(dirname(dirname(__file__))), "test")
        rmtree(self.path_dir, True)
        makedirs(self.path_dir)
        self.luct_glo = LucteriosGlobal(self.path_dir)

    def tearDown(self):
        rmtree(self.path_dir, True)

class TestGlobal(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        os.environ['extra_url'] = "http://v2.lucterios.org/simple"

    def test_installed(self):
        val = self.luct_glo.installed()
        self.assertEqual('lucterios', val[0][0])
        self.assertEqual('2.0', val[0][1][:3])
        self.assertEqual(([], []), val[1:])

    def test_check(self):
        val = self.luct_glo.check()
        list_key = list(val[0].keys())
        list_key.sort()
        self.assertEqual(['lucterios', 'lucterios-standard'], list_key)
        self.assertEqual(None, val[0]['lucterios'][1])
        self.assertEqual(False, val[0]['lucterios'][2])
        self.assertEqual(None, val[0]['lucterios-standard'][1])
        self.assertEqual(False, val[0]['lucterios-standard'][2])
        self.assertEqual(False, val[1])

    def test_refresh_all(self):
        self.assertEqual([], self.luct_glo.refresh_all())

class TestAdminSQLite(BaseTest):

    def run_sqlite_cmd(self, instancename, cmd):
        dbpath = join(self.path_dir, instancename, "db.sqlite3")
        sqliteres = join(self.path_dir, 'out.txt')
        complete_cmd = 'sqlite3 %s "%s" > %s' % (dbpath, cmd, sqliteres)
        os.system(complete_cmd)
        with open(sqliteres, 'r') as res_file:
            for line in res_file.readlines():
                yield line.strip()

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.add()
        self.assertEqual(["inst_a"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.read()
        self.assertEqual(("sqlite", {}), inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        waiting_table = ['CORE_label', 'CORE_parameter', 'CORE_printmodel', 'auth_group', 'auth_group_permissions', \
                         'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions', \
                         'django_admin_log', 'django_content_type', 'django_migrations', 'django_session']
        waiting_table.sort()
        table_list = list(self.run_sqlite_cmd("inst_a", "SELECT name FROM sqlite_master WHERE type='table';"))
        if "sqlite_sequence" in table_list:
            table_list.remove("sqlite_sequence")
        table_list.sort()
        self.assertEqual(waiting_table, table_list)

        inst = LucteriosInstance("inst_a", self.path_dir)
        inst.clear()

        table_list = list(self.run_sqlite_cmd("inst_a", "SELECT name FROM sqlite_master WHERE type='table';"))
        if "sqlite_sequence" in table_list:
            table_list.remove("sqlite_sequence")
        table_list.sort()
        self.assertEqual([], table_list)

        self.assertEqual(["inst_a"], self.luct_glo.listing())

    def test_add_modif(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.add()
        self.assertEqual(["inst_b"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.set_database("sqlite")
        inst.appli_name = "lucterios.standard"
        inst.modules = ('lucterios.dummy',)
        inst.modif()

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.read()
        self.assertEqual(("sqlite", {}), inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual(('lucterios.dummy',), inst.modules)

        inst = LucteriosInstance("inst_b", self.path_dir)
        inst.refresh()

    def test_add_del(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_c", self.path_dir)
        inst.add()
        self.assertEqual(["inst_c"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_d", self.path_dir)
        inst.add()
        list_res = self.luct_glo.listing()
        list_res.sort()
        self.assertEqual(["inst_c", "inst_d"], list_res)

        inst = LucteriosInstance("inst_c", self.path_dir)
        inst.delete()
        self.assertEqual(["inst_d"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_d", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_extra(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_e", self.path_dir)
        inst.set_extra("DEBUG=True,ALLOWED_HOSTS=[localhost]")
        inst.add()
        self.assertEqual(["inst_e"], self.luct_glo.listing())

        # print(open(self.path_dir + '/inst_a/settings.py', 'r').readlines())

        inst = LucteriosInstance("inst_e", self.path_dir)
        inst.read()
        self.assertEqual({'DEBUG':True, 'ALLOWED_HOSTS':['localhost']}, inst.extra)

    def test_archive(self):
        self.assertEqual([], self.luct_glo.listing())
        inst = LucteriosInstance("inst_e", self.path_dir)
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

        inst = LucteriosInstance("inst_f", self.path_dir)
        inst.add()
        inst.filename = join(self.path_dir, "inst_e.arc")
        self.assertEqual(True, inst.restore())
        self.assertEqual(True, isdir(join(self.path_dir, 'inst_f', 'usr')))
        self.assertEqual(True, isdir(join(self.path_dir, 'inst_f', 'usr', 'foo')))
        self.assertEqual(True, isfile(join(self.path_dir, 'inst_f', 'usr', 'foo', 'myfile')))

    def test_migration(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_h", self.path_dir)
        inst.add()
        self.assertEqual(["inst_h"], self.luct_glo.listing())
        mirg = MigrateFromV1("inst_h", self.path_dir, "")
        mirg.restore(join(dirname(self.path_dir), 'data', 'archive_demo.bkf'))

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

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.set_database("mysql:name=testv2,user=myuser,password=123456,host=localhost")
        inst.add()
        self.assertEqual(["inst_mysql"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.read()
        self.assertEqual("mysql", inst.database[0])
        self.assertEqual("localhost", inst.database[1]['host'])
        self.assertEqual("testv2", inst.database[1]['name'])
        self.assertEqual("123456", inst.database[1]['password'])
        self.assertEqual("myuser", inst.database[1]['user'])
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

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.clear()
        table_list = list(self.run_mysql_cmd("use testv2;show tables;"))
        self.assertEqual([], table_list)

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_archive(self):
        self.assertEqual([], self.luct_glo.listing())
        inst = LucteriosInstance("inst_g", self.path_dir)
        inst.add()
        inst.filename = join(self.path_dir, "inst_g.arc")
        self.assertEqual(True, inst.archive())

        inst = LucteriosInstance("inst_mysql", self.path_dir)
        inst.set_database("mysql:name=testv2,user=myuser,password=123456,host=localhost")
        inst.add()
        inst.filename = join(self.path_dir, "inst_g.arc")
        self.assertEqual(True, inst.restore())
#
#     def test_migration(self):
#         self.assertEqual([], self.luct_glo.listing())
#
#         inst = LucteriosInstance("inst_mysql", self.path_dir)
#         inst.set_database("mysql:name=testv2,user=myuser,password=123456,host=localhost")
#         inst.add()
#         self.assertEqual(["inst_mysql"], self.luct_glo.listing())
#         mirg = MigrateFromV1("inst_mysql", self.path_dir, "")
#         mirg.restore(join(dirname(self.path_dir), 'data', 'archive_demo.bkf'))

class TestAdminPostGreSQL(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        self.data = {'dbname':'testv2', 'username':'puser', 'passwd':'123456', 'server':'localhost'}
        for cmd in ("DROP DATABASE %(dbname)s;", "DROP USER %(username)s;", \
                    "CREATE USER %(username)s;", \
                    "CREATE DATABASE %(dbname)s OWNER %(username)s;", \
                    "ALTER USER %(username)s WITH ENCRYPTED PASSWORD '%(passwd)s';"):
            complete_cmd = 'sudo -u postgres psql -c "%s"' % (cmd % self.data)
            os.system(complete_cmd)

    def tearDown(self):
        for cmd in ("DROP DATABASE %(dbname)s;", "DROP USER %(username)s;"):
            complete_cmd = 'sudo -u postgres psql -c "%s"' % (cmd % self.data)
            os.system(complete_cmd)
        BaseTest.tearDown(self)

    def run_psql_cmd(self, cmd):
        psqlres = join(self.path_dir, 'out.txt')
        complete_cmd = 'sudo -u postgres psql -d "%s" -c "%s" > %s' % (self.data['dbname'], cmd, psqlres)
        os.system(complete_cmd)
        with open(psqlres, 'r') as res_file:
            for line in res_file.readlines():
                yield line.strip()

    def test_add_read(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.set_database("postgresql:name=testv2,user=puser,password=123456,host=localhost")
        inst.add()
        self.assertEqual(["inst_psql"], self.luct_glo.listing())

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.read()
        self.assertEqual("postgresql", inst.database[0])
        self.assertEqual("localhost", inst.database[1]['host'])
        self.assertEqual("testv2", inst.database[1]['name'])
        self.assertEqual("123456", inst.database[1]['password'])
        self.assertEqual("puser", inst.database[1]['user'])
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        waiting_table = ['CORE_label', 'CORE_parameter', 'CORE_printmodel', 'auth_group', 'auth_group_permissions', \
                         'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions', \
                         'django_admin_log', 'django_content_type', 'django_migrations', 'django_session']
        waiting_table.sort()
        table_list = list(self.run_psql_cmd("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'"))
        table_list = table_list[2:-2]
        table_list.sort()
        self.assertEqual(waiting_table, table_list)

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.clear()
        #table_list = list(self.run_psql_cmd("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'"))
        #table_list = table_list[2:-2]
        #self.assertEqual([], len(table_list)

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.delete()
        self.assertEqual([], self.luct_glo.listing())

    def test_migration(self):
        self.assertEqual([], self.luct_glo.listing())

        inst = LucteriosInstance("inst_psql", self.path_dir)
        inst.set_database("postgresql:name=testv2,user=puser,password=123456,host=localhost")
        inst.add()
        self.assertEqual(["inst_psql"], self.luct_glo.listing())
        mirg = MigrateFromV1("inst_psql", self.path_dir, "")
        mirg.restore(join(dirname(self.path_dir), 'data', 'archive_demo.bkf'))

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
    suite.addTest(loader.loadTestsFromTestCase(TestAdminSQLite))
    suite.addTest(loader.loadTestsFromTestCase(TestAdminMySQL))
    suite.addTest(loader.loadTestsFromTestCase(TestAdminPostGreSQL))
    #suite.addTest(loader.loadTestsFromTestCase(TestGlobal))
    XMLTestRunner(verbosity=1).run(suite)
