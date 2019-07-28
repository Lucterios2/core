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
from os.path import join, dirname, isfile, isdir
import os

from unittest.suite import TestSuite
from unittest.loader import TestLoader

from lucterios.install.lucterios_admin import delete_path, run_main_ext, get_options
from lucterios.framework.juxd import JUXDTestRunner


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.path_dir = join(dirname(dirname(dirname(__file__))), "test")
        rmtree(self.path_dir, True)
        makedirs(self.path_dir)
        self.waiting_table = ['CORE_label', 'CORE_parameter', 'CORE_printmodel', 'CORE_savedcriteria', 'auditlog_logentry',
                              'auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions',
                              'django_admin_log', 'django_content_type', 'django_migrations', 'django_session']
        self.waiting_table.sort()

    def tearDown(self):
        rmtree(self.path_dir, True)

    def luct_listing(self):
        return run_main_ext('listing', get_options(instance_path=self.path_dir))


class TestGlobal(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        os.environ['extra_url'] = "http://pypi.lucterios.org/simple"
        delete_path(join(self.path_dir, 'extra_url'))

    def test_installed(self):
        val = run_main_ext('installed', get_options(instance_path=self.path_dir))
        self.assertEqual('lucterios', val[0][0])
        self.assertEqual('???', val[0][1][:3])
        self.assertEqual(([], []), val[1:])

    def test_check(self):
        val = run_main_ext('check', get_options(instance_path=self.path_dir))
        list_key = list(val[0].keys())
        list_key.sort()
        self.assertEqual([], list_key)

    def test_refresh_all(self):
        val = run_main_ext('refreshall', get_options(instance_path=self.path_dir))
        self.assertEqual([], val)

    def write_extraurl_file(self, values):
        with open(join(self.path_dir, 'extra_url'), mode='w') as file:
            for val in values:
                file.write(val + '\n')

    def test_check_pypi(self):
        from lucterios.install.lucterios_admin import LucteriosGlobal
        luct_glo = LucteriosGlobal(self.path_dir)
        try:
            old_http_proxy = os.environ['http_proxy']
            del os.environ['http_proxy']
        except KeyError:
            old_http_proxy = None
        try:
            self.assertEqual(['--quiet', '--extra-index-url', 'http://pypi.lucterios.org/simple', '--trusted-host', 'pypi.lucterios.org'],
                             luct_glo.get_default_args_([]))
            del os.environ['extra_url']
            self.assertEqual(['--quiet'], luct_glo.get_default_args_([]))
            self.write_extraurl_file([])
            self.assertEqual(['--quiet'], luct_glo.get_default_args_([]))
            self.write_extraurl_file(['# pypi server list', 'http://pypi.diacamma.org/simple', 'https://pypi.supersecure.net/simple', 'http://pypi.lucterios.org/simple', ''])
            self.assertEqual(['--quiet', '--extra-index-url', 'http://pypi.diacamma.org/simple', '--trusted-host', 'pypi.diacamma.org', '--extra-index-url', 'https://pypi.supersecure.net/simple',
                              '--extra-index-url', 'http://pypi.lucterios.org/simple', '--trusted-host', 'pypi.lucterios.org'], luct_glo.get_default_args_([]))
            self.write_extraurl_file([])
            os.environ['http_proxy'] = 'http://myproxy.truc.com:8000'
            self.write_extraurl_file([])
            self.assertEqual(['--quiet', '--proxy=http://myproxy.truc.com:8000'], luct_glo.get_default_args_([]))
        finally:
            if old_http_proxy is not None:
                os.environ['http_proxy'] = old_http_proxy


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
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_a", instance_path=self.path_dir))
        self.assertEqual(["inst_a"], self.luct_listing())

        inst = run_main_ext('read', get_options(name="inst_a", instance_path=self.path_dir))
        self.assertEqual(("sqlite", {}), inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        table_list = list(self.run_sqlite_cmd("inst_a", "SELECT name FROM sqlite_master WHERE type='table';"))
        if "sqlite_sequence" in table_list:
            table_list.remove("sqlite_sequence")
        table_list.sort()
        self.assertEqual(self.waiting_table, table_list)

        run_main_ext('clear', get_options(name="inst_a", instance_path=self.path_dir))

        table_list = list(self.run_sqlite_cmd("inst_a", "SELECT name FROM sqlite_master WHERE type='table';"))
        if "sqlite_sequence" in table_list:
            table_list.remove("sqlite_sequence")
        table_list.sort()
        self.assertEqual([], table_list)

        self.assertEqual(["inst_a"], self.luct_listing())

    def test_add_modif(self):
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_b", instance_path=self.path_dir))
        self.assertEqual(["inst_b"], self.luct_listing())

        run_main_ext('modif', get_options(name="inst_b", database="sqlite", appli="lucterios.standard",
                                          module='lucterios.dummy', instance_path=self.path_dir))

        inst = run_main_ext('read', get_options(name="inst_b", instance_path=self.path_dir))
        self.assertEqual(("sqlite", {}), inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual(('lucterios.dummy',), inst.modules)

        run_main_ext('refresh', get_options(name="inst_b", instance_path=self.path_dir))

    def test_add_del(self):
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_c", instance_path=self.path_dir))
        self.assertEqual(["inst_c"], self.luct_listing())

        run_main_ext('add', get_options(name="inst_d", instance_path=self.path_dir))
        list_res = self.luct_listing()
        list_res.sort()
        self.assertEqual(["inst_c", "inst_d"], list_res)

        run_main_ext('delete', get_options(name="inst_c", instance_path=self.path_dir))
        self.assertEqual(["inst_d"], self.luct_listing())

        run_main_ext('delete', get_options(name="inst_d", instance_path=self.path_dir))
        self.assertEqual([], self.luct_listing())

    def test_extra(self):
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_e", instance_path=self.path_dir,
                                        extra="DEBUG=True,ALLOWED_HOSTS=[localhost;127.0.0.1],DEFAULT_PAGE=cms/,NBMAX=5,PIVALUE=3.1415"
                                        ))
        self.assertEqual(["inst_e"], self.luct_listing())

        inst = run_main_ext('read', get_options(name="inst_e", instance_path=self.path_dir))
        self.assertEqual({'DEBUG': True, '': {'mode': (0, 'Connexion toujours nécessaire')},
                          'ALLOWED_HOSTS': ['localhost', '127.0.0.1'], 'DEFAULT_PAGE': 'cms/',
                          "NBMAX": 5, 'PIVALUE': 3.1415}, inst.extra)
        run_main_ext('modif', get_options(name="inst_e", instance_path=self.path_dir))
        run_main_ext('read', get_options(name="inst_e", instance_path=self.path_dir))

    def test_archive(self):
        self.assertEqual([], self.luct_listing())
        run_main_ext('add', get_options(name="inst_f", instance_path=self.path_dir))

        path_usr = join(self.path_dir, 'inst_f', 'usr', 'foo')
        makedirs(path_usr)
        with open(join(path_usr, 'myfile'), mode='w+') as myfile:
            myfile.write('boooo!!')

        inst_filename = join(self.path_dir, "inst_f.arc")
        run_main_ext('archive', get_options(name="inst_f", filename=inst_filename, instance_path=self.path_dir))

        import tarfile
        list_file = []
        with tarfile.open(inst_filename, "r:gz") as tar:
            for tarinfo in tar:
                list_file.append(tarinfo.name)
        list_file.sort()
        self.assertEqual(['dump.json', 'target', 'usr', 'usr/foo', 'usr/foo/myfile'], list_file)

        run_main_ext('add', get_options(name="inst_f_bis", instance_path=self.path_dir))
        run_main_ext('restore', get_options(name="inst_f_bis", filename=inst_filename, instance_path=self.path_dir))
        self.assertEqual(True, isdir(join(self.path_dir, 'inst_f_bis', 'usr')))
        self.assertEqual(True, isdir(join(self.path_dir, 'inst_f_bis', 'usr', 'foo')))
        self.assertEqual(True, isfile(join(self.path_dir, 'inst_f_bis', 'usr', 'foo', 'myfile')))

        self.assertEqual(['inst_f', 'inst_f_bis'], self.luct_listing())
        inst = run_main_ext('read', get_options(name="inst_f_bis", instance_path=self.path_dir))
        self.assertEqual(("sqlite", {}), inst.database)
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

    def get_authenticate(self, instance_name, username, password):
        def run_authentication(instance_name, instance_path, username, password, queue):
            from lucterios.install.lucterios_admin import LucteriosInstance
            inst = LucteriosInstance(instance_name, instance_path)
            inst.read()
            from django.contrib.auth import authenticate
            auth = authenticate(username=username, password=password)
            if auth is None:
                queue.put(None)
            else:
                auth_dict = {}
                for key, val in auth.__dict__.items():
                    if key[0] != '_':
                        auth_dict[key] = val
                queue.put(auth_dict)
        from multiprocessing import Process, Queue
        from collections import namedtuple
        queue_return = Queue()
        ext_main = Process(target=run_authentication, args=(instance_name, self.path_dir, username, password, queue_return))
        ext_main.start()
        ext_main.join()
        ret_auth = queue_return.get()
        if isinstance(ret_auth, dict):
            return namedtuple("User", ret_auth.keys())(*ret_auth.values())
        else:
            return ret_auth

    def test_security(self):
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_g", instance_path=self.path_dir))
        self.assertEqual(["inst_g"], self.luct_listing())

        self.assertEqual(["0"], list(self.run_sqlite_cmd("inst_g", "SELECT value FROM CORE_parameter WHERE name='CORE-connectmode';")))
        self.assertEqual(self.get_authenticate("inst_g", 'admin', 'admin').username, 'admin')

        inst = run_main_ext('security', get_options(name="inst_g", instance_path=self.path_dir, extra="PASSWORD=abc123,MODE=2"))
        self.assertEqual(["Admin password change in 'inst_g'.",
                          "Security mode change in 'inst_g'."], inst.msg_list)
        self.assertEqual(["2"], list(self.run_sqlite_cmd("inst_g", "SELECT value FROM CORE_parameter WHERE name='CORE-connectmode';")))
        self.assertEqual(self.get_authenticate("inst_g", 'admin', 'admin'), None)
        self.assertEqual(self.get_authenticate("inst_g", 'admin', 'abc123').username, 'admin')

        inst = run_main_ext('security', get_options(name="inst_g", instance_path=self.path_dir, extra="MODE=1,PASSWORD=abc,123;ABC=789,3333"))
        self.assertEqual(self.get_authenticate("inst_g", 'admin', 'admin'), None)
        self.assertEqual(self.get_authenticate("inst_g", 'admin', 'abc123'), None)
        self.assertEqual(self.get_authenticate("inst_g", 'admin', 'abc,123;ABC=789,3333').username, 'admin')

        inst = run_main_ext('security', get_options(name="inst_g", instance_path=self.path_dir, extra="PASSWORD=ppooi=jjhg,fdd,MODE=0"))
        self.assertEqual(self.get_authenticate("inst_g", 'admin', 'ppooi=jjhg,fdd').username, 'admin')


class TestAdminMySQL(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        self.data = {'dbname': 'testv2', 'username': 'myuser',
                     'passwd': '123456', 'server': 'localhost'}
        for cmd in ("CREATE DATABASE %(dbname)s",
                    "GRANT all ON %(dbname)s.* TO %(username)s@'%(server)s' IDENTIFIED BY '%(passwd)s'",
                    "GRANT all ON %(dbname)s.* TO %(username)s@'127.0.0.1' IDENTIFIED BY '%(passwd)s'"):
            complete_cmd = 'echo "%s;" | mysql -u root -pabc123' % (
                cmd % self.data)
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
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_mysql",
                                        database="mysql:name=testv2,user=myuser,password=123456,host=localhost",
                                        instance_path=self.path_dir))
        self.assertEqual(["inst_mysql"], self.luct_listing())

        inst = run_main_ext('read', get_options(name="inst_mysql", instance_path=self.path_dir))
        self.assertEqual("mysql", inst.database[0])
        self.assertEqual("localhost", inst.database[1]['host'])
        self.assertEqual("testv2", inst.database[1]['name'])
        self.assertEqual("123456", inst.database[1]['password'])
        self.assertEqual("myuser", inst.database[1]['user'])
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        table_list = list(self.run_mysql_cmd("use testv2;show tables;"))
        if "Tables_in_testv2" in table_list:
            table_list.remove("Tables_in_testv2")
        table_list.sort()
        self.assertEqual(self.waiting_table, table_list)

        run_main_ext('clear', get_options(name="inst_mysql", instance_path=self.path_dir))
        table_list = list(self.run_mysql_cmd("use testv2;show tables;"))
        self.assertEqual([], table_list)

        run_main_ext('delete', get_options(name="inst_mysql", instance_path=self.path_dir))
        self.assertEqual([], self.luct_listing())

    def test_archive(self):
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_g", instance_path=self.path_dir))
        run_main_ext('archive', get_options(name="inst_g", filename=join(self.path_dir, "inst_g.arc"), instance_path=self.path_dir))

        run_main_ext('add', get_options(name="inst_mysql",
                                        database="mysql:name=testv2,user=myuser,password=123456,host=localhost",
                                        instance_path=self.path_dir))
        run_main_ext('restore', get_options(name="inst_mysql", filename=join(self.path_dir, "inst_g.arc"), instance_path=self.path_dir))


class TestAdminPostGreSQL(BaseTest):

    def setUp(self):
        BaseTest.setUp(self)
        self.data = {'dbname': self._testMethodName, 'username': 'puser',
                     'passwd': '123456', 'server': 'localhost'}
        for cmd in ("DROP DATABASE %(dbname)s;", "DROP USER %(username)s;",
                    "CREATE USER %(username)s;",
                    "CREATE DATABASE %(dbname)s OWNER %(username)s;",
                    "ALTER USER %(username)s WITH ENCRYPTED PASSWORD '%(passwd)s';"):
            complete_cmd = 'sudo -u postgres psql -c "%s"' % (cmd % self.data)
            os.system(complete_cmd)

    def tearDown(self):
        from django import db
        db.close_old_connections()
        for cmd in ("DROP DATABASE %(dbname)s;", "DROP USER %(username)s;"):
            complete_cmd = 'sudo -u postgres psql -c "%s"' % (cmd % self.data)
            os.system(complete_cmd)
        BaseTest.tearDown(self)

    def run_psql_cmd(self, cmd):
        psqlres = join(self.path_dir, 'out.txt')
        complete_cmd = 'sudo -u postgres psql -d "%s" -c "%s" > %s' % (
            self.data['dbname'], cmd, psqlres)
        os.system(complete_cmd)
        with open(psqlres, 'r') as res_file:
            for line in res_file.readlines():
                yield line.strip()

    def test_add_read(self):
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_psql",
                                        database="postgresql:name=" + self.data['dbname'] + ",user=puser,password=123456,host=localhost",
                                        instance_path=self.path_dir))
        self.assertEqual(["inst_psql"], self.luct_listing())

        inst = run_main_ext('read', get_options(name="inst_psql", instance_path=self.path_dir))
        self.assertEqual("postgresql", inst.database[0])
        self.assertEqual("localhost", inst.database[1]['host'])
        self.assertEqual(self._testMethodName, inst.database[1]['name'])
        self.assertEqual("123456", inst.database[1]['password'])
        self.assertEqual("puser", inst.database[1]['user'])
        self.assertEqual("lucterios.standard", inst.appli_name)
        self.assertEqual((), inst.modules)

        table_list = list(self.run_psql_cmd("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'"))
        table_list.sort()
        table_list = table_list[2:-2]
        self.assertEqual(self.waiting_table, table_list)

        run_main_ext('clear', get_options(name="inst_psql", instance_path=self.path_dir))
        table_list = list(self.run_psql_cmd("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public'"))
        table_list = table_list[2:-2]
        self.assertEqual([], table_list)

        run_main_ext('delete', get_options(name="inst_psql", instance_path=self.path_dir))
        self.assertEqual([], self.luct_listing())

    def test_archive(self):
        self.assertEqual([], self.luct_listing())

        run_main_ext('add', get_options(name="inst_h", instance_path=self.path_dir))
        run_main_ext('archive', get_options(name="inst_h", filename=join(self.path_dir, "inst_h.arc"), instance_path=self.path_dir))

        run_main_ext('add', get_options(name="inst_psql",
                                        database="postgresql:name=" + self.data['dbname'] + ",user=puser,password=123456,host=localhost",
                                        instance_path=self.path_dir))
        run_main_ext('restore', get_options(name="inst_psql", filename=join(self.path_dir, "inst_h.arc"), instance_path=self.path_dir))


if __name__ == "__main__":
    suite = TestSuite()
    loader = TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(TestAdminSQLite))
    suite.addTest(loader.loadTestsFromTestCase(TestAdminMySQL))
    suite.addTest(loader.loadTestsFromTestCase(TestAdminPostGreSQL))
    suite.addTest(loader.loadTestsFromTestCase(TestGlobal))
    JUXDTestRunner(verbosity=1).run(suite)
else:
    from lucterios.install.lucterios_admin import setup_from_none
    setup_from_none()
