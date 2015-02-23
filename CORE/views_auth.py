# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import describ_action
from lucterios.framework.xferbasic import XferContainerAuth
from lucterios.framework.xfergraphic import XferContainerAcknowledge

def get_info_server():
    res = []
    from django.conf import settings
    from django.utils.module_loading import import_module
    for appname in settings.INSTALLED_APPS:
        if not "django" in appname:
            appmodule = import_module(appname)
            res.append(six.text_type("%s=%s") % (appmodule.__title__(), appmodule.__version__))
    from platform import python_version, uname
    res.append(six.text_type("{[i]}Python %s - %s %s %s{[/i]}") % (python_version(), uname()[0], uname()[4], uname()[2]))
    return six.text_type("{[newline]}").join(res)

@describ_action('')
class Authentification(XferContainerAuth):

    def get_connection_info(self):
        from lxml import etree
        from inspect import isfunction
        from django.conf import settings
        import lucterios.CORE
        connextion = etree.SubElement(self.responsexml, "CONNECTION")
        etree.SubElement(connextion, 'TITLE').text = six.text_type(settings.APPLIS_NAME)
        if isinstance(settings.APPLIS_SUBTITLE, str):
            etree.SubElement(connextion, 'SUBTITLE').text = six.text_type(settings.APPLIS_SUBTITLE)
        if isfunction(settings.APPLIS_SUBTITLE):
            etree.SubElement(connextion, 'SUBTITLE').text = settings.APPLIS_SUBTITLE()
        else:
            etree.SubElement(connextion, 'SUBTITLE').text = ""
        etree.SubElement(connextion, 'VERSION').text = six.text_type(settings.APPLIS_VERSION)
        etree.SubElement(connextion, 'SERVERVERSION').text = six.text_type(lucterios.CORE.__version__)
        etree.SubElement(connextion, 'COPYRIGHT').text = six.text_type(settings.APPLIS_COPYRIGHT)
        etree.SubElement(connextion, 'LOGONAME').text = settings.APPLIS_LOGO
        etree.SubElement(connextion, 'SUPPORT_EMAIL').text = six.text_type(settings.APPLI_EMAIL)
        etree.SubElement(connextion, 'INFO_SERVER').text = get_info_server()
        if self.request.user.is_authenticated():
            etree.SubElement(connextion, 'LOGIN').text = self.request.user.username
            etree.SubElement(connextion, 'REALNAME').text = "%s %s" % (self.request.user.first_name, self.request.user.last_name)
        else:
            etree.SubElement(connextion, 'LOGIN').text = ''
            etree.SubElement(connextion, 'REALNAME').text = ''
        self.responsexml.text = "OK"

@describ_action('')
class ExitConnection(XferContainerAcknowledge):

    def fillresponse(self):
        from django.contrib.auth import logout
        self.caption = _("Disconnect")
        logout(self.request)

