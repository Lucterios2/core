# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
'''
Django middleware for Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from lxml import etree
from lucterios.framework.xferbasic import XferContainerException
from lucterios.framework.error import LucteriosRedirectException
from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_YES


class LucteriosErrorMiddleware(XferContainerException):

    def process_exception(self, request, exception):
        self.request = request
        self.set_except(exception)
        self.closeaction = None
        if isinstance(exception, LucteriosRedirectException) and (exception.redirectclassview is not None):
            redirectaction = exception.redirectclassview.get_action()
            if self.check_action_permission(redirectaction):
                self.closeaction = (redirectaction, FORMTYPE_MODAL, CLOSE_YES, None)
        self.responsesxml = etree.Element('REPONSES')
        self.responsexml = etree.SubElement(self.responsesxml, 'REPONSE')
        self._initialize(request)
        self.fillresponse()
        self._finalize()
        return self.get_response()
