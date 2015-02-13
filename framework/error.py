# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from lucterios.framework.xferbasic import XferContainerAbstract

import logging

class LucteriosException(Exception):

    INTERNAL = 0
    CRITIC = 1
    GRAVE = 2
    IMPORTANT = 3
    MINOR = 4

    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code

def get_error_trace():
    import sys, traceback
    _, _, exc_tb = sys.exc_info()
    trace = traceback.extract_tb(exc_tb)[3:]
    res = ''
    for item in trace:
        res += "%s in line %d in %s : %s\n" % item
    return res

class LucteriosErrorMiddleware(XferContainerAbstract):

    observer_name = 'CORE.Exception'
    exception = None

    def process_exception(self, request, exception):
        from lxml import etree
        self.params = {}
        self.responsexml = etree.Element('REPONSE')
        if not isinstance(exception, Exception):
            return None
        logging.getLogger(__name__).exception(exception)
        self.exception = exception
        return self.get(request)

    def fillresponse(self):
        from lxml import etree
        expt = etree.SubElement(self.responsexml, "EXCEPTION")
        etree.SubElement(expt, 'MESSAGE').text = self.exception.message
        if isinstance(self.exception, LucteriosException):
            etree.SubElement(expt, 'CODE').text = str(self.exception.code)
        else:
            etree.SubElement(expt, 'CODE').text = '0'
        etree.SubElement(expt, 'DEBUG_INFO').text = get_error_trace()
        etree.SubElement(expt, 'TYPE').text = self.exception.__class__.__name__
