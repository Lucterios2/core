# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from lxml import etree

from django.views.generic import View
from django.http import HttpResponse
from django.utils import translation

from lucterios.framework.tools import check_permission, raise_bad_permission, get_action_xml, menu_key_to_comp
from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_YES

XFER_DBOX_INFORMATION = 1
XFER_DBOX_CONFIRMATION = 2
XFER_DBOX_WARNING = 3
XFER_DBOX_ERROR = 4

class XferContainerAbstract(View):

    observer_name = ''
    extension = ""
    action = ""
    caption = ""
    closeaction = None
    icon = ""
    url_text = ""
    modal = None

    def __init__(self, **kwargs):
        View.__init__(self, **kwargs)
        self.request = None
        self.params = {}
        self.responsesxml = etree.Element('REPONSES')
        self.responsexml = etree.SubElement(self.responsesxml, 'REPONSE')

    def get_changed(self, caption, icon, extension=None, action=None):
        self.caption = caption
        self.icon = icon
        if extension is not None:
            self.extension = extension
        if action is not None:
            self.action = action
        return self

    def getparam(self, key):
        if key in self.params.keys():
            return self.params[key]
        else:
            return None

    def _initialize(self, request, *_, **kwargs):
        raise_bad_permission(self, request)
        _, self.extension, self.action = request.path.split('/')
        self.request = request
        for key in kwargs.keys():
            self.params[key] = kwargs[key]
        for key in request.GET.keys():
            self.params[key] = request.GET[key]
        for key in request.POST.keys():
            self.params[key] = request.POST[key]
        language = translation.get_language_from_request(request)
        translation.activate(language)

    def set_close_action(self, action, **option):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            self.closeaction = (action, option)

    def fillresponse(self):
        pass

    def _finalize(self):
        if self.caption != '':
            etree.SubElement(self.responsexml, "TITLE").text = str(self.caption)
        self.responsexml.attrib['observer'] = self.observer_name
        self.responsexml.attrib['source_extension'] = self.extension
        self.responsexml.attrib['source_action'] = self.action
        if len(self.params) > 0:
            context = etree.SubElement(self.responsexml, "CONTEXT")
            for key, value in self.params.items():
                new_param = etree.SubElement(context, 'PARAM')
                new_param.text = value
                new_param.attrib['name'] = key
        if self.closeaction != None:
            etree.SubElement(self.responsexml, "CLOSE_ACTION").append(get_action_xml(self.closeaction[0], **self.closeaction[1]))
        return HttpResponse(etree.tostring(self.responsesxml, xml_declaration=True, pretty_print=True, encoding='utf-8'))

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        self.fillresponse()
        return self._finalize()

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

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
            dlg.caption = "Message"
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
                etree.SubElement(self.responsexml, "CLOSE_ACTION").append(act_xml)
        return XferContainerAbstract._finalize(self)

class XferContainerAuth(XferContainerAbstract):
    observer_name = 'CORE.Auth'

    def fillresponse(self):
        from django.contrib.auth import authenticate, login, logout
        username = self.getparam('login')
        password = self.getparam('pass')
        if (login is not None) and (password is not None):
            if self.request.user.is_authenticated():
                logout(self.request)
            user = authenticate(username=username, password=password)
            if user is not None:
                login(self.request, user)
                self.params["ses"] = user.username
                self.get_connection_info()
            else:
                self.must_autentificate('BADAUTH')
        elif self.getparam('info') is not None:
            self.get_connection_info()
        else:
            if self.request.user.is_authenticated():
                self.get_connection_info()
            else:
                self.must_autentificate('NEEDAUTH')

    def get_connection_info(self):
        pass

    def must_autentificate(self, mess):
        self.responsexml.text = mess

class XferContainerMenu(XferContainerAbstract):

    observer_name = 'CORE.Menu'

    def fill_menu(self, parentref, parentxml):
        from lucterios.framework.tools import MENU_LIST
        if parentref in MENU_LIST.keys():
            sub_menus = MENU_LIST[parentref]
            sub_menus.sort(key=menu_key_to_comp)  # menu_comp)
            for sub_menu_item in sub_menus:
                if check_permission(sub_menu_item[0], self.request):
                    new_xml = get_action_xml(sub_menu_item[0], sub_menu_item[1], "MENU")
                    if new_xml != None:
                        parentxml.append(new_xml)
                        self.fill_menu(sub_menu_item[0].url_text, new_xml)

    def fillresponse(self):
        main_menu = etree.SubElement(self.responsexml, "MENUS")
        self.fill_menu(None, main_menu)

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
