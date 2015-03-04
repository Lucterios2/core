# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from lucterios.framework.error import LucteriosException, GRAVE
# from django.utils import six, formats

_SIGNAL_LIST = {}

def signal(name):
    def wrapper(item):
        if not name in _SIGNAL_LIST.keys():
            _SIGNAL_LIST[name] = []
        _SIGNAL_LIST[name].append(item)
        return item
    return wrapper

def call_signal(name, *args):
    if not name in _SIGNAL_LIST.keys():
        raise LucteriosException(GRAVE, _("Unknown signal %s") % name)
    for sign_fct in _SIGNAL_LIST[name]:
        sign_fct(*args)
