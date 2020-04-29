#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
GUI tool to manage Lucterios instance

@author: Laurent GAY
@organization: sd-libre.fr
@contact: instance@sd-libre.fr
@copyright: 2019 sd-libre.fr
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

import sys
import webbrowser
import logging
import os
from subprocess import Popen, PIPE, STDOUT, run
from time import sleep
from traceback import print_exc
from multiprocessing.context import Process
from threading import Thread
from re import compile

from django.utils.translation import ugettext
from django.utils.module_loading import import_module
from django.utils import six

from lucterios.framework.settings import get_lan_ip
from lucterios.install.lucterios_admin import LucteriosGlobal, LucteriosInstance, get_module_title


FIRST_HTTP_PORT = 8100
if 'FIRST_HTTP_PORT' in os.environ.keys():
    FIRST_HTTP_PORT = os.environ['FIRST_HTTP_PORT']


class RunException(Exception):
    pass


def ProvideException(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as e:
            print_exc()
            if LucteriosMain.show_error_fct is not None:
                LucteriosMain.show_error_fct(ugettext("Lucterios launcher"), e)
    return wrapper


def ThreadRun(func):
    def wrapper(*args):
        def sub_fct():
            args[0].enabled(False)
            try:
                return func(*args)
            except Exception as e:
                print_exc()
                if LucteriosMain.show_error_fct is not None:
                    LucteriosMain.show_error_fct(ugettext("Lucterios launcher"), e)
            finally:
                args[0].enabled(True)
        Thread(target=sub_fct).start()
    return wrapper


class RunServer(object):

    def __init__(self, instance_name, port):
        self.instance_name = instance_name
        self.port = port
        self.lan_ip = get_lan_ip()
        self.process = None
        self.out = None

    def start(self):
        self.stop()
        cmd = [sys.executable, 'manage_%s.py' % self.instance_name,
               'runserver', '--nostatic', '--noreload', '--traceback', '0.0.0.0:%d' % self.port]
        self.process = Popen(cmd)
        sleep(3.0)
        if self.process.poll() is not None:
            self.stop()
            raise RunException(ugettext("Error to start!"))
        self.open_url()

    def open_url(self):
        webbrowser.open_new("http://%(ip)s:%(port)d" % {'ip': self.lan_ip, 'port': self.port})

    def stop(self):
        if self.is_running():
            self.process.terminate()
        self.process = None
        self.out = None

    def is_running(self):
        return (self.process is not None) and (self.process.poll() is None)


def LucteriosRefreshAll():
    try:
        luct_glo = LucteriosGlobal()
        luct_glo.refreshall()
    except Exception:
        logging.getLogger(__name__).exception("refreshall")


class EditorInstance(object):

    def __init__(self):
        self.name_rull = compile(r"[a-z0-9_\-]+")
        self.is_new_instance = True

    def _define_values(self):
        from lucterios.framework.settings import DEFAULT_LANGUAGES
        self.mode_values = [six.text_type(ugettext("CORE-connectmode.0")), six.text_type(ugettext("CORE-connectmode.1")), six.text_type(ugettext("CORE-connectmode.2"))]
        self.lang_values = [lang[1] for lang in DEFAULT_LANGUAGES]
        self.dbtype_values = ["SQLite", "MySQL", "PostgreSQL"]
        lct_glob = LucteriosGlobal()
        _, self.mod_applis, mod_modules = lct_glob.installed()
        self.current_inst_names = lct_glob.listing()
        self.mod_applis.sort(key=lambda item: get_module_title(item[0]))
        self.module_list = []
        for mod_module_item in mod_modules:
            self.module_list.append((get_module_title(mod_module_item[0]), mod_module_item[0]))
        self.module_list.sort(key=lambda module: module[0])
        self.appli_list = []
        for mod_appli_item in self.mod_applis:
            self.appli_list.append(get_module_title(mod_appli_item[0]))

    def _get_instance_elements(self, instance_name):
        from lucterios.framework.settings import get_locale_lang
        lct_inst = LucteriosInstance(instance_name)
        lct_inst.read()
        applis_id = 0
        for appli_iter in range(len(self.mod_applis)):
            if self.mod_applis[appli_iter][0] == lct_inst.appli_name:
                applis_id = appli_iter
                break
        if lct_inst.extra['']['mode'] is not None:
            mode_id = lct_inst.extra['']['mode'][0]
        else:
            mode_id = 2
        typedb_index = 0
        for typedb_idx in range(len(self.dbtype_values)):
            if self.dbtype_values[typedb_idx].lower() == lct_inst.database[0].lower():
                typedb_index = typedb_idx
                break
        current_lang = get_locale_lang()
        if 'LANGUAGE_CODE' in lct_inst.extra.keys():
            current_lang = lct_inst.extra['LANGUAGE_CODE']
        return lct_inst, applis_id, mode_id, typedb_index, current_lang


class LucteriosMain(object):

    show_error_fct = None

    def __init__(self):
        self.running_instance = {}
        LucteriosMain.show_error_fct = self.show_error

    def start_up_app(self):
        self.show_splash_screen()
        try:
            # load db in separate process
            process_startup = Process(target=LucteriosRefreshAll)
            process_startup.start()

            while process_startup.is_alive():
                # print('updating')
                self.splash.update()
        finally:
            self.remove_splash_screen()

    def is_all_stop(self):
        all_stop = True
        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if (self.running_instance[old_item] is not None) and self.running_instance[old_item].is_running():
                all_stop = False
        return all_stop

    def stop_all(self):
        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if self.running_instance[old_item] is not None:
                self.running_instance[old_item].stop()
                del self.running_instance[old_item]

    @classmethod
    def show_info(self, text, message):
        pass

    @classmethod
    def show_error(self, text, message):
        pass

    def show_splash_screen(self):
        pass

    def remove_splash_screen(self):
        pass

    def enabled(self, is_enabled, widget=None):
        pass

    def run_after(self, ms, func=None, *args):
        pass

    def get_selected_instance_name(self):
        return ""

    @ThreadRun
    def upgrade(self, *_args):
        from logging import getLogger
        admin_path = import_module("lucterios.install.lucterios_admin").__file__
        proc = Popen([sys.executable, admin_path, "update"], stderr=STDOUT, stdout=PIPE)
        value = proc.communicate()[0]
        try:
            value = value.decode('ascii')
        except Exception:
            pass
        print(value)
        if proc.returncode != 0:
            getLogger("lucterios.admin").error(value)
        else:
            getLogger("lucterios.admin").info(value)
        self.set_ugrade_state(2)

    def ugrade_message(self, must_upgrade):
        if must_upgrade:
            msg = ugettext("Upgrade needs")
        else:
            msg = ugettext("No upgrade")
        return msg

    def set_ugrade_state(self, upgrade_mode):
        pass

    def check(self):
        must_upgrade = False
        try:
            lct_glob = LucteriosGlobal()
            _, must_upgrade = lct_glob.check()
        finally:
            self.run_after(300, self.set_ugrade_state, 1 if must_upgrade else 0)

    @ThreadRun
    def add_modif_inst_result(self, result, to_create):
        inst = LucteriosInstance(result[0])
        inst.set_extra("LANGUAGE_CODE=%s" % result[5])
        inst.set_appli(result[1])
        inst.set_module(result[2])
        inst.set_database(result[4])
        if to_create:
            inst.add()
        else:
            inst.modif()
        inst = LucteriosInstance(result[0])
        inst.set_extra(result[3])
        inst.security()
        self.refresh(result[0])

    @ThreadRun
    def delete_inst_name(self, instance_name):
        inst = LucteriosInstance(instance_name)
        inst.delete()
        self.refresh()

    @ThreadRun
    def open_inst(self):
        global FIRST_HTTP_PORT
        instance_name = self.get_selected_instance_name()
        if (instance_name != '') and (instance_name is not None):
            try:
                if instance_name not in self.running_instance.keys():
                    self.running_instance[instance_name] = None
                if self.running_instance[instance_name] is None:
                    port = FIRST_HTTP_PORT
                    for inst_obj in self.running_instance.values():
                        if (inst_obj is not None) and (inst_obj.port >= port):
                            port = inst_obj.port + 1
                    self.running_instance[instance_name] = RunServer(instance_name, port)
                    self.running_instance[instance_name].start()
                else:
                    self.running_instance[instance_name].stop()
                    self.running_instance[instance_name] = None
            except RunException:
                FIRST_HTTP_PORT += 10
                raise
            finally:
                self.refresh(instance_name)

    def stop_current_instance(self, instance_name):
        if (instance_name != '') and (self.running_instance[instance_name] is not None) and self.running_instance[instance_name].is_running():
            self.running_instance[instance_name].stop()
            self.running_instance[instance_name] = None

    @ThreadRun
    def save_instance(self, instance_name, file_name):
        self.stop_current_instance(instance_name)
        if not file_name.endswith('.lbk'):
            file_name += '.lbk'
        proc_res = run([sys.executable, '-m', 'lucterios.install.lucterios_admin', 'archive', '-n', instance_name, '-f', file_name], stdout=PIPE, stderr=STDOUT, env=os.environ.copy())
        if proc_res.returncode == 0:
            self.show_info(ugettext("Lucterios launcher"), ugettext("Instance saved to %s") % file_name)
        else:
            self.show_error(ugettext("Lucterios launcher"), ugettext("Instance not saved!"))
            logging.getLogger(__name__).error(proc_res.stdout.decode())
        self.refresh(instance_name)

    @ThreadRun
    def restore_instance(self, instance_name, file_name):
        self.stop_current_instance(instance_name)
        proc_res = run([sys.executable, '-m', 'lucterios.install.lucterios_admin', 'restore', '-n', instance_name, '-f', file_name], stdout=PIPE, stderr=STDOUT, env=os.environ.copy())
        if proc_res.returncode == 0:
            self.show_info(ugettext("Lucterios launcher"), ugettext("Instance restore from %s") % file_name)
        else:
            self.show_error(ugettext("Lucterios launcher"), ugettext("Instance not restored!"))
            logging.getLogger(__name__).error(proc_res.stdout.decode())
        self.refresh(instance_name)

    def modify_inst(self):
        pass

    def delete_inst(self):
        pass

    def save_inst(self):
        pass

    def restore_inst(self):
        pass

    def add_inst(self):
        pass
