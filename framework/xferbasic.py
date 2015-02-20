# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lxml import etree

from django.views.generic import View
from django.http import HttpResponse
from django.utils import translation

from lucterios.framework.tools import check_permission, raise_bad_permission, get_action_xml, menu_key_to_comp

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
            etree.SubElement(self.responsexml, "TITLE").text = str(self.caption.replace('_', ''))
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
