# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from lxml import etree
from lucterios.framework.xferbasic import XferContainerException

class LucteriosErrorMiddleware(XferContainerException):

    def process_exception(self, request, exception):
        self.set_except(exception)
        self.responsesxml = etree.Element('REPONSES')
        self.responsexml = etree.SubElement(self.responsesxml, 'REPONSE')
        self._initialize(request)
        self.fillresponse()
        return self._finalize()
