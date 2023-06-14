# -*- coding: utf-8 -*-
'''
Unit test classes from user, group and session in Lucterios

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
from datetime import date

from django.contrib.auth.models import Permission
from django.conf import settings

from lucterios.framework.test import LucteriosTest, add_empty_user, add_user
from lucterios.framework import tools, signal_and_lock
from lucterios.framework.auditlog import LucteriosAuditlogModelRegistry

from lucterios.CORE.views_usergroup import UsersList, UsersDelete, UsersDisabled, UsersEnabled, UsersEdit,\
    AudiLogConfig, GroupsDelete, PreferenceEdit, UsersShow, ChangeOnlySuperAdmin
from lucterios.CORE.views_usergroup import GroupsList, GroupsEdit

from lucterios.CORE.views import Unlock
from lucterios.CORE.models import LucteriosGroup, LucteriosUser
from lucterios.CORE import parameters
from lucterios.framework.signal_and_lock import Signal


class UserTest(LucteriosTest):

    def setUp(self):
        settings.LOGIN_FIELD = 'username'
        settings.ASK_LOGIN_EMAIL = False
        signal_and_lock.unlocker_view_class = Unlock
        signal_and_lock.RecordLocker.clear()
        LucteriosTest.setUp(self)
        add_empty_user()

    def tearDown(self):
        LucteriosTest.tearDown(self)
        LucteriosAuditlogModelRegistry.set_state_packages([])

    def test_userlist(self):
        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assertEqual(self.json_meta['title'], 'Utilisateurs du logiciel')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('GET', self.json_actions[0], ('Rechercher', 'images/user.png', 'CORE', 'usersSearch', 0, 0, 1))
        self.assert_action_equal('POST', self.json_actions[1], ('Fermer', 'images/close.png'))
        self.assert_count_equal('', 9)
        self.assert_json_equal('IMAGE', "img", '/static/lucterios.CORE/images/user.png')
        self.assert_coordcomp_equal("img", ('0', '0', '1', '1'))
        self.assert_json_equal('LABELFORM', "title", 'Utilisateurs du logiciel')
        self.assert_attrib_equal("title", "formatstr", "{[br/]}{[center]}{[u]}{[b]}%s{[/b]}{[/u]}{[/center]}")
        self.assert_coordcomp_equal("title", ('1', '0', '1', '1'))
        self.assert_coordcomp_equal("user_actif", ('0', '0', '3', '1'))
        self.assert_attrib_equal("user_actif", 'description', 'Liste des utilisateurs actifs')
        self.assert_coordcomp_equal("user_inactif", ('0', '2', '3', '1'))
        self.assert_attrib_equal("user_inactif", 'description', 'Liste des utilisateurs inactifs')
        self.assert_json_equal('LABELFORM', "CORE-OnlySuperAdmin", 'Non')

        self.assert_grid_equal('user_actif', {"username": "nom d'utilisateur", "first_name": "prénom", "last_name": "nom", "last_login": "dernière connexion"}, 2)
        self.assert_json_equal('', 'user_actif/@0/username', 'admin')
        self.assert_json_equal('', 'user_actif/@1/username', 'empty')
        self.assert_json_equal('', 'user_actif/@0/first_name', 'administrator')
        self.assert_json_equal('', 'user_actif/@1/first_name', 'empty')
        self.assert_json_equal('', 'user_actif/@0/last_name', 'ADMIN')
        self.assert_json_equal('', 'user_actif/@1/last_name', 'NOFULL')

        self.assert_count_equal('#user_actif/actions', 4)
        self.assert_action_equal('POST', '#user_actif/actions/@0', ('Modifier', 'images/edit.png', 'CORE', 'usersEdit', 0, 1, 0))
        self.assert_action_equal('DELETE', '#user_actif/actions/@1', ('Supprimer', 'images/delete.png', 'CORE', 'usersDelete', 0, 1, 2))
        self.assert_action_equal('POST', '#user_actif/actions/@2', ('Créer', 'images/new.png', 'CORE', 'usersEdit', 0, 1, 1))
        self.assert_action_equal('POST', '#user_actif/actions/@3', ('Désactiver', 'images/delete.png', 'CORE', 'usersDisabled', 0, 1, 0))

        self.assert_grid_equal('user_inactif', {"username": "nom d'utilisateur", "first_name": "prénom", "last_name": "nom"}, 0)
        self.assert_count_equal('#user_inactif/actions', 3)
        self.assert_action_equal('POST', '#user_inactif/actions/@0', ('Réactiver', 'images/ok.png', 'CORE', 'usersEnabled', 0, 1, 0))
        self.assert_action_equal('POST', '#user_inactif/actions/@1', ('Modifier', 'images/edit.png', 'CORE', 'usersEdit', 0, 1, 0))
        self.assert_action_equal('DELETE', '#user_inactif/actions/@2', ('Supprimer', 'images/delete.png', 'CORE', 'usersDelete', 0, 1, 2))

        self.assert_grid_equal('preference', {"title": "nom", "value_txt": "valeur"}, 3)

    def test_userdelete(self):
        add_user("user1")
        add_user("user2")
        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_count_equal('user_actif', 4)
        self.assert_json_equal('', 'user_actif/@0/username', 'admin')
        self.assert_json_equal('', 'user_actif/@1/username', 'empty')
        self.assert_json_equal('', 'user_actif/@2/username', 'user1')
        self.assert_json_equal('', 'user_actif/@3/username', 'user2')

        self.factory.xfer = UsersDelete()
        self.calljson('/CORE/usersDelete', {'user_actif': '3;4'}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'usersDelete')
        self.assertEqual(len(self.json_context), 1)
        self.assertEqual(self.json_context['user_actif'], '3;4')
        self.assert_json_equal('', 'type', '2')
        self.assert_json_equal('', 'text', 'Voulez-vous supprimer ces 2 utilisateurs?')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('DELETE', self.json_actions[0], ('Oui', 'images/ok.png', 'CORE', 'usersDelete', 1, 1, 1))
        self.assert_action_equal('POST', self.json_actions[1], ('Non', 'images/cancel.png'))

        self.factory.xfer = UsersDelete()
        self.calljson('/CORE/usersDelete', {'user_actif': '3;4', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDelete')
        self.assertEqual(len(self.json_context), 1)
        self.assertEqual(self.json_context['user_actif'], '3;4')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_count_equal('user_actif', 2)
        self.assert_json_equal('', 'user_actif/@0/username', 'admin')
        self.assert_json_equal('', 'user_actif/@1/username', 'empty')

    def test_user_himself(self):
        self.calljson('/CORE/authentification', {'login': 'admin', 'password': 'admin'})
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/usersDelete', {'user_actif': '1'}, 'delete')
        self.assert_observer('core.exception', 'CORE', 'usersDelete')
        self.assert_json_equal('', "message", "Vous ne pouvez vous supprimer!")

        self.calljson('/CORE/usersDisabled', {'user_actif': '1'})
        self.assert_observer('core.exception', 'CORE', 'usersDisabled')
        self.assert_json_equal('', "message", "Vous ne pouvez vous désactiver!")

        self.calljson('/CORE/exitConnection', {})

    def test_userdisabledenabled(self):
        user1 = add_user("user1")
        user1.email = "empty@lucterios.org"
        user1.save()

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_count_equal("user_actif", 3)
        self.assert_count_equal("user_inactif", 0)
        self.assert_json_equal('', 'user_actif/@0/username', 'admin')
        self.assert_json_equal('', 'user_actif/@1/username', 'empty')
        self.assert_json_equal('', 'user_actif/@2/username', 'user1')

        self.factory.xfer = UsersDisabled()
        self.calljson('/CORE/usersDisabled', {'user_actif': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDisabled')
        self.assertEqual(self.json_context['user_actif'], '3')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_count_equal('user_actif', 2)
        self.assert_count_equal('user_inactif', 1)
        self.assert_json_equal('', 'user_actif/@0/username', 'admin')
        self.assert_json_equal('', 'user_actif/@1/username', 'empty')
        self.assert_json_equal('', 'user_inactif/@0/username', 'user1')

        self.factory.xfer = UsersEnabled()
        self.calljson('/CORE/usersEnabled', {'user_inactif': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEnabled')
        self.assertEqual(self.json_context['user_inactif'], '3')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_count_equal('user_actif', 3)
        self.assert_count_equal('user_inactif', 0)
        self.assert_json_equal('', 'user_actif/@0/username', 'admin')
        self.assert_json_equal('', 'user_actif/@1/username', 'empty')
        self.assert_json_equal('', 'user_actif/@2/username', 'user1')

    def test_userenabled_conf_email(self):
        settings.LOGIN_FIELD = 'email'
        settings.ASK_LOGIN_EMAIL = True
        user1 = add_user("user1", last_login=None)
        user1.is_active = False
        user1.save()
        user2 = add_user('empty2', last_login=None)
        user2.email = "empty@lucterios.org"
        user2.is_active = False
        user2.save()
        user3 = add_user('empty3', last_login=None)
        user3.email = ""
        user3.is_active = False
        user3.save()

        self.factory.xfer = UsersEnabled()
        self.calljson('/CORE/usersEnabled', {'user_inactif': user1.id}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEnabled')
        self.assertEqual(self.json_context['user_inactif'], str(user1.id))

        self.factory.xfer = UsersEnabled()
        self.calljson('/CORE/usersEnabled', {'user_inactif': user2.id}, False)
        self.assert_observer('core.exception', 'CORE', 'usersEnabled')
        self.assert_json_equal('', "message", "Utilisateur non activable: un autre avec le même courriel est actif !")

        self.factory.xfer = UsersEnabled()
        self.calljson('/CORE/usersEnabled', {'user_inactif': user3.id}, False)
        self.assert_observer('core.exception', 'CORE', 'usersEnabled')
        self.assert_json_equal('', "message", "Utilisateur non activable: pas de courriel !")

    def test_useredit(self):
        add_user("user1")
        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'user_actif': '3'}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assertEqual(self.json_meta['title'], 'Modifier un utilisateur')
        self.assertEqual(self.json_context['user_actif'], '3')
        self.assertEqual(len(self.json_actions), 3)
        self.assert_action_equal('POST', self.json_actions[0], ('Ok', 'images/ok.png', 'CORE', 'usersEdit', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal('POST', self.json_actions[1], ('Désactiver', 'images/delete.png', 'CORE', 'usersDisabled', 0, 1, 0))
        self.assert_action_equal('POST', self.json_actions[2], ('Annuler', 'images/cancel.png'))

        self.assert_json_equal('IMAGE', "img", '/static/lucterios.CORE/images/user.png')
        self.assert_coordcomp_equal("img", (0, 0, 1, 6))

        self.assert_coordcomp_equal('username', (1, 0, 1, 1))
        self.assert_json_equal('LABELFORM', "username", 'user1')
        self.assert_coordcomp_equal('date_joined', (1, 1, 1, 1))
        self.assert_json_equal('LABELFORM', "date_joined", date.today().isoformat(), True)
        self.assert_coordcomp_equal('last_login', (1, 2, 1, 1))
        self.assert_json_equal('LABELFORM', "last_login", date.today().isoformat(), True)

        self.assert_json_equal('TAB', '__tab_1', "Informations")

        self.assert_json_equal('CHECK', "is_staff", '0')
        self.assert_json_equal('CHECK', "is_superuser", '0')
        self.assert_json_equal('EDIT', "first_name", 'user1')
        self.assert_json_equal('EDIT', "last_name", 'USER1')
        self.assert_json_equal('EDIT', "email", 'user1@lucterios.org')
        self.assert_attrib_equal("email", 'needed', 'False')

        self.assert_json_equal('CHECK', "password_change", "0")
        self.assert_json_equal('PASSWD', "password1", '')
        self.assert_json_equal('PASSWD', "password2", '')

        self.assert_json_equal('TAB', '__tab_2', "Permissions")
        self.assert_comp_equal(('CHECKLIST', "groups"), [], (0, 0, 3, 1))
        self.assert_comp_equal(('CHECKLIST', "user_permissions"), [], (0, 1, 3, 1))

        self.assert_json_equal('TAB', '__tab_3', "Préférences")
        self.assert_grid_equal('preferences', {"title": "nom", "value_txt": "valeur"}, 3)

    def test_usermodif(self):
        add_user("user1")
        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3', "is_staff": '1',
                                          "is_superuser": 'o', "first_name": 'foo', "last_name": 'SUPER', "email": 'foo@super.com'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assertEqual(len(self.json_context), 6)
        self.assertEqual(self.json_context['user_actif'], '3')
        self.assertEqual(self.json_context['is_staff'], '1')
        self.assertEqual(self.json_context['is_superuser'], 'o')
        self.assertEqual(self.json_context['first_name'], 'foo')
        self.assertEqual(self.json_context['last_name'], 'SUPER')
        self.assertEqual(self.json_context['email'], 'foo@super.com')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'user_actif': '3'}, False)
        self.assert_json_equal('CHECK', "is_staff", '1')
        self.assert_json_equal('CHECK', "is_superuser", '1')
        self.assert_json_equal('EDIT', "first_name", 'foo')
        self.assert_json_equal('EDIT', "last_name", 'SUPER')
        self.assert_json_equal('EDIT', "email", 'foo@super.com')

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosuser'}, False)
        self.assert_count_equal('lucterioslogentry', 0)

    def test_useradd(self):
        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assertEqual(self.json_meta['title'], 'Ajouter un utilisateur')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_count_equal('', 17)
        self.assert_action_equal('POST', self.json_actions[0], ('Ok', 'images/ok.png', 'CORE', 'usersEdit', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal('POST', self.json_actions[1], ('Annuler', 'images/cancel.png'))

        self.assert_json_equal('IMAGE', "img", '/static/lucterios.CORE/images/user.png')
        self.assert_coordcomp_equal("img", (0, 0, 1, 6))

        self.assert_coordcomp_equal("username", (1, 0, 1, 1))
        self.assert_attrib_equal("username", 'needed', 'True')
        self.assert_attrib_equal("username", 'description', "nom d'utilisateur")

        self.assert_json_equal('TAB', '__tab_1', "Informations")

        self.assert_comp_equal(('LABELFORM', "is_active"), True, (0, 0, 1, 1, 1))
        self.assert_comp_equal(('CHECK', "is_staff"), '0', (0, 1, 1, 1, 1))
        self.assert_comp_equal(('CHECK', "is_superuser"), '0', (0, 2, 1, 1, 1))
        self.assert_comp_equal(('EDIT', "first_name"), '', (0, 3, 1, 1, 1))
        self.assert_attrib_equal('first_name', 'needed', 'True')
        self.assert_comp_equal(('EDIT', "last_name"), '', (0, 4, 1, 1, 1))
        self.assert_attrib_equal('last_name', 'needed', 'True')
        self.assert_comp_equal(('EDIT', "email"), '', (0, 5, 1, 1, 1))
        self.assert_attrib_equal("email", 'needed', 'False')
        self.assert_comp_equal(('CHECK', "password_change"), '0', (0, 6, 1, 1, 1))
        self.assert_comp_equal(('PASSWD', "password1"), '', (0, 7, 1, 1))
        self.assert_comp_equal(('PASSWD', "password2"), '', (0, 8, 1, 1))

        self.assert_json_equal('TAB', '__tab_2', "Permissions")
        self.assert_comp_equal(('CHECKLIST', "groups"), [], (0, 0, 3, 1))
        self.assert_comp_equal(('CHECKLIST', "user_permissions"), [], (0, 1, 3, 1))

    def test_useraddsave(self):
        group = LucteriosGroup.objects.create(name="my_group")
        group.permissions.set(Permission.objects.filter(id__in=[1, 3]))
        group.save()

        add_user("user1")
        add_user("user2")
        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'username': 'newuser', "is_staff": '0', "is_superuser": '1', "first_name": 'my', "last_name": 'BIG',
                                          "email": 'my@big.org', 'groups': '1', 'user_permissions': '7;9;11'}, False)

        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assertEqual(len(self.json_context), 8)
        self.assertEqual(self.json_context['username'], 'newuser')
        self.assertEqual(self.json_context['is_staff'], '0')
        self.assertEqual(self.json_context['is_superuser'], '1')
        self.assertEqual(self.json_context['first_name'], 'my')
        self.assertEqual(self.json_context['last_name'], 'BIG')
        self.assertEqual(self.json_context['email'], 'my@big.org')
        self.assertEqual(self.json_context['groups'], '1')
        self.assertEqual(self.json_context['user_permissions'], '7;9;11')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'username': 'newuser2', "is_staff": '0', "is_superuser": '1', "first_name": 'my', "last_name": 'BIG',
                                          "email": 'my@big.org'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assert_action_equal('POST', self.response_json['action'], ("", "images/edit.png", "CORE", "usersShow", 1, 1, 1, {"user_actif": 6}))
        self.factory.xfer = UsersShow()
        self.calljson('/CORE/usersShow', {"user_actif": 6}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersShow')

        self.assertEqual(6, len(LucteriosUser.objects.all()))

        user = LucteriosUser.objects.get(id=5)
        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'user_actif': '5'}, False)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.date_joined.strftime('%d %m %Y'), date.today().strftime('%d %m %Y'))
        self.assertEqual(user.last_login, None)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.first_name, 'my')
        self.assertEqual(user.last_name, 'BIG')
        self.assertEqual(user.email, 'my@big.org')
        groups = user.groups.all().order_by('id')
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].id, 1)
        perms = user.user_permissions.all().order_by('id')
        self.assertEqual(len(perms), 3)
        self.assertEqual(perms[0].id, 7)
        self.assertEqual(perms[1].id, 9)
        self.assertEqual(perms[2].id, 11)

    def test_useraddsave_conf_email(self):
        settings.LOGIN_FIELD = 'email'
        settings.ASK_LOGIN_EMAIL = True

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assert_attrib_equal("email", 'needed', 'True')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'username': 'user1', "is_staff": '0', "is_superuser": '0', "first_name": 'user1', "last_name": 'USER',
                                          "email": 'user@big.org'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assert_action_equal('POST', self.response_json['action'], ("", "images/edit.png", "CORE", "usersShow", 1, 1, 1, {"user_actif": 3}))
        self.factory.xfer = UsersShow()
        self.calljson('/CORE/usersShow', {"user_actif": 3}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersShow')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'username': 'user2', "is_staff": '0', "is_superuser": '0', "first_name": 'user2', "last_name": 'USER',
                                          "email": 'user@big.org'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assert_action_equal('POST', self.response_json['action'], ("", "images/edit.png", "CORE", "usersShow", 1, 1, 1, {"user_actif": 4}))

        self.factory.xfer = UsersShow()
        self.calljson('/CORE/usersShow', {"user_actif": 4}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'usersShow')
        self.assert_json_equal('', 'type', '1')
        self.assert_json_equal('', 'text', 'Utilisateur déactivé: un autre avec le même courriel est actif !')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'username': 'user3', "is_staff": '0', "is_superuser": '0', "first_name": 'user3', "last_name": 'USER',
                                          "email": ''}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assert_action_equal('POST', self.response_json['action'], ("", "images/edit.png", "CORE", "usersShow", 1, 1, 1, {"user_actif": 5}))

        self.factory.xfer = UsersShow()
        self.calljson('/CORE/usersShow', {"user_actif": 5}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'usersShow')
        self.assert_json_equal('', 'type', '1')
        self.assert_json_equal('', 'text', 'Utilisateur déactivé: pas de courriel !')

    def test_userdeldisabled(self):

        user = add_user("user1")
        user.is_active = False
        user.save()
        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_count_equal('user_actif', 2)
        self.assert_count_equal('user_inactif', 1)

        self.factory.xfer = UsersDelete()
        self.calljson('/CORE/usersDelete', {'user_inactif': '3'}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'usersDelete')
        self.assert_json_equal('', 'text', "Voulez-vous supprimer cet enregistrement de 'utilisateur'?")
        self.assertEqual(len(self.json_context), 1)
        self.assertEqual(self.json_context['user_inactif'], '3')

        self.factory.xfer = UsersDelete()
        self.calljson('/CORE/usersDelete', {'user_inactif': '3', "CONFIRME": 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDelete')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_count_equal('user_actif', 2)
        self.assert_count_equal('user_inactif', 0)

    def test_userpassword(self):
        user = add_user("user1")
        user.set_password('user')
        user.save()

        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('user'), 'init')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
                                          'password_change': 'o', 'password1': 'abc', 'password2': '132'}, False)
        self.assert_observer('core.exception', 'CORE', 'usersEdit')
        self.assert_json_equal('', 'message', 'Les mots de passes sont différents!')
        self.assert_json_equal('', 'code', '3')

        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('user'), 'after different')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
                                          'password_change': 'n', 'password1': '', 'password2': ''}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('user'), 'after empty')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
                                          'password_change': 'o', 'password1': 'abc', 'password2': 'abc'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('abc'), 'success after change')
        self.assertFalse(user.check_password('user'), 'wrong after change')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
                                          'password_change': 'o', 'password1': '', 'password2': ''}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password(''), 'success after change')
        self.assertFalse(user.check_password('abc'), 'wrong1 after change')
        self.assertFalse(user.check_password('user'), 'wrong2 after change')

    def test_concurentedit(self):
        user1 = add_user("user1")
        user1.is_superuser = True
        user1.save()

        self.calljson('/CORE/authentification', {'login': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/usersEdit', {'user_actif': '3'})
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assertEqual(len(self.json_actions), 3)
        self.assert_action_equal('POST', self.response_json['close'], ('unlock', None, "CORE", "unlock", 1, 1, 1))
        self.assertEqual(len(self.json_context), 2)
        self.assertEqual(self.json_context["user_actif"], '3')
        self.assertEqual(self.json_context["LOCK_IDENT"], 'lucterios.CORE.models-LucteriosUser-3')

        new_test = LucteriosTest("setUp")
        new_test.setUp()
        new_test.calljson('/CORE/authentification', {'login': 'user1', 'password': 'user1'})
        new_test.assert_observer('core.auth', 'CORE', 'authentification')
        new_test.assert_json_equal('', '', 'OK')

        new_test.calljson('/CORE/usersEdit', {'user_actif': '3'})
        new_test.assert_observer('core.exception', 'CORE', 'usersEdit')
        new_test.assert_json_equal('', 'message', str("Enregistrement verrouillé par 'admin'!"))
        new_test.assert_json_equal('', 'code', '3')

        self.calljson('/CORE/unlock', {'user_actif': '3', "LOCK_IDENT": 'lucterios.CORE.models-LucteriosUser-3'})
        self.assert_observer('core.acknowledge', 'CORE', 'unlock')

        new_test.calljson('/CORE/usersEdit', {'user_actif': '3'})
        new_test.assert_observer('core.custom', 'CORE', 'usersEdit')

    def test_auditlog_user(self):
        LucteriosAuditlogModelRegistry.set_state_packages(['CORE'])

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosuser'}, False)
        self.assert_count_equal('lucterioslogentry', 0)

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_count_equal('user_actif', 2)
        self.assert_count_equal('user_inactif', 0)

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'SAVE': 'YES', 'username': 'abc', 'first_name': 'John', 'last_name': 'Doe', 'user_permissions': '1;3;4'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosuser'}, False)
        self.assert_count_equal('lucterioslogentry', 1)

        self.factory.xfer = UsersDisabled()
        self.calljson('/CORE/usersDisabled', {'user_actif': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDisabled')

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosuser'}, False)
        self.assert_count_equal('lucterioslogentry', 2)

        self.factory.xfer = UsersDelete()
        self.calljson('/CORE/usersDelete', {'user_actif': '3', "CONFIRME": 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDelete')

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosuser'}, False)
        self.assert_count_equal('lucterioslogentry', 3)
        self.assert_json_equal('', 'lucterioslogentry/@0/action', 2)
        self.assert_json_equal('', 'lucterioslogentry/@0/object_repr', "abc")
        self.assert_json_equal('', 'lucterioslogentry/@1/action', 1)
        self.assert_json_equal('', 'lucterioslogentry/@1/object_repr', "abc")
        self.assert_json_equal('', 'lucterioslogentry/@2/action', 0)
        self.assert_json_equal('', 'lucterioslogentry/@2/object_repr', "abc")

    def test_default_preference(self):
        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')

        self.assert_count_equal('preference', 3)
        self.assert_json_equal('', 'preference/@0/id', 2)
        self.assert_json_equal('', 'preference/@0/title', 'dummy-default-price')
        self.assert_json_equal('', 'preference/@0/value_txt', '100')
        self.assert_json_equal('', 'preference/@1/id', 3)
        self.assert_json_equal('', 'preference/@1/title', 'dummy-default-valid')
        self.assert_json_equal('', 'preference/@1/value_txt', 'Non')
        self.assert_json_equal('', 'preference/@2/id', 1)
        self.assert_json_equal('', 'preference/@2/title', 'dummy-default-value')
        self.assert_json_equal('', 'preference/@2/value_txt', '0')
        self.assert_count_equal('#preference/actions', 1)
        self.assert_action_equal('POST', '#preference/actions/@0', ('Modifier', 'images/edit.png', 'CORE', 'preferenceEdit', 0, 1, 0))

        self.factory.xfer = PreferenceEdit()
        self.calljson('/CORE/preferenceEdit', {'preference': 2}, False)
        self.assert_observer('core.custom', 'CORE', 'preferenceEdit')
        self.assert_count_equal('', 3)
        self.assert_json_equal('LABELFORM', 'title', 'dummy-default-price')
        self.assert_json_equal('FLOAT', 'dummy-default-price', '100')
        self.assertEqual(self.json_context['user'], 0)

        self.factory.xfer = PreferenceEdit()
        self.calljson('/CORE/preferenceEdit', {'preference': 2, 'user': 0, 'SAVE': 'YES', 'dummy-default-price': '49.99'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'preferenceEdit')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_json_equal('', 'preference/@0/title', 'dummy-default-price')
        self.assert_json_equal('', 'preference/@0/value_txt', '49.99')

    def test_user_preferences(self):
        user = add_user("user1")
        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'user_actif': user.id}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assert_count_equal('preferences', 3)
        self.assert_json_equal('', 'preferences/@0/id', 'dummy-default-price')
        self.assert_json_equal('', 'preferences/@0/title', 'dummy-default-price')
        self.assert_json_equal('', 'preferences/@0/value_txt', '100')
        self.assert_json_equal('', 'preferences/@1/id', 'dummy-default-valid')
        self.assert_json_equal('', 'preferences/@1/title', 'dummy-default-valid')
        self.assert_json_equal('', 'preferences/@1/value_txt', 'Non')
        self.assert_json_equal('', 'preferences/@2/id', 'dummy-default-value')
        self.assert_json_equal('', 'preferences/@2/title', 'dummy-default-value')
        self.assert_json_equal('', 'preferences/@2/value_txt', '0')
        self.assert_count_equal('#preferences/actions', 1)
        self.assert_action_equal('POST', '#preferences/actions/@0', ('Modifier', 'images/edit.png', 'CORE', 'preferenceEdit', 0, 1, 0))

        self.factory.xfer = PreferenceEdit()
        self.calljson('/CORE/preferenceEdit', {'preferences': 'dummy-default-value', 'user_actif': user.id}, False)
        self.assert_observer('core.custom', 'CORE', 'preferenceEdit')
        self.assert_count_equal('', 5)
        self.assert_json_equal('LABELFORM', 'title', 'dummy-default-value')
        self.assert_json_equal('LABELFORM', 'user', 'user1')
        self.assert_json_equal('FLOAT', 'dummy-default-value', '0')
        self.assert_json_equal('CHECK', 'setdefault', False)
        self.assertEqual(self.json_context['user'], user.id)

        self.factory.xfer = PreferenceEdit()
        self.calljson('/CORE/preferenceEdit', {'preferences': 'dummy-default-value', 'user': user.id, 'SAVE': 'YES', 'dummy-default-value': '7', 'setdefault': False}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'preferenceEdit')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'user_actif': user.id}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assert_count_equal('preferences', 3)
        self.assert_json_equal('', 'preferences/@2/id', 'dummy-default-value')
        self.assert_json_equal('', 'preferences/@2/title', 'dummy-default-value')
        self.assert_json_equal('', 'preferences/@2/value_txt', '7')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_json_equal('', 'preference/@2/title', 'dummy-default-value')
        self.assert_json_equal('', 'preference/@2/value_txt', '0')

        self.factory.xfer = PreferenceEdit()
        self.calljson('/CORE/preferenceEdit', {'preferences': 'dummy-default-value', 'user': user.id, 'SAVE': 'YES', 'dummy-default-value': '7', 'setdefault': True}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'preferenceEdit')

        self.factory.xfer = UsersEdit()
        self.calljson('/CORE/usersEdit', {'user_actif': user.id}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assert_count_equal('preferences', 3)
        self.assert_json_equal('', 'preferences/@2/id', 'dummy-default-value')
        self.assert_json_equal('', 'preferences/@2/title', 'dummy-default-value')
        self.assert_json_equal('', 'preferences/@2/value_txt', '0')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_json_equal('', 'preference/@2/title', 'dummy-default-value')
        self.assert_json_equal('', 'preference/@2/value_txt', '0')

    def test_user_conf_username(self):
        user2 = add_user('empty2')
        user2.email = "empty@lucterios.org"
        user2.is_active = True
        user2.save()
        user3 = add_user('empty3')
        user3.email = ""
        user3.is_active = True
        user3.save()

        self.assertEqual(LucteriosUser.objects.filter(is_active=True).count(), 4)
        self.assertEqual(LucteriosUser.objects.filter(is_active=False).count(), 0)
        Signal.call_signal("convertdata")
        self.assertEqual([user.username for user in LucteriosUser.objects.filter(is_active=True)], ["admin", "empty", "empty2", "empty3"])
        self.assertEqual([user.username for user in LucteriosUser.objects.filter(is_active=False)], [])

    def test_user_conf_email(self):
        settings.LOGIN_FIELD = 'email'
        settings.ASK_LOGIN_EMAIL = True
        user2 = add_user('empty2', last_login=None)
        user2.email = "empty@lucterios.org"
        user2.is_active = True
        user2.save()
        user3 = add_user('empty3', last_login=None)
        user3.email = ""
        user3.is_active = True
        user3.save()

        self.assertEqual(LucteriosUser.objects.filter(is_active=True).count(), 4)
        self.assertEqual(LucteriosUser.objects.filter(is_active=False).count(), 0)
        Signal.call_signal("convertdata")
        self.assertEqual([user.username for user in LucteriosUser.objects.filter(is_active=True)], ["empty"])
        self.assertEqual([user.username for user in LucteriosUser.objects.filter(is_active=False)], ["admin", "empty2", "empty3"])

    def test_only_admin_user(self):
        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_json_equal('LABELFORM', "CORE-OnlySuperAdmin", 'Non')

        self.assertEqual(parameters.Params.getvalue('CORE-OnlySuperAdmin'), False)

        self.factory.xfer = ChangeOnlySuperAdmin()
        self.calljson('/CORE/changeOnlySuperAdmin', {}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'changeOnlySuperAdmin')
        self.assert_json_equal('', 'text', "Voulez-vous limiter l'accès aux seuls administrateurs ?")

        self.factory.xfer = ChangeOnlySuperAdmin()
        self.calljson('/CORE/changeOnlySuperAdmin', {'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'changeOnlySuperAdmin')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_json_equal('LABELFORM', "CORE-OnlySuperAdmin", 'Oui')

        self.assertEqual(parameters.Params.getvalue('CORE-OnlySuperAdmin'), True)

        self.factory.xfer = ChangeOnlySuperAdmin()
        self.calljson('/CORE/changeOnlySuperAdmin', {}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'changeOnlySuperAdmin')

        self.factory.xfer = UsersList()
        self.calljson('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_json_equal('LABELFORM', "CORE-OnlySuperAdmin", 'Non')

        self.assertEqual(parameters.Params.getvalue('CORE-OnlySuperAdmin'), False)


class GroupTest(LucteriosTest):

    def setUp(self):
        tools.WrapAction.mode_connect_notfree = None
        LucteriosTest.setUp(self)
        signal_and_lock.unlocker_view_class = Unlock
        signal_and_lock.RecordLocker.clear()
        add_empty_user()

    def tearDown(self):
        LucteriosTest.tearDown(self)
        tools.WrapAction.mode_connect_notfree = parameters.notfree_mode_connect
        LucteriosAuditlogModelRegistry.set_state_packages([])

    def test_grouplist(self):
        self.factory.xfer = GroupsList()
        self.calljson('/CORE/groupsList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'groupsList')
        self.assertEqual(self.json_meta['title'], 'Les groupes')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal('POST', self.json_actions[0], ('Fermer', 'images/close.png'))
        self.assert_count_equal('', 3)
        self.assert_comp_equal(('IMAGE', "img"), '/static/lucterios.CORE/images/group.png', ('0', '0', '1', '1'))
        self.assert_comp_equal(('LABELFORM', "title"), 'Les groupes', ('1', '0', '1', '1'))
        self.assert_attrib_equal("title", "formatstr", "{[br/]}{[center]}{[u]}{[b]}%s{[/b]}{[/u]}{[/center]}")
        self.assert_coordcomp_equal('group', ('0', '1', '2', '1'))
        self.assert_count_equal('#group/actions', 3)
        self.assert_action_equal('POST', '#group/actions/@0', ('Modifier', 'images/edit.png', 'CORE', 'groupsEdit', 0, 1, 0))
        self.assert_action_equal('DELETE', '#group/actions/@1', ('Supprimer', 'images/delete.png', 'CORE', 'groupsDelete', 0, 1, 2))
        self.assert_action_equal('POST', '#group/actions/@2', ('Créer', 'images/new.png', 'CORE', 'groupsEdit', 0, 1, 1))
        self.assert_grid_equal('group', {"name": "nom"}, 1)
        self.assert_attrib_equal('group', "nb_lines", '1')

    def test_groupadd(self):
        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {}, False)
        self.assert_observer('core.custom', 'CORE', 'groupsEdit')
        self.assertEqual(self.json_meta['title'], 'Ajouter un groupe')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('POST', self.json_actions[0], ('Ok', 'images/ok.png', 'CORE', 'groupsEdit', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal('POST', self.json_actions[1], ('Annuler', 'images/cancel.png'))

        self.assert_count_equal('', 3)
        self.assert_comp_equal(('IMAGE', "img"), '/static/lucterios.CORE/images/group.png', (0, 0, 1, 6))
        self.assert_comp_equal(('EDIT', "name"), '', (1, 0, 3, 1))
        self.assert_comp_equal(('CHECKLIST', "permissions"), [], (1, 1, 3, 1))

    def test_useraddsave(self):
        groups = LucteriosGroup.objects.all()
        self.assertEqual(len(groups), 1)

        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'SAVE': 'YES', 'name': 'newgroup', "permissions": '1;3;5;7'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'groupsEdit')
        self.assertEqual(len(self.json_context), 2)
        self.assertEqual(self.json_context["name"], 'newgroup')
        self.assertEqual(self.json_context["permissions"], '1;3;5;7')

        groups = LucteriosGroup.objects.all().order_by('-id')
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0].name, "newgroup")
        perm = groups[0].permissions.all().order_by('id')
        self.assertEqual(len(perm), 4)
        self.assertEqual(perm[0].id, 1)
        self.assertEqual(perm[1].id, 3)
        self.assertEqual(perm[2].id, 5)
        self.assertEqual(perm[3].id, 7)

    def test_groupedit(self):
        group = LucteriosGroup.objects.create(name="my_group")
        group.permissions.set(Permission.objects.filter(id__in=[1, 3]))
        group.save()

        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'group': '2'}, False)
        self.assert_observer('core.custom', 'CORE', 'groupsEdit')
        self.assertEqual(self.json_meta['title'], 'Modifier un groupe')
        self.assert_comp_equal(('EDIT', "name"), 'my_group', (1, 0, 3, 1))

    def test_groupedit_notexist(self):
        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'group': '50'}, False)
        self.assert_observer('core.exception', 'CORE', 'groupsEdit')
        self.assert_json_equal('', 'message', str("Cet enregistrement n'existe pas!\nVeuillez rafraichir votre application."))
        self.assert_json_equal('', 'code', '3')

    def test_groupadd_same(self):
        grp = LucteriosGroup.objects.create(name="mygroup")
        grp.save()

        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'SAVE': 'YES', 'name': 'mygroup', "permissions": '1;3;5;7'}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'groupsEdit')
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context["name"], 'mygroup')
        self.assertEqual(self.json_context["permissions"], '1;3;5;7')
        self.assert_json_equal('', 'type', '3')
        self.assert_json_equal('', 'text', str('Cet enregistrement existe déjà!'))
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal('POST', self.json_actions[0], ('Recommencer', None, "CORE", "groupsEdit", 1, 1, 1))

    def test_groupedit_fornew(self):
        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'name': 'mygroup', "permissions": '1;3;5;7'}, False)
        self.assertEqual(self.json_meta['title'], 'Ajouter un groupe')
        self.assertEqual(len(self.json_context), 2)
        self.assertEqual(self.json_context["name"], 'mygroup')
        self.assertEqual(self.json_context["permissions"], '1;3;5;7')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_comp_equal(('EDIT', "name"), 'mygroup', (1, 0, 3, 1))

    def test_concurentedit(self):
        user1 = add_user("user1")
        user1.is_superuser = True
        user1.save()
        grp = LucteriosGroup.objects.create(name="mygroup")
        grp.save()

        self.calljson('/CORE/authentification', {'login': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/groupsEdit', {'group': '1'})
        self.assert_observer('core.custom', 'CORE', 'groupsEdit')
        self.assert_action_equal('POST', self.response_json['close'], ('unlock', None, "CORE", "unlock", 1, 1, 1))
        self.assertEqual(len(self.json_context), 2)
        self.assertEqual(self.json_context["group"], '1')
        self.assertEqual(self.json_context["LOCK_IDENT"], 'lucterios.CORE.models-LucteriosGroup-1')

        new_test = LucteriosTest("setUp")
        new_test.setUp()
        new_test.calljson('/CORE/authentification', {'login': 'user1', 'password': 'user1'})
        new_test.assert_observer('core.auth', 'CORE', 'authentification')
        new_test.assert_json_equal('', '', 'OK')

        new_test.calljson('/CORE/groupsEdit', {'group': '1'})
        new_test.assert_observer('core.exception', 'CORE', 'groupsEdit')
        new_test.assert_json_equal('', 'message', str("Enregistrement verrouillé par 'admin'!"))
        new_test.assert_json_equal('', 'code', '3')

        self.calljson('/CORE/exitConnection', {})

        new_test.calljson('/CORE/groupsEdit', {'group': '1'})
        new_test.assert_observer('core.custom', 'CORE', 'groupsEdit')

    def test_auditlog_user(self):
        LucteriosAuditlogModelRegistry.set_state_packages(['CORE'])

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosuser'}, False)
        self.assert_count_equal('lucterioslogentry', 0)

        self.factory.xfer = GroupsList()
        self.calljson('/CORE/groupsList', {}, False)
        self.assert_count_equal('group', 1)

        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'SAVE': 'YES', 'name': 'truc', 'permissions': '7;9;13'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'groupsEdit')

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosuser'}, False)
        self.assert_count_equal('lucterioslogentry', 1)

        self.factory.xfer = GroupsDelete()
        self.calljson('/CORE/groupsDelete', {'group': '2', "CONFIRME": 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'groupsDelete')

        self.factory.xfer = AudiLogConfig()
        self.calljson('/CORE/audiLogConfig', {'type_selected': 'CORE.lucteriosgroup'}, False)
        self.assert_count_equal('lucterioslogentry', 2)
        self.assert_json_equal('', 'lucterioslogentry/@0/action', 2)
        self.assert_json_equal('', 'lucterioslogentry/@0/object_repr', "truc")
        self.assert_json_equal('', 'lucterioslogentry/@1/action', 0)
        self.assert_json_equal('', 'lucterioslogentry/@1/object_repr', "truc")


class SessionTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        add_empty_user()

    def test_sessionlist(self):
        self.calljson('/CORE/authentification', {'login': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/sessionList', {}, 'get')
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assertEqual(self.json_meta['title'], 'Sessions & taches')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal('POST', self.json_actions[0], ('Fermer', 'images/close.png'))
        self.assert_count_equal('', 6)
        self.assert_json_equal('IMAGE', "img", '/static/lucterios.CORE/images/session.png')
        self.assert_coordcomp_equal('img', ('0', '0', '1', '1'))
        self.assert_json_equal('LABELFORM', "title", 'Sessions & taches')
        self.assert_attrib_equal("title", "formatstr", "{[br/]}{[center]}{[u]}{[b]}%s{[/b]}{[/u]}{[/center]}")
        self.assert_coordcomp_equal("title", ('1', '0', '1', '1'))
        self.assert_coordcomp_equal("session", ('0', '0', '2', '1'))
        self.assert_coordcomp_equal("tasks", ('0', '0', '2', '1'))

        self.assert_grid_equal('session', {"username": "nom d'utilisateur", "expire_date": "date d'expiration", "is_active": "actif ?"}, 1)
        self.assert_json_equal('', 'session/@0/username', 'admin')
        self.assert_json_equal('', 'session/@0/is_active', True)
        self.assert_attrib_equal('session', "nb_lines", '1')

    def test_sessiondel(self):
        self.calljson('/CORE/authentification', {'login': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')

        self.calljson('/CORE/sessionList', {}, 'get')
        self.assert_count_equal("session", 1)
        session_id = self.json_data["session"][0]["id"]

        self.calljson('/CORE/sessionDelete', {'session': session_id, 'CONFIRME': 'YES'}, 'delete')
        self.assert_observer('core.acknowledge', 'CORE', 'sessionDelete')

        self.calljson('/CORE/sessionList', {}, 'get')
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assert_count_equal("session", 1)
        self.assert_json_equal('', 'session/@0/id', session_id)
