# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from os.path import join, dirname
import lucterios.standard

def get_subtitle():
    return "other subtitle"

APPLIS_NAME = lucterios.standard.__title__()
APPLIS_VERSION = lucterios.standard.__version__
APPLI_EMAIL = "support@sd-libre.fr"
APPLIS_LOGO_NAME = join(dirname(__file__), "logo.gif")
APPLIS_COPYRIGHT = _("(c) GPL Licence")
APPLIS_SUBTITLE = get_subtitle
