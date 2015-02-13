# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from lucterios.framework.tools import describ_action
from lucterios.framework.xferbasic import XferContainerAuth
from lucterios.framework.xferbasic import XferContainerAcknowledge

@describ_action('')
class Authentification(XferContainerAuth):

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

@describ_action('')
class ExitConnection(XferContainerAcknowledge):

    def fillresponse(self):
        from django.contrib.auth import logout
        self.caption = u"Déconnexion"
        logout(self.request)

