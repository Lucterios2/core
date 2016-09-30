# -*- coding: utf-8 -*-
'''
Views for login/logoff in Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import MenuManage, FORMTYPE_MODAL, CLOSE_NO,\
    SELECT_NONE, get_actions_xml
from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.parameters import Params, secure_mode_connect
from lucterios.framework import signal_and_lock


def get_info_server():
    res = []
    from django import VERSION
    from django.conf import settings
    from django.utils.module_loading import import_module
    for appname in settings.INSTALLED_APPS:
        if ("django" not in appname) and ("lucterios.framework" != appname):
            appmodule = import_module(appname)
            if hasattr(appmodule, '__title__'):
                try:
                    app_title = appmodule.__title__()
                except TypeError:
                    app_title = six.text_type(appmodule.__title__)
                res.append(six.text_type("%s=%s") %
                           (app_title, appmodule.__version__))
    res.append("")
    from platform import python_version, uname
    django_version = "%d.%d.%d" % (VERSION[0], VERSION[1], VERSION[2])
    os_version = "%s %s %s" % (uname()[0], uname()[4], uname()[2])
    res.append(six.text_type("{[i]}%s - Python %s - Django %s{[/i]}") %
               (os_version, python_version(), django_version))
    return six.text_type("{[br/]}").join(res)


@MenuManage.describ('')
class Authentification(XferContainerAbstract):
    caption = 'info'
    observer_name = 'core.auth'

    def fillresponse(self, username, password, info):
        from django.contrib.auth import authenticate, login, logout
        if (username is not None) and (password is not None):
            if self.request.user.is_authenticated():
                logout(self.request)
            if (username == '') and (password == '') and not secure_mode_connect():
                self.params["ses"] = 'null'
                self.get_connection_info()
            else:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(self.request, user)
                    self.params["ses"] = user.username
                    self.get_connection_info()
                else:
                    self.must_autentificate('BADAUTH')
        elif info is not None:
            self.get_connection_info()
        else:
            if self.request.user.is_authenticated() or not secure_mode_connect():
                self.get_connection_info()
            else:
                self.must_autentificate('NEEDAUTH')

    def must_autentificate(self, mess):
        self.responsexml.text = mess
        if secure_mode_connect():
            basic_actions = []
            signal_and_lock.Signal.call_signal("auth_action", basic_actions)
            actions = []
            for action in basic_actions:
                if self.check_action_permission(action):
                    actions.append((action, FORMTYPE_MODAL, CLOSE_NO, SELECT_NONE, None))
            if len(actions) != 0:
                self.responsexml.append(get_actions_xml(actions))

    def get_connection_info(self):
        from lxml import etree
        from django.conf import settings
        import lucterios.CORE
        import os
        connextion = etree.SubElement(self.responsexml, "CONNECTION")
        etree.SubElement(connextion, 'TITLE').text = six.text_type(settings.APPLIS_NAME)
        etree.SubElement(connextion, 'SUBTITLE').text = settings.APPLIS_SUBTITLE()
        etree.SubElement(connextion, 'VERSION').text = six.text_type(settings.APPLIS_VERSION)
        etree.SubElement(connextion, 'SERVERVERSION').text = six.text_type(lucterios.CORE.__version__)
        etree.SubElement(connextion, 'COPYRIGHT').text = six.text_type(settings.APPLIS_COPYRIGHT)
        etree.SubElement(connextion, 'LOGONAME').text = settings.APPLIS_LOGO
        etree.SubElement(connextion, 'BACKGROUND').text = settings.APPLIS_BACKGROUND
        etree.SubElement(connextion, 'SUPPORT_EMAIL').text = six.text_type(settings.APPLI_EMAIL)
        etree.SubElement(connextion, 'SUPPORT_HTML').text = six.text_type(settings.APPLI_SUPPORT())
        etree.SubElement(connextion, 'INFO_SERVER').text = get_info_server()
        setting_module_name = os.getenv("DJANGO_SETTINGS_MODULE", "???.???")
        etree.SubElement(connextion, 'INSTANCE').text = setting_module_name.split('.')[0]
        etree.SubElement(connextion, 'LANGUAGE').text = self.language
        etree.SubElement(connextion, 'MODE').text = six.text_type(Params.getvalue("CORE-connectmode"))
        if self.request.user.is_authenticated():
            etree.SubElement(connextion, 'LOGIN').text = self.request.user.username
            etree.SubElement(connextion, 'REALNAME').text = "%s %s" % (self.request.user.first_name, self.request.user.last_name)
            etree.SubElement(connextion, 'EMAIL').text = self.request.user.email
        else:
            etree.SubElement(connextion, 'LOGIN').text = ''
            etree.SubElement(connextion, 'REALNAME').text = ''
            etree.SubElement(connextion, 'EMAIL').text = ''
        self.responsexml.text = "OK"


@MenuManage.describ('')
class ExitConnection(XferContainerAcknowledge):
    caption = 'exit'

    def fillresponse(self):
        from django.contrib.auth import logout
        self.caption = _("Disconnect")
        logout(self.request)
