# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from os.path import dirname, join, isfile

def get_build():
    file_name = join(dirname(__file__), 'build')
    if isfile(file_name):
        with open(file_name) as flb:
            return flb.read()
    return "0"

__version__ = "2.0b" + get_build()

def __title__():
    from django.utils.translation import ugettext_lazy as _
    return _("Lucterios core")
