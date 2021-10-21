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
import signal
from socket import socket, AF_INET, SOCK_STREAM
from os.path import isfile
from subprocess import Popen, PIPE, STDOUT, run
from time import sleep
from traceback import print_exc
from multiprocessing.context import Process
from threading import Thread
from re import compile
from json import dumps

from django.utils.translation import gettext
from django.utils.module_loading import import_module

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
                LucteriosMain.show_error_fct(gettext("Lucterios launcher"), e)
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
                    LucteriosMain.show_error_fct(gettext("Lucterios launcher"), e)
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

    @classmethod
    def get_serverfile_name(cls, instance_name):
        return "%s/server_pid" % instance_name

    def save_serverfile(self):
        with open(self.get_serverfile_name(self.instance_name), "w") as pid_file:
            pid_file.write('%d:%d' % (self.port, self.process.pid))

    def delete_serverfile(self):
        if isfile(self.get_serverfile_name(self.instance_name)):
            os.unlink(self.get_serverfile_name(self.instance_name))

    @classmethod
    def read_serverfile(cls, instance_name):
        port, pid = None, None
        if isfile(cls.get_serverfile_name(instance_name)):
            try:
                with open(cls.get_serverfile_name(instance_name), "r") as pid_file:
                    port, pid = pid_file.read().strip().split(':')
                port, pid = int(port), int(pid)
            except Exception:
                port, pid = None, None
        return port, pid

    def start(self):
        self.stop()
        current_env = os.environ.copy()
        current_env['DJANGO_SETTINGS_MODULE'] = '%s.settings' % self.instance_name
        cmd = [sys.executable, "-m", "waitress", "--port", str(self.port), "lucterios.framework.wsgi:application"]
        logging.getLogger(__name__).info("start instance : %s" % cmd)
        self.process = Popen(cmd, env=current_env)
        sleep(3.0)
        if self.process.poll() is not None:
            self.stop()
            raise RunException(gettext("Error to start!"))
        self.save_serverfile()

    def get_url(self):
        return "http://%(ip)s:%(port)d" % {'ip': self.lan_ip, 'port': self.port}

    def open_url(self):
        webbrowser.open_new("http://localhost:%(port)d" % {'port': self.port})

    def stop(self, remove_file=True):
        if self.is_running():
            self.process.terminate()
        self.process = None
        self.out = None
        if remove_file:
            self.delete_serverfile()

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
        self.mode_values = [str(gettext("CORE-connectmode.0")), str(gettext("CORE-connectmode.1")), str(gettext("CORE-connectmode.2"))]
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


class LucteriosChecker(Thread):

    HOST = '127.0.0.1'
    PORT = 9901

    def __init__(self):
        Thread.__init__(self)
        self.open_function = None
        self.startedlist_function = None

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _tb):
        self.stop()

    def run(self):
        try:
            while self.loop:
                conn, _addr = self.current_socket.accept()
                with conn:
                    while self.loop:
                        binary_data = conn.recv(1024)
                        if not binary_data:
                            break
                        if binary_data == b'OPEN':
                            if self.open_function is not None:
                                self.open_function()
                        if self.startedlist_function is not None:
                            result = dumps(self.startedlist_function()).encode()
                        else:
                            result = b'OK'
                        conn.sendall(result)
        finally:
            self.stop()

    def stop(self):
        self.loop = False
        self.current_socket.close()

    def send_message(self):
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect((self.HOST, self.PORT))
            client_socket.sendall(b'OPEN')
            result = client_socket.recv(1024)
            if isinstance(result, bytes):
                return result.decode()

    def execute(self):
        try:
            self.current_socket = socket(AF_INET, SOCK_STREAM)
            self.current_socket.bind((self.HOST, self.PORT))
            self.current_socket.listen()
            self.loop = True
            self.start()
            return True
        except OSError:
            print("Exist yet, open windows")
            print(self.send_message())
            return False


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
            self.run_all_needed()
            self.run_after(1000, lambda: Thread(target=self.check).start())
        finally:
            self.remove_splash_screen()

    def is_all_stop(self):
        all_stop = True
        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if (self.running_instance[old_item] is not None) and self.running_instance[old_item].is_running():
                all_stop = False
        return all_stop

    def run_all_needed(self):
        luct_glo = LucteriosGlobal()
        for instance_name in luct_glo.listing():
            if instance_name not in self.running_instance.keys():
                self.running_instance[instance_name] = None
            port, pid = RunServer.read_serverfile(instance_name)
            if pid is not None:
                try:
                    os.kill(pid, signal.SIGTERM)
                except (ProcessLookupError, OSError):
                    pass
            if port is not None:
                self.open_inst(instance_name, port)

    def stop_all(self):
        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if self.running_instance[old_item] is not None:
                self.running_instance[old_item].stop(remove_file=False)
                del self.running_instance[old_item]

    def started_list(self):
        result = {}
        for instance_name, instance_item in self.running_instance.items():
            if instance_item is not None:
                result[instance_name] = instance_item.get_url()
        return result

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
            msg = gettext("Upgrade needs")
        else:
            msg = gettext("No upgrade")
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
    def open_inst(self, instance_name=None, port=None):
        global FIRST_HTTP_PORT
        instance_name = self.get_selected_instance_name() if instance_name is None else instance_name
        if (instance_name != '') and (instance_name is not None):
            try:
                if instance_name not in self.running_instance.keys():
                    self.running_instance[instance_name] = None
                if self.running_instance[instance_name] is None:
                    if port is None:
                        port = FIRST_HTTP_PORT
                        for inst_obj in self.running_instance.values():
                            if (inst_obj is not None) and (inst_obj.port >= port):
                                port = inst_obj.port + 1
                    self.running_instance[instance_name] = RunServer(instance_name, port)
                    self.running_instance[instance_name].start()
                else:
                    self.running_instance[instance_name].stop(remove_file=True)
                    self.running_instance[instance_name] = None
            except RunException:
                FIRST_HTTP_PORT += 10
                raise
            finally:
                self.refresh(instance_name)

    @ThreadRun
    def open_browser(self):
        instance_name = self.get_selected_instance_name()
        if (instance_name != '') and (instance_name is not None) and (instance_name in self.running_instance.keys()) and (self.running_instance[instance_name] is not None):
            self.running_instance[instance_name].open_url()

    def stop_current_instance(self, instance_name):
        if (instance_name != '') and (self.running_instance[instance_name] is not None) and self.running_instance[instance_name].is_running():
            self.running_instance[instance_name].stop(remove_file=True)
            self.running_instance[instance_name] = None

    @ThreadRun
    def save_instance(self, instance_name, file_name):
        self.stop_current_instance(instance_name)
        if not file_name.endswith('.lbk'):
            file_name += '.lbk'
        proc_res = run([sys.executable, '-m', 'lucterios.install.lucterios_admin', 'archive', '-n', instance_name, '-f', file_name], stdout=PIPE, stderr=STDOUT, env=os.environ.copy())
        if proc_res.returncode == 0:
            self.show_info(gettext("Lucterios launcher"), gettext("Instance saved to %s") % file_name)
        else:
            self.show_error(gettext("Lucterios launcher"), gettext("Instance not saved!"))
            logging.getLogger(__name__).error(proc_res.stdout.decode())
        self.refresh(instance_name)

    @ThreadRun
    def restore_instance(self, instance_name, file_name):
        self.stop_current_instance(instance_name)
        proc_res = run([sys.executable, '-m', 'lucterios.install.lucterios_admin', 'restore', '-n', instance_name, '-f', file_name], stdout=PIPE, stderr=STDOUT, env=os.environ.copy())
        if proc_res.returncode == 0:
            self.show_info(gettext("Lucterios launcher"), gettext("Instance restore from %s") % file_name)
        else:
            self.show_error(gettext("Lucterios launcher"), gettext("Instance not restored!"))
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
