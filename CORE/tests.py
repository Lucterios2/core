# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lucterios.framework.test import LucteriosTest, add_admin_user, add_empty_user
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XFER_DBOX_WARNING
from django.utils import six

class AuthentificationTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        LucteriosTest.setUp(self)
        add_admin_user()
        add_empty_user()

    def test_blank(self):
        response = self.client.call('/', {})
        if six.PY2:
            self.assertEqual(response.content, six.binary_type(''))
        else:
            self.assertEqual(response.content, six.binary_type('', 'ascii'))

    def test_menu_noconnect(self):
        self.call('/CORE/menu', {})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_attrib_equal('', 'source_extension', 'CORE')
        self.assert_attrib_equal('', 'source_action', 'menu')
        self.assert_xml_equal('', 'NEEDAUTH')
        self.assert_count_equal('CONNECTION', 0)

    def test_badconnect(self):
        self.call('/CORE/authentification', {})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_attrib_equal('', 'source_extension', 'CORE')
        self.assert_attrib_equal('', 'source_action', 'authentification')
        self.assert_xml_equal('', 'NEEDAUTH')
        self.assert_count_equal('CONNECTION', 0)

        self.call('/CORE/authentification', {'login':'', 'pass':''})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

        self.call('/CORE/authentification', {'login':'aaa', 'pass':'bbb'})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

    def test_connect(self):
        self.call('/CORE/authentification', {'login':'admin', 'pass':'admin'})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/TITLE', 'Lucterios standard')
        self.assert_xml_equal('CONNECTION/SUBTITLE', 'other subtitle')
        self.assert_xml_equal('CONNECTION/VERSION', '1.999')
        self.assert_xml_equal('CONNECTION/SERVERVERSION', '1.9')
        self.assert_xml_equal('CONNECTION/COPYRIGHT', '(c) ', (0, 4))
        self.assert_xml_equal('CONNECTION/LOGONAME', 'data:image/*;base64,', (0, 20))
        self.assert_xml_equal('CONNECTION/SUPPORT_EMAIL', 'support@', (0, 8))
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'admin')
        self.assert_xml_equal('CONNECTION/REALNAME', 'administrator ADMIN')

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')
        self.assert_attrib_equal('', 'source_extension', 'CORE')
        self.assert_attrib_equal('', 'source_action', 'exitConnection')

    def test_menu_connected(self):
        self.call('/CORE/authentification', {'login':'admin', 'pass':'admin'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/menu', {})
        self.assert_attrib_equal('', 'observer', 'CORE.Menu')
        self.assert_attrib_equal('', 'source_extension', 'CORE')
        self.assert_attrib_equal('', 'source_action', 'menu')
        self.assert_xml_equal("MENUS/MENU[@id='core.general']", six.text_type('Général'))
        self.assert_xml_equal("MENUS/MENU[@id='core.general']/MENU[@id='CORE/changerpassword']", 'Mot de _passe')
        self.assert_xml_equal("MENUS/MENU[@id='core.admin']", 'Administration')

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

        self.call('/CORE/menu', {})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_xml_equal('', 'NEEDAUTH')

    def test_menu_reconnected(self):
        self.call('/CORE/authentification', {'login':'admin', 'pass':'admin'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/authentification', {})
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'admin')
        self.assert_xml_equal('CONNECTION/REALNAME', 'administrator ADMIN')

        self.call('/CORE/authentification', {'login':'empty', 'pass':'empty'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/authentification', {'info':'true'})
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'empty')
        self.assert_xml_equal('CONNECTION/REALNAME', 'empty NOFULL')

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

class ContainerAcknowledgeTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    xfer_class = XferContainerAcknowledge

    def setUp(self):
        LucteriosTest.setUp(self)
        self.value = False

    def test_simple(self):
        self.call('/customer/details', {'id':12, 'value':'abc'}, False)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="id"]', '12')
        self.assert_xml_equal('CONTEXT/PARAM[@name="value"]', 'abc')
        self.assert_count_equal('CLOSE_ACTION', 0)

    def test_close(self):
        def fillresponse_close():
            self.factory.xfer.set_close_action(XferContainerAcknowledge().get_changed("close", "", "customer", "list"))
        self.factory.xfer.fillresponse = fillresponse_close
        self.call('/customer/details', {}, False)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTION', 0)
        self.assert_count_equal('CLOSE_ACTION', 1)
        self.assert_count_equal('CLOSE_ACTION/ACTION', 1)
        self.assert_xml_equal('CLOSE_ACTION/ACTION', "close")
        self.assert_attrib_equal('CLOSE_ACTION/ACTION', 'extension', "customer")
        self.assert_attrib_equal('CLOSE_ACTION/ACTION', 'action', "list")

    def test_redirect(self):
        def fillresponse_redirect():
            self.factory.xfer.redirect_action(XferContainerAcknowledge().get_changed("redirect", "", "customer", "list"))
        self.factory.xfer.fillresponse = fillresponse_redirect
        self.call('/customer/details', {}, False)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTION', 1)
        self.assert_xml_equal('ACTION', "redirect")
        self.assert_attrib_equal('ACTION', 'extension', "customer")
        self.assert_attrib_equal('ACTION', 'action', "list")

    def test_confirme(self):
        self.value = False
        def fillresponse_confirme():
            if self.factory.xfer.confirme("Do you want?"):
                self.value = True
        self.factory.xfer.fillresponse = fillresponse_confirme
        self.call('/customer/details', {}, False)
        self.assertEqual(self.value, False)
        self.assert_attrib_equal('', 'observer', 'Core.DialogBox')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_attrib_equal('CONTEXT/PARAM', 'name', 'CONFIRME')
        self.assert_xml_equal('CONTEXT/PARAM', 'YES')
        self.assert_attrib_equal('TEXT', 'type', '2')
        self.assert_xml_equal('TEXT', 'Do you want?')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_xml_equal('ACTIONS/ACTION[1]', 'Oui')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'icon', 'images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'extension', 'customer')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'action', 'details')
        self.assert_xml_equal('ACTIONS/ACTION[2]', 'Non')
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'icon', 'images/cancel.png')
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'action', None)

        self.call('/customer/details', {'CONFIRME':'YES'}, False)
        self.assertEqual(self.value, True)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

    def test_message(self):
        self.value = False
        def fillresponse_message():
            self.factory.xfer.message("Finished!", XFER_DBOX_WARNING)
        self.factory.xfer.fillresponse = fillresponse_message
        self.call('/customer/details', {}, False)
        self.assert_attrib_equal('', 'observer', 'Core.DialogBox')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_attrib_equal('TEXT', 'type', '3')
        self.assert_xml_equal('TEXT', 'Finished!')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_xml_equal('ACTIONS/ACTION', 'Ok')
        self.assert_attrib_equal('ACTIONS/ACTION', 'icon', 'images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION', 'action', None)
