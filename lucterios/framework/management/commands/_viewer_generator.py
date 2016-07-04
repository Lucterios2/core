#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Describe database model for Django

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
import os
import inspect
from os.path import isfile, join, isdir, dirname, basename
from glob import glob

from django.utils.module_loading import import_module
from django.utils import six
from django_fsm import FSMFieldMixin
try:
    from importlib import reload
except ImportError:
    pass

try:
    from tkinter import Tk, StringVar, IntVar, ttk, Label, Checkbutton, Frame, Button, E, W, N, S, SUNKEN
    from tkinter.messagebox import showerror, showinfo
except:
    from Tkinter import Tk, StringVar, IntVar, Label, Checkbutton, Frame, Button, E, W, N, S, SUNKEN
    from tkMessageBox import showerror, showinfo
    import ttk

LIST_VIEWER = {'0List': ('XferListEditor', 'list'),
               '1AddModify': ('XferAddEditor', 'edit', 'modify', 'add'),
               '2Show': ('XferShowEditor', 'show'),
               '3Transition': ('XferTransition', 'transition'),
               '4Del': ('XferDelete', 'delete'),
               '5Print': ('XferPrintAction', 'print'),
               '6Search': ('XferSearchEditor', 'search'),
               '7Label': ('XferPrintLabel', 'label'),
               '8Listing': ('XferPrintListing', 'listing'),
               }

LIST_AFFECT = {'list': '',
               'search': '',
               'edit': '@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)',
               'modify': '@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES)',
               'add': '@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")',
               'show': '@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)',
               'delete': '@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)',
               'print': '@ActionsManage.affect_show(TITLE_PRINT, "images/print.png")',
               'label': '@ActionsManage.affect_list(TITLE_LABEL, "images/print.png")',
               'listing': '@ActionsManage.affect_list(TITLE_LISTING, "images/print.png")',
               'transition': '@ActionsManage.affect_transition("%(statname)s")',
               }


class GeneratorException(Exception):
    pass


class GenForm(Tk):

    def __init__(self):
        Tk.__init__(self)
        self.minsize(200, 250)
        self.result = None
        self._model_name = ''
        self._icon_name = ''
        self.title("Viewer generator")
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.resizable(True, True)
        Label(self, text='Model').grid(row=0, column=0, sticky=(N, E))
        self.models = ttk.Combobox(
            self, textvariable=StringVar(), state='readonly')
        self.models.grid(row=0, column=1, sticky=(N, W, E, S), padx=3, pady=3)
        mainframe = Frame(self, bd=1, relief=SUNKEN)
        mainframe.grid(
            row=1, column=0, columnspan=2, sticky=(N, S, E, W), padx=3, pady=3)
        current_row = 0
        current_col = 0
        self.check = []
        for value in ('add', 'list', 'edit', 'search', 'modify', 'listing', 'show', 'label', 'delete', 'print', 'transition'):
            chkbtn_val = IntVar()
            chkbtn = Checkbutton(mainframe, text=value, variable=chkbtn_val)
            chkbtn.grid(
                row=current_row, column=current_col, sticky=W, padx=3, pady=3)
            self.check.append((value, chkbtn_val))
            current_col += 1
            if current_col == 2:
                current_col = 0
                current_row += 1
        Label(mainframe, text='Icon').grid(
            row=(current_row + 1), column=0, columnspan=2, sticky=(N, W, E, S), padx=3)
        self.icons = ttk.Combobox(
            mainframe, textvariable=StringVar(), state='readonly')
        self.icons.grid(
            row=(current_row + 2), column=0, columnspan=2, sticky=(N, W, E, S), padx=3)
        btnframe = Frame(self, bd=1)
        btnframe.grid(row=2, column=0, columnspan=2)
        Button(btnframe, text="OK", width=10, command=self.cmd_ok).grid(
            row=1, column=0, sticky=(N, S, E, W), padx=5, pady=3)
        Button(btnframe, text="Cancel", width=10, command=self.cmd_cancel).grid(
            row=1, column=1, sticky=(N, S, E, W), padx=5, pady=3)

    def cmd_ok(self):
        self.result = {}
        chk_res = {}
        for chktext, chkbtn_val in self.check:
            chk_res[chktext] = chkbtn_val.get()
        item_names = list(LIST_VIEWER.keys())
        item_names.sort()
        for item_name in item_names:
            acts = ()
            for act in LIST_VIEWER[item_name]:
                if act in chk_res.keys() and (chk_res[act] == 1):
                    acts = acts + (act,)
            if len(acts) > 0:
                self.result[item_name] = acts
        if len(self.result) == 0:
            self.result = None
            self._model_name = ''
            self._icon_name = ''
        else:
            self._model_name = self.models.get()
            self._icon_name = self.icons.get()
        self.cmd_cancel()

    def get_model_name(self):
        return self._model_name

    def get_icon_name(self):
        return self._icon_name

    def cmd_cancel(self):
        self.destroy()

    def load(self, model_list, icon_list):
        self.models['values'] = model_list
        self.models.current(0)
        self.icons['values'] = icon_list
        self.icons.current(0)
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        size = tuple(int(_) for _ in self.geometry().split('+')[0].split('x'))
        x = w / 4 - size[0] / 2
        y = h / 2 - size[1] / 2
        self.geometry("%dx%d+%d+%d" % (size + (x, y)))
        self.mainloop()


class Generator(object):

    def __init__(self, project_path, module_name):
        self.class_model = []
        self.module_obj = None
        self.project_path = project_path
        self.module_name = module_name
        self.root_module = module_name.split('.')[-1]
        self._load_model_classes()

    def _load_model_classes(self):
        from lucterios.framework.models import LucteriosModel
        self.module_obj = import_module(self.module_name + ".models")
        self.full_modulepath = self.module_obj.__file__
        self.class_model = []
        for obj in inspect.getmembers(self.module_obj):
            try:
                if inspect.isclass(obj[1]) and issubclass(obj[1], LucteriosModel) and  \
                        not (hasattr(obj[1]._meta, 'abstract') and obj[1]._meta.abstract) and (obj[1].__module__ == self.module_obj.__name__):
                    self.class_model.append(obj[1].__name__)
            except AttributeError:
                pass
        if len(self.class_model) == 0:
            raise GeneratorException("Module %s has not model!" % self.module_name)
        self.class_model

    def extract_icons(self):
        icon_list = []
        images_dir = join(dirname(self.full_modulepath), 'static', self.module_name, 'images')
        if isdir(images_dir):
            for file_item in glob(join(images_dir, '*')):
                icon_list.append(basename(file_item))
        return icon_list

    def writedata(self, text):
        try:
            self.viewfile.write(six.binary_type(text, 'UTF-8'))
        except:
            self.viewfile.write(six.binary_type(text))

    def _write_header(self, model_name, item_actions, is_new):
        if is_new:
            self.writedata(
                "# -*- coding: utf-8 -*-\nfrom __future__ import unicode_literals\n")
        self.writedata("""
from django.utils.translation import ugettext_lazy as _\n\n""")
        self.writedata(
            "from lucterios.framework.xferadvance import TITLE_MODIFY, TITLE_ADD, TITLE_EDIT, TITLE_DELETE, TITLE_LISTING, TITLE_LABEL, TITLE_PRINT\n")
        for item_name in sorted(list(item_actions.keys())):
            if item_name == '4Search':
                self.writedata(
                    "from lucterios.framework.xfersearch import %s\n" % LIST_VIEWER[item_name][0])
            elif item_name == '5Print' or item_name == '6Label' or item_name == '7Listing':
                self.writedata(
                    "from lucterios.CORE.xferprint import %s\n" % LIST_VIEWER[item_name][0])
            else:
                self.writedata(
                    "from lucterios.framework.xferadvance import %s\n" % LIST_VIEWER[item_name][0])
        if '0List' in item_actions.keys() or '4Search' in item_actions.keys():
            self.writedata(
                "from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage\n")
        else:
            self.writedata(
                "from lucterios.framework.tools import ActionsManage, MenuManage\n")
        self.writedata("from lucterios.framework.tools import SELECT_SINGLE, CLOSE_YES, SELECT_MULTI\n")
        self.writedata("\nfrom %s.models import %s\n" % (self.module_name, model_name))

    def _define_params(self, model_name, item_name, acts, verbose_name, verbose_name_plural):
        if item_name == '1AddModify':
            caption = 'caption_add = _("Add %(name)s")\n    caption_modify = _("Modify %(name)s")' % {
                'name': verbose_name.lower()}
        elif item_name == '0List':
            caption = 'caption = _("%(name)s")' % {'name': verbose_name_plural}
        else:
            name = LIST_VIEWER[item_name][1]
            name = name[0:1].upper() + name[1:].lower()
            caption = 'caption = _("%s %s")' % (name, verbose_name)
        actions = ['']
        for act in acts:
            actions.append(LIST_AFFECT[act])
        actions = "\n".join(actions)
        if actions == "\n":
            actions = ""
        if item_name == '3Del':
            right = '%s.delete_%s' % (self.root_module, model_name.lower())
        elif item_name == '1AddModify':
            right = '%s.add_%s' % (self.root_module, model_name.lower())
        else:
            right = '%s.change_%s' % (self.root_module, model_name.lower())
        if item_name == '0List' or item_name == '4Search':
            menuext = ", FORMTYPE_NOMODAL, 'core.general', _('menu %s')" % LIST_VIEWER[item_name][1]
        else:
            menuext = ''
        return actions, caption, right, menuext

    def write_actions(self, model_name, icon_name, item_actions):
        viewer_file = join(
            dirname(self.full_modulepath), 'views_%s.py' % model_name.lower())
        is_new = not isfile(viewer_file)
        with open(viewer_file, 'ab') as self.viewfile:
            self._write_header(model_name, item_actions, is_new)
            class_inst = getattr(self.module_obj, model_name)
            verbose_name = six.text_type(class_inst._meta.verbose_name)
            verbose_name_plural = six.text_type(
                class_inst._meta.verbose_name_plural)
            for item_name in sorted(list(item_actions.keys())):
                acts = item_actions[item_name]
                actions, caption, right, menuext = self._define_params(model_name, item_name, acts, verbose_name, verbose_name_plural)
                if item_name == '3Transition':
                    loop = []
                    for field in class_inst._meta.get_fields():
                        if isinstance(field, FSMFieldMixin):
                            loop.append({'statname': field.name})
                    six.print_(loop)
                else:
                    loop = [{'statname': ''}]
                for item in loop:
                    actions = actions % item
                    self.writedata("""
%(actions)s
@MenuManage.describ('%(right)s'%(menuext)s)
class %(modelname)s%(itemname)s(%(classname)s):
    icon = "%(iconname)s"
    model = %(modelname)s
    field_id = '%(fieldidname)s'
    %(caption)s
""" % {'modelname': model_name, 'iconname': icon_name, 'fieldidname': model_name.lower(), 'itemname': item_name[1:],
                        'classname': LIST_VIEWER[item_name][0], 'actions': actions, 'caption': caption, 'right': right, 'menuext': menuext})
        showinfo("View generator", "Views generated in %s" % os.path.relpath(viewer_file, self.project_path))
