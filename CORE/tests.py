# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lucterios.framework.test import LucteriosTest, add_admin_user, add_empty_user
from django.utils import six
from unittest.suite import TestSuite
from unittest import TestLoader
from lucterios.CORE import tests_framework, tests_usergroup

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

        self.call('/CORE/authentification', {'username':'', 'password':''})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

        self.call('/CORE/authentification', {'username':'aaa', 'password':'bbb'})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

    def test_connect(self):
        self.call('/CORE/authentification', {'username':'admin', 'password':'admin'})
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
        self.call('/CORE/authentification', {'username':'admin', 'password':'admin'})
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
        self.call('/CORE/authentification', {'username':'admin', 'password':'admin'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/authentification', {})
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'admin')
        self.assert_xml_equal('CONNECTION/REALNAME', 'administrator ADMIN')

        self.call('/CORE/authentification', {'username':'empty', 'password':'empty'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/authentification', {'info':'true'})
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'empty')
        self.assert_xml_equal('CONNECTION/REALNAME', 'empty NOFULL')

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

def suite():
    # pylint: disable=redefined-outer-name
    suite = TestSuite()
    loader = TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(AuthentificationTest))
    suite.addTest(loader.loadTestsFromTestCase(tests_framework.ContainerAcknowledgeTest))
    suite.addTest(loader.loadTestsFromTestCase(tests_usergroup.UserGroupTest))
    return suite
