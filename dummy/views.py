# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import describ_action, add_sub_menu, FORMTYPE_NOMODAL
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XFER_DBOX_INFORMATION

add_sub_menu('dummy.foo', None, 'dummy/images/10.png', _('Dummy'), _('Dummy menu'), 20)

@describ_action('', FORMTYPE_NOMODAL, 'dummy.foo', _("Bidule action."))
class Bidule(XferContainerAcknowledge):
    caption = _("_Bidule")
    icon = "1.png"

    def fillresponse(self):
        from lucterios.framework.error import LucteriosException, GRAVE
        raise LucteriosException(GRAVE, "Error of bidule")

@describ_action('', FORMTYPE_NOMODAL, 'dummy.foo', _("Truc action."))
class Truc(XferContainerAcknowledge):
    caption = _("_Truc")
    icon = "2.png"

    def fillresponse(self):
        self.message("Hello world!", XFER_DBOX_INFORMATION)
