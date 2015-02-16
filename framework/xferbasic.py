# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from lxml import etree

from django.views.generic import View
from django.http import HttpResponse

from lucterios.framework.tools import check_permission, raise_bad_permission, get_action_xml

class XferContainerAbstract(View):

    observer_name = ''
    extension = ""
    action = ""
    caption = ""
    closeaction = None
    icon = ""

    def __init__(self, **kwargs):
        View.__init__(self, **kwargs)
        self.request = None
        self.params = {}
        self.responsesxml = etree.Element('REPONSES')
        self.responsexml = etree.SubElement(self.responsesxml, 'REPONSE')

    def getparam(self, key):
        if self.params.has_key(key):
            return self.params[key]
        else:
            return None

    def _initialize(self, request, *_, **kwargs):
        _, self.extension, self.action = request.path.split('/')
        self.request = request
        for key in kwargs.keys():
            self.params[key] = kwargs[key]
        for key in request.GET.keys():
            self.params[key] = request.GET[key]
        for key in request.POST.keys():
            self.params[key] = request.POST[key]

    def set_close_action(self, action, **option):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            self.closeaction = (action, option)

    def fillresponse(self):
        pass

    def _finalize(self):
        if self.caption != '':
            etree.SubElement(self.responsexml, "TITLE").text = self.caption
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

    def get(self, request, *args, **kwargs):
        raise_bad_permission(self, request)
        self._initialize(request, *args, **kwargs)
        self.fillresponse()
        self._finalize()
        return HttpResponse(etree.tostring(self.responsesxml, xml_declaration=True, pretty_print=True, encoding='utf-8'), mimetype='application/xml')

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

class XferContainerAcknowledge(XferContainerAbstract):

    observer_name = 'Core.Acknowledge'
    title = ""
    msg = ""
    traitment_data = None
    typemsg = 1
    redirect_act = None

    def confirme(self, title):
        self.title = title
        if self.title != "":
            if self.params.has_key("CONFIRME"):
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
        if self.params.has_key("RELOAD"):
            return self.params["RELOAD"] != ""
        else:
            return False

    def redirect_action(self, action):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            self.redirect_act = action

    def fillresponse(self):
        pass

    def _finalize(self):
        XferContainerAbstract._finalize(self)
        if self.redirect_act != None:
            etree.SubElement(self.responsexml, "CLOSE_ACTION").append(get_action_xml(self.redirect_act))

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
        if MENU_LIST.has_key(parentref):
            sub_menus = MENU_LIST[parentref]
            for sub_menu_item in sub_menus:
                print sub_menu_item
                if check_permission(sub_menu_item[0], self.request):
                    new_xml = get_action_xml(sub_menu_item[0], sub_menu_item[1], "MENU")
                    if new_xml != None:
                        parentxml.append(new_xml)
                        self.fill_menu(sub_menu_item[0].url_text, new_xml)

    def fillresponse(self):
        main_menu = etree.SubElement(self.responsexml, "MENUS")
        self.fill_menu("", main_menu)

