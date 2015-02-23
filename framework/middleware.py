# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils import six

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.error import LucteriosException, get_error_trace

from logging import getLogger
from lxml import etree

class LucteriosErrorMiddleware(XferContainerAbstract):

    observer_name = 'CORE.Exception'
    exception = None

    def process_exception(self, request, exception):
        if not isinstance(exception, LucteriosException):
            getLogger(__name__).exception(exception)
        self.exception = exception
        self._initialize(request)
        self.fillresponse()
        return self._finalize()

    def fillresponse(self):
        expt = etree.SubElement(self.responsexml, "EXCEPTION")
        etree.SubElement(expt, 'MESSAGE').text = six.text_type(self.exception)
        if isinstance(self.exception, LucteriosException):
            etree.SubElement(expt, 'CODE').text = six.text_type(self.exception.code)
        else:
            etree.SubElement(expt, 'CODE').text = '0'
        etree.SubElement(expt, 'DEBUG_INFO').text = get_error_trace()
        etree.SubElement(expt, 'TYPE').text = self.exception.__class__.__name__
