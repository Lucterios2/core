# -*- coding: utf-8 -*-
'''
Unit test class for connection and login in Lucterios

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
from lucterios.framework.test import LucteriosTest, add_empty_user
from django.utils import six
from lucterios.CORE.views import Configuration, ParamEdit, ParamSave
from lucterios.CORE.parameters import Params
from lucterios.framework.tools import WrapAction
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from lucterios.CORE.models import Parameter


class AuthentificationTest(LucteriosTest):

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
        self.assert_observer('core.auth', 'CORE', 'menu')
        self.assert_xml_equal('', 'NEEDAUTH')
        self.assert_count_equal('CONNECTION', 0)

    def test_badconnect(self):
        self.call('/CORE/authentification', {})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'NEEDAUTH')
        self.assert_count_equal('CONNECTION', 0)

        self.call('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

        self.call(
            '/CORE/authentification', {'username': 'aaa', 'password': 'bbb'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')
        self.assert_count_equal('CONNECTION', 0)

    def test_connect(self):
        self.call(
            '/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/TITLE', 'Lucterios standard')
        self.assert_xml_equal(
            'CONNECTION/SUBTITLE', six.text_type('Application générique de gestion'))
        self.assert_xml_equal('CONNECTION/VERSION', '2.1.', (0, 4))
        self.assert_xml_equal('CONNECTION/SERVERVERSION', '2.1.', (0, 4))
        self.assert_xml_equal('CONNECTION/COPYRIGHT', '(c) ', (0, 4))
        self.assert_xml_equal(
            'CONNECTION/LOGONAME', 'data:image/*;base64,', (0, 20))
        self.assert_xml_equal('CONNECTION/SUPPORT_EMAIL', 'support@', (0, 8))
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'admin')
        self.assert_xml_equal('CONNECTION/REALNAME', 'administrator ADMIN')
        self.assert_xml_equal('CONNECTION/MODE', '0')

        self.call('/CORE/exitConnection', {})
        self.assert_observer('core.acknowledge', 'CORE', 'exitConnection')

    def test_menu_connected(self):
        self.call(
            '/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU", 4)
        self.assert_xml_equal(
            "MENUS/MENU[@id='core.general']", six.text_type('Général'))
        self.assert_xml_equal(
            "MENUS/MENU[@id='core.general']/MENU[@id='CORE/changePassword']", 'Mot de passe')
        self.assert_xml_equal("MENUS/MENU[@id='core.admin']", 'Administration')
        self.assert_xml_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.right']", 'Gestion des droits')
        self.assert_xml_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU[@id='CORE/groupsList']", 'Les groupes')
        self.assert_count_equal("MENUS/MENU[@id='core.menu']/MENU", 1)

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'core.acknowledge')

        self.call('/CORE/menu', {})
        self.assert_attrib_equal('', 'observer', 'core.auth')
        self.assert_xml_equal('', 'NEEDAUTH')

    def test_menu_connected_with_empty(self):
        self.call(
            '/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/LOGIN', 'empty')
        self.assert_xml_equal('CONNECTION/REALNAME', 'empty NOFULL')
        self.assert_xml_equal('CONNECTION/MODE', '0')

        self.call('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU", 4)
        self.assert_xml_equal(
            "MENUS/MENU[@id='core.general']", six.text_type('Général'))
        self.assert_count_equal("MENUS/MENU[@id='core.general']/MENU", 1)
        self.assert_xml_equal(
            "MENUS/MENU[@id='core.general']/MENU[@id='CORE/changePassword']", 'Mot de passe')
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU", 3)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.extensions']/MENU", 0)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.print']/MENU", 0)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.menu']/MENU", 1)

        self.call('/CORE/configuration', {})
        self.assert_observer('core.exception', 'CORE', 'configuration')
        self.assert_xml_equal(
            "EXCEPTION/MESSAGE", "Mauvaise permission pour 'empty'")

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'core.acknowledge')

    def test_connect_anonymous(self):
        Params.clear()
        self.call('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')

        param = Parameter.objects.get(
            name='CORE-connectmode')
        param.value = '1'
        param.save()
        Params.clear()

        self.call('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/LOGIN', None)
        self.assert_xml_equal('CONNECTION/REALNAME', None)
        self.assert_xml_equal('CONNECTION/MODE', '1')

        self.call('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU", 3)
        self.assert_count_equal("MENUS/MENU[@id='core.general']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU", 3)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.extensions']/MENU", 0)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.print']/MENU", 0)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU", 0)

    def test_connect_free(self):
        Params.clear()
        self.call('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')

        param = Parameter.objects.get(
            name='CORE-connectmode')
        param.value = '2'
        param.save()
        Params.clear()

        self.call('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')
        self.assert_xml_equal('CONNECTION/LOGIN', None)
        self.assert_xml_equal('CONNECTION/REALNAME', None)
        self.assert_xml_equal('CONNECTION/MODE', '2')

        self.assertTrue(
            WrapAction.mode_connect_notfree is not None, "mode_connect_notfree is not None")
        self.assertFalse(
            WrapAction('', '').mode_connect_notfree(), "mode_connect_notfree()")
        self.assertFalse(WrapAction.mode_connect_notfree is None or WrapAction(
            '', '').mode_connect_notfree(), "mode_connect_notfree is None or mode_connect_notfree()")
        request = RequestFactory().post('/')
        request.user = AnonymousUser()
        act1 = WrapAction('free', 'free', is_view_right=None)
        self.assertEqual(act1.is_view_right, None, 'act1.is_view_right')
        self.assertFalse(
            act1.check_permission(request), 'check_permission None')
        act2 = WrapAction(
            'free', 'free', is_view_right='CORE.change_parameter')
        act2.with_log = True
        self.assertEqual(
            act2.is_view_right, 'CORE.change_parameter', 'act2.is_view_right')
        self.assertTrue(
            act2.check_permission(request), 'check_permission CORE.change_parameter')

        self.call('/CORE/configuration', {})
        self.assert_observer('core.custom', 'CORE', 'configuration')
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="CORE-connectmode"]', "Accès libre")

        self.call('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')
        self.assert_count_equal("MENUS/MENU[@id='core.general']/MENU", 0)
        self.assert_count_equal("MENUS/MENU[@id='core.admin']/MENU", 4)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.extensions']/MENU", 1)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.print']/MENU", 2)
        self.assert_count_equal(
            "MENUS/MENU[@id='core.admin']/MENU[@id='core.right']/MENU", 3)
        self.assert_count_equal("MENUS/MENU[@id='core.menu']/MENU", 1)
        self.assert_count_equal("MENUS/MENU", 4)

    def test_menu_reconnected(self):
        self.call(
            '/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/authentification', {})
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'admin')
        self.assert_xml_equal('CONNECTION/REALNAME', 'administrator ADMIN')

        self.call(
            '/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/authentification', {'info': 'true'})
        # self.assert_xml_equal('CONNECTION/INFO_SERVER', '')
        self.assert_xml_equal('CONNECTION/LOGIN', 'empty')
        self.assert_xml_equal('CONNECTION/REALNAME', 'empty NOFULL')

        self.call('/CORE/exitConnection', {})
        self.assert_attrib_equal('', 'observer', 'core.acknowledge')

    def test_password(self):
        self.call(
            '/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_observer('core.auth', 'CORE', 'authentification')

        self.call('/CORE/changePassword', {})
        self.assert_observer('core.custom', 'CORE', 'changePassword')
        self.assert_xml_equal('TITLE', 'Mot de passe')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal(
            'ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'modifyPassword', 1, 1, 1))
        self.assert_action_equal(
            'ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_comp_equal(
            'COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/passwd.png', ('0', '0', '1', '3'))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_oldpass"]', '{[b]}ancien mot de passe{[/b]}', ('1', '0', '1', '1'))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_newpass1"]', '{[b]}nouveau mot de passe{[/b]}', ('1', '1', '1', '1'))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_newpass2"]', '{[b]}re-nouveau mot de passe{[/b]}', ('1', '2', '1', '1'))
        self.assert_comp_equal(
            'COMPONENTS/PASSWD[@name="oldpass"]', None, ('2', '0', '1', '1'))
        self.assert_comp_equal(
            'COMPONENTS/PASSWD[@name="newpass1"]', None, ('2', '1', '1', '1'))
        self.assert_comp_equal(
            'COMPONENTS/PASSWD[@name="newpass2"]', None, ('2', '2', '1', '1'))

    def test_changepassword(self):
        self.call(
            '/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/modifyPassword',
                  {'oldpass': 'aaa', 'newpass1': '123', 'newpass2': '123'})
        self.assert_observer('core.exception', 'CORE', 'modifyPassword')
        self.assert_xml_equal(
            'EXCEPTION/MESSAGE', six.text_type('Mot de passe actuel erroné!'))
        self.assert_xml_equal('EXCEPTION/CODE', '3')

        self.call('/CORE/modifyPassword',
                  {'oldpass': 'empty', 'newpass1': '123', 'newpass2': '456'})
        self.assert_observer('core.exception', 'CORE', 'modifyPassword')
        self.assert_xml_equal(
            'EXCEPTION/MESSAGE', six.text_type('Les mots de passes sont différents!'))
        self.assert_xml_equal('EXCEPTION/CODE', '3')

        self.call('/CORE/modifyPassword',
                  {'oldpass': 'empty', 'newpass1': '123', 'newpass2': '123'})
        self.assert_observer('core.dialogbox', 'CORE', 'modifyPassword')
        # self.assert_xml_equal('TEXT', six.text_type('Mot de passe modifié'))
        self.assert_attrib_equal('TEXT', 'type', '1')

        self.call(
            '/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'BADAUTH')

        self.call(
            '/CORE/authentification', {'username': 'empty', 'password': '123'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')


class ConfigTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        add_empty_user()

    def test_config(self):
        self.factory.xfer = Configuration()
        self.call('/CORE/configuration', {}, False)
        self.assert_observer('core.custom', 'CORE', 'configuration')
        self.assert_xml_equal('TITLE', 'Configuration générale')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="params"]', 'CORE-connectmode;CORE-Wizard')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Modifier', 'images/edit.png', 'CORE', 'paramEdit', 0, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Fermer', 'images/close.png'))
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/config.png', (0, 0, 1, 10))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="title"]',
                               "{[br/]}{[center]}{[b]}{[u]}Configuration du logiciel{[/u]}{[/b]}{[/center]}", (1, 0, 3, 1))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_CORE-connectmode"]', "{[b]}Mode de connexion{[/b]}", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="CORE-connectmode"]', "Connexion toujours nécessaire", (2, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_CORE-Wizard"]',
                               "{[b]}Toujours ouvrir l'assistant de configuration au démarrage.{[/b]}", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="CORE-Wizard"]', "Oui", (2, 2, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="conf_wizard"]/ACTIONS/ACTION', ("Assistant", 'images/config.png', 'CORE', 'configurationWizard', 0, 1, 1))

    def test_config_edit(self):
        self.factory.xfer = ParamEdit()
        self.call('/CORE/paramEdit', {'params': 'CORE-connectmode'}, False)
        self.assert_observer('core.custom', 'CORE', 'paramEdit')

        self.assert_xml_equal('TITLE', 'Paramètres')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal(
            'CONTEXT/PARAM[@name="params"]', 'CORE-connectmode')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal(
            'ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'paramSave', 1, 1, 1))
        self.assert_action_equal(
            'ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_comp_equal(
            'COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/config.png', (0, 0, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="title"]', "{[br/]}{[center]}{[u]}{[b]}Edition de paramètres{[/b]}{[/u]}{[/center]}", (1, 0, 2, 1))

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_CORE-connectmode"]', "{[b]}Mode de connexion{[/b]}", (1, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/SELECT[@name="CORE-connectmode"]', "0", (2, 1, 1, 1))
        self.assert_count_equal(
            'COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE', 3)
        self.assert_xml_equal(
            'COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE[@id=0]', "Connexion toujours nécessaire")
        self.assert_xml_equal(
            'COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE[@id=1]', "Ouvert en tant qu'anonyme")
        self.assert_xml_equal(
            'COMPONENTS/SELECT[@name="CORE-connectmode"]/CASE[@id=2]', "Accès libre")

    def test_config_save(self):
        param = Parameter.objects.get(
            name='CORE-connectmode')
        self.assertEqual("0", param.value)

        self.factory.xfer = ParamSave()
        self.call(
            '/CORE/paramSave', {'params': 'CORE-connectmode', 'CORE-connectmode': '1'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')

        param = Parameter.objects.get(
            name='CORE-connectmode')
        self.assertEqual("1", param.value)
