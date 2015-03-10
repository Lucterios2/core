# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from lxml import etree
from lucterios.framework.xferbasic import XferContainerException, XferContainerAbstract
from lucterios.framework.error import LucteriosRedirectException
from lucterios.framework.tools import check_permission

class LucteriosErrorMiddleware(XferContainerException):

    def process_exception(self, request, exception):
        self.set_except(exception)
        self.closeaction = None
        if isinstance(exception, LucteriosRedirectException) and (exception.redirectclassaction is not None):
            redirectaction = exception.redirectclassaction()
            if isinstance(redirectaction, XferContainerAbstract) and check_permission(redirectaction, self.request):
                self.closeaction = (redirectaction, {})
        self.responsesxml = etree.Element('REPONSES')
        self.responsexml = etree.SubElement(self.responsesxml, 'REPONSE')
        self._initialize(request)
        self.fillresponse()
        return self._finalize()
