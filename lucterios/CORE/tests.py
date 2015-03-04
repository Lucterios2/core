# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lucterios.framework.test import LucteriosTest, add_empty_user
from django.utils import six
from unittest.suite import TestSuite
from unittest import TestLoader
from lucterios.CORE import tests_framework, tests_usergroup
from lucterios.CORE.views import Configuration, ParamEdit, ParamSave
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import clear_parameters

class AuthentificationTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        LucteriosTest.setUp(self)
        add_empty_user()

    def test_blank(self):
        response = self.client.call('/', {})
        if six.PY2:
            self.assertEqual(response.content, six.binary_type(''))
        else:
            self.assertEqual(response.content, six.binary_type('', 'ascii'))

    def test_menu_noconnect(self):

        self.call('/CORE/menu', {})
        self.assert_observer('CORE.Auth', 'CORE', 'menu')
        self.assert_xml_equal('', 'NEEDAUTH')
        self.assert_count_equal('CONNECTION', 0)

    def test_badconnect(self):
        self.call('/CORE/authentification', {})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'NEEDAUTH')
        self.assert_count_equal('CONNECTION', 0)

        self.call('/CORE/authentification', {'username':'', 'password':''})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

        self.call('/CORE/authentification', {'username':'aaa', 'password':'bbb'})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

    def test_connect(self):
        self.call('/CORE/authentification', {'username':'admin', 'password':'admin'})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/TITLE', 'Lucterios standard')
        self.assert_xml_equal('CONNECTION/SUBTITLE', 'other subtitle')
        self.assert_xml_equal('CONNECTION/VERSION', '2.0.1.', (0, 6))
        self.assert_xml_equal('CONNECTION/SERVERVERSION', '2.0b', (0, 4))
        self.assert_xml_equal('CONNECTION/COPYRIGHT', '(c) ', (0, 4))
        self.assert_xml_equal('CONNECTION/LOGONAME', 'data:image/*;base64,', (0, 20))
        self.assert_xml_equal('CONNECTION/SUPPORT_EMAIL', 'support@', (0, 8))
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'admin')
        self.assert_xml_equal('CONNECTION/REALNAME', 'administrator ADMIN')
        self.assert_xml_equal('CONNECTION/MODE', '0')

        self.call('/CORE/exitConnection', {})
        self.assert_observer('Core.Acknowledge', 'CORE', 'exitConnection')

    def test_menu_connected(self):
        self.call('/CORE/authentification', {'username':'admin', 'password':'admin'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/menu', {})
        self.assert_observer('CORE.Menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU", 3)
        self.assert_xml_equal("MENUS/MENU[@id='core.general']", six.text_type('Général'))
        self.assert_xml_equal("MENUS/MENU[@id='core.general']/MENU[@id='CORE/changePassword']", 'Mot de _passe')
        self.assert_xml_equal("MENUS/MENU[@id='core.admin']", 'Administration')
        self.assert_xml_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.right']", 'Gestion des droits')
        self.assert_xml_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU[@id='CORE/groupsList']", '_Groupes')

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

        self.call('/CORE/menu', {})
        self.assert_attrib_equal('', 'observer', 'CORE.Auth')
        self.assert_xml_equal('', 'NEEDAUTH')

    def test_menu_connected_with_empty(self):
        self.call('/CORE/authentification', {'username':'empty', 'password':'empty'})
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/LOGIN', 'empty')
        self.assert_xml_equal('CONNECTION/REALNAME', 'empty NOFULL')
        self.assert_xml_equal('CONNECTION/MODE', '0')

        self.call('/CORE/menu', {})
        self.assert_observer('CORE.Menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU", 3)
        self.assert_xml_equal("MENUS/MENU[@id='core.general']", six.text_type('Général'))
        self.assert_count_equal("MENUS/MENU[@id='core.general']/MENU", 1)
        self.assert_xml_equal("MENUS/MENU[@id='core.general']/MENU[@id='CORE/changePassword']", 'Mot de _passe')
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU", 2)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.extensions']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU", 0)

        self.call('/CORE/configuration', {})
        self.assert_observer('CORE.Exception', 'CORE', 'configuration')
        self.assert_xml_equal("EXCEPTION/MESSAGE", "Mauvaise permission pour 'empty'")

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

    def test_connect_anonymous(self):
        clear_parameters()
        self.call('/CORE/authentification', {'username':'', 'password':''})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')

        param = Parameter.objects.get(name='CORE-connectmode')  # pylint: disable=no-member
        param.value = '1'
        param.save()
        clear_parameters()

        self.call('/CORE/authentification', {'username':'', 'password':''})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/LOGIN', None)
        self.assert_xml_equal('CONNECTION/REALNAME', None)
        self.assert_xml_equal('CONNECTION/MODE', '1')

        self.call('/CORE/menu', {})
        self.assert_observer('CORE.Menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU", 3)
        self.assert_count_equal("MENUS/MENU[@id='core.general']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU", 2)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.extensions']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU", 0)

    def test_connect_free(self):
        clear_parameters()
        self.call('/CORE/authentification', {'username':'', 'password':''})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')

        param = Parameter.objects.get(name='CORE-connectmode')  # pylint: disable=no-member
        param.value = '2'
        param.save()
        clear_parameters()

        self.call('/CORE/authentification', {'username':'', 'password':''})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/LOGIN', None)
        self.assert_xml_equal('CONNECTION/REALNAME', None)
        self.assert_xml_equal('CONNECTION/MODE', '2')

        self.call('/CORE/menu', {})
        self.assert_observer('CORE.Menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU", 3)
        self.assert_count_equal("MENUS/MENU[@id='core.general']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU", 3)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.extensions']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU", 2)

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

    def test_password(self):
        self.call('/CORE/authentification', {'username':'empty', 'password':'empty'})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')

        self.call('/CORE/changePassword', {})
        self.assert_observer('Core.Custom', 'CORE', 'changePassword')
        self.assert_xml_equal('TITLE', 'Mot de passe')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'modifyPassword', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', 'images/passwd.png', ('0', '0', '1', '3'))
        self.assert_comp_equal('COMPONENTS/LABEL[@name="lbl_oldpass"]', 'ancien mot de passe', ('1', '0', '1', '1'))
        self.assert_comp_equal('COMPONENTS/LABEL[@name="lbl_newpass1"]', 'nouveau mot de passe', ('1', '1', '1', '1'))
        self.assert_comp_equal('COMPONENTS/LABEL[@name="lbl_newpass2"]', 're-nouveau mot de passe', ('1', '2', '1', '1'))
        self.assert_comp_equal('COMPONENTS/PASSWD[@name="oldpass"]', None, ('2', '0', '1', '1'))
        self.assert_comp_equal('COMPONENTS/PASSWD[@name="newpass1"]', None, ('2', '1', '1', '1'))
        self.assert_comp_equal('COMPONENTS/PASSWD[@name="newpass2"]', None, ('2', '2', '1', '1'))

    def test_changepassword(self):
        self.call('/CORE/authentification', {'username':'empty', 'password':'empty'})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/modifyPassword', {'oldpass':'aaa', 'newpass1':'123', 'newpass2':'123'})
        self.assert_observer('CORE.Exception', 'CORE', 'modifyPassword')
        self.assert_xml_equal('EXCEPTION/MESSAGE', six.text_type('Mot de passe actuel érroné!'))
        self.assert_xml_equal('EXCEPTION/CODE', '3')

        self.call('/CORE/modifyPassword', {'oldpass':'empty', 'newpass1':'123', 'newpass2':'456'})
        self.assert_observer('CORE.Exception', 'CORE', 'modifyPassword')
        self.assert_xml_equal('EXCEPTION/MESSAGE', six.text_type('Les mots de passes sont différents!'))
        self.assert_xml_equal('EXCEPTION/CODE', '3')

        self.call('/CORE/modifyPassword', {'oldpass':'empty', 'newpass1':'123', 'newpass2':'123'})
        self.assert_observer('Core.DialogBox', 'CORE', 'modifyPassword')
        # self.assert_xml_equal('TEXT', six.text_type('Mot de passe modifié'))
        self.assert_attrib_equal('TEXT', 'type', '1')

        self.call('/CORE/authentification', {'username':'empty', 'password':'empty'})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')

        self.call('/CORE/authentification', {'username':'empty', 'password':'123'})
        self.assert_observer('CORE.Auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')

class ConfigTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        LucteriosTest.setUp(self)
        add_empty_user()

    def test_config(self):
        self.factory.xfer = Configuration()
        self.call('/CORE/configuration', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'configuration')
        self.assert_xml_equal('TITLE', 'Configuration générale')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="params"]', 'CORE-connectmode')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Modifier', 'images/edit.png', 'CORE', 'paramEdit', 0, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Fermer', 'images/close.png'))
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', 'images/config.png', (0, 0, 1, 10))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="title"]', "{[newline]}{[center]}{[bold]}{[underline]}Configuration du logiciel{[/underline]}{[/bold]}{[/center]}", (1, 0, 3, 1))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_CORE-connectmode"]', "{[bold]}Mode de connexion{[/bold]}", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="CORE-connectmode"]', "Connection toujours nécessaire", (2, 1, 1, 1))

    def test_config_edit(self):
        self.factory.xfer = ParamEdit()
        self.call('/CORE/paramEdit', {'params':'CORE-connectmode'}, False)
        self.assert_observer('Core.Custom', 'CORE', 'paramEdit')

        self.assert_xml_equal('TITLE', 'Paramètres')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="params"]', 'CORE-connectmode')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'paramSave', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', 'images/config.png', (0, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="title"]', "{[newline]}{[center]}{[bold]}{[underline]}Edition de paramètres{[/underline]}{[/bold]}{[/center]}", (1, 0, 1, 1))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_CORE-connectmode"]', "{[bold]}Mode de connexion{[/bold]}", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="CORE-connectmode"]', "0", (2, 1, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE', 3)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE[@id=0]', "Connection toujours nécessaire")
        self.assert_xml_equal('COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE[@id=1]', "Ouvert entant qu'anonyme")
        self.assert_xml_equal('COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE[@id=2]', "Accès libre")

    def test_config_save(self):
        param = Parameter.objects.get(name='CORE-connectmode')  # pylint: disable=no-member
        self.assertEqual("0", param.value)

        self.factory.xfer = ParamSave()
        self.call('/CORE/paramSave', {'params':'CORE-connectmode', 'CORE-connectmode':'1'}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'paramSave')

        param = Parameter.objects.get(name='CORE-connectmode')  # pylint: disable=no-member
        self.assertEqual("1", param.value)

def suite():
    # pylint: disable=redefined-outer-name
    suite = TestSuite()
    loader = TestLoader()
    suite.addTest(loader.loadTestsFromTestCase(AuthentificationTest))
    suite.addTest(loader.loadTestsFromTestCase(ConfigTest))
    suite.addTest(loader.loadTestsFromTestCase(tests_framework.ContainerAcknowledgeTest))
    suite.addTest(loader.loadTestsFromTestCase(tests_usergroup.UserTest))
    suite.addTest(loader.loadTestsFromTestCase(tests_usergroup.GroupTest))
    return suite
