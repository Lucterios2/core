# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, StubAction
from lucterios.framework.xferbasic import XferContainerMenu
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom, XFER_DBOX_INFORMATION
from lucterios.framework.xfercomponents import XferCompLABEL, XferCompPassword, XferCompImage, XferCompLabelForm
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock, tools
from lucterios.CORE.parameters import Params, secure_mode_connect
from lucterios.CORE.models import Parameter
from django.utils import six

MenuManage.add_sub('core.general', None, 'images/general.png', _('General'), _('Generality'), 1)
MenuManage.add_sub('core.admin', None, 'images/admin.png', _('Management'), _('Manage settings and configurations.'), 100)

@MenuManage.describ('')
class Unlock(XferContainerAcknowledge):

    def fillresponse(self):
        signal_and_lock.RecordLocker.unlock(self.request, self.params)

signal_and_lock.unlocker_action_class = Unlock

@MenuManage.describ('')
class Menu(XferContainerMenu):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated() or not secure_mode_connect():
            return XferContainerMenu.get(self, request, *args, **kwargs)
        else:
            from lucterios.CORE.views_auth import Authentification
            auth = Authentification()
            return auth.get(request, *args, **kwargs)

@MenuManage.describ(None, FORMTYPE_NOMODAL, 'core.general', _("To Change your password."))
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
        self.add_action(StubAction(_('Cancel'), 'images/cancel.png'), {})

@MenuManage.describ('')
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

@signal_and_lock.Signal.decorate('config')
def config_core(xfer):
    Params.fill(xfer, ['CORE-connectmode'], 1, 1)
    xfer.params['params'].append('CORE-connectmode')

@MenuManage.describ('CORE.change_parameter', FORMTYPE_NOMODAL, 'core.admin', _("To view and to modify main parameters."))
class Configuration(XferContainerCustom):
    caption = _("Main configuration")
    icon = "config.png"

    def fillresponse(self):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 10)
        img_title.set_value('images/config.png')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 3)
        lab.set_value('{[br/]}{[center]}{[b]}{[u]}%s{[/u]}{[/b]}{[/center]}' % _("Software configuration"))
        self.add_component(lab)
        self.params['params'] = []
        signal_and_lock.Signal.call_signal("config", self)
        self.add_action(ParamEdit().get_changed(_('Modify'), 'images/edit.png'), {'close':0})
        self.add_action(StubAction(_('Close'), 'images/close.png'), {})

@MenuManage.describ('CORE.add_parameter')
class ParamEdit(XferContainerCustom):
    caption = _("Parameters")
    icon = "config.png"

    def fillresponse(self, params=()):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0)
        img_title.set_value('images/config.png')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0)
        lab.set_value('{[br/]}{[center]}{[b]}{[u]}%s{[/u]}{[/b]}{[/center]}' % _("Edition of parameters"))
        self.add_component(lab)
        Params.fill(self, params, 1, 1, False)
        self.add_action(ParamSave().get_changed(_('Ok'), 'images/ok.png'), {})
        self.add_action(StubAction(_('Cancel'), 'images/cancel.png'), {})

@MenuManage.describ('CORE.add_parameter')
class ParamSave(XferContainerAcknowledge):
    caption = _("Parameters")
    icon = "config.png"

    def fillresponse(self, params=()):
        for pname in params:
            db_param = Parameter.objects.get(name=pname)  # pylint: disable=no-member
            if db_param.typeparam == 3:
                db_param.value = six.text_type(self.getparam(pname) == '1')
            else:
                db_param.value = self.getparam(pname)
            db_param.save()
        Params.clear()

MenuManage.add_sub("core.extensions", 'core.admin', "images/config_ext.png", _("_Extensions (conf.)"), _("To manage of modules configurations."), 20)

# MenuManage.add_sub("core.print", 'core.admin', "images/PrintReport.png", _("_Report and print"), _("To manage reports and tools of printing."), 30)
#

# @MenuManage.describ('', FORMTYPE_NOMODAL, 'core.print', _("To Manage printing models."))
# class PrintmodelList(XferContainerAcknowledge):
#     caption = _("_Report models")
#     icon = "PrintReportModel.png"
#

# @MenuManage.describ('', FORMTYPE_NOMODAL, 'core.print', _("To print old saved report."))
# class FinalreportList(XferContainerAcknowledge):
#     caption = _("_Saved reports")
#     icon = "PrintReportSave.png"
#

# @MenuManage.describ('', FORMTYPE_NOMODAL, 'core.print', _("To manage boards of labels"))
# class EtiquettesListe(XferContainerAcknowledge):
#     caption = _("_Labels")
#     icon = "PrintReportLabel.png"

tools.bad_permission_redirect_classaction = Menu
