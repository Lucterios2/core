# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from lucterios.framework.decorators import url_view
from lucterios.framework.xferview import XferContainerAbstract
from lucterios.framework.xferview import XferContainerAcknowledge

@url_view('')
class Authentification(XferContainerAbstract):
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
        from lxml import etree
        connextion = etree.SubElement(self.responsexml, "CONNECTION")
        etree.SubElement(connextion, 'TITLE').text = 'Lucterios'
        etree.SubElement(connextion, 'SUBTITLE').text = ''
        etree.SubElement(connextion, 'VERSION').text = '1.999'
        etree.SubElement(connextion, 'SERVERVERSION').text = '1.999'
        etree.SubElement(connextion, 'COPYRIGHT').text = '(c) 2015 SdLibre'
        etree.SubElement(connextion, 'LOGONAME').text = ''
        etree.SubElement(connextion, 'SUPPORT_EMAIL').text = 'info@sd-libre.fr'
        etree.SubElement(connextion, 'INFO_SERVER').text = ''
        if self.request.user.is_authenticated():
            etree.SubElement(connextion, 'LOGIN').text = self.request.user.username
            etree.SubElement(connextion, 'REALNAME').text = "%s %s" % (self.request.user.first_name, self.request.user.last_name)
        else:
            etree.SubElement(connextion, 'LOGIN').text = ''
            etree.SubElement(connextion, 'REALNAME').text = ''
        self.responsexml.text = "OK"

    def must_autentificate(self, mess):
        self.responsexml.text = mess

@url_view('')
class ExitConnection(XferContainerAcknowledge):

    def fillresponse(self):
        from django.contrib.auth import logout
        self.caption = u"Déconnexion"
        logout(self.request)

