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

from shutil import move
from os import mkdir
from os.path import join, isdir, isfile, abspath
from optparse import OptionParser
from importlib import import_module
from django.utils import six
from time import sleep
try:
    from importlib import reload
except ImportError:
    pass
import sys
import os

INSTANCE_PATH = '.'

EXTRA_URL = 'extra_url'
SECURITY_PASSWD = 'PASSWORD'
SECURITY_MODE = 'MODE'
SECURITY_LIST = [SECURITY_PASSWD, SECURITY_MODE]


def delete_path(path, ignore_error=False):
    from shutil import rmtree
    from os import remove
    max_loop = 5
    for loop_id in range(max_loop + 1):
        try:
            if isdir(path):
                rmtree(path)
            if isfile(path):
                remove(path)
            break
        except:
            if max_loop == loop_id:
                if ignore_error:
                    if isdir(path):
                        rmtree(path, True)
                else:
                    raise
            sleep(loop_id)


def clear_modules():
    framework_classes = ()
    import django.conf
    if django.conf.ENVIRONMENT_VARIABLE in os.environ:
        try:
            framework_classes = django.conf.settings.INSTALLED_APPS
            framework_classes += django.conf.settings.MIDDLEWARE_CLASSES
            for template in django.conf.settings.TEMPLATES:
                framework_classes += template['OPTIONS']['loaders']
                framework_classes += template['OPTIONS']['context_processors']
        except:
            pass
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


def get_module_title(module_name):
    try:
        current_mod = import_module(module_name)
        result = getattr(current_mod, '__title__')()
    except AttributeError:
        result = "??? (%s)" % module_name
    return six.text_type(result)


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
        for msg_item in self.msg_list:
            six.print_(msg_item)


class LucteriosGlobal(LucteriosManage):

    def __init__(self, instance_path=INSTANCE_PATH):
        LucteriosManage.__init__(self, instance_path)

    def listing(self):
        import re
        list_res = []
        for manage_file in os.listdir(self.instance_path):
            val = re.match(r"manage_(.+)\.py", manage_file)
            if val is not None:
                sub_dir = val.group(1)
                if isdir(join(self.instance_path, sub_dir)) and isfile(join(self.instance_path, sub_dir, 'settings.py')):
                    list_res.append(sub_dir)
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

    def get_extra_urls(self):
        extra_urls = []
        if EXTRA_URL in os.environ.keys():
            extra_urls = os.environ[EXTRA_URL].split(';')
        if isfile(join(self.instance_path, EXTRA_URL)):
            with open(join(self.instance_path, EXTRA_URL), mode='r') as url_file:
                for line in url_file:
                    line = line.strip()
                    if line.startswith('http'):
                        extra_urls.append(line)
        return extra_urls

    def get_default_args_(self, other_args):
        import logging
        logging.captureWarnings(True)
        args = list(other_args)
        args.append('--quiet')
        if 'http_proxy' in os.environ.keys():
            args.append('--proxy=' + os.environ['http_proxy'])
        extra_urls = self.get_extra_urls()
        if len(extra_urls) > 0:
            for extra_url in extra_urls:
                args.append('--extra-index-url')
                args.append(extra_url)
                if extra_url.startswith('http://'):
                    import re
                    url_parse = re.compile(
                        r'^(([^:/?#]+):)?//(([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?')
                    url_sep = url_parse.search(extra_url)
                    if url_sep:
                        args.append('--trusted-host')
                        args.append(url_sep.groups()[2])
        return args

    def check(self):
        from pip import get_installed_distributions
        from pip.commands import list as list_
        try:
            import pip.utils.logging
            pip.utils.logging._log_state.indentation = 0
        except:
            pass
        check_list = {}
        list_command = list_.ListCommand()
        options, _ = list_command.parse_args(self.get_default_args_([]))
        unvers_packages = get_installed_distributions(local_only=options.local, user_only=options.user, editables_only=options.editable)
        packages = list_command.iter_packages_latest_infos(unvers_packages, options)
        must_upgrade = False
        self.print_info_("check list:")
        for dist in packages:
            requires = [req.key for req in dist.requires()]
            if (dist.key == 'lucterios') or ('lucterios' in requires):
                check_list[dist.project_name] = (dist.version, dist.latest_version, dist.latest_version > dist.parsed_version)
                must_upgrade = must_upgrade or (dist.latest_version > dist.parsed_version)
                if dist.latest_version > dist.parsed_version:
                    text_version = 'to upgrade'
                else:
                    text_version = ''
                self.print_info_("%25s\t%10s\t=>\t%10s\t%s" % (dist.project_name, dist.version, dist.latest_version, text_version))
        if must_upgrade:
            self.print_info_("\t\t=> Must upgrade")
        else:
            self.print_info_("\t\t=> No upgrade")
        return check_list, must_upgrade

    def update(self):
        import pip
        try:
            import pip.utils.logging
            pip.utils.logging._log_state.indentation = 0
        except:
            pass
        module_list = []
        for dist in pip.get_installed_distributions():
            requires = [req.key for req in dist.requires()]
            if (dist.key == 'lucterios') or ('lucterios' in requires):
                module_list.append(dist.project_name)
        if len(module_list) > 0:
            try:
                self.print_info_("Modules to update: %s" %
                                 ",".join(module_list))
                options = self.get_default_args_(['install', '-U'])
                options.extend(module_list)
                pip.main(options)
            finally:
                self.refreshall()
            return True
        else:
            self.print_info_("No modules to update")
            return False

    def refreshall(self):
        instances = self.listing()
        self.clear_info_()
        for instance in instances:
            luct = LucteriosInstance(
                instance, instance_path=self.instance_path)
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
                    self.instance_dir, 'db.sqlite3').replace('\\', '\\\\')
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

    def clear(self, only_delete=False, ignore_db=None):
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
                with connection.cursor() as curs:
                    curs.execute('SET foreign_key_checks = 0;')
            except:
                option = 'CASCADE'
        loop = 10
        while loop > 0:
            tables = connection.introspection.table_names()
            tables.sort()
            no_error = True
            for table in tables:
                if (ignore_db is None) or (table not in ignore_db):
                    try:
                        try:
                            with connection.cursor() as curs:
                                curs.execute(sql_cmd % (table, option))
                        except:
                            with connection.cursor() as curs:
                                curs.execute(sql_cmd % (table, ''))
                    except:
                        no_error = False
            if no_error:
                loop = -1
            else:
                loop -= 1
        if self.database[0] != 'postgresql':
            try:
                with connection.cursor() as curs:
                    curs.execute('SET foreign_key_checks = 1;')
            except:
                pass
        if loop == 0:
            raise Exception("not clear!!")
        user_path = get_user_dir()
        delete_path(user_path)
        self.print_info_("Instance '%s' clear." %
                         self.name)

    def delete(self):
        delete_path(self.instance_dir, True)
        delete_path(self.instance_conf)
        self.print_info_("Instance '%s' deleted." %
                         self.name)

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
        if self.name != '' and isfile(self.setting_path) and isfile(self.instance_conf):
            self.read()

    def read(self):
        clear_modules()
        import django.conf
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isfile(self.setting_path) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists !")
        os.environ[django.conf.ENVIRONMENT_VARIABLE] = self.setting_module_name
        if self.setting_module_name in sys.modules.keys():
            mod_set = sys.modules[self.setting_module_name]
            del mod_set
            del sys.modules[self.setting_module_name]
        import_module(self.setting_module_name)
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
        if isfile(self.setting_path) or isfile(self.instance_conf):
            raise AdminException("Instance exists yet!")
        if isdir(self.instance_dir):
            for file_item in os.listdir(self.instance_dir):
                delete_path(os.path.join(self.instance_dir, file_item), True)
        else:
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
        if not isfile(self.setting_path) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        self.clear_info_()
        self.write_setting_()
        self.print_info_("Instance '%s' modified." %
                         self.name)
        self.refresh()

    def security(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isfile(self.setting_path) or not isfile(self.instance_conf):
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
        if not isfile(self.setting_path) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        self.read()
        self.print_info_("Instance '%s' refreshed." %
                         self.name)
        from django.core.management import call_command
        call_command('migrate', stdout=sys.stdout)

    def archive(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isfile(self.setting_path) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        if self.filename == '':
            raise AdminException("Archive file not precise!")
        self.read()
        from lucterios.framework.filetools import get_tmp_dir, get_user_dir
        from django.core.management import call_command
        from django.db import connection
        output_filename = join(get_tmp_dir(), 'dump.json')
        with open(output_filename, 'w') as output:
            call_command('dumpdata', stdout=output)
        target_filename = join(get_tmp_dir(), 'target')
        with open(target_filename, 'w') as output:
            with connection.cursor() as curs:
                curs.execute(
                    "SELECT app,name FROM django_migrations ORDER BY applied")
                output.write(six.text_type(curs.fetchall()))
        import tarfile
        with tarfile.open(self.filename, "w:gz") as tar:
            tar.add(output_filename, arcname="dump.json")
            tar.add(target_filename, arcname="target")
            user_dir = get_user_dir()
            if isdir(user_dir):
                tar.add(user_dir, arcname="usr")
        delete_path(target_filename)
        delete_path(output_filename)
        return isfile(self.filename)

    def get_other_targets(self, tmp_path, executor):
        def cmp_node():
            class CmpNode:

                def __init__(self, obj, *args):
                    self.obj = obj

                def comp_node(self, other):
                    if self.obj in executor.loader.graph.node_map[other.obj].parents:
                        return -1
                    elif other.obj in executor.loader.graph.node_map[self.obj].parents:
                        return 1
                    else:
                        return 0

                def __lt__(self, other):
                    return self.comp_node(other) < 0

                def __gt__(self, other):
                    return self.comp_node(other) > 0

                def __eq__(self, other):
                    return self.comp_node(other) == 0

                def __le__(self, other):
                    return self.comp_node(other) <= 0

                def __ge__(self, other):
                    return self.comp_node(other) >= 0

                def __ne__(self, other):
                    return self.comp_node(other) != 0
            return CmpNode

        target_filename = join(tmp_path, 'target')
        old_targets = []
        if isfile(target_filename):
            with open(target_filename, 'r') as output:
                old_targets = eval(output.read())
        if len(old_targets) == 0:
            old_targets = [('contenttypes', '0001_initial'),
                           ('auth', '0001_initial'),
                           ('CORE', '0001_initial'),
                           ('CORE', '0002_savedcriteria'),
                           ('CORE', '0003_printmodel_mode'),
                           ('contacts', '0001_initial'),
                           ('accounting', '0001_initial'),
                           ('admin', '0001_initial'),
                           ('admin', '0002_logentry_remove_auto_add'),
                           ('contenttypes', '0002_remove_content_type_name'),
                           ('auth', '0002_alter_permission_name_max_length'),
                           ('auth', '0003_alter_user_email_max_length'),
                           ('auth', '0004_alter_user_username_opts'),
                           ('auth', '0005_alter_user_last_login_null'),
                           ('auth', '0006_require_contenttypes_0002'),
                           ('auth',
                            '0007_alter_validators_add_error_messages'),
                           ('payoff', '0001_initial'),
                           ('invoice', '0001_initial'),
                           ('member', '0001_initial'),
                           ('member', '0002_change_activity'),
                           ('member', '0003_change_permission'),
                           ('condominium', '0001_initial'),
                           ('documents', '0001_initial'),
                           ('mailing', '0001_initial'),
                           ('mailing', '0002_message'),
                           ('sessions', '0001_initial'),
                           ('framework', '0001_initial'),
                           ('asso', '0001_initial'),
                           ('syndic', '0001_initial')]
        targets = []
        for target in executor.loader.graph.nodes:
            if target not in old_targets:
                targets.append(target)
        targets = sorted(set(targets), key=cmp_node())
        return targets

    def _migrate_from_old_targets(self, tmp_path):
        if "sqlite3" in self.databases['default']['ENGINE']:
            try:
                delete_path(self.databases['default']['NAME'])
            except:
                self.clear(False)
                setup_from_none()
            self.read()
        else:
            self.clear(False)

        from django.db import DEFAULT_DB_ALIAS, connections
        from django.apps import apps
        from django.utils.module_loading import module_has_submodule
        from django.db.migrations.executor import MigrationExecutor
        from django.core.management.sql import emit_pre_migrate_signal, emit_post_migrate_signal

        for app_config in apps.get_app_configs():
            if module_has_submodule(app_config.module, "management"):
                import_module('.management', app_config.name)

        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        emit_pre_migrate_signal(0, None, connection.alias)
        executor.migrate(executor.loader.graph.leaf_nodes())
        emit_post_migrate_signal(0, None, connection.alias)
        self.clear(True, ['django_migrations'])

    def run_new_migration(self, tmp_path):
        from inspect import getmembers, isfunction
        from django.apps import apps
        from django.db import DEFAULT_DB_ALIAS, connections
        from django.db.migrations.executor import MigrationExecutor
        connection = connections[DEFAULT_DB_ALIAS]
        connection.prepare_database()
        executor = MigrationExecutor(connection)
        for target in self.get_other_targets(tmp_path, executor):
            try:
                target_conf = apps.get_app_config(target[0])
                migrat_mod = import_module(
                    "%s.migrations.%s" % (target_conf.module.__name__, target[1]))
                for migr_obj in getmembers(migrat_mod):
                    if isfunction(migr_obj[1]) and (migr_obj[0][0] != '_'):
                        six.print_("run %s.%s.%s" %
                                   (target[0], target[1], migr_obj[0]))
                        migr_obj[1]()
            except:
                pass

    def restore(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isfile(self.setting_path) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        if self.filename == '':
            raise AdminException("Archive file not precise!")
        self.read()
        from lucterios.framework.filetools import get_tmp_dir, get_user_dir
        import tarfile
        tmp_path = join(get_tmp_dir(), 'tmp_resore')
        delete_path(tmp_path)
        mkdir(tmp_path)
        with tarfile.open(self.filename, "r:gz") as tar:
            for item in tar:
                tar.extract(item, tmp_path)
        output_filename = join(tmp_path, 'dump.json')
        success = False
        if isfile(output_filename):
            self._migrate_from_old_targets(tmp_path)
            self.clear_info_()
            from django.core.management import call_command
            call_command('loaddata', output_filename)
            self.run_new_migration(tmp_path)
            self.print_info_("instance restored with '%s'" % self.filename)
            if isdir(join(tmp_path, 'usr')):
                target_dir = get_user_dir()
                if isdir(target_dir):
                    delete_path(target_dir)
                move(join(tmp_path, 'usr'), target_dir)
            success = True
        delete_path(tmp_path)
        self.refresh()
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
                      help="extra parameters (<name>=value,...).For 'security': 'MODE=<M>,PASSWORD=<xxx>'(<M> equals to 0,1 or 2)",)
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
    if six.PY3:
        clear_modules()
    from lucterios.framework.settings import fill_appli_settings
    import types
    import gc
    gc.collect()
    lct_modules = []
    glob = LucteriosGlobal()
    _, mod_applis, mod_modules = glob.installed()
    for mod_item in mod_applis:
        lct_modules.append(mod_item[0])
    for mod_item in mod_modules:
        lct_modules.append(mod_item[0])
    try:
        module = types.ModuleType("default_setting")
    except TypeError:
        module = types.ModuleType(six.binary_type("default_setting"))
    setattr(module, '__file__', "")
    setattr(module, 'SECRET_KEY', "default_setting")
    setattr(
        module, 'DATABASES', {'default': {'ENGINE': 'django.db.backends.dummy'}})
    fill_appli_settings("lucterios.standard", lct_modules, module)
    sys.modules["default_setting"] = module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "default_setting")
    import django
    from django import db
    django.setup()
    db.close_old_connections()

if __name__ == '__main__':
    main()
