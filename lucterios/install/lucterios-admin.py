# -*- coding: utf-8 -*-
#!/usr/bin/env python
# pylint: disable=invalid-name
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from shutil import rmtree
from os import mkdir, remove
from os.path import join, isdir, isfile, abspath
from optparse import OptionParser
from django.utils import six

INSTANCE_PATH = '.'

class AdminException(Exception):
    pass

class LucteriosInstance(object):

    def __init__(self, name):
        import random
        self.secret_key = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])
        self.msg_list = []
        self.name = name
        self.instance_dir = join(abspath(INSTANCE_PATH), self.name)
        self.setting_path = join(self.instance_dir, 'settings.py')
        self.instance_conf = join(abspath(INSTANCE_PATH), "manage_%s.py" % name)
        self.appli_name = ''
        self.database = ''

        self.modules = ()

    def set_database(self, database):
        self.database = database

    def set_module(self, module):
        if module != '':
            self.modules = tuple(module.split(','))
        else:
            self.modules = ()

    def print_info(self, msg):
        self.msg_list.append(msg)

    def show_info(self):
        six.print_("\n".join(self.msg_list))

    def listing(self):
        import re, os
        list_res = []
        for manage_file in os.listdir(abspath(INSTANCE_PATH)):
            val = re.match(r"manage_([a-zA-Z0-9_]+)\.py", manage_file)
            if val is not None and isdir(join(abspath(INSTANCE_PATH), val.group(1))):
                list_res.append(val.group(1))
        self.print_info("Instance listing: %s" % ",".join(list_res))
        return list_res

    def write_setting(self):
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
            file_py.write('# configuration\n')
            file_py.write('from lucterios.framework.settings import fill_appli_settings\n')
            file_py.write('fill_appli_settings("%s", %s) \n' % (self.appli_name, six.text_type(self.modules)))
            file_py.write('\n')

    def delete(self):
        if isdir(self.instance_dir):
            rmtree(self.instance_dir)
        if isfile(self.instance_conf):
            remove(self.instance_conf)
        self.print_info("Instance '%s' deleted." % self.name)  # pylint: disable=superfluous-parens

    def read(self):
        import sys, os
        from django import setup
        if self.name == '':
            raise AdminException("Instance not precise!")
        if not isdir(self.instance_dir) or not isfile(self.instance_conf):
            raise AdminException("Instance not exists !")
        sys.path.insert(0, abspath(INSTANCE_PATH))
        os.environ["DJANGO_SETTINGS_MODULE"] = "%s.settings" % self.name
        setup()
        from django.conf import settings
        self.secret_key = settings.SECRET_KEY
        self.database = settings.DATABASES['default']['ENGINE']
        if "sqlite3" in self.database:
            self.database = 'sqlite'
        self.appli_name = settings.APPLIS_MODULE.__name__
        self.modules = ()
        for appname in settings.INSTALLED_APPS:
            if (not "django" in appname) and (appname != 'lucterios.framework') and (appname != 'lucterios.CORE') and (self.appli_name != appname):

                self.modules = self.modules + (six.text_type(appname),)

        self.print_info("""Instance %s:
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
        with open(self.instance_conf, "w") as file_py:
            file_py.write('#!/usr/bin/env python\n')
            file_py.write('import os, sys\n')
            file_py.write('if __name__ == "__main__":\n')
            file_py.write('    sys.path.append(os.path.dirname(__file__))\n')
            file_py.write('    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings")\n' % self.name)
            file_py.write('    from django.core.management import execute_from_command_line\n')
            file_py.write('    execute_from_command_line(sys.argv)\n')
        mkdir(self.instance_dir)
        with open(join(self.instance_dir, '__init__.py'), "w") as file_py:
            file_py.write('\n')
        self.write_setting()
        self.print_info("Instance '%s' created." % self.name)  # pylint: disable=superfluous-parens
        self.read()
        from django.core.management import ManagementUtility
        migrate = ManagementUtility(['lucterios-admin', 'migrate', '--noinput', '--verbosity=1'])
        migrate.execute()

def main():
    import lucterios.CORE
    parser = OptionParser(usage="usage: %prog <listing|add|read|del> [option]",
                          version="%prog " + lucterios.CORE.__version__)
    parser.add_option("-n", "--name",
                      dest="name",
                      default='',
                      help="Add new instance")
    parser.add_option("-p", "--appli",
                      dest="appli",
                      default="lucterios.standard",
                      help="Application to install",)
    parser.add_option("-d", "--database",
                      type='choice',
                      dest="database",
                      choices=['sqlite', 'MySQL', 'ProstGreSQL', ],
                      default='sqlite',
                      help="Database configuration")
    parser.add_option("-m", "--module",
                      dest="module",
                      default="",
                      help="Modules to add (comma separator)",)
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Bad arguments!")
    instance = None
    try:
        if args[0] == 'listing':
            instance = LucteriosInstance('')
            instance.listing()
            instance.show_info()
            return
        if args[0] == 'read':
            instance = LucteriosInstance(options.name)
            instance.read()
            instance.show_info()
            return
        if args[0] == 'add':
            instance = LucteriosInstance(options.name)
            instance.appli_name = options.appli
            instance.set_database(options.database)
            instance.set_module(options.module)
            instance.add()
            instance.show_info()
            return
        if args[0] == 'del':
            instance = LucteriosInstance(options.name)
            instance.delete()
            instance.show_info()
            return
    except AdminException as error:
        parser.error(six.text_type(error))
    else:
        if instance is not None:
            instance.show_info()
        raise

if __name__ == '__main__':
    main()
