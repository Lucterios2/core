# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from shutil import rmtree
from os import mkdir, remove
from os.path import join, isdir, isfile
from optparse import OptionParser

INSTANCE_PATH = '.'

def write_setting(name, appli_name, database):
    setting_path = join(INSTANCE_PATH, name, 'settings.py')
    import random
    secret_key = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])
    with open(setting_path, "w") as file_py:
        file_py.write('#!/usr/bin/env python\n')
        file_py.write('# -*- coding: utf8 -*-\n')
        file_py.write('\n')
        file_py.write('# Initial constant\n')
        file_py.write('SECRET_KEY = "%s"\n' % secret_key)
        file_py.write('\n')
        file_py.write('# Database\n')
        file_py.write('import os\n')
        file_py.write('BASE_DIR = os.path.dirname(__file__)\n')
        file_py.write('DATABASES = {\n')
        file_py.write('     "default": {\n')
        if database == 'sqlite':
            file_py.write('         "ENGINE": "django.db.backends.sqlite3",\n')
            file_py.write('         "NAME": os.path.join(BASE_DIR, "db.sqlite3"),\n')
        else:
            raise Exception("Database not supported!")
        file_py.write('     }\n')
        file_py.write('}\n')
        file_py.write('\n')
        file_py.write('# configuration\n')
        file_py.write('from lucterios.framework.settings import fill_appli_settings\n')
        file_py.write('fill_appli_settings("%s", ()) \n' % appli_name)
        file_py.write('\n')

def del_lucterios_instance(name):
    instance_dir = join(INSTANCE_PATH, name)
    instance_conf = join(INSTANCE_PATH, "manage_%s.py" % name)
    if isdir(instance_dir):
        rmtree(instance_dir)
    if isfile(instance_conf):
        remove(instance_conf)
    print ("Instance '%s' deleted." % name) # pylint: disable=superfluous-parens

def add_lucterios_instance(name, appli_name, database):
    instance_dir = join(INSTANCE_PATH, name)
    instance_conf = join(INSTANCE_PATH, "manage_%s.py" % name)
    if isdir(instance_dir) or isfile(instance_conf):
        raise Exception("Instance exists yet!")
    with open(instance_conf, "w") as file_py:
        file_py.write('#!/usr/bin/env python\n')
        file_py.write('import os, sys\n')
        file_py.write('if __name__ == "__main__":\n')
        file_py.write('    sys.path.append(os.path.dirname(__file__))\n')
        file_py.write('    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings")\n' % name)
        file_py.write('    from django.core.management import execute_from_command_line\n')
        file_py.write('    execute_from_command_line(sys.argv)\n')
    mkdir(instance_dir)
    with open(join(instance_dir, '__init__.py'), "w") as file_py:
        file_py.write('\n')
    write_setting(name, appli_name, database)
    print ("Instance '%s' created." % name) # pylint: disable=superfluous-parens

def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 0.1")
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
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Only one arg")
    if args[0] == 'add':
        add_lucterios_instance(options.name, options.appli, options.database)
        return
    if args[0] == 'del':
        del_lucterios_instance(options.name)
        return

if __name__ == '__main__':
    main()
