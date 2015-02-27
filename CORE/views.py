# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import describ_action, add_sub_menu, FORMTYPE_NOMODAL
from lucterios.framework.xferbasic import XferContainerMenu
from lucterios.framework.xfergraphic import XferContainerAcknowledge

add_sub_menu('core.general', None, 'images/general.png', _('General'), _('Generality'), 1)
add_sub_menu('core.admin', None, 'images/admin.png', _('Management'), _('Manage settings and configurations.'), 100)

@describ_action('')
class Menu(XferContainerMenu):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return XferContainerMenu.get(self, request, *args, **kwargs)
        else:
            from lucterios.CORE.views_auth import Authentification
            auth = Authentification()
            return auth.get(request, *args, **kwargs)

@describ_action('', FORMTYPE_NOMODAL, 'core.general', _("To Change your password."))
class ChangerPassword(XferContainerAcknowledge):
    caption = _("_Password")
    icon = "passwd.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.admin', _("To view and to modify main parameters."))
class Configuration(XferContainerAcknowledge):
    caption = _("Main configuration")
    icon = "config.png"

add_sub_menu("core.extensions", 'core.admin', "images/config_ext.png", _("_Extensions (conf.)"), _("To manage of modules configurations."), 20)

# add_sub_menu("core.print", 'core.admin', "images/PrintReport.png", _("_Report and print"), _("To manage reports and tools of printing."), 30)
#

# @describ_action('', FORMTYPE_NOMODAL, 'core.print', _("To Manage printing models."))
# class PrintmodelList(XferContainerAcknowledge):
#     caption = _("_Report models")
#     icon = "PrintReportModel.png"
#

# @describ_action('', FORMTYPE_NOMODAL, 'core.print', _("To print old saved report."))
# class FinalreportList(XferContainerAcknowledge):
#     caption = _("_Saved reports")
#     icon = "PrintReportSave.png"
#

# @describ_action('', FORMTYPE_NOMODAL, 'core.print', _("To manage boards of labels"))
# class EtiquettesListe(XferContainerAcknowledge):
#     caption = _("_Labels")
#     icon = "PrintReportLabel.png"
