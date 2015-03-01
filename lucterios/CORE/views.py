# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import describ_action, add_sub_menu, FORMTYPE_NOMODAL
from lucterios.framework.xferbasic import XferContainerMenu
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom,\
    XFER_DBOX_INFORMATION
from lucterios.framework.xfercomponents import XferCompLABEL, XferCompPassword, XferCompImage
from lucterios.framework.error import LucteriosException, IMPORTANT

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
class ChangePassword(XferContainerCustom):
    caption = _("_Password")
    icon = "passwd.png"

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value('images/passwd.png')
        img.set_location(0, 0, 1, 3)
        self.add_component(img)

        lbl = XferCompLABEL('lbl_oldpass')
        lbl.set_location(1, 0, 1, 1)
        lbl.set_value(_("old password"))
        self.add_component(lbl)
        pwd = XferCompPassword('oldpass')
        pwd.set_location(2, 0, 1, 1)
        self.add_component(pwd)

        lbl = XferCompLABEL('lbl_newpass1')
        lbl.set_location(1, 1, 1, 1)
        lbl.set_value(_("new password"))
        self.add_component(lbl)
        pwd = XferCompPassword('newpass1')
        pwd.set_location(2, 1, 1, 1)
        self.add_component(pwd)

        lbl = XferCompLABEL('lbl_newpass2')
        lbl.set_location(1, 2, 1, 1)
        lbl.set_value(_("new password (again)"))
        self.add_component(lbl)
        pwd = XferCompPassword('newpass2')
        pwd.set_location(2, 2, 1, 1)
        self.add_component(pwd)

        self.add_action(ModifyPassword().get_changed(_('Ok'), 'images/ok.png'), {})
        self.add_action(XferContainerAcknowledge().get_changed(_('Cancel'), 'images/cancel.png'), {})

@describ_action('')
class ModifyPassword(XferContainerAcknowledge):
    caption = _("_Password")
    icon = "passwd.png"

    def fillresponse(self, oldpass='', newpass1='', newpass2=''):
        if not self.request.user.check_password(oldpass):
            raise LucteriosException(IMPORTANT, _("Bad current password!"))

        if newpass1 != newpass2:

            raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
        self.request.user.set_password(newpass1)
        self.request.user.save()
        self.message(_("Password modify"), XFER_DBOX_INFORMATION)

@describ_action('CORE.change_parameter', FORMTYPE_NOMODAL, 'core.admin', _("To view and to modify main parameters."))
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
