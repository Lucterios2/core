# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from lxml import etree

from django.views.generic import View
from django.http import HttpResponse

def check_action_rigth(action):
    return isinstance(action, XferAction)  # add check right

class XferAction(object):

    title = ""
    icon = ""
    extension = ""
    action = ""
    close = ""
    modal = ""
    select = ""
    _tag = ""

    def __init__(self, title, icon="", extension="", action="", modal="", close="", select=""):
        self.title = title
        self.icon = icon

        # if( is_file($rootPath."extensions/$extension/images/$icon"))
        #    self.icon = $rootPath."extensions/$extension/images/$icon";
        # else if( is_file($rootPath."images/$icon"))
        #    self.icon = $rootPath."images/$icon";
        # else if( is_file($rootPath."$icon"))
        #    self.icon = $rootPath.$icon;
        self.extension = extension
        self.action = action
        self.close = close
        self.modal = modal
        self.select = select
        self._tag = "ACTION"

    def get_xml(self):
        actionxml = etree.Element('self._tag')
        if self.icon != "":
            actionxml.attrib['icon'] = self.icon
            # actionxml.attrib['sizeicon']=filesize(self.icon)
        if self.extension != "":
            actionxml.attrib['extension'] = self.extension
        if self.action != "":
            actionxml.attrib['action='] = self.action
        if isinstance(self.close, int):
            actionxml.attrib['close'] = self.close
        if isinstance(self.modal, int):
            actionxml.attrib['modal'] = self.modal
        if isinstance(self.select, int):
            actionxml.attrib['unique'] = self.select
        actionxml.text = self.title
        return actionxml

class XferContainerAbstract(View):

    observer_name = ''
    extension = ""
    action = ""
    caption = ""
    closeaction = None

    def __init__(self, **kwargs):
        View.__init__(self, **kwargs)
        self.request = None
        self.params = {}
        self.responsexml = etree.Element('REPONSE')

    def getparam(self, key):
        if self.params.has_key(key):
            return self.params[key]
        else:
            return None

    def _initialize(self, request, *_, **kwargs):
        self.request = request
        for key in kwargs.keys():
            self.params[key] = kwargs[key]
        for key in request.GET.keys():
            self.params[key] = request.GET[key]
        for key in request.POST.keys():
            self.params[key] = request.POST[key]

    def set_close_action(self, action):
        if check_action_rigth(action):
            self.closeaction = action

    def fillresponse(self):
        pass

    def _finalize(self):
        etree.SubElement(self.responsexml, "TITLE").text = self.caption
        self.responsexml.attrib['observer'] = self.observer_name
        self.responsexml.attrib['source_extension'] = self.extension
        self.responsexml.attrib['source_action'] = self.action
        context = etree.SubElement(self.responsexml, "CONTEXT")
        for key, value in self.params.items():
            new_param = etree.SubElement(context, 'PARAM')
            new_param.text = value
            new_param.attrib['name'] = key
        if (self.closeaction != None) and isinstance(self.closeaction, XferAction):
            etree.SubElement(self.responsexml, "CLOSE_ACTION").append(self.closeaction.get_xml())

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        self.fillresponse()
        self._finalize()
        return HttpResponse(etree.tostring(self.responsexml, pretty_print=True), mimetype='application/xml')

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
        if check_action_rigth(action):
            self.redirect_act = action

    def fillresponse(self):
        pass

    def _finalize(self):
        XferContainerAbstract._finalize(self)
        if self.redirect_act != None:
            self.responsexml.append(self.redirect_act.get_xml())
