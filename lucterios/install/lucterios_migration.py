#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Migration tools to import old Lucterios backup

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

from os.path import join, isfile
from os import mkdir
import sys
import io
from time import time
from logging import getLogger
import sqlite3

from django.utils import six
from django.utils.module_loading import import_module

from lucterios.install.lucterios_admin import delete_path, LucteriosInstance, INSTANCE_PATH
from traceback import format_exc

MODULE_LINKS = [('data_CORE.sql', ('lucterios.CORE',)),
                ('data_org_lucterios_documents.sql', ('lucterios.documents',)),
                ('data_org_lucterios_contacts.sql',
                 ('lucterios.contacts', 'lucterios.mailing')),
                ('data_fr_sdlibre_compta.sql', ('diacamma.accounting',)),
                ('data_fr_sdlibre_facture.sql', ('diacamma.invoice',)),
                ('data_fr_sdlibre_membres.sql', ('diacamma.member',)),
                ('data_fr_sdlibre_copropriete.sql', ('diacamma.condominium',)),
                ('data_fr_sdlibre_FormationSport.sql', ('diacamma.event',))]


def dict_factory(cursor, row):
    dictdb = {}
    for idx, col in enumerate(cursor.description):
        dictdb[col[0]] = row[idx]
    return dictdb


class OldDataBase(object):

    def __init__(self, debug='', withlog=False):
        self.db_path = ""
        self.tmp_path = ""
        self.con = None
        self.debug = debug
        self.objectlinks = {}
        self.log_file = None
        self.withlog = withlog
        self.cursors = []

    def initial(self, instance_dir):
        self.db_path = join(instance_dir, 'old_database.sqlite3')
        self.tmp_path = join(instance_dir, 'tmp_resore')
        if self.withlog:
            self.log_file = join(instance_dir, 'last_migrate.log')
            delete_path(self.log_file)
        self.clear()
        mkdir(self.tmp_path)

    def is_exist(self):
        return isfile(self.db_path)

    def clear(self):
        self.close()
        if self.debug == '':
            delete_path(self.db_path)
            delete_path(self.tmp_path)

    def open(self, with_factory=False):
        if self.con is None:
            self.con = sqlite3.connect(self.db_path)
        if with_factory:
            self.con.row_factory = dict_factory
        else:

            self.con.row_factory = None
        new_cursor = self.con.cursor()
        self.cursors.append(new_cursor)
        return new_cursor

    def close(self):
        for old_cursor in self.cursors:
            try:
                old_cursor.close()
            except:
                pass
        self.cursors = []
        if self.con is not None:
            self.con.close()
        self.con = None

    def read_sqlfile(self, sql_file_path):
        import re
        import codecs
        rigth_insert_script = []
        create_script = []
        insert_script = []
        sql_file = join(self.tmp_path, sql_file_path)
        if isfile(sql_file):
            with codecs.open(sql_file, 'rb', encoding='ISO-8859-1') as sqlf:
                new_create_script = None
                new_insert_script = None
                for line in sqlf.readlines():
                    try:
                        line = line.strip()
                    except UnicodeEncodeError:
                        line = line.encode("ascii", 'replace').strip()
                    if new_insert_script is not None:
                        if line[-1:] == ";":
                            new_insert_script.append(six.text_type(line))
                            insert_script.append(
                                six.text_type("\n").join(new_insert_script))
                            if 'CORE_extension_rights' in six.text_type("\n").join(new_insert_script):
                                rigth_insert_script.append(new_insert_script)
                            new_insert_script = None
                        else:
                            new_insert_script.append(line)
                    if new_create_script is not None:
                        if line[:8] == ') ENGINE':
                            new_create_script.append(')')
                            new_script = " ".join(new_create_script)
                            if new_script[-3:] == ", )":
                                new_script = new_script[:-3] + ")"
                            create_script.append(new_script)
                            new_create_script = None
                        elif (line[:11] != 'PRIMARY KEY') and (line[:3] != 'KEY') and (line[:10] != 'UNIQUE KEY'):
                            line = re.sub(
                                r'int\([0-9]+\) unsigned', 'NUMERIC', line)
                            line = re.sub(
                                r'tinyint\([0-9]+\)', 'NUMERIC', line)
                            line = re.sub(r'int\([0-9]+\)', 'NUMERIC', line)
                            line = re.sub(r'varchar\([0-9]+\)', 'TEXT', line)
                            line = re.sub(r'longtext', 'TEXT', line)
                            line = re.sub(r'enum\(.*\)', 'TEXT', line)
                            line = re.sub(
                                r' AUTO_INCREMENT,', ' PRIMARY KEY,', line)
                            if (line.find('NOT NULL') != -1) and (line.find('DEFAULT') == -1):
                                line = re.sub(
                                    ' NOT NULL,', ' NOT NULL DEFAULT "",', line)
                            new_create_script.append(line)
                    elif line[:12] == 'CREATE TABLE':
                        new_create_script = []
                        new_create_script.append(line)
                    elif line[:11] == 'INSERT INTO':
                        if line[-1:] == ";":
                            insert_script.append(line)
                            if 'CORE_extension_rights' in line:
                                rigth_insert_script.append(line)
                        else:
                            new_insert_script = []
                            new_insert_script.append(line)
        return create_script, insert_script

    def importsql(self, sql_file_path):
        create_script, insert_script = self.read_sqlfile(sql_file_path)
        cur = self.open()
        try:
            for item_script in create_script:
                try:
                    cur.execute(item_script)
                except (sqlite3.IntegrityError, sqlite3.OperationalError):
                    six.print_('error: %s', item_script)
                    raise
            last_begin = ""
            for item_script in insert_script:
                try:
                    if last_begin != item_script[:70]:
                        self.con.commit()
                        last_begin = item_script[:70]
                    cur.execute(item_script)
                except (sqlite3.IntegrityError, sqlite3.OperationalError):
                    six.print_('error: %s', item_script)
                    raise
        finally:
            self.con.commit()
            self.close()


class MigrateAbstract(object):

    def __init__(self, old_db):
        self.old_db = old_db

    def print_debug(self, msg, arg):
        try:
            if isinstance(arg, tuple):
                getLogger("lucterios.migration").debug(msg, *arg)
            else:
                getLogger("lucterios.migration").debug(msg, arg)
        except UnicodeEncodeError:
            getLogger("lucterios.migration").debug(
                "*** UnicodeEncodeError ***")
            try:
                getLogger("lucterios.migration").debug(msg)
                getLogger("lucterios.migration").debug(six.text_type(arg))
            except UnicodeEncodeError:
                pass

    def print_info(self, msg, arg):
        if self.old_db.log_file is None:
            stdout = sys.stdout
        else:
            stdout = io.open(self.old_db.log_file, mode="a", encoding='utf-8')
        try:
            text = msg % arg
            six.print_(text, file=stdout)
        except UnicodeEncodeError:
            pass
        finally:
            if self.old_db.log_file is not None:
                stdout.close()

    def run(self):
        pass


class MigrateFromV1(LucteriosInstance, MigrateAbstract):

    def __init__(self, name, instance_path=INSTANCE_PATH, debug='', withlog=False):
        LucteriosInstance.__init__(self, name, instance_path)
        MigrateAbstract.__init__(self, OldDataBase(debug, withlog))
        self.read()
        self.debug = debug
        self.filename = ""

    def clear_current(self):
        self.clear()
        self.refresh()

    def extract_archive(self):
        import tarfile
        tar = tarfile.open(self.filename, 'r:gz')
        for item in tar:
            tar.extract(item, self.old_db.tmp_path)

    def run_module_migrate(self, module_name):
        from django.apps import apps
        module_names = module_name.split('.')
        try:
            current_mod = apps.get_app_config(module_names[-1])
            self.print_info("\n*** module '%s' ***", current_mod.verbose_name)
            appmodule = import_module(module_name + ".from_v1")
            class_name = "%sMigrate" % module_names[-1].lower()
            class_name = class_name[0].upper() + class_name[1:]
            migrate_class = getattr(appmodule, class_name)
            migrate_class(self.old_db).run()
        except (LookupError, ImportError, AttributeError):
            self.print_info("\n=> No module %s", module_name)
        except Exception as e:
            self.print_info(
                "\n#### Error '%s' ####\n%s", (six.text_type(e), format_exc()))
            raise

    def restore(self):
        begin_time = time()
        self.old_db.initial(join(self.instance_path, self.name))
        self.extract_archive()
        if not self.old_db.is_exist():
            for filename, modulenames in MODULE_LINKS:
                self.old_db.importsql(filename)
        self.clear_current()
        for filename, modulenames in MODULE_LINKS:
            if isfile(join(self.old_db.tmp_path, filename)):
                for modulename in modulenames:
                    self.run_module_migrate(modulename)
        self.old_db.clear()
        duration_sec = time() - begin_time
        duration_min = int(duration_sec / 60)
        duration_sec = duration_sec - duration_min * 60
        self.print_info(
            "Migration duration: %d min %d sec", (duration_min, duration_sec))
        return True


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog --name <instance name> --archive <archive file>",
                          version="%prog 0.1")
    parser.add_option("-n", "--name",
                      dest="name",
                      help="Instance to restore")
    parser.add_option("-a", "--archive",
                      dest="archive",
                      default="",
                      help="Archive to restore",)
    parser.add_option("-i", "--instance_path",
                      dest="instance_path",
                      default=INSTANCE_PATH,
                      help="Directory of instance storage",)
    parser.add_option("-d", "--debug",
                      dest="debug",
                      default="",
                      help="Debug option",)
    (options, _) = parser.parse_args()
    if options.name is None:
        parser.error('Name needed!')
    if not isfile(options.archive):
        parser.error('Archive "%s" no found!' % options.archive)
    mirg = MigrateFromV1(options.name, options.instance_path, options.debug)
    mirg.filename = options.archive
    mirg.restore()

if __name__ == '__main__':
    main()
