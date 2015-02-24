# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from os.path import dirname, join

__version__ = "2.0.beta." + open(join(dirname(__file__), 'build'), 'r').read()

def __title__():
    from django.utils.translation import ugettext_lazy as _
    return _("Lucterios core")
