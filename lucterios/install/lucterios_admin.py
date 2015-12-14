#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Admin tool to manage Lucterios instance

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

from __future__ import unicode_literals

from shutil import rmtree
from os import mkdir, remove
from os.path import join, isdir, isfile, abspath
from optparse import OptionParser
from importlib import import_module
import shutil
from django.utils import six
import traceback
try:
    from importlib import reload
except ImportError:
    pass
import sys
import os

INSTANCE_PATH = '.'

SECURITY_PASSWD = 'PASSWORD'
SECURITY_MODE = 'MODE'
SECURITY_LIST = [SECURITY_PASSWD, SECURITY_MODE]


def get_module_title(module_name):
    try:
        current_mod = import_module(module_name)
        return six.text_type(getattr(current_mod, '__title__')())
    except AttributeError:
        return "??? (%s)" % module_name


def get_package_list():
    def get_files(dist):
        paths = []
        # RECORDs should be part of .dist-info metadatas
        if dist.has_metadata('RECORD'):
            lines = dist.get_metadata_lines('RECORD')
            paths = [l.split(',')[0].replace('/', os.sep) for l in lines]
            paths = [os.path.join(dist.location, p) for p in paths]
        # Otherwise use pip's log for .egg-info's
        elif dist.has_metadata('installed-files.txt'):
            paths = dist.get_metadata_lines('installed-files.txt')
            paths = [
                os.path.join(dist.egg_info, p.replace('/', os.sep)) for p in paths]
        elif os.path.join(dist.location, '__init__.py'):
            paths = [os.path.join(dir_desc[0], file_item) for dir_desc in os.walk(
                dist.location) for file_item in dir_desc[2] if file_item[-3:] == '.py']
        return [os.path.relpath(p, dist.location) for p in paths]

    def get_module_desc(modname):
        appmodule = import_module(modname)
        if hasattr(appmodule, 'link'):
            return (modname, appmodule.__version__, appmodule.link())
        else:
            return (modname, appmodule.__version__, [])
    import pip
    package_list = {}
    dists = pip.get_installed_distributions()
    for dist in dists:
        requires = [req.key for req in dist.requires()]
        if (dist.key == 'lucterios') or ('lucterios' in requires):
            current_applis = []
            current_modules = []
            for file_item in get_files(dist):
                try:
                    py_mod_name = ".".join(file_item.split(os.sep)[:-1])
                    if file_item.endswith('appli_settings.py'):
                        current_applis.append(get_module_desc(py_mod_name))
                    elif file_item.endswith('models.py'):
                        current_modules.append(get_module_desc(py_mod_name))
                except:
                    pass
            current_applis.sort()
            current_modules.sort()
            package_list[dist.key] = (
                dist.version, current_applis, current_modules, requires)
    return package_list


class AdminException(Exception):
    pass


class LucteriosManage(object):

    def __init__(self, instance_path):
        self.clear_info_()
        self.instance_path = abspath(instance_path)

    def clear_info_(self):
        self.msg_list = []

    def print_info_(self, msg):
        self.msg_list.append(msg)

    def show_info_(self):
        six.print_("\n".join(self.msg_list))


class LucteriosGlobal(LucteriosManage):

    def __init__(self, instance_path=INSTANCE_PATH):
        LucteriosManage.__init__(self, instance_path)

    def listing(self):
        import re
        list_res = []
        for manage_file in os.listdir(self.instance_path):
            val = re.match(r"manage_(.+)\.py", manage_file)
            if val is not None and isdir(join(self.instance_path, val.group(1))):
                list_res.append(val.group(1))
        list_res.sort()
        self.print_info_("Instance listing: %s" % ",".join(list_res))
        return list_res

    def installed(self):
        def show_list(modlist):
            res = []
            for item in modlist:
                res.append("\t%s\t[%s]\t%s" %
                           (item[0], item[1], ",".join(item[2])))
            return "\n".join(res)
        package_list = get_package_list()
        if 'lucterios' in package_list.keys():
            mod_lucterios = ('lucterios', package_list['lucterios'][0])
            del package_list['lucterios'][2][0]
        else:
            mod_lucterios = ('lucterios', '???')
        mod_applis = []
        mod_modules = []
        for _, appli_list, module_list, _ in package_list.values():
            mod_applis.extend(appli_list)
            mod_modules.extend(module_list)
        self.print_info_("Description:\n\t%s\t\t[%s]" % mod_lucterios)
        self.print_info_("Applications:\n%s" % show_list(mod_applis))
        self.print_info_("Modules:\n%s" % show_list(mod_modules))
        return mod_lucterios, mod_applis, mod_modules

    def get_default_args_(self, other_args):

        import logging
        logging.captureWarnings(True)
        args = ['--quiet']
        args.extend(other_args)
        if 'http_proxy' in os.environ.keys():
            args.append('--proxy=' + os.environ['http_proxy'])
        if 'extra_url' in os.environ.keys():
            extra_urls = os.environ['extra_url']
            args.append('--extra-index-url=' + extra_urls)
            trusted_host = []
            for extra_url in extra_urls.split(','):
                if extra_url.startswith('http://'):
                    import re
                    url_parse = re.compile(
                        r'^(([^:/?#]+):)?//(([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
                    url_sep = url_parse.search(os.environ['extra_url'])
                    if url_sep:
                        trusted_host.append(url_sep.groups()[2])
            if len(trusted_host) > 0:
                args.append('--trusted-host=' + ",".join(trusted_host))
        return args

    def check(self):
        from pip import get_installed_distributions
        from pip.commands import list as list_
        import pip.utils.logging
        pip.utils.logging._log_state.indentation = 0
        check_list = {}
        for dist in get_installed_distributions():
            requires = [req.key for req in dist.requires()]
            if (dist.key == 'lucterios') or ('lucterios' in requires):
                check_list[dist.project_name] = (dist.version, None, False)
        list_command = list_.ListCommand()
        options, _ = list_command.parse_args(self.get_default_args_([]))
        try:
            packages = [(pack[0], pack[1]) for pack in list_command.find_packages_latest_versions(
                options)]
        except AttributeError:
            packages = [(pack[0], pack[1]) for pack in list_command.find_packages_latests_versions(
                options)]
        for dist, remote_version_parsed in packages:
            if dist.project_name in check_list.keys():
                check_list[dist.project_name] = (
                    dist.version, remote_version_parsed.public, remote_version_parsed > dist.parsed_version)
        must_upgrade = False
        self.print_info_("check list:")
        for project_name, versions in check_list.items():
            must_upgrade = must_upgrade or versions[2]
            if versions[2]:
                text_version = 'to upgrade'
            else:
                text_version = ''
            self.print_info_("%25s\t%10s\t=>\t%10s\t%s" % (
                project_name, versions[0], versions[1], text_version))
        if must_upgrade:
            self.print_info_("\t\t=> Must upgrade")
        else:
            self.print_info_("\t\t=> No upgrade")
        return check_list, must_upgrade

    def update(self):
        from pip import get_installed_distributions
        from pip.commands import install
        import pip.utils.logging
        pip.utils.logging._log_state.indentation = 0
        module_list = []
        for dist in get_installed_distributions():
            requires = [req.key for req in dist.requires()]
            if (dist.key == 'lucterios') or ('lucterios' in requires):
                module_list.append(dist.project_name)
        if len(module_list) > 0:
            self.print_info_("Modules to update: %s" % ",".join(module_list))
            install_command = install.InstallCommand()
            options, _ = install_command.parse_args(
                self.get_default_args_(['-U']))
            requirement_set = install_command.run(options, module_list)
            requirement_set.install(options)
            self.print_info_("Modules updated: %s" %
                             ",".join(requirement_set.successfully_installed))
            self.refresh_all()
            return True
        else:
            self.print_info_("No modules to update")
            return False

    def refresh_all(self):
        instances = self.listing()
        self.clear_info_()
        for instance in instances:
            luct = LucteriosInstance(instance)
            luct.refresh()
            self.print_info_("Refresh %s" % instance)
        return instances


class LucteriosInstance(LucteriosManage):

    def __init__(self, name, instance_path=INSTANCE_PATH):
        LucteriosManage.__init__(self, instance_path)
        import random
        self.secret_key = ''.join([random.SystemRandom().choice(
            'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])
        self.name = name
        self.filename = ""
        self.setting_module_name = "%s.settings" % self.name
        self.instance_dir = join(self.instance_path, self.name)
        self.setting_path = join(self.instance_dir, 'settings.py')
        self.instance_conf = join(self.instance_path, "manage_%s.py" % name)
        self.appli_name = 'lucterios.standard'
        self.databases = {}
        self.database = ('sqlite', {})
        self.modules = ()
        self.extra = {}
        sys.path.insert(0, self.instance_path)
        self.reloader = None
        if self.setting_module_name in sys.modules.keys():
            del sys.modules[self.setting_module_name]

    def set_appli(self, appli_name):
        if appli_name is not None:
            self.appli_name = appli_name

    def set_extra(self, extra):
        self.extra[''] = extra
        for item in extra.split(','):
            if '=' in item:
                key, value = item.split('=')[:2]
                if (value.lower() == 'true') or (value.lower() == 'false'):
                    self.extra[key] = value.lower() == 'true'
                elif isinstance(value, float):
                    self.extra[key] = float(value)
                elif (len(value) > 0) and (value[0] == '[') and (value[-1] == ']'):
                    self.extra[key] = value[1:-1].split(',')
                else:
                    self.extra[key] = value

    def set_database(self, database):
        if database is not None:
            if ':' in database:
                dbtype, info_text = database.split(':')
                info = {'name': 'default', 'user': 'root',
                        'password': '', 'host': 'localhost'}
                for val in info_text.split(','):
                    if '=' in val:
                        key, value = val.split('=')
                        info[key] = value
            else:
                dbtype = database
                info = {}
            self.database = (dbtype, info)

    def set_module(self, module):
        if module is not None:
            if module != '':
                self.modules = tuple(module.split(','))
            else:
                self.modules = ()

    def get_appli_txt(self):
        return get_module_title(self.appli_name)

    def get_extra_txt(self):
        extra_txt = ''
        for key, val in self.extra.items():
            if key != '':
                extra_txt += '\n\t\t%s=%s ' % (key, val)
            else:
                if ('mode' in val.keys()) and (val['mode'] is not None):
                    extra_txt += '\n\t\tmode=%s ' % val['mode'][1]
        return extra_txt

    def get_database_txt(self):
        database_txt = self.database[0]
        if database_txt != 'sqlite':
            database_txt += ' ('
            for key in ['name', 'user', 'password', 'port', 'host']:
                if key in self.database[1].keys():
                    val = self.database[1][key]
                    if val != '':
                        database_txt += '%s=%s,' % (key, val)
            database_txt = database_txt[:-1] + ')'
        return database_txt

    def get_module_txt(self):
        mod_list = []
        for module in self.modules:
            mod_list.append(get_module_title(module))
        return ', '.join(mod_list)

    def _add_dependancy_modules(self):
        glob = LucteriosGlobal(self.instance_path)
        checked_modules = []
        _, _, mod_modules = glob.installed()
        for mod_item in mod_modules:
            if mod_item[0] in self.modules:
                checked_modules.extend(mod_item[2])
        for mod_name in checked_modules:
            if mod_name not in self.modules:
                self.modules += (mod_name,)

    def _get_module_text(self):
        modules_text = ''
        for module_item in self.modules:
            modules_text += '"%s"' % six.text_type(module_item)
            modules_text += ','
        return modules_text

    def _write_db_params(self, file_py):
        file_py.write('DATABASES = {\n')
        for db_ident, db_values in self.databases.items():
            file_py.write('     "%s": {\n' % db_ident)
            for db_key, db_data in db_values.items():
                if isinstance(db_data, six.string_types):
                    file_py.write('         "%s": "%s",\n' %
                                  (db_key.upper(), db_data))
                else:
                    file_py.write('         "%s": %s,\n' %
                                  (db_key.upper(), db_data))
            file_py.write('     },\n')
        file_py.write('}\n')

    def write_setting_(self):
        self._add_dependancy_modules()
        with open(self.setting_path, "w") as file_py:
            file_py.write('#!/usr/bin/env python\n')
            file_py.write('# -*- coding: utf8 -*-\n')
            file_py.write('\n')
            file_py.write('import os\n')
            file_py.write(
                'from lucterios.framework.settings import fill_appli_settings\n')
            file_py.write('\n')
            file_py.write('# Initial constant\n')
            file_py.write('SECRET_KEY = "%s"\n' % self.secret_key)
            file_py.write('\n')
            file_py.write('# Database\n')
            file_py.write('BASE_DIR = os.path.dirname(__file__)\n')
            if not isinstance(self.databases, dict):
                self.databases = {}
            self.databases["default"] = {}
            if self.database[0].lower() == 'sqlite':
                self.databases["default"][
                    "ENGINE"] = 'django.db.backends.sqlite3'
                self.databases["default"]["NAME"] = join(
                    self.instance_dir, 'db.sqlite3')
            elif self.database[0].lower() == 'mysql':
                self.databases["default"] = self.database[1]
                self.databases["default"][
                    "ENGINE"] = 'django.db.backends.mysql'
            elif self.database[0].lower() == 'postgresql':
                self.databases["default"] = self.database[1]
                self.databases["default"][
                    "ENGINE"] = 'django.db.backends.postgresql_psycopg2'
            elif self.database[0].lower() == 'oracle':
                self.databases["default"] = self.database[1]
                self.databases["default"][
                    "ENGINE"] = 'django.db.backends.oracle'
            else:
                raise AdminException("Database not supported!")
            self._write_db_params(file_py)
            file_py.write('\n')
            file_py.write('# extra\n')
            for key, value in self.extra.items():
                if key != '':
                    file_py.write('%s = %s\n' % (key, value))
            file_py.write('# configuration\n')
            file_py.write('fill_appli_settings("%s", (%s)) \n' %
                          (self.appli_name, self._get_module_text()))
            file_py.write('\n')

    def clear(self, only_delete=False):
        self.read()
        from lucterios.framework.filetools import get_user_dir
        from django.db import connection
        option = 'CASCADE'
        if self.database[0] == 'postgresql':
            if only_delete:
                sql_cmd = 'DELETE FROM "%s" %s;'
            else:
                sql_cmd = 'DROP TABLE IF EXISTS "%s" %s;'
        else:
            if only_delete:
                sql_cmd = 'DELETE FROM %s %s;'
            else:
                sql_cmd = 'DROP TABLE IF EXISTS %s %s;'
            try:
                connection.cursor().execute('SET foreign_key_checks = 0;')
            except:
                option = 'CASCADE'
        loop = 10
        while loop > 0:
            tables = connection.introspection.table_names()
            tables.sort()
            no_error = True
            for table in tables:
                try:
                    try:
                        connection.cursor().execute(sql_cmd % (table, option))
                    except:
                        connection.cursor().execute(sql_cmd % (table, ''))
                except:
                    traceback.print_exc()
                    no_error = False
            if no_error:
                loop = -1
            else:
                loop -= 1
        if self.database[0] != 'postgresql':
            try:
                connection.cursor().execute('SET foreign_key_checks = 1;')
            except:
                pass
        if loop == 0:
            raise Exception("not clear!!")
        user_path = get_user_dir()
        if isdir(user_path):
            rmtree(user_path)
        self.print_info_("Instance '%s' clear." %
                         self.name)

    def delete(self):
        if isdir(self.instance_dir):
            rmtree(self.instance_dir)
        if isfile(self.instance_conf):
            remove(self.instance_conf)
        self.print_info_("Instance '%s' deleted." %
                         self.name)

    def _clear_modules_(self):

        framework_classes = ()
        import django.conf
        if django.conf.ENVIRONMENT_VARIABLE in os.environ:
            framework_classes = django.conf.settings.INSTALLED_APPS
            framework_classes += django.conf.settings.MIDDLEWARE_CLASSES
            framework_classes += django.conf.settings.TEMPLATE_LOADERS
            framework_classes += django.conf.settings.TEMPLATE_CONTEXT_PROCESSOR
        module_list = list(sys.modules.keys())
        for module_item in module_list:
            is_in_framwork_list = False
            if not module_item.startswith('django'):
                for framework_class in framework_classes:
                    if module_item.startswith(framework_class):
                        is_in_framwork_list = True
                        break
            else:
                is_in_framwork_list = True
            if is_in_framwork_list:
                del sys.modules[module_item]

    def _get_db_info_(self):

        import django.conf
        info = {}
        key_list = list(django.conf.settings.DATABASES['default'].keys())
        key_list.sort()
        for key in key_list:
            if key != 'ENGINE':
                info[key.lower()] = django.conf.settings.DATABASES[
                    'default'][key]
        return info

    def read_before(self):
        if self.name != '' and isdir(self.instance_dir) and isfile(self.instance_conf):
            self.read()

    def read(self):
        self._clear_modules_()
        import django.conf
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists !")
        os.environ[django.conf.ENVIRONMENT_VARIABLE] = self.setting_module_name
        if self.setting_module_name in sys.modules.keys():
            mod_set = sys.modules[self.setting_module_name]
            del mod_set
            del sys.modules[self.setting_module_name]
        __import__(self.setting_module_name)
        reload(django.conf)
        django.setup()
        self.secret_key = django.conf.settings.SECRET_KEY
        self.extra = django.conf.settings.EXTRA
        self.databases = django.conf.settings.DATABASES
        self.database = django.conf.settings.DATABASES['default']['ENGINE']
        if "sqlite3" in self.database:
            self.database = ('sqlite', {})
        if "mysql" in self.database:
            self.database = ('mysql', self._get_db_info_())
        if "postgresql" in self.database:
            self.database = ('postgresql', self._get_db_info_())
        self.appli_name = django.conf.settings.APPLIS_MODULE.__name__
        self.modules = ()
        for appname in django.conf.settings.INSTALLED_APPS:
            if ("django" not in appname) and (appname != 'lucterios.framework') and (appname != 'lucterios.CORE') and (self.appli_name != appname):
                self.modules = self.modules + (six.text_type(appname),)
        from lucterios.CORE.parameters import Params
        from lucterios.framework.error import LucteriosException
        try:
            self.extra[''] = {'mode': (
                Params.getvalue("CORE-connectmode"), Params.gettext("CORE-connectmode"))}
        except LucteriosException:
            self.extra[''] = {'mode': None}
        self.print_info_("""Instance %s:
    path\t%s
    appli\t%s
    database\t%s
    modules\t%s
    extra\t%s
""" % (self.name, self.instance_dir, self.get_appli_txt(), self.get_database_txt(), self.get_module_txt(), self.get_extra_txt()))
        return

    def add(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if isdir(self.instance_dir) or isfile(self.instance_conf):
            raise AdminException("Instance exists yet!")
        mkdir(self.instance_dir)
        with open(join(self.instance_dir, '__init__.py'), "w") as file_py:
            file_py.write('\n')
        self.write_setting_()
        with open(self.instance_conf, "w") as file_py:
            file_py.write('#!/usr/bin/env python\n')
            file_py.write('import os\n')
            file_py.write('import sys\n')
            file_py.write('if __name__ == "__main__":\n')
            file_py.write('    sys.path.append(os.path.dirname(__file__))\n')
            file_py.write(
                '    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings")\n' % self.name)
            file_py.write(
                '    from django.core.management import execute_from_command_line\n')
            file_py.write('    execute_from_command_line(sys.argv)\n')
        self.print_info_("Instance '%s' created." %
                         self.name)
        self.refresh()

    def modif(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        self.clear_info_()
        self.write_setting_()
        self.print_info_("Instance '%s' modified." %
                         self.name)
        self.refresh()

    def security(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        security_param = self.extra
        self.read()
        self.clear_info_()
        if SECURITY_PASSWD in security_param.keys():
            passwd = security_param['']
            for sec_item in SECURITY_LIST:
                if (sec_item in security_param.keys()) and (sec_item != SECURITY_PASSWD):
                    item_str = "%s=%s" % (sec_item, security_param[sec_item])
                    if passwd[:len(item_str)] == item_str:
                        passwd = passwd[len(item_str) + 1:]
                    elif passwd[-1 * len(item_str):] == item_str:
                        passwd = passwd[:-1 * len(item_str) - 1]
                    else:
                        item_idx = passwd.find(item_str)
                        if item_idx != -1:
                            passwd = passwd[:item_idx] + \
                                passwd[item_idx + len(item_str):]
            passwd = passwd[len(SECURITY_PASSWD) + 1:]
            from lucterios.CORE.models import LucteriosUser
            adm_user = LucteriosUser.objects.get(
                username='admin')
            adm_user.set_password(passwd)
            adm_user.save()
            self.print_info_("Admin password change in '%s'." %
                             self.name)
        if (SECURITY_MODE in security_param.keys()) and (int(security_param[SECURITY_MODE]) in [0, 1, 2]):
            from lucterios.CORE.models import Parameter
            from lucterios.CORE.parameters import Params
            db_param = Parameter.objects.get(
                name='CORE-connectmode')
            db_param.value = six.text_type(security_param[SECURITY_MODE])
            db_param.save()
            Params.clear()

            self.print_info_("Security mode change in '%s'." %
                             self.name)

    def refresh(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        self.read()
        self.print_info_("Instance '%s' refreshed." %
                         self.name)
        from django.core.management import call_command
        call_command('migrate', stdout=sys.stdout)

    def archive(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        if self.filename == '':
            raise AdminException("Archive file not precise!")
        self.read()
        from lucterios.framework.filetools import get_tmp_dir, get_user_dir
        output_filename = join(get_tmp_dir(), 'dump.json')
        from django.core.management import call_command
        # Point stdout at a file for dumping data to.
        with open(output_filename, 'w') as output:
            call_command('dumpdata', stdout=output)
        import tarfile
        with tarfile.open(self.filename, "w:gz") as tar:
            tar.add(output_filename, arcname="dump.json")
            user_dir = get_user_dir()
            if isdir(user_dir):
                tar.add(user_dir, arcname="usr")
        remove(output_filename)
        return isfile(self.filename)

    def restore(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        if self.filename == '':
            raise AdminException("Archive file not precise!")
        self.read()
        from lucterios.framework.filetools import get_tmp_dir, get_user_dir
        import tarfile
        tmp_path = join(get_tmp_dir(), 'tmp_resore')
        if isdir(tmp_path):
            rmtree(tmp_path)
        mkdir(tmp_path)
        with tarfile.open(self.filename, "r:gz") as tar:
            for item in tar:
                tar.extract(item, tmp_path)
        output_filename = join(tmp_path, 'dump.json')
        success = False
        if isfile(output_filename):
            self.clear(True)
            from django.core.management import call_command
            call_command('loaddata', output_filename)
            if isdir(join(tmp_path, 'usr')):
                shutil.move(join(tmp_path, 'usr'), get_user_dir())
            success = True
        if isdir(tmp_path):
            rmtree(tmp_path)
        return success


def list_method(from_class):
    import inspect
    res = []
    for item in inspect.getmembers(from_class):
        name = item[0]
        if ('_' not in name) and not name.startswith('get_') and not name.startswith('set_') and (inspect.ismethod(item[1]) or inspect.isfunction(item[1])):
            res.append(name)
    return "|".join(res)


def main():
    parser = OptionParser(usage="\n\t%%prog <%s>\n\t%%prog <%s> [option]" % (list_method(LucteriosGlobal), list_method(LucteriosInstance)),
                          version="%prog 2.0")
    parser.add_option("-n", "--name",
                      dest="name",
                      default='',
                      help="Instance name")
    parser.add_option("-p", "--appli",
                      dest="appli",
                      default=None,
                      help="Instance application",)
    parser.add_option("-d", "--database",
                      dest="database",
                      default=None,
                      help="Database configuration 'sqlite', 'MySQL:...' or 'PostGreSQL:...'")
    parser.add_option("-m", "--module",
                      dest="module",
                      default=None,
                      help="Modules to add (comma separator)",)
    parser.add_option("-e", "--extra",
                      dest="extra",
                      default="",
                      help="extra parameters (<name>=value,...)",)
    parser.add_option("-f", "--file",
                      dest="filename",
                      default="",
                      help="file name for restor or archive")
    parser.add_option("-i", "--instance_path",
                      dest="instance_path",
                      default=INSTANCE_PATH,
                      help="Directory of instance storage",)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Bad arguments!")
    try:
        luct = None
        if hasattr(LucteriosGlobal, args[0]):
            luct = LucteriosGlobal(options.instance_path)
        elif hasattr(LucteriosInstance, args[0]):
            luct = LucteriosInstance(options.name, options.instance_path)
            luct.filename = options.filename
            if args[0] == 'modif':
                luct.read_before()
            luct.set_extra(options.extra)
            luct.set_appli(options.appli)
            luct.set_database(options.database)
            luct.set_module(options.module)
        if luct is not None:
            getattr(luct, args[0])()
            luct.show_info_()
            return
        else:
            parser.print_help()
    except AdminException as error:
        parser.error(six.text_type(error))


def setup_from_none():
    from lucterios.framework.settings import fill_appli_settings
    import types
    module = types.ModuleType("default_setting")
    setattr(module, '__file__', "")
    setattr(module, 'SECRET_KEY', "default_setting")
    fill_appli_settings("lucterios.standard", None, module)
    sys.modules["default_setting"] = module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "default_setting")
    import django
    django.setup()

if __name__ == '__main__':
    main()
