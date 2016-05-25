#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
GUI tool to manage Lucterios instance

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

import sys
import os
import webbrowser
from subprocess import Popen, PIPE, STDOUT
from time import sleep
from traceback import print_exc
from threading import Thread

from django.utils.module_loading import import_module
from django.utils.translation import ugettext
from django.utils import six

from lucterios.install.lucterios_admin import LucteriosGlobal, LucteriosInstance, get_module_title,\
    setup_from_none
from lucterios.install.lucterios_migration import MigrateFromV1
from lucterios.framework.settings import get_lan_ip
from os.path import join, dirname

FIRST_HTTP_PORT = 8100
if 'FIRST_HTTP_PORT' in os.environ.keys():
    FIRST_HTTP_PORT = os.environ['FIRST_HTTP_PORT']

READLONY = 'readonly'
VALUES = 'values'

try:
    from tkinter import Toplevel, Tk, ttk, Label, Entry, Frame, Button, Listbox, Text, StringVar
    from tkinter import E, W, N, S, END, NORMAL, DISABLED, EXTENDED
    from tkinter.messagebox import showerror, showinfo, askokcancel
    from tkinter.filedialog import asksaveasfilename, askopenfilename
    from tkinter import Image
except ImportError:
    from Tkinter import Image
    from Tkinter import Toplevel, Tk, Label, Entry, Frame, Button, Listbox, Text, StringVar
    from Tkinter import E, W, N, S, END, NORMAL, DISABLED, EXTENDED
    from tkMessageBox import showerror, showinfo, askokcancel
    from tkFileDialog import asksaveasfilename, askopenfilename
    import ttk


class RunException(Exception):
    pass


def ProvideException(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception as e:
            print_exc()
            showerror(ugettext("Lucterios installer"), e)
    return wrapper


def ThreadRun(func):
    def wrapper(*args):
        @ProvideException
        def sub_fct():
            args[0].enabled(False)
            try:
                return func(*args)
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
               'runserver', '--noreload', '--traceback', '0.0.0.0:%d' % self.port]
        self.process = Popen(cmd)
        sleep(3.0)
        if self.process.poll() is not None:
            self.stop()
            raise RunException(ugettext("Error to start!"))
        self.open_url()

    def open_url(self):
        webbrowser.open_new("http://%(ip)s:%(port)d" %
                            {'ip': self.lan_ip, 'port': self.port})

    def stop(self):
        if self.is_running():
            self.process.terminate()
        self.process = None
        self.out = None

    def is_running(self):
        return (self.process is not None) and (self.process.poll() is None)


def center(root, size=None):
    root.update_idletasks()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    if size is None:
        size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
    pos_x = int(width / 2 - size[0] / 2)
    pos_y = int(height / 2 - size[1] / 2)
    root.geometry("%dx%d+%d+%d" % (size + (pos_x, pos_y)))


class InstanceEditor(Toplevel):

    def __init__(self):
        Toplevel.__init__(self)
        self.focus_set()
        self.grab_set()

        self.result = None
        self.module_data = None
        self.mod_applis = None
        self.title(ugettext("Instance editor"))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.ntbk = ttk.Notebook(self)
        self.ntbk.grid(row=0, column=0, columnspan=1, sticky=(N, S, E, W))

        self.frm_general = Frame(self.ntbk, width=350, height=150)
        self.frm_general.grid_columnconfigure(0, weight=0)
        self.frm_general.grid_columnconfigure(1, weight=1)
        self._general_tabs()
        self.ntbk.add(self.frm_general, text=ugettext('General'))

        self.frm_database = Frame(self.ntbk, width=350, height=150)
        self.frm_database.grid_columnconfigure(0, weight=0)
        self.frm_database.grid_columnconfigure(1, weight=1)
        self._database_tabs()
        self.ntbk.add(self.frm_database, text=ugettext('Database'))

        btnframe = Frame(self, bd=1)
        btnframe.grid(row=1, column=0, columnspan=1)
        Button(btnframe, text=ugettext("OK"), width=10, command=self.apply).grid(
            row=0, column=0, sticky=(N, S, E))
        Button(btnframe, text=ugettext("Cancel"), width=10, command=self.destroy).grid(
            row=0, column=1, sticky=(N, S, W))

    def _database_tabs(self):
        Label(self.frm_database, text=ugettext("Type")).grid(
            row=0, column=0, sticky=(N, W), padx=5, pady=3)
        self.typedb = ttk.Combobox(
            self.frm_database, textvariable=StringVar(), state=READLONY)
        self.typedb.bind("<<ComboboxSelected>>", self.typedb_selection)
        self.typedb.grid(row=0, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_database, text=ugettext("Name")).grid(
            row=1, column=0, sticky=(N, W), padx=5, pady=3)
        self.namedb = Entry(self.frm_database)
        self.namedb.grid(row=1, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_database, text=ugettext("User")).grid(
            row=2, column=0, sticky=(N, W), padx=5, pady=3)
        self.userdb = Entry(self.frm_database)
        self.userdb.grid(row=2, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_database, text=ugettext("Password")).grid(
            row=3, column=0, sticky=(N, W), padx=5, pady=3)
        self.pwddb = Entry(self.frm_database)
        self.pwddb.grid(row=3, column=1, sticky=(N, S, E, W), padx=5, pady=3)

    def _general_tabs(self):
        Label(self.frm_general, text=ugettext("Name")).grid(
            row=0, column=0, sticky=(N, W), padx=5, pady=3)
        self.name = Entry(self.frm_general)
        self.name.grid(row=0, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=ugettext("Appli")).grid(
            row=1, column=0, sticky=(N, W), padx=5, pady=3)
        self.applis = ttk.Combobox(
            self.frm_general, textvariable=StringVar(), state=READLONY)
        self.applis.bind("<<ComboboxSelected>>", self.appli_selection)
        self.applis.grid(row=1, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=ugettext("Modules")).grid(
            row=2, column=0, sticky=(N, W), padx=5, pady=3)
        self.modules = Listbox(self.frm_general, selectmode=EXTENDED)
        self.modules.configure(exportselection=False)
        self.modules.grid(row=2, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=ugettext("Language")).grid(
            row=3, column=0, sticky=(N, W), padx=5, pady=3)
        self.language = ttk.Combobox(
            self.frm_general, textvariable=StringVar(), state=READLONY)
        self.language.grid(
            row=3, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=ugettext("CORE-connectmode")
              ).grid(row=4, column=0, sticky=(N, W), padx=5, pady=3)
        self.mode = ttk.Combobox(
            self.frm_general, textvariable=StringVar(), state=READLONY)
        self.mode.bind("<<ComboboxSelected>>", self.mode_selection)
        self.mode.grid(row=4, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=ugettext("Password")).grid(
            row=5, column=0, sticky=(N, W), padx=5, pady=3)
        self.password = Entry(self.frm_general, show="*")
        self.password.grid(
            row=5, column=1, sticky=(N, S, E, W), padx=5, pady=3)

    def typedb_selection(self, event):

        visible = list(self.typedb[VALUES]).index(self.typedb.get()) != 0
        for child_cmp in self.frm_database.winfo_children()[2:]:
            if visible:
                child_cmp.config(state=NORMAL)
            else:
                child_cmp.config(state=DISABLED)

    def appli_selection(self, event):
        if self.applis.get() != '':
            appli_id = list(self.applis[VALUES]).index(self.applis.get())
            luct_glo = LucteriosGlobal()
            current_inst_names = luct_glo.listing()
            appli_root_name = self.mod_applis[appli_id][0].split('.')[-1]
            default_name_idx = 1
            while appli_root_name + six.text_type(default_name_idx) in current_inst_names:
                default_name_idx += 1
            self.name.delete(0, END)
            self.name.insert(
                0, appli_root_name + six.text_type(default_name_idx))
            mod_depended = self.mod_applis[appli_id][2]
            self.modules.select_clear(0, self.modules.size())
            for mod_idx in range(len(self.module_data)):
                current_mod = self.module_data[mod_idx]
                if current_mod in mod_depended:
                    self.modules.selection_set(mod_idx)

    def mode_selection(self, event):
        visible = list(self.mode[VALUES]).index(self.mode.get()) != 2
        for child_cmp in self.frm_general.winfo_children()[-2:]:
            if visible:
                child_cmp.config(state=NORMAL)
            else:
                child_cmp.config(state=DISABLED)

    def apply(self):
        from lucterios.framework.settings import DEFAULT_LANGUAGES, get_locale_lang
        if self.name.get() == '':
            showerror(ugettext("Instance editor"), ugettext("Name empty!"))
            return
        if self.applis.get() == '':
            showerror(ugettext("Instance editor"), ugettext("No application!"))
            return
        db_param = "%s:name=%s,user=%s,password=%s" % (
            self.typedb.get(), self.namedb.get(), self.userdb.get(), self.pwddb.get())
        security = "MODE=%s" % list(
            self.mode[VALUES]).index(self.mode.get())
        if self.password.get() != '':
            security += ",PASSWORD=%s" % self.password.get()
        module_list = [
            self.module_data[int(item)] for item in self.modules.curselection()]
        appli_id = list(self.applis[VALUES]).index(self.applis.get())
        current_lang = get_locale_lang()
        for lang in DEFAULT_LANGUAGES:
            if lang[1] == self.language.get():
                current_lang = lang[0]
        self.result = (self.name.get(), self.mod_applis[appli_id][
                       0], ",".join(module_list), security, db_param, current_lang)
        self.destroy()

    def _load_current_data(self, instance_name):
        from lucterios.framework.settings import DEFAULT_LANGUAGES, get_locale_lang
        lct_inst = LucteriosInstance(instance_name)
        lct_inst.read()
        self.name.delete(0, END)
        self.name.insert(0, lct_inst.name)
        self.name.config(state=DISABLED)
        applis_id = 0
        for appli_iter in range(len(self.mod_applis)):
            if self.mod_applis[appli_iter][0] == lct_inst.appli_name:
                applis_id = appli_iter
                break
        self.applis.current(applis_id)
        if lct_inst.extra['']['mode'] is not None:
            self.mode.current(lct_inst.extra['']['mode'][0])
        else:
            self.mode.current(2)
        self.mode_selection(None)
        typedb_index = 0
        for typedb_idx in range(len(self.typedb[VALUES])):
            if self.typedb[VALUES][typedb_idx].lower() == lct_inst.database[0].lower():
                typedb_index = typedb_idx
                break
        self.typedb.current(typedb_index)
        self.typedb.config(state=DISABLED)
        self.typedb_selection(None)
        self.namedb.delete(0, END)
        if 'name' in lct_inst.database[1].keys():
            self.namedb.insert(0, lct_inst.database[1]['name'])
        self.userdb.delete(0, END)
        if 'user' in lct_inst.database[1].keys():
            self.userdb.insert(0, lct_inst.database[1]['user'])
        self.pwddb.delete(0, END)
        if 'password' in lct_inst.database[1].keys():
            self.pwddb.insert(0, lct_inst.database[1]['password'])
        self.modules.select_clear(0, self.modules.size())
        for mod_idx in range(len(self.module_data)):
            current_mod = self.module_data[mod_idx]
            if current_mod in lct_inst.modules:
                self.modules.select_set(mod_idx)
        current_lang = get_locale_lang()
        if 'LANGUAGE_CODE' in lct_inst.extra.keys():
            current_lang = lct_inst.extra['LANGUAGE_CODE']
        for lang in DEFAULT_LANGUAGES:
            if lang[0] == current_lang:
                self.language.current(self.language[VALUES].index(lang[1]))

    def execute(self, instance_name=None):
        from lucterios.framework.settings import DEFAULT_LANGUAGES, get_locale_lang
        self.mode[VALUES] = [ugettext(
            "CORE-connectmode.0"), ugettext("CORE-connectmode.1"), ugettext("CORE-connectmode.2")]
        self.language[VALUES] = [lang[1] for lang in DEFAULT_LANGUAGES]
        self.typedb[VALUES] = ["SQLite", "MySQL", "PostgreSQL"]
        lct_glob = LucteriosGlobal()
        _, self.mod_applis, mod_modules = lct_glob.installed()
        self.mod_applis.sort(key=lambda item: get_module_title(item[0]))
        self.modules.delete(0, END)
        self.module_data = []
        module_list = []
        for mod_module_item in mod_modules:
            module_list.append(
                (get_module_title(mod_module_item[0]), mod_module_item[0]))
        module_list.sort(key=lambda module: module[0])
        for module_title, module_name in module_list:
            self.modules.insert(END, module_title)
            self.module_data.append(module_name)
        appli_list = []
        for mod_appli_item in self.mod_applis:
            appli_list.append(get_module_title(mod_appli_item[0]))
        self.applis[VALUES] = appli_list
        if instance_name is not None:
            self._load_current_data(instance_name)
        else:
            self.typedb.current(0)
            self.mode.current(2)
            if len(appli_list) > 0:
                self.applis.current(0)
            self.appli_selection(None)
            self.mode_selection(None)
            self.typedb_selection(None)
            for lang in DEFAULT_LANGUAGES:
                if lang[0] == get_locale_lang():
                    self.language.current(self.language[VALUES].index(lang[1]))
        center(self)


class LucteriosMainForm(Tk):

    def __init__(self):
        Tk.__init__(self)
        try:
            img = Image("photo", file=join(
                dirname(import_module('lucterios.install').__file__), "lucterios.png"))
            self.tk.call('wm', 'iconphoto', self._w, img)
        except:
            pass
        self.has_checked = False
        self.title(ugettext("Lucterios installer"))
        self.minsize(475, 260)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.running_instance = {}
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.ntbk = ttk.Notebook(self)
        self.ntbk.grid(row=0, column=0, columnspan=1, sticky=(N, S, E, W))

        self.create_instance_panel()
        self.create_module_panel()

        stl = ttk.Style()
        stl.theme_use("default")
        stl.configure("TProgressbar", thickness=5)
        self.progress = ttk.Progressbar(
            self, style="TProgressbar", orient='horizontal', mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(E, W))

        self.btnframe = Frame(self, bd=1)
        self.btnframe.grid(row=2, column=0, columnspan=1)
        Button(self.btnframe, text=ugettext("Refresh"), width=20, command=self.refresh).grid(
            row=0, column=0, padx=3, pady=3, sticky=(N, S))
        self.btnupgrade = Button(
            self.btnframe, text=ugettext("Search upgrade"), width=20, command=self.upgrade)
        self.btnupgrade.config(state=DISABLED)
        self.btnupgrade.grid(row=0, column=1, padx=3, pady=3, sticky=(N, S))
        Button(self.btnframe, text=ugettext("Close"), width=20, command=self.on_closing).grid(
            row=0, column=2, padx=3, pady=3, sticky=(N, S))

    def on_closing(self):
        all_stop = True
        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if (self.running_instance[old_item] is not None) and self.running_instance[old_item].is_running():
                all_stop = False
        if all_stop or askokcancel(None, ugettext("An instance is always running.\nDo you want to close?")):
            self.destroy()
        else:
            self.refresh()

    def destroy(self):
        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if self.running_instance[old_item] is not None:
                self.running_instance[old_item].stop()
                del self.running_instance[old_item]
        Tk.destroy(self)

    def create_instance_panel(self):
        frm_inst = Frame(self.ntbk)
        frm_inst.grid_columnconfigure(0, weight=1)
        frm_inst.grid_rowconfigure(0, weight=1)
        frm_inst.grid_columnconfigure(1, weight=3)
        frm_inst.grid_rowconfigure(1, weight=0)
        self.instance_list = Listbox(frm_inst, width=20)
        self.instance_list.bind('<<ListboxSelect>>', self.select_instance)
        self.instance_list.pack()
        self.instance_list.grid(row=0, column=0, sticky=(N, S, W, E))

        self.instance_txt = Text(frm_inst, width=75)
        self.instance_txt.grid(row=0, column=1, rowspan=2, sticky=(N, S, W, E))
        self.instance_txt.config(state=DISABLED)

        self.btninstframe = Frame(frm_inst, bd=1)
        self.btninstframe.grid(row=1, column=0, columnspan=1)
        self.btninstframe.grid_columnconfigure(0, weight=1)
        Button(self.btninstframe, text=ugettext("Launch"), width=25, command=self.open_inst).grid(
            row=0, column=0, columnspan=2, sticky=(N, S))
        Button(self.btninstframe, text=ugettext("Modify"), width=10,
               command=self.modify_inst).grid(row=1, column=0, sticky=(N, S))
        Button(self.btninstframe, text=ugettext("Delete"), width=10,
               command=self.delete_inst).grid(row=1, column=1, sticky=(N, S))
        Button(self.btninstframe, text=ugettext("Save"), width=10,
               command=self.save_inst).grid(row=2, column=0, sticky=(N, S))
        Button(self.btninstframe, text=ugettext("Restore"), width=10,
               command=self.restore_inst).grid(row=2, column=1, sticky=(N, S))
        Button(self.btninstframe, text=ugettext("Add"), width=25, command=self.add_inst).grid(
            row=3, column=0, columnspan=2, sticky=(N, S))

        self.ntbk.add(frm_inst, text=ugettext('Instances'))

    def create_module_panel(self):
        frm_mod = Frame(self.ntbk)
        frm_mod.grid_columnconfigure(0, weight=1)
        frm_mod.grid_rowconfigure(0, weight=1)
        self.module_txt = Text(frm_mod)
        self.module_txt.grid(row=0, column=0, sticky=(N, S, W, E))
        self.module_txt.config(state=DISABLED)
        self.ntbk.add(frm_mod, text=ugettext('Modules'))

    def do_progress(self, progressing):
        if not progressing:
            self.progress.stop()
            self.progress.grid_remove()
        else:
            self.progress.start(25)
            self.progress.grid(row=1, column=0, sticky=(E, W))

    def enabled(self, is_enabled, widget=None):
        if widget is None:
            widget = self
            self.do_progress(not is_enabled)
        if is_enabled:
            widget.config(cursor="")
        else:

            widget.config(cursor="watch")
        if isinstance(widget, Button) and (widget != self.btnupgrade):
            if is_enabled and (not hasattr(widget, 'disabled') or not widget.disabled):
                widget.config(state=NORMAL)
            else:
                widget.config(state=DISABLED)
        else:
            for child_cmp in widget.winfo_children():
                self.enabled(is_enabled, child_cmp)

    @ThreadRun
    def refresh(self, instance_name=None):
        if instance_name is None:
            instance_name = self.get_selected_instance_name()
        self.instance_txt.delete("1.0", END)
        self._refresh_instance_list()
        self.set_select_instance_name(instance_name)
        if not self.has_checked:
            self._refresh_modules()
            if self.instance_list.size() == 0:
                sleep(.3)
                self._refresh_modules()
                sleep(.3)
                self.after_idle(self.add_inst)

    def _refresh_modules(self):
        self.btnupgrade.config(state=DISABLED)
        self.module_txt.config(state=NORMAL)
        self.module_txt.delete("1.0", END)
        lct_glob = LucteriosGlobal()
        mod_lucterios, mod_applis, mod_modules = lct_glob.installed()
        self.module_txt.insert(
            END, ugettext("Lucterios core\t\t%s\n") % mod_lucterios[1])
        self.module_txt.insert(END, '\n')
        self.module_txt.insert(END, ugettext("Application\n"))
        for appli_item in mod_applis:
            self.module_txt.insert(
                END, "\t%s\t%s\n" % (appli_item[0].ljust(30), appli_item[1]))
        self.module_txt.insert(END, ugettext("Modules\n"))
        for module_item in mod_modules:
            self.module_txt.insert(
                END, "\t%s\t%s\n" % (module_item[0].ljust(30), module_item[1]))
        extra_urls = lct_glob.get_extra_urls()
        if len(extra_urls) > 0:
            self.module_txt.insert(END, "\n")
            self.module_txt.insert(END, ugettext("Pypi servers\n"))
            for extra_url in extra_urls:
                self.module_txt.insert(END, "\t%s\n" % extra_url)
        self.module_txt.config(state=DISABLED)
        self.has_checked = True

        self.after(1000, lambda: Thread(target=self.check).start())

    def _refresh_instance_list(self):
        self.instance_list.delete(0, END)
        luct_glo = LucteriosGlobal()
        instance_list = luct_glo.listing()
        for item in instance_list:
            self.instance_list.insert(END, item)
            if item not in self.running_instance.keys():
                self.running_instance[item] = None

        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if old_item not in instance_list:
                if self.running_instance[old_item] is not None:
                    self.running_instance[old_item].stop()
                del self.running_instance[old_item]

    def set_select_instance_name(self, instance_name):
        cur_sel = 0
        for sel_iter in range(self.instance_list.size()):
            if self.instance_list.get(sel_iter) == instance_name:
                cur_sel = sel_iter
                break
        self.instance_list.selection_set(cur_sel)
        self.select_instance(None)

    def get_selected_instance_name(self):
        if len(self.instance_list.curselection()) > 0:
            return self.instance_list.get(int(self.instance_list.curselection()[0]))
        else:
            return ""

    def set_ugrade_state(self, must_upgrade):
        if must_upgrade:
            self.btnupgrade.config(state=NORMAL)
            self.btnupgrade["text"] = ugettext("Upgrade needs")
        else:
            self.btnupgrade["text"] = ugettext("No upgrade")
            self.btnupgrade.config(state=DISABLED)

    def check(self):
        must_upgrade = False
        try:
            lct_glob = LucteriosGlobal()
            _, must_upgrade = lct_glob.check()
        finally:
            self.after(300, self.set_ugrade_state, must_upgrade)

    @ThreadRun
    def upgrade(self):
        self.btnupgrade.config(state=DISABLED)
        self.instance_list.config(state=DISABLED)
        try:
            from logging import getLogger
            admin_path = import_module(
                "lucterios.install.lucterios_admin").__file__
            proc = Popen(
                [sys.executable, admin_path, "update"], stderr=STDOUT, stdout=PIPE)
            value = proc.communicate()[0]
            try:
                value = value.decode('ascii')
            except:
                pass
            six.print_(value)
            if proc.returncode != 0:
                getLogger("lucterios.admin").error(value)
            else:
                getLogger("lucterios.admin").info(value)
            showinfo(ugettext("Lucterios installer"), ugettext(
                "The application must restart"))
            python = sys.executable
            os.execl(python, python, *sys.argv)
        finally:
            self._refresh_modules()
            self.btnupgrade.config(state=NORMAL)
            self.instance_list.config(state=NORMAL)

    @ThreadRun
    def select_instance(self, evt):

        if self.instance_list['state'] == NORMAL:
            self.instance_list.config(state=DISABLED)
            try:
                instance_name = self.get_selected_instance_name()
                self.instance_txt.configure(state=NORMAL)
                self.instance_txt.delete("1.0", END)
                if instance_name != '':
                    if instance_name not in self.running_instance.keys():
                        self.running_instance[instance_name] = None
                    inst = LucteriosInstance(instance_name)
                    inst.read()
                    self.instance_txt.insert(END, "\t\t\t%s\n\n" % inst.name)
                    self.instance_txt.insert(
                        END, ugettext("Database\t\t%s\n") % inst.get_database_txt())
                    self.instance_txt.insert(
                        END, ugettext("Appli\t\t%s\n") % inst.get_appli_txt())
                    self.instance_txt.insert(
                        END, ugettext("Modules\t\t%s\n") % inst.get_module_txt())
                    self.instance_txt.insert(
                        END, ugettext("Extra\t\t%s\n") % inst.get_extra_txt())
                    self.instance_txt.insert(END, '\n')
                    if self.running_instance[instance_name] is not None and self.running_instance[instance_name].is_running():
                        self.instance_txt.insert(END, ugettext(
                            "=> Running in http://%(ip)s:%(port)d\n") % {'ip': self.running_instance[instance_name].lan_ip, 'port': self.running_instance[instance_name].port})
                        self.btninstframe.winfo_children()[0]["text"] = ugettext(
                            "Stop")
                    else:
                        self.running_instance[instance_name] = None
                        self.instance_txt.insert(END, ugettext("=> Stopped\n"))
                        self.btninstframe.winfo_children()[0]["text"] = ugettext(
                            "Launch")
                else:
                    self.btninstframe.winfo_children()[0]["text"] = ugettext(
                        "Launch")
                self.btninstframe.winfo_children()[0].disabled = (
                    instance_name == '')
                self.btninstframe.winfo_children()[1].disabled = (
                    instance_name == '')
                self.btninstframe.winfo_children()[2].disabled = (
                    instance_name == '')
                self.btninstframe.winfo_children()[3].disabled = (
                    instance_name == '')
                self.btninstframe.winfo_children()[4].disabled = (
                    instance_name == '')
                self.instance_txt.configure(state=DISABLED)
            finally:
                setup_from_none()
                self.instance_list.config(state=NORMAL)

    @ThreadRun
    def add_modif_inst_result(self, result, to_create):
        inst = LucteriosInstance(result[0])
        inst.set_extra("LANGUAGE_CODE='%s'" % result[5])
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

    def add_inst(self):
        self.enabled(False)
        try:
            self.do_progress(False)
            ist_edt = InstanceEditor()
            ist_edt.execute()
            ist_edt.transient(self)
            self.wait_window(ist_edt)
        finally:
            self.enabled(True)
        if ist_edt.result is not None:
            self.add_modif_inst_result(ist_edt.result, True)

    def modify_inst(self):
        self.enabled(False)
        try:
            self.do_progress(False)
            ist_edt = InstanceEditor()
            ist_edt.execute(self.get_selected_instance_name())
            ist_edt.transient(self)
            self.wait_window(ist_edt)
        finally:
            self.enabled(True)
        if ist_edt.result is not None:
            self.add_modif_inst_result(ist_edt.result, False)

    @ThreadRun
    def delete_inst_name(self, instance_name):
        inst = LucteriosInstance(instance_name)
        inst.delete()
        self.refresh()

    def delete_inst(self):
        setup_from_none()
        instance_name = self.get_selected_instance_name()
        if askokcancel(None, ugettext("Do you want to delete '%s'?") % instance_name):
            self.delete_inst_name(instance_name)
        else:
            self.refresh()

    @ThreadRun
    def open_inst(self):
        instance_name = self.get_selected_instance_name()
        if instance_name != '':
            try:
                if instance_name not in self.running_instance.keys():
                    self.running_instance[instance_name] = None
                if self.running_instance[instance_name] is None:
                    port = FIRST_HTTP_PORT
                    for inst_obj in self.running_instance.values():
                        if (inst_obj is not None) and (inst_obj.port >= port):
                            port = inst_obj.port + 1
                    self.running_instance[instance_name] = RunServer(
                        instance_name, port)
                    self.running_instance[instance_name].start()
                else:
                    self.running_instance[instance_name].stop()
                    self.running_instance[instance_name] = None
            finally:
                self.set_select_instance_name(instance_name)

    @ThreadRun
    def save_instance(self, instance_name, file_name):
        inst = LucteriosInstance(instance_name)
        inst.filename = file_name
        if inst.archive():
            showinfo(ugettext("Lucterios installer"), ugettext(
                "Instance saved to %s") % file_name)
        else:
            showerror(
                ugettext("Lucterios installer"), ugettext("Instance not saved!"))
        self.refresh(instance_name)

    def save_inst(self):
        instance_name = self.get_selected_instance_name()
        if instance_name != '':
            file_name = asksaveasfilename(
                parent=self, filetypes=[('lbk', '.lbk'), ('*', '.*')])
            if file_name != '':
                self.save_instance(instance_name, file_name)

    @ThreadRun
    def restore_instance(self, instance_name, file_name):
        if file_name[-4:] == '.bkf':
            rest_inst = MigrateFromV1(instance_name, withlog=True)
        else:
            rest_inst = LucteriosInstance(instance_name)
        rest_inst.filename = file_name
        if rest_inst.restore():
            showinfo(ugettext("Lucterios installer"), ugettext(
                "Instance restore from %s") % file_name)
        else:
            showerror(
                ugettext("Lucterios installer"), ugettext("Instance not restored!"))
        self.refresh(instance_name)

    def restore_inst(self):
        instance_name = self.get_selected_instance_name()
        if instance_name != '':
            file_name = askopenfilename(
                parent=self, filetypes=[('lbk', '.lbk'), ('bkf', '.bkf'), ('*', '.*')])
            if file_name != '':
                self.restore_instance(instance_name, file_name)

    def execute(self):
        self.refresh()
        center(self, (700, 300))
        self.mainloop()


def main():
    setup_from_none()
    lct_form = LucteriosMainForm()
    lct_form.execute()

if __name__ == '__main__':
    main()
