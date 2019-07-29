# -*- coding: utf-8 -*-
'''
Tools to manage Lucterios parameters

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
from logging import getLogger
import threading

from django.utils.translation import ugettext_lazy
from django.utils import six
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist

from lucterios.CORE.models import Parameter
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompMemo, XferCompEdit, XferCompFloat, XferCompCheck, XferCompSelect,\
    XferCompPassword
from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework import tools, signal_and_lock


class ParamCache(object):

    def __init__(self, name, param=None):
        def convert_to_int():
            try:
                return int(param.value)
            except ValueError:
                return int('0' + param.value)

        def convert_to_float():
            try:
                return float(param.value)
            except ValueError:
                return float('0' + param.value)

        if param is None:
            param = Parameter.objects.get(name=name)
        self.db_obj = None
        self.name = param.name
        self.type = param.typeparam
        self.meta_info = param.get_meta_select()
        if self.meta_info is not None:  # select in object
            if self.type == 1:  # Integer
                self.value = convert_to_int()
            elif self.type == 2:  # Real
                self.value = convert_to_float()
            else:
                self.value = six.text_type(param.value)
            self.args = {'oldtype': self.type}
            self.type = 6
        if self.type == 0:  # String
            self.value = six.text_type(param.value)
            self.args = {'Multi': False, 'HyperText': False}
        elif self.type == 1:  # Integer
            self.args = {'Min': 0, 'Max': 10000000}
            self.value = convert_to_int()
        elif self.type == 2:  # Real
            self.value = convert_to_float()
            self.args = {'Min': 0, 'Max': 10000000, 'Prec': 2}
        elif self.type == 3:  # Boolean
            self.value = (param.value == 'True')
            self.args = {}
        elif self.type == 4:  # Select
            self.value = convert_to_int()
            self.args = {'Enum': 0}
        elif self.type == 5:  # password
            self.value = six.text_type(param.value)
            self.args = {}
        try:
            current_args = eval(param.args)
        except Exception as expt:
            getLogger(__name__).exception(expt)
            current_args = {}
        for arg_key in self.args.keys():
            if arg_key in current_args.keys():
                self.args[arg_key] = current_args[arg_key]

    def get_label_comp(self):
        lbl = XferCompLabelForm('lbl_' + self.name)
        lbl.set_value_as_name(ugettext_lazy(self.name))
        return lbl

    def get_write_comp(self):
        if self.type == 0:  # String
            if self.args['Multi']:
                param_cmp = XferCompMemo(self.name)
                param_cmp.with_hypertext = self.args['HyperText']
            else:
                param_cmp = XferCompEdit(self.name)
            param_cmp.set_value(self.value)
        elif self.type == 1:  # Integer
            param_cmp = XferCompFloat(
                self.name, minval=self.args['Min'], maxval=self.args['Max'], precval=0)
            param_cmp.set_value(self.value)
            param_cmp.set_needed(True)
        elif self.type == 2:  # Real
            param_cmp = XferCompFloat(self.name, minval=self.args['Min'], maxval=self.args[
                                      'Max'], precval=self.args['Prec'])
            param_cmp.set_value(self.value)
            param_cmp.set_needed(True)
        elif self.type == 3:  # Boolean
            param_cmp = XferCompCheck(self.name)
            param_cmp.set_value(six.text_type(self.value))
            param_cmp.set_needed(True)
        elif self.type == 4:  # Select
            param_cmp = XferCompSelect(self.name)
            selection = []
            for sel_idx in range(0, self.args['Enum']):
                selection.append((sel_idx, ugettext_lazy(self.name + ".%d" % sel_idx)))
            param_cmp.set_select(selection)
            param_cmp.set_value(self.value)
            param_cmp.set_needed(True)
        elif self.type == 5:  # password
            param_cmp = XferCompPassword(self.name)
            param_cmp.security = 0
            param_cmp.set_value('')
        elif self.type == 6:  # select in object
            if (self.meta_info[0] != "") and (self.meta_info[1] != ""):
                db_mdl = apps.get_model(self.meta_info[0], self.meta_info[1])
            else:
                db_mdl = None
            param_cmp = XferCompSelect(self.name)
            param_cmp.set_needed(self.meta_info[4])
            selection = []
            if not self.meta_info[4]:
                if (self.args['oldtype'] == 1) or (self.args['oldtype'] == 2):
                    selection.append((0, None))
                else:
                    selection.append(('', None))
            if db_mdl is None:
                selection = self.meta_info[2]
            else:
                for obj_item in db_mdl.objects.filter(self.meta_info[2]):
                    selection.append((getattr(obj_item, self.meta_info[3]), six.text_type(obj_item)))
            param_cmp.set_select(selection)
            param_cmp.set_value(self.value)
        param_cmp.description = six.text_type(ugettext_lazy(self.name))
        return param_cmp

    def get_read_text(self):
        value_text = ""
        if self.type == 3:  # Boolean
            if self.value:
                value_text = ugettext_lazy("Yes")
            else:
                value_text = ugettext_lazy("No")
        elif self.type == 4:  # Select
            value_text = ugettext_lazy(self.name + ".%d" % self.value)
        elif self.type == 6:  # selected
            if self.meta_info[3] == "id":
                db_obj = self.get_object()
                if db_obj is not None:
                    value_text = six.text_type(db_obj)
                else:
                    value_text = "---"
            else:
                value_text = self.value
        else:
            value_text = self.value
        return value_text

    def get_read_comp(self):
        param_cmp = XferCompLabelForm(self.name)
        if self.type == 5:  # password
            param_cmp.set_value(''.ljust(len(self.value), '*'))
        else:
            param_cmp.set_value(self.get_read_text())
        return param_cmp

    def get_object(self):
        if (self.type == 6):
            if self.db_obj is None:
                try:
                    db_mdl = apps.get_model(self.meta_info[0], self.meta_info[1])
                    db_objs = db_mdl.objects.filter(**{self.meta_info[3]: self.value})
                    if len(db_objs) > 0:
                        self.db_obj = (db_objs[0],)
                    else:
                        self.db_obj = (None,)
                except Exception:
                    self.db_obj = (None,)
            return self.db_obj[0]
        else:
            return None


class Params(object):

    _PARAM_CACHE_LIST = {}

    _paramlock = threading.RLock()

    @classmethod
    def clear(cls):
        cls._paramlock.acquire()
        try:
            cls._PARAM_CACHE_LIST.clear()
        finally:
            cls._paramlock.release()

    @classmethod
    def _get(cls, name):
        if name not in cls._PARAM_CACHE_LIST.keys():
            try:
                cls._PARAM_CACHE_LIST[name] = ParamCache(name)
            except ObjectDoesNotExist:
                raise LucteriosException(GRAVE, "Parameter %s unknown!" % name)
            except Exception:
                raise LucteriosException(GRAVE, "Parameter %s not found!" % name)
        return cls._PARAM_CACHE_LIST[name]

    @classmethod
    def getvalue(cls, name):
        cls._paramlock.acquire()
        try:
            return cls._get(name).value
        finally:
            cls._paramlock.release()

    @classmethod
    def getobject(cls, name):
        cls._paramlock.acquire()
        try:
            return cls._get(name).get_object()
        finally:
            cls._paramlock.release()

    @classmethod
    def gettext(cls, name):
        cls._paramlock.acquire()
        try:
            return six.text_type(cls._get(name).get_read_text())
        finally:
            cls._paramlock.release()

    @classmethod
    def fill(cls, xfer, names, col, row, readonly=True, nb_col=1):
        cls._paramlock.acquire()
        try:
            coloffset = 0
            titles = {}
            signal_and_lock.Signal.call_signal('get_param_titles', names, titles)
            param_cmp = None
            for name in names:
                param = cls._get(name)
                if param is not None:
                    if readonly:
                        param_cmp = param.get_read_comp()
                    else:
                        param_cmp = param.get_write_comp()
                    param_cmp.set_location(col + coloffset, row, 1, 1)
                    if param.name in titles:
                        param_cmp.description = titles[param.name]
                    else:
                        param_cmp.description = ugettext_lazy(param.name)
                    xfer.add_component(param_cmp)
                    coloffset += 1
                    if coloffset == nb_col:
                        coloffset = 0
                        row += 1
            if (param_cmp is not None) and (coloffset != 0):
                param_cmp.colspan = nb_col - coloffset + 1
        finally:
            cls._paramlock.release()


def notfree_mode_connect(*args):
    mode_connection = Params.getvalue("CORE-connectmode")
    return mode_connection != 2


def secure_mode_connect():
    mode_connection = Params.getvalue("CORE-connectmode")
    return mode_connection == 0


tools.WrapAction.mode_connect_notfree = notfree_mode_connect
