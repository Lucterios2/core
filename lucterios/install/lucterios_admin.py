#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from shutil import rmtree
from os import mkdir, remove
from os.path import join, isdir, isfile, abspath
from optparse import OptionParser
from django.utils import six
from django.conf import Settings, ENVIRONMENT_VARIABLE
from importlib import import_module
import sys, os

INSTANCE_PATH = '.'

def get_package_list():
    def get_files(dist):
        paths = []
        import pkg_resources
        if isinstance(dist, pkg_resources.DistInfoDistribution):
            # RECORDs should be part of .dist-info metadatas
            if dist.has_metadata('RECORD'):
                lines = dist.get_metadata_lines('RECORD')
                paths = [l.split(',')[0] for l in lines]
                paths = [os.path.join(dist.location, p) for p in paths]
        else:
            # Otherwise use pip's log for .egg-info's
            if dist.has_metadata('installed-files.txt'):
                paths = dist.get_metadata_lines('installed-files.txt')
                paths = [os.path.join(dist.egg_info, p) for p in paths]
        return [os.path.relpath(p, dist.location) for p in paths]
    def get_module_desc(modname):
        appmodule = import_module(modname)
        return (modname, appmodule.__version__)
    import pip
    package_list = {}
    for dist in pip.get_installed_distributions():
        requires = [req.key for req in dist.requires()]
        if (dist.key == 'lucterios') or ('lucterios' in requires):
            current_applis = []
            current_modules = []
            for file_item in get_files(dist):
                try:
                    py_mod_name = ".".join(file_item.split('/')[:-1])
                    if file_item.endswith('appli_settings.py'):
                        current_applis.append(get_module_desc(py_mod_name))
                    elif file_item.endswith('models.py'):
                        current_modules.append(get_module_desc(py_mod_name))
                except:  # pylint: disable=bare-except
                    pass
            package_list[dist.key] = (dist.version, current_applis, current_modules, requires)
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
            val = re.match(r"manage_([a-zA-Z0-9_]+)\.py", manage_file)
            if val is not None and isdir(join(self.instance_path, val.group(1))):
                list_res.append(val.group(1))
        self.print_info_("Instance listing: %s" % ",".join(list_res))
        return list_res

    def installed(self):
        def show_list(modlist):
            res = []
            for item in modlist:
                res.append("\t%s\t[%s]\t%s" % (item[0], item[1], ",".join(item[2])))
            return "\n".join(res)
        package_list = get_package_list()
        mod_lucterios = ('lucterios', package_list['lucterios'][0] if ('lucterios' in package_list.keys()) else '???')
        if 'lucterios' in package_list.keys():
            mod_lucterios = ('lucterios', package_list['lucterios'][0])
            del package_list['lucterios']
        else:
            mod_lucterios = ('lucterios', '???')
        mod_applis = []
        mod_modules = []
        for _, appli_list, module_list, require_list in package_list.values():
            requires = []
            for require_item in require_list:
                if require_item in package_list.keys():
                    for sub_item in package_list[require_item][2]:
                        requires.append(sub_item[0])
            for appli_item in appli_list:
                mod_applis.append(appli_item + (requires,))
            for module_item in module_list:
                mod_modules.append(module_item + (requires,))
        self.print_info_("Description:\n\t%s\t%s" % mod_lucterios)
        self.print_info_("Applications:\n%s" % show_list(mod_applis))
        self.print_info_("Modules:\n%s" % show_list(mod_modules))
        return mod_lucterios, mod_applis, mod_modules

    def get_default_args_(self, other_args):
        # pylint: disable=no-self-use
        import logging
        logging.captureWarnings(True)
        args = ['--quiet']
        args.extend(other_args)
        if 'http_proxy' in os.environ.keys():
            args.append('--proxy=' + os.environ['http_proxy'])
        return args

    def check(self):
        # pylint: disable=too-many-locals
        from pip import get_installed_distributions
        from pip.commands import list as list_
        check_list = {}
        for dist in get_installed_distributions():
            requires = [req.key for req in dist.requires()]
            if (dist.key == 'lucterios') or ('lucterios' in requires):
                check_list[dist.project_name] = (dist.parsed_version, None, False)
        list_command = list_.ListCommand()
        options, _ = list_command.parse_args(self.get_default_args_([]))
        try:
            packages = [(pack[0], pack[2]) for pack in list_command.find_packages_latest_versions(options)]  # pylint: disable=no-member
        except AttributeError:
            packages = [(pack[0], pack[1]) for pack in list_command.find_packages_latests_versions(options)]  # pylint: disable=no-member
        for dist, remote_version_parsed in packages:
            if dist.project_name in check_list.keys():
                check_list[dist.project_name] = (dist.parsed_version, remote_version_parsed, remote_version_parsed > dist.parsed_version)
        must_upgrade = False
        self.print_info_("check list:")
        for project_name, versions in check_list.items():
            must_upgrade = must_upgrade or versions[2]
            self.print_info_("%25s\t%s" % (project_name, versions))
        if must_upgrade:
            self.print_info_("\t\t=> Must upgrade")
        else:
            self.print_info_("\t\t=> No upgrade")
        return check_list, must_upgrade

    def update(self):
        from pip import get_installed_distributions
        from pip.commands import install
        module_list = []
        for dist in get_installed_distributions():
            requires = [req.key for req in dist.requires()]
            if (dist.key == 'lucterios') or ('lucterios' in requires):
                module_list.append(dist.project_name)
        if len(module_list) > 0:
            self.print_info_("Modules to update: %s" % ",".join(module_list))
            install_command = install.InstallCommand()
            options, _ = install_command.parse_args(self.get_default_args_(['-U']))
            requirement_set = install_command.run(options, module_list)
            requirement_set.install(options)
            self.print_info_("Modules updated: %s" % ",".join(requirement_set.successfully_installed))
            has_updated = len(requirement_set.successfully_installed) > 0
            if has_updated:
                self.refresh_all()
            return has_updated
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

class LucteriosInstance(LucteriosManage):
    # pylint: disable=too-many-instance-attributes

    def __init__(self, name, instance_path=INSTANCE_PATH):
        LucteriosManage.__init__(self, instance_path)
        import random
        self.secret_key = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])
        self.name = name
        self.setting_module_name = "%s.settings" % self.name
        self.instance_dir = join(self.instance_path, self.name)
        self.setting_path = join(self.instance_dir, 'settings.py')
        self.instance_conf = join(self.instance_path, "manage_%s.py" % name)
        self.appli_name = 'lucterios.standard'
        self.database = 'sqlite'
        self.modules = ()
        self.extra = {}
        sys.path.insert(0, self.instance_path)
        self.reloader = None
        if self.setting_module_name in sys.modules.keys():
            del sys.modules[self.setting_module_name]

    def set_appli(self, appli_name):
        self.appli_name = appli_name

    def set_extra(self, extra):
        self.extra = {}
        for item in extra.split(','):
            if '=' in item:
                key, value = item.split('=')
                if (value == 'True') or (value == 'True'):
                    self.extra[key] = value == 'True'
                elif isinstance(value, float):
                    self.extra[key] = float(value)
                elif value[0] == '[' and value[-1] == ']':
                    self.extra[key] = value[1:-1].split(',')
                else:
                    self.extra[key] = value

    def set_database(self, database):
        self.database = database

    def set_module(self, module):
        if module != '':
            self.modules = tuple(module.split(','))
        else:
            self.modules = ()

    def write_setting_(self):
        with open(self.setting_path, "w") as file_py:
            file_py.write('#!/usr/bin/env python\n')
            file_py.write('# -*- coding: utf8 -*-\n')
            file_py.write('\n')
            file_py.write('# Initial constant\n')
            file_py.write('SECRET_KEY = "%s"\n' % self.secret_key)
            file_py.write('\n')
            file_py.write('# Database\n')
            file_py.write('import os\n')
            file_py.write('BASE_DIR = os.path.dirname(__file__)\n')
            file_py.write('DATABASES = {\n')
            file_py.write('     "default": {\n')
            if self.database == 'sqlite':
                file_py.write('         "ENGINE": "django.db.backends.sqlite3",\n')
                file_py.write('         "NAME": os.path.join(BASE_DIR, "db.sqlite3"),\n')
            else:
                raise AdminException("Database not supported!")
            file_py.write('     }\n')
            file_py.write('}\n')
            file_py.write('\n')
            file_py.write('# extra\n')
            for key, value in self.extra.items():
                file_py.write('%s = %s\n' % (key, value))
            file_py.write('# configuration\n')
            file_py.write('from lucterios.framework.settings import fill_appli_settings\n')
            file_py.write('fill_appli_settings("%s", %s) \n' % (self.appli_name, six.text_type(self.modules)))
            file_py.write('\n')

    def clear(self):
        # pylint: disable=no-self-use
        self.read()
        from lucterios.framework.filetools import get_user_dir
        from django.db import connection
        tables = connection.introspection.table_names()
        tables.sort()
        for table in tables:
            connection.cursor().execute('DROP TABLE IF EXISTS %s;' % table)
        user_path = get_user_dir()
        if isdir(user_path):
            rmtree(user_path)
        self.print_info_("Instance '%s' clear." % self.name)  # pylint: disable=superfluous-parens

    def delete(self):
        if isdir(self.instance_dir):
            rmtree(self.instance_dir)
        if isfile(self.instance_conf):
            remove(self.instance_conf)
        self.print_info_("Instance '%s' deleted." % self.name)  # pylint: disable=superfluous-parens

    def read(self):
        from django import setup
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists !")
        os.environ[ENVIRONMENT_VARIABLE] = self.setting_module_name
        if self.setting_module_name in sys.modules.keys():
            mod_set = sys.modules[self.setting_module_name]
            del mod_set
            del sys.modules[self.setting_module_name]

        __import__(self.setting_module_name)
        setup()
        from django.conf import settings
        settings._wrapped = Settings(self.setting_module_name)  # pylint: disable=protected-access
        self.secret_key = settings.SECRET_KEY
        self.extra = settings.EXTRA
        self.database = settings.DATABASES['default']['ENGINE']
        if "sqlite3" in self.database:
            self.database = 'sqlite'
        self.appli_name = settings.APPLIS_MODULE.__name__
        self.modules = ()
        for appname in settings.INSTALLED_APPS:
            if (not "django" in appname) and (appname != 'lucterios.framework') and (appname != 'lucterios.CORE') and (self.appli_name != appname):

                self.modules = self.modules + (six.text_type(appname),)
        self.print_info_("""Instance %s:
    path=%s
    appli=%s
    database=%s
    modules=%s
    secret_key=%s
""" % (self.name, self.instance_dir, self.appli_name, self.database, ",".join(self.modules), self.secret_key))
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
            file_py.write('import os, sys\n')
            file_py.write('if __name__ == "__main__":\n')
            file_py.write('    sys.path.append(os.path.dirname(__file__))\n')
            file_py.write('    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings")\n' % self.name)
            file_py.write('    from django.core.management import execute_from_command_line\n')
            file_py.write('    execute_from_command_line(sys.argv)\n')
        self.print_info_("Instance '%s' created." % self.name)  # pylint: disable=superfluous-parens
        self.refresh()

    def modif(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        self.write_setting_()
        self.print_info_("Instance '%s' modified." % self.name)  # pylint: disable=superfluous-parens
        self.refresh()

    def refresh(self):
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists!")
        self.read()
        self.print_info_("Instance '%s' refreshed." % self.name)  # pylint: disable=superfluous-parens
        from django.core.management import ManagementUtility
        migrate = ManagementUtility(['lucterios-admin', 'migrate', '--noinput', '--verbosity=1'])
        migrate.execute()

def list_method(from_class):
    import inspect
    res = []
    for item in inspect.getmembers(from_class):
        name = item[0]
        if (name[-1] != '_') and not name.startswith('set_') and (inspect.ismethod(item[1]) or inspect.isfunction(item[1])):
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
                      default="lucterios.standard",
                      help="Instance application",)
    parser.add_option("-d", "--database",
                      type='choice',
                      dest="database",
                      choices=['sqlite', 'MySQL', 'PostGreSQL', ],
                      default='sqlite',
                      help="Database configuration")
    parser.add_option("-m", "--module",
                      dest="module",
                      default="",
                      help="Modules to add (comma separator)",)
    parser.add_option("-e", "--extra",
                      dest="extra",
                      default="",
                      help="extra parameters (<name>=value,...)",)

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

if __name__ == '__main__':
    main()
