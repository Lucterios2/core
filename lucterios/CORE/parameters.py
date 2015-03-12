# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
import threading

from django.utils.translation import ugettext_lazy
from django.utils import six
from django.utils.log import getLogger
from django.core.exceptions import ObjectDoesNotExist

from lucterios.CORE.models import Parameter
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompMemo, XferCompEdit, XferCompFloat, XferCompCheck, XferCompSelect
from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework import tools

class ParamCache(object):

    def __init__(self, name):
        param = Parameter.objects.get(name=name)  # pylint: disable=no-member
        self.name = param.name
        self.type = param.typeparam
        if self.type == 0:  # String
            self.value = six.text_type(param.value)
            self.args = {'Multi':False}
        elif self.type == 1:  # Integer
            self.args = {'Min':0, 'Max':10000000}
            self.value = int(param.value)
        elif self.type == 2:  # Real
            self.value = float(param.value)
            self.args = {'Min':0, 'Max':10000000, 'Prec':2}
        elif self.type == 3:  # Boolean
            self.value = bool(param.value)
            self.args = {}
        elif self.type == 4:  # Select
            self.value = int(param.value)
            self.args = {'Enum':0}
        try:
            current_args = eval(param.args)  # pylint: disable=eval-used
        except Exception as expt:  # pylint: disable=broad-except
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
            else:
                param_cmp = XferCompEdit(self.name)
            param_cmp.set_value(self.value)
        elif self.type == 1:  # Integer
            param_cmp = XferCompFloat(self.name, minval=self.args['Min'], maxval=self.args['Max'])
            param_cmp.set_value(self.value)
        elif self.type == 2:  # Real
            param_cmp = XferCompFloat(self.name, minval=self.args['Min'], maxval=self.args['Max'], precval=self.args['Prec'])
            param_cmp.set_value(self.value)
        elif self.type == 3:  # Boolean
            param_cmp = XferCompCheck(self.name)
            param_cmp.set_value(self.value)
        elif self.type == 4:  # Select
            param_cmp = XferCompSelect(self.name)
            selection = {}
            for sel_idx in range(0, self.args['Enum']):
                selection[sel_idx] = ugettext_lazy(self.name + ".%d" % sel_idx)
            param_cmp.set_select(selection)
            param_cmp.set_value(self.value)
        return param_cmp

    def get_read_comp(self):
        param_cmp = XferCompLabelForm(self.name)
        if self.type == 3:  # Boolean
            if self.value == 'True':
                param_cmp.set_value(ugettext_lazy("Yes"))
            else:
                param_cmp.set_value(ugettext_lazy("No"))
        elif self.type == 4:  # Select
            param_cmp.set_value(ugettext_lazy(self.name + ".%d" % self.value))
        else:
            param_cmp.set_value(self.value)
        return param_cmp

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
        if not name is cls._PARAM_CACHE_LIST.keys():
            try:
                cls._PARAM_CACHE_LIST[name] = ParamCache(name)
            except ObjectDoesNotExist:
                raise LucteriosException(GRAVE, "Parameter %s unknow!" % name)
        return cls._PARAM_CACHE_LIST[name]

    @classmethod
    def getvalue(cls, name):
        cls._paramlock.acquire()
        try:
            return cls._get(name).value
        finally:
            cls._paramlock.release()

    @classmethod
    def fill(cls, xfer, names, col, row, readonly=True):
        cls._paramlock.acquire()
        try:
            for name in names:
                param = cls._get(name)
                if param is not None:
                    lbl = param.get_label_comp()
                    lbl.set_location(col, row, 1, 1)
                    xfer.add_component(lbl)
                    if readonly:
                        param_cmp = param.get_read_comp()
                    else:
                        param_cmp = param.get_write_comp()
                    param_cmp.set_location(col + 1, row, 1, 1)
                    xfer.add_component(param_cmp)
                    row += 1
        finally:
            cls._paramlock.release()

def notfree_mode_connect():
    mode_connection = Params.getvalue("CORE-connectmode")
    return mode_connection != 2

def secure_mode_connect():
    mode_connection = Params.getvalue("CORE-connectmode")
    return mode_connection == 0

tools.notfree_mode_connect = notfree_mode_connect
