# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy

from lucterios.CORE.models import Parameter
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompMemo, \
    XferCompEdit, XferCompFloat, XferCompCheck, XferCompSelect
from django.core.exceptions import ObjectDoesNotExist
from lucterios.framework.error import LucteriosException, GRAVE

class ParamCache(object):

    def __init__(self, name):
        param = Parameter.objects.get(name=name)  # pylint: disable=no-member
        self.name = param.name
        self.type = param.typeparam
        self.args = eval(param.args)
        self.value = param.value

    def get_label_comp(self):
        lbl = XferCompLabelForm('lbl_' + self.name)
        lbl.set_value('{[bold]}%s{[/bold]}' % ugettext_lazy(self.name))
        return lbl

    def get_write_comp(self):
        if self.type == 0: # String
            if self.args['Multi']:
                param_cmp = XferCompMemo(self.name)
            else:
                param_cmp = XferCompEdit(self.name)
            param_cmp.set_value(self.value)
        elif self.type == 1: # Integer
            param_cmp = XferCompFloat(self.name, minval=self.args['min'], maxval=self.args['max'])
            param_cmp.set_value(self.value)
        elif self.type == 2: # Real
            param_cmp = XferCompFloat(self.name, minval=self.args['min'], maxval=self.args['max'], precval=self.args['prec'])
            param_cmp.set_value(self.value)
        elif self.type == 3: # Boolean
            param_cmp = XferCompCheck(self.name)
            param_cmp.set_value(self.value)
        elif self.type == 4: # Select
            param_cmp = XferCompSelect(self.name)
            selection = {}
            for sel_idx in range(0, self.args['Enum']):
                selection[sel_idx] = ugettext_lazy(self.name + ".%d" % sel_idx)
            param_cmp.set_select(selection)
            param_cmp.set_value(self.value)
        return param_cmp

    def get_read_comp(self):
        param_cmp = XferCompLabelForm(self.name)
        if self.type == 3: # Boolean
            if self.value == 'True':
                param_cmp.set_value(ugettext_lazy("Yes"))
            else:
                param_cmp.set_value(ugettext_lazy("No"))
        elif self.type == 4: # Select
            param_cmp.set_value(ugettext_lazy(self.name + "." + self.value))
        else:
            param_cmp.set_value(self.value)
        return param_cmp


PARAM_CACHE_LIST = {}

def clear_parameters():
    PARAM_CACHE_LIST.clear()

def get_parameter(name):
    if not name is PARAM_CACHE_LIST.keys():
        try:
            PARAM_CACHE_LIST[name] = ParamCache(name)
        except ObjectDoesNotExist:
            raise LucteriosException(GRAVE, "Parameter %s unknow!" % name)
    return PARAM_CACHE_LIST[name]

def fill_parameter(xfer, names, col, row, readonly=True):
    for name in names:
        param = get_parameter(name)
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
