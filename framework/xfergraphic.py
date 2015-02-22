# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from lxml import etree

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.xfercomponents import XferCompTab, XferCompImage, XferCompLabelForm, XferCompButton
from lucterios.framework.tools import check_permission, get_action_xml, get_actions_xml
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
        self.fillresponse(**self._get_params())
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
        elif self.traitment_data != None:
            dlg = XferContainerCustom()
            dlg.caption = self.caption
            dlg.extension = self.extension
            dlg.action = self.action
            img_title = XferCompImage('img_title')
            img_title.set_location(0, 0, 1, 2)
            img_title.set_value(self.traitment_data[0])
            dlg.add_component(img_title)

            lbl = XferCompLabelForm("info")
            lbl.set_location(1, 0)
            dlg.add_component(lbl)
            if self.getparam("RELOAD") is not None:
                lbl.set_value("{[newline]}{[center]}" + self.traitment_data[2] + "{[/center]}")
                dlg.add_action(XferContainerAbstract().get_changed(_("Close"), "images/close.png"))
            else:
                lbl.set_value("{[newline]}{[center]}" + self.traitment_data[1] + "{[/center]}")
                kwargs["RELOAD"] = "YES"
                btn = XferCompButton("Next")
                btn.set_location(1, 1)
                btn.set_size(50, 300)
                btn.set_action(self.request, self.get_changed(_('Traitment...'), ""))
                btn.java_script = "parent.refresh()"
                dlg.add_component(btn)
                dlg.add_action(XferContainerAbstract().get_changed(_("Cancel"), "images/cancel.png"))
            return dlg.get(request, *args, **kwargs)
        else:
            return self._finalize()

    def _finalize(self):
        if self.redirect_act != None:
            act_xml = get_action_xml(self.redirect_act, {})
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
        if len(self.actions) != 0:
            self.responsexml.append(get_actions_xml(self.actions))
        return XferContainerAbstract._finalize(self)


class XferContainerCustom(XferContainerAbstract):

    observer_name = "Core.Custom"

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.actions = []
        self.components = {}
        self.tab = 0

    def add_component(self, component):
        component.tab = self.tab
        comp_id = component.get_id()
        self.components[comp_id] = component

    def resize(self, col, hmin, vmin):
        for comp in self.components.values():
            if (comp.col == col) and (comp.colspan == 1):
                comp.set_size(vmin, hmin)

    def find_tab(self, tab_name):
        num = -1
        index = 0
        for comp in self.components.values():
            if 'XferCompTab' == comp.__class__:
                index = max(index, comp.tab)
                if comp.value == tab_name:
                    num = comp.tab
        if isinstance(tab_name, six.text_type):
            return num
        else:
            return index

    def new_tab(self, tab_name, num=-1):
        old_num = self.find_tab(tab_name)
        if old_num == -1:
            if num == -1:
                self.tab = self.find_tab(None) + 1
            else:
                for comp in self.components.values():
                    if comp.tab >= num:
                        comp.tab = comp.tab + 1
                self.tab = num
            new_tab = XferCompTab()
            new_tab.set_value(tab_name)
            new_tab.set_location(-1, -1)
            self.add_component(new_tab)
        else:
            self.tab = old_num
    def get_component_count(self):
        if self.components == None:
            return 0
        else:
            return len(self.components)

    def get_components(self, cmp_idx):
        if isinstance(cmp_idx, six.integer_types):
            nb_comp = len(self.components)
            if cmp_idx < 0:
                cmp_idx = nb_comp + cmp_idx
            if (cmp_idx >= 0) and (cmp_idx < nb_comp):
                list_ids = self.components.keys()
                comp_id = list_ids[cmp_idx]
                return self.components[comp_id]
            else:
                return cmp_idx - nb_comp
        elif isinstance(cmp_idx, six.text_type):
            comp_res = None
            for comp in self.components.values():
                if comp.name == cmp_idx:
                    comp_res = comp
            return comp_res
        else:
            return None

    def remove_components(self, cmp_idx):
        if isinstance(cmp_idx, six.integer_types):
            nb_comp = len(self.components)
            if cmp_idx < 0:
                cmp_idx = nb_comp + cmp_idx
            if (cmp_idx >= 0) and (cmp_idx < nb_comp):
                list_ids = self.components.keys()
                comp_id = list_ids[cmp_idx]
                del self.components[comp_id]
        elif isinstance(cmp_idx, six.text_type):
            comp_id = ''
            for key, comp in self.components.items():
                if comp.name == cmp_idx:
                    comp_id = key
            if comp_id != '':
                del self.components[comp_id]

    def add_action(self, action, pos_act=-1, **option):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            if pos_act != -1:
                self.actions.insert(pos_act, (action, option))
            else:
                self.actions.append((action, option))

    def get_sort_components(self):
        final_components = {}
        for comp in self.components.values():
            comp_id = comp.get_id()
            final_components[comp_id] = comp
        return final_components  # TODO: check order

    def _finalize(self):
        if len(self.components) != 0:
            final_components = self.get_sort_components()
            xml_comps = etree.SubElement(self.responsexml, "COMPONENTS")
            for comp in final_components.values():
                xml_comp = comp.get_reponse_xml()
                xml_comps.append(xml_comp)
        if len(self.actions) != 0:
            self.responsexml.append(get_actions_xml(self.actions))
        return XferContainerAbstract._finalize(self)
