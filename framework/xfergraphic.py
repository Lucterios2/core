# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from lxml import etree

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.tools import check_permission, get_action_xml
from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_YES

class XferContainerAcknowledge(XferContainerAbstract):

    observer_name = 'Core.Acknowledge'
    title = ""
    msg = ""
    traitment_data = None
    typemsg = 1
    redirect_act = None

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.title = ""
        self.msg = ""
        self.traitment_data = None
        self.typemsg = 1
        self.redirect_act = None

    def confirme(self, title):
        self.title = title
        if self.title != "":
            if self.getparam("CONFIRME") is not None:
                return self.params["CONFIRME"] != ""
            else:
                return False
        else:
            return True

    def message(self, title, typemsg=1):
        self.msg = title
        self.typemsg = typemsg

    def traitment(self, icon, waiting_message, finish_message):
        self.traitment_data = [icon, waiting_message, finish_message]
        if self.getparam("RELOAD") is not None:
            return self.params["RELOAD"] != ""
        else:
            return False

    def redirect_action(self, action):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            self.redirect_act = action

    def fillresponse(self):
        pass

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        self.fillresponse()
        if (self.title != '') and (self.getparam("CONFIRME") != "YES"):
            kwargs["CONFIRME"] = "YES"
            dlg = XferContainerDialogBox()
            dlg.caption = "Confirmation"
            dlg.extension = self.extension
            dlg.action = self.action
            dlg.set_dialog(self.title, XFER_DBOX_CONFIRMATION)
            dlg.add_action(self.get_changed(_("Yes"), "images/ok.png"), modal=FORMTYPE_MODAL, close=CLOSE_YES)
            dlg.add_action(XferContainerAbstract().get_changed(_("No"), "images/cancel.png"))
            dlg.closeaction = self.closeaction
            return dlg.get(request, *args, **kwargs)
        elif self.msg != "":
            dlg = XferContainerDialogBox()
            dlg.caption = self.caption
            dlg.set_dialog(self.msg, self.typemsg)
            dlg.add_action(XferContainerAbstract().get_changed(_("Ok"), "images/ok.png"))
            dlg.closeaction = self.closeaction
            return dlg.get(request, *args, **kwargs)
        else:
            return self._finalize()

    def _finalize(self):
        if self.redirect_act != None:
            act_xml = get_action_xml(self.redirect_act)
            if act_xml is not None:
                self.responsexml.append(act_xml)
        return XferContainerAbstract._finalize(self)

XFER_DBOX_INFORMATION = 1
XFER_DBOX_CONFIRMATION = 2
XFER_DBOX_WARNING = 3
XFER_DBOX_ERROR = 4

class XferContainerDialogBox(XferContainerAbstract):

    observer_name = "Core.DialogBox"

    msgtype = XFER_DBOX_INFORMATION
    msgtext = ""
    actions = []

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.msgtype = XFER_DBOX_INFORMATION
        self.msgtext = ""
        self.actions = []

    def set_dialog(self, msgtext, msgtype):
        self.msgtype = msgtype
        self.msgtext = msgtext

    def add_action(self, action, **options):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            self.actions.append((action, options))

    def _finalize(self):
        text_dlg = etree.SubElement(self.responsexml, "TEXT")
        text_dlg.attrib['type'] = str(self.msgtype)
        text_dlg.text = str(self.msgtext)
        if len(self.actions) > 0:
            act_dlg = etree.SubElement(self.responsexml, "ACTIONS")
            for (action, options) in self.actions:
                new_xml = get_action_xml(action, **options)
                if new_xml != None:
                    act_dlg.append(new_xml)
        return XferContainerAbstract._finalize(self)
