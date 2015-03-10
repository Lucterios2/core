# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils import six

INTERNAL = 0
CRITIC = 1
GRAVE = 2
IMPORTANT = 3
MINOR = 4

class LucteriosException(Exception):

    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code

class LucteriosRedirectException(LucteriosException):

    def __init__(self, msg, redirectclassaction):
        LucteriosException.__init__(self, IMPORTANT, msg)
        self.redirectclassaction = redirectclassaction

def get_error_trace():
    import sys, traceback
    trace = traceback.extract_tb(sys.exc_info()[2])[3:]
    res = six.text_type('')
    for item in trace:
        res += six.text_type("%s in line %d in %s : %s{[newline]}") % item
    return res
