#!/usr/bin/env python3
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
from os.path import join, dirname, expanduser
from time import sleep

from django.utils.module_loading import import_module
from django.utils.translation import gettext

from tkinter import Toplevel, Tk, ttk, Label, Entry, Frame, Button, Listbox, Text, StringVar, TclError
from tkinter import E, W, N, S, END, NORMAL, DISABLED, EXTENDED, CENTER
from tkinter.messagebox import showerror, showinfo, askokcancel
from tkinter.filedialog import asksaveasfilename, askopenfilename
from tkinter import Image

from lucterios.install.lucterios_admin import LucteriosGlobal, LucteriosInstance, setup_from_none
from lucterios.install.graphic_lib import ThreadRun, LucteriosMain, EditorInstance, LucteriosChecker

READLONY = 'readonly'
VALUES = 'values'


def center(root, size=None):
    root.update_idletasks()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    if size is None:
        size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))
    pos_x = int(width / 2 - size[0] / 2)
    pos_y = int(height / 2 - size[1] / 2)
    root.geometry("%dx%d+%d+%d" % (size + (pos_x, pos_y)))


class SplashScreen(Toplevel):

    HEIGHT = 150
    WIDTH = 400

    def __init__(self, root, img):
        Toplevel.__init__(self, root)
        self.config(cursor="watch")
        self.geometry('%dx%d' % (self.WIDTH, self.HEIGHT))
        self.overrideredirect(True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        img = ttk.Label(self, image=img, anchor=W)
        img.grid(column=0, row=0, sticky=(N, S, W), rowspan=2, padx=3, pady=3)

        title = ttk.Label(self, text=gettext("Lucterios launcher"), font='Helvetica 18 bold', anchor=CENTER)
        title.grid(column=1, row=0, sticky=(N, E), padx=(5, 25), pady=(1, 5))

        label = ttk.Label(self, text=gettext('Application loading\nWaiting a minute ...'), anchor=CENTER)
        label.grid(column=1, row=1, sticky=(N, E), padx=(0, 15), pady=(5, 50))

        self.center_splash_screen()

    def center_splash_screen(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        x = w / 2 - self.WIDTH / 2
        y = h / 2 - self.HEIGHT / 2
        self.geometry("%dx%d+%d+%d" % ((self.WIDTH, self.HEIGHT) + (x, y)))

    def destroy_splash_screen(self):
        self.destroy()


class InstanceEditor(Toplevel, EditorInstance):

    def __init__(self):
        Toplevel.__init__(self)
        EditorInstance.__init__(self)
        self.focus_set()
        self.grab_set()

        self.result = None
        self.module_data = None
        self.mod_applis = None
        self.title(gettext("Instance editor"))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.ntbk = ttk.Notebook(self)
        self.ntbk.grid(row=0, column=0, columnspan=1, sticky=(N, S, E, W))

        self.frm_general = Frame(self.ntbk, width=350, height=150)
        self.frm_general.grid_columnconfigure(0, weight=0)
        self.frm_general.grid_columnconfigure(1, weight=1)
        self._general_tabs()
        self.ntbk.add(self.frm_general, text=gettext('General'))

        self.frm_database = Frame(self.ntbk, width=350, height=150)
        self.frm_database.grid_columnconfigure(0, weight=0)
        self.frm_database.grid_columnconfigure(1, weight=1)
        self._database_tabs()
        self.ntbk.add(self.frm_database, text=gettext('Database'))

        btnframe = Frame(self, bd=1)
        btnframe.grid(row=1, column=0, columnspan=1)
        Button(btnframe, text=gettext("OK"), width=10, command=self.apply).grid(
            row=0, column=0, sticky=(N, S, E))
        Button(btnframe, text=gettext("Cancel"), width=10, command=self.destroy).grid(
            row=0, column=1, sticky=(N, S, W))

    def _database_tabs(self):
        Label(self.frm_database, text=gettext("Type")).grid(
            row=0, column=0, sticky=(N, W), padx=5, pady=3)
        self.typedb = ttk.Combobox(
            self.frm_database, textvariable=StringVar(), state=READLONY)
        self.typedb.bind("<<ComboboxSelected>>", self.typedb_selection)
        self.typedb.grid(row=0, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_database, text=gettext("Name")).grid(
            row=1, column=0, sticky=(N, W), padx=5, pady=3)
        self.namedb = Entry(self.frm_database)
        self.namedb.grid(row=1, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_database, text=gettext("User")).grid(
            row=2, column=0, sticky=(N, W), padx=5, pady=3)
        self.userdb = Entry(self.frm_database)
        self.userdb.grid(row=2, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_database, text=gettext("Password")).grid(
            row=3, column=0, sticky=(N, W), padx=5, pady=3)
        self.pwddb = Entry(self.frm_database)
        self.pwddb.grid(row=3, column=1, sticky=(N, S, E, W), padx=5, pady=3)

    def _general_tabs(self):
        Label(self.frm_general, text=gettext("Name")).grid(
            row=0, column=0, sticky=(N, W), padx=5, pady=3)
        self.name = Entry(self.frm_general)
        self.name.grid(row=0, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=gettext("Appli")).grid(
            row=1, column=0, sticky=(N, W), padx=5, pady=3)
        self.applis = ttk.Combobox(
            self.frm_general, textvariable=StringVar(), state=READLONY)
        self.applis.bind("<<ComboboxSelected>>", self.appli_selection)
        self.applis.grid(row=1, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=gettext("Modules")).grid(
            row=2, column=0, sticky=(N, W), padx=5, pady=3)
        self.modules = Listbox(self.frm_general, selectmode=EXTENDED)
        self.modules.configure(exportselection=False)
        self.modules.grid(row=2, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=gettext("Language")).grid(
            row=3, column=0, sticky=(N, W), padx=5, pady=3)
        self.language = ttk.Combobox(
            self.frm_general, textvariable=StringVar(), state=READLONY)
        self.language.grid(
            row=3, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=gettext("CORE-connectmode")
              ).grid(row=4, column=0, sticky=(N, W), padx=5, pady=3)
        self.mode = ttk.Combobox(
            self.frm_general, textvariable=StringVar(), state=READLONY)
        self.mode.bind("<<ComboboxSelected>>", self.mode_selection)
        self.mode.grid(row=4, column=1, sticky=(N, S, E, W), padx=5, pady=3)
        Label(self.frm_general, text=gettext("Password")).grid(
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
            while appli_root_name + str(default_name_idx) in current_inst_names:
                default_name_idx += 1
            self.name.delete(0, END)
            self.name.insert(
                0, appli_root_name + str(default_name_idx))
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
        if self.is_new_instance and ((self.name.get() == '') or (self.name_rull.match(self.name.get()) is None)):
            showerror(gettext("Instance editor"), gettext("Name invalid!"))
            return
        if self.applis.get() == '':
            showerror(gettext("Instance editor"), gettext("No application!"))
            return
        db_param = "%s:name=%s,user=%s,password=%s" % (self.typedb.get(), self.namedb.get(), self.userdb.get(), self.pwddb.get())
        security = "MODE=%s" % list(self.mode[VALUES]).index(self.mode.get())
        if self.password.get() != '':
            security += ",PASSWORD=%s" % self.password.get()
        module_list = [self.module_data[int(item)] for item in self.modules.curselection()]
        appli_id = list(self.applis[VALUES]).index(self.applis.get())
        current_lang = get_locale_lang()
        for lang in DEFAULT_LANGUAGES:
            if lang[1] == self.language.get():
                current_lang = lang[0]
        self.result = (self.name.get(), self.mod_applis[appli_id][
                       0], ",".join(module_list), security, db_param, current_lang)
        self.destroy()

    def _load_current_data(self, instance_name):
        from lucterios.framework.settings import DEFAULT_LANGUAGES
        lct_inst, applis_id, mode_id, typedb_index, current_lang = self._get_instance_elements(instance_name)

        self.is_new_instance = False
        self.name.delete(0, END)
        self.name.insert(0, lct_inst.name)
        self.name.config(state=DISABLED)
        self.applis.current(applis_id)
        self.mode.current(mode_id)
        self.mode_selection(None)
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
        for lang in DEFAULT_LANGUAGES:
            if lang[0] == current_lang:
                self.language.current(self.language[VALUES].index(lang[1]))

    def execute(self, instance_name=None):
        from lucterios.framework.settings import DEFAULT_LANGUAGES, get_locale_lang
        self._define_values()

        self.module_data = []
        self.modules.delete(0, END)
        for module_title, module_name in self.module_list:
            self.modules.insert(END, module_title)
            self.module_data.append(module_name)

        self.mode[VALUES] = self.mode_values
        self.language[VALUES] = self.lang_values
        self.typedb[VALUES] = self.dbtype_values
        self.applis[VALUES] = self.appli_list
        if instance_name is not None:
            self._load_current_data(instance_name)
        else:
            self.typedb.current(0)
            self.mode.current(2)
            if len(self.appli_list) > 0:
                self.applis.current(0)
            self.appli_selection(None)
            self.mode_selection(None)
            self.typedb_selection(None)
            for lang in DEFAULT_LANGUAGES:
                if lang[0] == get_locale_lang():
                    self.language.current(self.language[VALUES].index(lang[1]))
        center(self)


class LucteriosMainForm(Tk, LucteriosMain):

    def __init__(self):
        Tk.__init__(self)
        LucteriosMain.__init__(self)
        try:
            try:
                self.tk.call('tk_getOpenFile', '-foobarbaz')
            except TclError:
                pass
            # now set the magic variables accordingly
            self.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except Exception:
            pass
        try:
            self.img = Image("photo", file=join(dirname(import_module('lucterios.install').__file__), "lucterios.png"))
            self.tk.call('wm', 'iconphoto', self._w, self.img)
        except Exception:
            self.img = None
        self.has_checked = False
        self.title(gettext("Lucterios launcher"))
        self.minsize(475, 260)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
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
        Button(self.btnframe, text=gettext("Refresh"), width=20, command=self.refresh).grid(
            row=0, column=0, padx=3, pady=3, sticky=(N, S))
        self.btnupgrade = Button(
            self.btnframe, text=gettext("Search upgrade"), width=20, command=self.upgrade)
        self.btnupgrade.config(state=DISABLED)
        self.btnupgrade.grid(row=0, column=1, padx=3, pady=3, sticky=(N, S))
        Button(self.btnframe, text=gettext("Close"), width=20, command=self.on_closing).grid(
            row=0, column=2, padx=3, pady=3, sticky=(N, S))
        self.start_up_app()

    def show(self):
        self.update()
        self.deiconify()

    def show_splash_screen(self):
        if sys.platform != 'darwin':
            self.withdraw()
        self.splash = SplashScreen(self, self.img)

    def remove_splash_screen(self):
        self.splash.destroy_splash_screen()
        del self.splash
        self.deiconify()

    def show_info(self, text, message):
        showinfo(text, message)

    def show_error(self, text, message):
        showerror(text, message)

    def on_closing(self):
        if self.is_all_stop() or askokcancel(None, gettext("An instance is always running.\nDo you want to close?")):
            self.destroy()
        else:
            self.refresh()

    def destroy(self):
        self.stop_all()
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
        Button(self.btninstframe, text=gettext("Browser"), width=10,
               command=self.open_browser).grid(row=0, column=0, sticky=(N, S))
        Button(self.btninstframe, text=gettext("Launch"), width=10,
               command=self.open_inst).grid(row=0, column=1, sticky=(N, S))
        Button(self.btninstframe, text=gettext("Modify"), width=10,
               command=self.modify_inst).grid(row=1, column=0, sticky=(N, S))
        Button(self.btninstframe, text=gettext("Delete"), width=10,
               command=self.delete_inst).grid(row=1, column=1, sticky=(N, S))
        Button(self.btninstframe, text=gettext("Save"), width=10,
               command=self.save_inst).grid(row=2, column=0, sticky=(N, S))
        Button(self.btninstframe, text=gettext("Restore"), width=10,
               command=self.restore_inst).grid(row=2, column=1, sticky=(N, S))
        Button(self.btninstframe, text=gettext("Add"), width=25, command=self.add_inst).grid(
            row=3, column=0, columnspan=2, sticky=(N, S))

        self.ntbk.add(frm_inst, text=gettext('Instances'))

    def create_module_panel(self):
        frm_mod = Frame(self.ntbk)
        frm_mod.grid_columnconfigure(0, weight=1)
        frm_mod.grid_rowconfigure(0, weight=1)
        self.module_txt = Text(frm_mod)
        self.module_txt.grid(row=0, column=0, sticky=(N, S, W, E))
        self.module_txt.config(state=DISABLED)
        self.ntbk.add(frm_mod, text=gettext('Modules'))

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

    def run_after(self, ms, func=None, *args):
        self.after(ms, func, *args)

    def _refresh_modules(self):
        self.btnupgrade.config(state=DISABLED)
        self.module_txt.config(state=NORMAL)
        self.module_txt.delete("1.0", END)
        lct_glob = LucteriosGlobal()
        mod_lucterios, mod_applis, mod_modules = lct_glob.installed()
        self.module_txt.insert(
            END, gettext("Lucterios core\t\t%s\n") % mod_lucterios[1])
        self.module_txt.insert(END, '\n')
        self.module_txt.insert(END, gettext("Application\n"))
        for appli_item in mod_applis:
            self.module_txt.insert(
                END, "\t%s\t%s\n" % (appli_item[0].ljust(30), appli_item[1]))
        self.module_txt.insert(END, gettext("Modules\n"))
        for module_item in mod_modules:
            self.module_txt.insert(
                END, "\t%s\t%s\n" % (module_item[0].ljust(30), module_item[1]))
        extra_urls = lct_glob.get_extra_urls()
        if len(extra_urls) > 0:
            self.module_txt.insert(END, "\n")
            self.module_txt.insert(END, gettext("Pypi servers\n"))
            for extra_url in extra_urls:
                self.module_txt.insert(END, "\t%s\n" % extra_url)
        self.module_txt.config(state=DISABLED)
        self.has_checked = True

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

    def set_ugrade_state(self, upgrade_mode):
        if upgrade_mode == 2:
            msg = gettext("The application must restart")
            self.show_info(gettext("Lucterios launcher"), msg)
            self.btnupgrade["text"] = msg
            self.btnupgrade.config(state=DISABLED)
            self._refresh_modules()
        else:
            self.btnupgrade["text"] = self.ugrade_message(upgrade_mode == 1)
            self.btnupgrade.config(state=NORMAL if upgrade_mode == 1 else DISABLED)

    def upgrade(self):
        self.btnupgrade.config(state=DISABLED)
        self.instance_list.config(state=DISABLED)
        try:
            LucteriosMain.upgrade(self)
        finally:
            self.btnupgrade.config(state=DISABLED)
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
                        END, gettext("Database\t\t%s\n") % inst.get_database_txt())
                    self.instance_txt.insert(
                        END, gettext("Appli\t\t%s\n") % inst.get_appli_txt())
                    self.instance_txt.insert(
                        END, gettext("Modules\t\t%s\n") % inst.get_module_txt())
                    self.instance_txt.insert(
                        END, gettext("Extra\t\t%s\n") % inst.get_extra_txt())
                    self.instance_txt.insert(END, '\n')
                    if self.running_instance[instance_name] is not None and self.running_instance[instance_name].is_running():
                        self.instance_txt.insert(END, gettext("Running in <a href='%(url)s'>%(url)s</a>") % {'url': self.running_instance[inst.name].get_url()})
                        self.btninstframe.winfo_children()[0].disabled = False
                        self.btninstframe.winfo_children()[1]["text"] = gettext("Stop")
                    else:
                        self.running_instance[instance_name] = None
                        self.instance_txt.insert(END, gettext("=> Stopped\n"))
                        self.btninstframe.winfo_children()[0].disabled = True
                        self.btninstframe.winfo_children()[1]["text"] = gettext("Launch")
                else:
                    self.btninstframe.winfo_children()[0]["text"] = gettext("Launch")
                self.btninstframe.winfo_children()[1].disabled = (instance_name == '')
                self.btninstframe.winfo_children()[2].disabled = (instance_name == '')
                self.btninstframe.winfo_children()[3].disabled = (instance_name == '')
                self.btninstframe.winfo_children()[4].disabled = (instance_name == '')
                self.btninstframe.winfo_children()[5].disabled = (instance_name == '')
                self.instance_txt.configure(state=DISABLED)
            finally:
                setup_from_none()
                self.instance_list.config(state=NORMAL)

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

    def delete_inst(self):
        setup_from_none()
        instance_name = self.get_selected_instance_name()
        if askokcancel(None, gettext("Do you want to delete '%s'?") % instance_name):
            self.delete_inst_name(instance_name)
        else:
            self.refresh()

    def save_inst(self):
        instance_name = self.get_selected_instance_name()
        if instance_name != '':
            file_name = asksaveasfilename(parent=self, filetypes=[('lbk', '.lbk'), ('*', '.*')], initialdir=expanduser('~'))
            if file_name != '':
                self.save_instance(instance_name, file_name)

    def restore_inst(self):
        instance_name = self.get_selected_instance_name()
        if instance_name != '':
            file_name = askopenfilename(parent=self, filetypes=[('lbk', '.lbk'), ('*', '.*')], initialdir=expanduser('~'))
            if isinstance(file_name, str) and (file_name != ''):
                self.restore_instance(instance_name, file_name)

    def execute(self):
        self.refresh()
        center(self, (700, 300))
        self.mainloop()


def main():
    setup_from_none()
    with LucteriosChecker() as checher:
        if checher.execute():
            lct_form = LucteriosMainForm()
            checher.open_function = lambda: lct_form.show()
            checher.startedlist_function = lambda: lct_form.started_list()
            lct_form.execute()
        else:
            sys.exit(1)


if __name__ == '__main__':
    main()
