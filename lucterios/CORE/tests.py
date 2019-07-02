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
        self.assertEqual(response.content, six.binary_type('', 'ascii'))

    def test_menu_noconnect(self):
        self.calljson('/CORE/menu', {})
        self.assert_observer('core.auth', 'CORE', 'menu')
        self.assert_json_equal('', '', 'NEEDAUTH')
        self.assertTrue('connexion' in self.response_json.keys())
        self.assertEqual(self.response_json['connexion']['REALNAME'], '')

    def test_badconnect(self):
        self.calljson('/CORE/authentification', {})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'NEEDAUTH')
        self.assertTrue('connexion' in self.response_json.keys())
        self.assertEqual(self.response_json['connexion']['REALNAME'], '')

        self.calljson('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'BADAUTH')
        self.assertTrue('connexion' in self.response_json.keys())
        self.assertEqual(self.response_json['connexion']['REALNAME'], '')

        self.calljson('/CORE/authentification', {'username': 'aaa', 'password': 'bbb'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'BADAUTH')
        self.assertTrue('connexion' in self.response_json.keys())
        self.assertEqual(self.response_json['connexion']['REALNAME'], '')

    def test_connect(self):
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')
        self.assertEqual(self.response_json['connexion']['TITLE'], 'Lucterios standard')
        self.assertEqual(self.response_json['connexion']['SUBTITLE'], six.text_type('Application générique de gestion'))
        self.assertEqual(self.response_json['connexion']['VERSION'][0:4], '2.4.')
        self.assertEqual(self.response_json['connexion']['SERVERVERSION'][0:4], '2.4.')
        self.assertEqual(self.response_json['connexion']['COPYRIGHT'][0:4], '(c) ')
        self.assertEqual(self.response_json['connexion']['LOGONAME'][0:20], 'data:image/*;base64,')
        self.assertEqual(self.response_json['connexion']['SUPPORT_EMAIL'][0:8], 'support@')
        self.assertEqual(self.response_json['connexion']['LOGIN'], 'admin')
        self.assertEqual(self.response_json['connexion']['REALNAME'], 'administrator ADMIN')
        self.assertEqual(self.response_json['connexion']['MODE'], '0')

        self.calljson('/CORE/exitConnection', {})
        self.assert_observer('core.acknowledge', 'CORE', 'exitConnection')

    def test_menu_connected(self):
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')

        self.assertEqual(len(self.response_json['menus']), 4)
        self.assertEqual(self.response_json['menus'][0]['id'], 'core.menu')
        self.assertEqual(len(self.response_json['menus'][0]['menus']), 1)

        self.assertEqual(self.response_json['menus'][1]['id'], 'core.general')
        self.assertEqual(self.response_json['menus'][1]['text'], six.text_type('Général'))
        self.assertEqual(self.response_json['menus'][1]['menus'][0]['id'], 'CORE/changePassword')
        self.assertEqual(self.response_json['menus'][1]['menus'][0]['text'], 'Mot de passe')

        self.assertEqual(self.response_json['menus'][2]['id'], 'dummy.foo')

        self.assertEqual(self.response_json['menus'][3]['id'], 'core.admin')
        self.assertEqual(self.response_json['menus'][3]['text'], 'Administration')
        self.assertEqual(self.response_json['menus'][3]['menus'][3]['id'], 'core.right')
        self.assertEqual(self.response_json['menus'][3]['menus'][3]['text'], 'Gestion des droits')
        self.assertEqual(self.response_json['menus'][3]['menus'][3]['menus'][0]['id'], 'CORE/groupsList')
        self.assertEqual(self.response_json['menus'][3]['menus'][3]['menus'][0]['text'], 'Les groupes')

        self.calljson('/CORE/exitConnection', {})
        self.assert_observer('core.acknowledge', 'CORE', 'exitConnection')

        self.calljson('/CORE/menu', {})
        self.assert_observer('core.auth', 'CORE', 'menu')
        self.assert_json_equal('', '', 'NEEDAUTH')

    def test_menu_connected_with_empty(self):
        self.calljson('/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_json_equal('', "", 'OK')
        self.assertEqual(self.response_json['connexion']['LOGIN'], 'empty')
        self.assertEqual(self.response_json['connexion']['REALNAME'], 'empty NOFULL')
        self.assertEqual(self.response_json['connexion']['MODE'], '0')

        self.calljson('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')

        self.assertEqual(len(self.response_json['menus']), 3)
        self.assertEqual(self.response_json['menus'][0]['id'], 'core.menu')
        self.assertEqual(self.response_json['menus'][1]['id'], 'core.general')
        self.assertEqual(self.response_json['menus'][1]['text'], six.text_type('Général'))
        self.assertEqual(len(self.response_json['menus'][1]['menus']), 1)
        self.assertEqual(self.response_json['menus'][1]['menus'][0]['id'], 'CORE/changePassword')
        self.assertEqual(self.response_json['menus'][1]['menus'][0]['text'], 'Mot de passe')
        self.assertEqual(self.response_json['menus'][2]['id'], 'dummy.foo')

        self.calljson('/CORE/configuration', {})
        self.assert_observer('core.exception', 'CORE', 'configuration')
        self.assert_json_equal('', "message", "Mauvaise permission pour 'empty'")

        self.calljson('/CORE/exitConnection', {})
        self.assert_observer('core.acknowledge', 'CORE', 'exitConnection')

    def test_connect_anonymous(self):
        Params.clear()
        self.calljson('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'BADAUTH')

        param = Parameter.objects.get(name='CORE-connectmode')
        param.value = '1'
        param.save()
        Params.clear()

        self.calljson('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')
        self.assertEqual(self.response_json['connexion']['LOGIN'], '')
        self.assertEqual(self.response_json['connexion']['REALNAME'], '')
        self.assertEqual(self.response_json['connexion']['MODE'], '1')

        self.calljson('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')

        self.assertEqual(len(self.response_json['menus']), 1)
        self.assertEqual(self.response_json['menus'][0]['id'], 'dummy.foo')
        self.assertEqual(self.response_json['menus'][0]['text'], six.text_type('Dummy'))
        self.assertEqual(len(self.response_json['menus'][0]['menus']), 6)

    def test_connect_free(self):
        Params.clear()
        self.calljson('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'BADAUTH')

        param = Parameter.objects.get(name='CORE-connectmode')
        param.value = '2'
        param.save()
        Params.clear()

        self.calljson('/CORE/authentification', {'username': '', 'password': ''})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')
        self.assertEqual(self.response_json['connexion']['LOGIN'], '')
        self.assertEqual(self.response_json['connexion']['REALNAME'], '')
        self.assertEqual(self.response_json['connexion']['MODE'], '2')

        self.assertTrue(WrapAction.mode_connect_notfree is not None, "mode_connect_notfree is not None")
        self.assertFalse(WrapAction('', '').mode_connect_notfree(), "mode_connect_notfree()")
        self.assertFalse(WrapAction.mode_connect_notfree is None or WrapAction('', '').mode_connect_notfree(), "mode_connect_notfree is None or mode_connect_notfree()")
        request = RequestFactory().post('/')
        request.user = AnonymousUser()
        act1 = WrapAction('free', 'free', is_view_right=None)
        self.assertEqual(act1.is_view_right, None, 'act1.is_view_right')
        self.assertFalse(act1.check_permission(request), 'check_permission None')
        act2 = WrapAction('free', 'free', is_view_right='CORE.change_parameter')
        act2.with_log = True
        self.assertEqual(act2.is_view_right, 'CORE.change_parameter', 'act2.is_view_right')
        self.assertTrue(act2.check_permission(request), 'check_permission CORE.change_parameter')

        self.calljson('/CORE/configuration', {})
        self.assert_observer('core.custom', 'CORE', 'configuration')
        self.assert_json_equal('LABELFORM', "CORE-connectmode", "Accès libre")

        self.calljson('/CORE/menu', {})
        self.assert_observer('core.menu', 'CORE', 'menu')
        self.assertEqual(len(self.response_json['menus']), 3)
        self.assertEqual(self.response_json['menus'][0]['id'], 'core.menu')
        self.assertEqual(self.response_json['menus'][1]['id'], 'dummy.foo')
        self.assertEqual(len(self.response_json['menus'][1]['menus']), 9)
        self.assertEqual(self.response_json['menus'][2]['id'], 'core.admin')
        self.assertEqual(self.response_json['menus'][2]['text'], 'Administration')
        self.assertEqual(self.response_json['menus'][2]['menus'][3]['id'], 'core.right')
        self.assertEqual(self.response_json['menus'][2]['menus'][3]['text'], 'Gestion des droits')
        self.assertEqual(self.response_json['menus'][2]['menus'][3]['menus'][0]['id'], 'CORE/groupsList')
        self.assertEqual(self.response_json['menus'][2]['menus'][3]['menus'][0]['text'], 'Les groupes')

    def test_menu_reconnected(self):
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/authentification', {})
        self.assertEqual(self.response_json['connexion']['LOGIN'], 'admin')
        self.assertEqual(self.response_json['connexion']['REALNAME'], 'administrator ADMIN')

        self.calljson('/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/authentification', {'info': 'true'})
        self.assertEqual(self.response_json['connexion']['LOGIN'], 'empty')
        self.assertEqual(self.response_json['connexion']['REALNAME'], 'empty NOFULL')

        self.calljson('/CORE/exitConnection', {})
        self.assert_observer('core.acknowledge', 'CORE', 'exitConnection')

    def test_password(self):
        self.calljson('/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_observer('core.auth', 'CORE', 'authentification')

        self.calljson('/CORE/changePassword', {})
        self.assert_observer('core.custom', 'CORE', 'changePassword')
        self.assertEqual(self.json_meta['title'], 'Mot de passe')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal(self.json_actions[0], ('Ok', 'images/ok.png', 'CORE', 'modifyPassword', 1, 1, 1))
        self.assert_action_equal(self.json_actions[1], ('Annuler', 'images/cancel.png'))
        self.assert_count_equal('', 4)
        self.assert_comp_equal(('IMAGE', "img"), '/static/lucterios.CORE/images/passwd.png', ('0', '0', '1', '3'))
        self.assert_attrib_equal("oldpass", 'description', 'ancien mot de passe')
        self.assert_attrib_equal("newpass1", 'description', 'nouveau mot de passe')
        self.assert_attrib_equal("newpass2", 'description', 're-nouveau mot de passe')
        self.assert_comp_equal(('PASSWD', "oldpass"), '', ('1', '0', '1', '1'))
        self.assert_comp_equal(('PASSWD', "newpass1"), '', ('1', '1', '1', '1'))
        self.assert_comp_equal(('PASSWD', "newpass2"), '', ('1', '2', '1', '1'))

    def test_changepassword(self):
        self.calljson('/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/modifyPassword', {'oldpass': 'aaa', 'newpass1': '123', 'newpass2': '123'})
        self.assert_observer('core.exception', 'CORE', 'modifyPassword')
        self.assert_json_equal('', 'message', six.text_type('Mot de passe actuel erroné!'))
        self.assert_json_equal('', 'code', '3')

        self.calljson('/CORE/modifyPassword', {'oldpass': 'empty', 'newpass1': '123', 'newpass2': '456'})
        self.assert_observer('core.exception', 'CORE', 'modifyPassword')
        self.assert_json_equal('', 'message', six.text_type('Les mots de passes sont différents!'))
        self.assert_json_equal('', 'code', '3')

        self.calljson('/CORE/modifyPassword', {'oldpass': 'empty', 'newpass1': '123', 'newpass2': '123'})
        self.assert_observer('core.dialogbox', 'CORE', 'modifyPassword')
        self.assert_json_equal('', 'text', six.text_type('Mot de passe modifié'))
        self.assert_json_equal('', 'type', '1')

        self.calljson('/CORE/authentification', {'username': 'empty', 'password': 'empty'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'BADAUTH')

        self.calljson('/CORE/authentification', {'username': 'empty', 'password': '123'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')


class ConfigTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        add_empty_user()

    def test_config(self):
        self.factory.xfer = Configuration()
        self.calljson('/CORE/configuration', {}, False)
        self.assert_observer('core.custom', 'CORE', 'configuration')
        self.assertEqual(self.json_meta['title'], 'Configuration générale')
        self.assertEqual(len(self.json_context), 1)
        self.assertEqual(self.json_context['params'], ['CORE-connectmode', 'CORE-Wizard', 'CORE-MessageBefore'])
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal(self.json_actions[0], ('Modifier', 'images/edit.png', 'CORE', 'paramEdit', 0, 1, 1))
        self.assert_action_equal(self.json_actions[1], ('Fermer', 'images/close.png'))
        self.assert_count_equal('', 6)
        self.assert_comp_equal(('IMAGE', "img"), '/static/lucterios.CORE/images/config.png', (0, 0, 1, 10))
        self.assert_comp_equal(('LABELFORM', "title"), "{[br/]}{[center]}{[b]}{[u]}Configuration du logiciel{[/u]}{[/b]}{[/center]}", (1, 0, 3, 1))

        self.assert_attrib_equal("CORE-connectmode", 'description', "Mode de connexion")
        self.assert_comp_equal(('LABELFORM', "CORE-connectmode"), "Connexion toujours nécessaire", (1, 1, 1, 1))
        self.assert_attrib_equal("CORE-Wizard", 'description', "Ouvrir l'assistant de configuration au démarrage.")
        self.assert_comp_equal(('LABELFORM', "CORE-Wizard"), "Oui", (1, 2, 1, 1))
        self.assert_attrib_equal("CORE-MessageBefore", 'description', "Message avant connexion")
        self.assert_comp_equal(('LABELFORM', "CORE-MessageBefore"), "", (1, 3, 1, 1))
        self.assert_action_equal(self.json_comp["conf_wizard"]['action'], ("Assistant", 'images/config.png', 'CORE', 'configurationWizard', 0, 1, 1))

    def test_config_edit(self):
        self.factory.xfer = ParamEdit()
        self.calljson('/CORE/paramEdit', {'params': 'CORE-connectmode'}, False)
        self.assert_observer('core.custom', 'CORE', 'paramEdit')

        self.assertEqual(self.json_meta['title'], 'Paramètres')
        self.assertEqual(len(self.json_context), 1)
        self.assertEqual(self.json_context['params'], 'CORE-connectmode')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal(self.json_actions[0], ('Ok', 'images/ok.png', 'CORE', 'paramSave', 1, 1, 1))
        self.assert_action_equal(self.json_actions[1], ('Annuler', 'images/cancel.png'))
        self.assert_count_equal('', 3)
        self.assert_comp_equal(('IMAGE', "img"), '/static/lucterios.CORE/images/config.png', (0, 0, 1, 1))
        self.assert_comp_equal(('LABELFORM', "title"), "Edition de paramètres", (1, 0, 2, 1))
        self.assert_attrib_equal("title", "formatstr", "{[br/]}{[center]}{[u]}{[b]}%s{[/b]}{[/u]}{[/center]}")

        self.assert_comp_equal(('SELECT', "CORE-connectmode"), "0", (1, 1, 1, 1))
        self.assert_attrib_equal("CORE-connectmode", 'description', "Mode de connexion")
        self.assert_select_equal("CORE-connectmode", {0: "Connexion toujours nécessaire", 1: "Ouvert en tant qu'anonyme", 2: "Accès libre"})

    def test_config_save(self):
        param = Parameter.objects.get(name='CORE-connectmode')
        self.assertEqual("0", param.value)

        self.factory.xfer = ParamSave()
        self.calljson('/CORE/paramSave', {'params': 'CORE-connectmode', 'CORE-connectmode': '1'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')

        param = Parameter.objects.get(name='CORE-connectmode')
        self.assertEqual("1", param.value)
