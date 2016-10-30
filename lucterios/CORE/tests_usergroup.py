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

from lucterios.framework.test import LucteriosTest, add_empty_user, add_user
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.views_usergroup import UsersList, UsersDelete, UsersDisabled, UsersEnabled, UsersEdit
from lucterios.CORE.views_usergroup import GroupsList, GroupsEdit
from lucterios.framework import tools, signal_and_lock

from django.contrib.auth.models import Permission
from django.utils import six
from lucterios.CORE.views import Unlock
from lucterios.CORE.models import LucteriosGroup, LucteriosUser
from lucterios.CORE import parameters


class UserTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        signal_and_lock.unlocker_view_class = Unlock
        signal_and_lock.RecordLocker.clear()
        LucteriosTest.setUp(self)
        add_empty_user()

    def test_userlist(self):
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersList')
        self.assert_xml_equal('TITLE', 'Utilisateurs')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal('ACTIONS/ACTION', ('Fermer', 'images/close.png'))
        self.assert_count_equal('COMPONENTS/*', 9)
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/user.png')
        self.assert_coordcomp_equal('COMPONENTS/IMAGE[@name="img"]', ('0', '0', '1', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="title"]', '{[br/]}{[center]}{[u]}{[b]}Utilisateurs du logiciel{[/b]}{[/u]}{[/center]}')
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="title"]', ('1', '0', '1', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_actifs"]', '{[b]}Liste des utilisateurs actifs{[/b]}')
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="lbl_actifs"]', ('0', '1', '2', '1'))
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="user_actif"]', ('0', '2', '2', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="separator"]', None)
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="separator"]', ('0', '4', '1', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_inactif"]', '{[b]}Liste des utilisateurs inactifs{[/b]}')
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="lbl_inactif"]', ('0', '5', '2', '1'))
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="user_inactif"]', ('0', '6', '2', '1'))

        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/HEADER', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/HEADER[@name="username"]', "nom d'utilisateur")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/HEADER[@name="first_name"]', "prénom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/HEADER[@name="last_name"]', "nom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/HEADER[@name="last_login"]', "dernière connexion")
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="first_name"]', 'administrator')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="first_name"]', 'empty')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="last_name"]', 'ADMIN')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="last_name"]', 'NOFULL')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="last_login"]',
                              date.today().strftime('%e').strip(), True)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="last_login"]',
                              date.today().strftime('%e').strip(), True)

        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION', 4)
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=1]',
                                 ('Modifier', 'images/edit.png', 'CORE', 'usersEdit', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=2]',
                                 ('Supprimer', 'images/delete.png', 'CORE', 'usersDelete', 0, 1, 2))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=3]',
                                 ('Ajouter', 'images/add.png', 'CORE', 'usersEdit', 0, 1, 1))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=4]',
                                 ('Désactiver', 'images/delete.png', 'CORE', 'usersDisabled', 0, 1, 0))

        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="username"]', "nom d'utilisateur")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="first_name"]', "prénom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="last_name"]', "nom")
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION', 2)
        self.assert_action_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION[position()=1]',
                                 ('Réactiver', 'images/ok.png', 'CORE', 'usersEnabled', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION[position()=2]',
                                 ('Supprimer', 'images/delete.png', 'CORE', 'usersDelete', 0, 1, 2))

    def test_userdelete(self):
        add_user("user1")
        add_user("user2")
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD', 4)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=4]/VALUE[@name="username"]', 'user2')

        self.factory.xfer = UsersDelete()
        self.call('/CORE/usersDelete', {'user_actif': '3;4'}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'usersDelete')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3;4')
        self.assert_attrib_equal('TEXT', 'type', '2')
        self.assert_xml_equal(
            'TEXT', 'Voulez-vous supprimer ces 2 utilisateurs?')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_xml_equal('ACTIONS/ACTION[1]', 'Oui')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'icon', '/static/lucterios.CORE/images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'extension', 'CORE')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'action', 'usersDelete')
        self.assert_xml_equal('ACTIONS/ACTION[2]', 'Non')
        self.assert_attrib_equal(
            'ACTIONS/ACTION[2]', 'icon', '/static/lucterios.CORE/images/cancel.png')
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'action', None)

        self.factory.xfer = UsersDelete()
        self.call(
            '/CORE/usersDelete', {'user_actif': '3;4', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDelete')
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3;4')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')

    def test_user_himself(self):
        self.call(
            '/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/usersDelete', {'user_actif': '1'})
        self.assert_observer('core.exception', 'CORE', 'usersDelete')
        self.assert_xml_equal(
            "EXCEPTION/MESSAGE", "Vous ne pouvez vous supprimer!")

        self.call('/CORE/usersDisabled', {'user_actif': '1'})
        self.assert_observer('core.exception', 'CORE', 'usersDisabled')
        self.assert_xml_equal(
            "EXCEPTION/MESSAGE", "Vous ne pouvez vous désactiver!")

        self.call('/CORE/exitConnection', {})

    def test_userdisabledenabled(self):
        add_user("user1")
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD', 3)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')

        self.factory.xfer = UsersDisabled()
        self.call('/CORE/usersDisabled', {'user_actif': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDisabled')
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_inactif"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_inactif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')

        self.factory.xfer = UsersEnabled()
        self.call('/CORE/usersEnabled', {'user_inactif': '3'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEnabled')
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_inactif"]', '3')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD', 3)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')

    def test_useredit(self):
        add_user("user1")
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'user_actif': '3'}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assert_xml_equal('TITLE', 'Modifier un utilisateur')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3')
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_action_equal(
            'ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'usersEdit', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal(
            'ACTIONS/ACTION[2]', ('Désactiver', 'images/delete.png', 'CORE', 'usersDisabled', 0, 1, 1))
        self.assert_action_equal(
            'ACTIONS/ACTION[3]', ('Annuler', 'images/cancel.png'))

        self.assert_xml_equal(
            'COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/user.png')
        self.assert_coordcomp_equal(
            'COMPONENTS/IMAGE[@name="img"]', (0, 0, 1, 6))

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_username"]', "{[b]}nom d'utilisateur{[/b]}", (1, 0, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/LABELFORM[@name="username"]', (2, 0, 1, 1))
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="username"]', 'user1')
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_date_joined"]', "{[b]}date d'inscription{[/b]}", (1, 1, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/LABELFORM[@name="date_joined"]', (2, 1, 1, 1))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="date_joined"]', date.today().strftime('%e').strip(), True)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_last_login"]', "{[b]}dernière connexion{[/b]}", (1, 2, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/LABELFORM[@name="last_login"]', (2, 2, 1, 1))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="last_login"]', date.today().strftime('%e').strip(), True)

        self.assert_xml_equal('COMPONENTS/TAB[1]', "Informations")

        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_is_staff"]', "{[b]}statut équipe{[/b]}")
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_staff"]', '0')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_is_superuser"]', "{[b]}statut super-utilisateur{[/b]}")
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_superuser"]', '0')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_first_name"]', "{[b]}prénom{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="first_name"]', 'user1')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_last_name"]', "{[b]}nom{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="last_name"]', 'USER1')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_email"]', "{[b]}adresse électronique{[/b]}")
        self.assert_xml_equal('COMPONENTS/EDIT[@name="email"]', None)

        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_password_change"]', "{[b]}Changer le mot de passe ?{[/b]}")
        self.assert_xml_equal('COMPONENTS/CHECK[@name="password_change"]', "1")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_password1"]', "{[b]}mot de passe{[/b]}")
        self.assert_xml_equal('COMPONENTS/PASSWD[@name="password1"]', None)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_password2"]', "{[b]}re-mot de passe{[/b]}")
        self.assert_xml_equal('COMPONENTS/PASSWD[@name="password2"]', None)

        self.assert_xml_equal('COMPONENTS/TAB[2]', "Permissions")

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_groups"]', "{[b]}groupes{[/b]}", (0, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="hd_groups_available"]', "{[center]}{[i]}Groupes disponibles{[/i]}{[/center]}", (1, 0, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECKLIST[@name="groups_available"]', (1, 1, 1, 5))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="hd_groups_chosen"]', "{[center]}{[i]}Groupes choisis{[/i]}{[/center]}", (3, 0, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECKLIST[@name="groups_chosen"]', (3, 1, 1, 5))

        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="groups_addall"]', (2, 1, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="groups_add"]', (2, 2, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="groups_del"]', (2, 3, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="groups_delall"]', (2, 4, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="groups_addall"]/ACTIONS/ACTION', ('>>', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="groups_add"]/ACTIONS/ACTION', ('>', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="groups_del"]/ACTIONS/ACTION', ('<', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="groups_delall"]/ACTIONS/ACTION', ('<<', None, None, None, 0, 1, 1))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_user_permissions"]', "{[b]}permissions de l'utilisateur{[/b]}", (0, 5, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="hd_user_permissions_available"]',
                               "{[center]}{[i]}Permissions disponibles{[/i]}{[/center]}", (1, 5, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECKLIST[@name="user_permissions_available"]', (1, 6, 1, 5))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="hd_user_permissions_chosen"]', "{[center]}{[i]}Permissions choisies{[/i]}{[/center]}", (3, 5, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECKLIST[@name="user_permissions_chosen"]', (3, 6, 1, 5))

        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="user_permissions_addall"]', (2, 6, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="user_permissions_add"]', (2, 7, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="user_permissions_del"]', (2, 8, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="user_permissions_delall"]', (2, 9, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="user_permissions_addall"]/ACTIONS/ACTION', ('>>', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="user_permissions_add"]/ACTIONS/ACTION', ('>', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="user_permissions_del"]/ACTIONS/ACTION', ('<', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="user_permissions_delall"]/ACTIONS/ACTION', ('<<', None, None, None, 0, 1, 1))

    def test_usermodif(self):
        add_user("user1")
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3', "is_staff": '1',
                                      "is_superuser": 'o', "first_name": 'foo', "last_name": 'SUPER', "email": 'foo@super.com'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assert_count_equal('CONTEXT/PARAM', 6)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_staff"]', '1')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_superuser"]', 'o')
        self.assert_xml_equal('CONTEXT/PARAM[@name="first_name"]', 'foo')
        self.assert_xml_equal('CONTEXT/PARAM[@name="last_name"]', 'SUPER')
        self.assert_xml_equal('CONTEXT/PARAM[@name="email"]', 'foo@super.com')

        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'user_actif': '3'}, False)
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_staff"]', '1')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_superuser"]', '1')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="first_name"]', 'foo')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="last_name"]', 'SUPER')
        self.assert_xml_equal(
            'COMPONENTS/EDIT[@name="email"]', 'foo@super.com')

    def test_useradd(self):
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {}, False)
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assert_xml_equal('TITLE', 'Ajouter un utilisateur')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_count_equal('COMPONENTS/*', 41)
        self.assert_action_equal(
            'ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'usersEdit', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal(
            'ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))

        self.assert_xml_equal(
            'COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/user.png')
        self.assert_coordcomp_equal(
            'COMPONENTS/IMAGE[@name="img"]', (0, 0, 1, 6))

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_username"]', "{[b]}nom d'utilisateur{[/b]}", (1, 0, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/EDIT[@name="username"]', (2, 0, 1, 1))
        self.assert_attrib_equal(
            'COMPONENTS/EDIT[@name="username"]', 'needed', '1')
        self.assert_attrib_equal(
            'COMPONENTS/EDIT[@name="username"]', 'description', "nom d'utilisateur")

        self.assert_xml_equal('COMPONENTS/TAB[1]', "Informations")

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_is_active"]', "{[b]}actif{[/b]}", (0, 0, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_is_staff"]', "{[b]}statut équipe{[/b]}", (0, 1, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_is_superuser"]', "{[b]}statut super-utilisateur{[/b]}", (0, 2, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_first_name"]', "{[b]}prénom{[/b]}", (0, 3, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_last_name"]', "{[b]}nom{[/b]}", (0, 4, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_email"]', "{[b]}adresse électronique{[/b]}", (0, 5, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_password_change"]', "{[b]}Changer le mot de passe ?{[/b]}", (0, 6, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_password1"]', "{[b]}mot de passe{[/b]}", (0, 7, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_password2"]', "{[b]}re-mot de passe{[/b]}", (0, 8, 1, 1))

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="is_active"]', "Oui", (1, 0, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/CHECK[@name="is_staff"]', '0', (1, 1, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/CHECK[@name="is_superuser"]', '0', (1, 2, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/EDIT[@name="first_name"]', None, (1, 3, 1, 1, 1))
        self.assert_attrib_equal(
            'COMPONENTS/EDIT[@name="first_name"]', 'needed', '0')
        self.assert_comp_equal(
            'COMPONENTS/EDIT[@name="last_name"]', None, (1, 4, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/EDIT[@name="email"]', None, (1, 5, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/CHECK[@name="password_change"]', '1', (1, 6, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/PASSWD[@name="password1"]', None, (1, 7, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/PASSWD[@name="password2"]', None, (1, 8, 1, 1))

        self.assert_xml_equal('COMPONENTS/TAB[2]', "Permissions")
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_groups"]', "{[b]}groupes{[/b]}", (0, 0, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="hd_groups_available"]', "{[center]}{[i]}Groupes disponibles{[/i]}{[/center]}", (1, 0, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/CHECKLIST[@name="groups_available"]', (1, 1, 1, 5))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="hd_groups_chosen"]', "{[center]}{[i]}Groupes choisis{[/i]}{[/center]}", (3, 0, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/CHECKLIST[@name="groups_chosen"]', (3, 1, 1, 5))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_user_permissions"]', "{[b]}permissions de l'utilisateur{[/b]}", (0, 5, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="hd_user_permissions_available"]',
                               "{[center]}{[i]}Permissions disponibles{[/i]}{[/center]}", (1, 5, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/CHECKLIST[@name="user_permissions_available"]', (1, 6, 1, 5))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="hd_user_permissions_chosen"]', "{[center]}{[i]}Permissions choisies{[/i]}{[/center]}", (3, 5, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/CHECKLIST[@name="user_permissions_chosen"]', (3, 6, 1, 5))

    def test_useraddsave(self):
        group = LucteriosGroup.objects.create(
            name="my_group")
        group.permissions = Permission.objects.filter(
            id__in=[1, 3])
        group.save()

        add_user("user1")
        add_user("user2")
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'SAVE': 'YES', 'username': 'newuser', "is_staff": '0', "is_superuser": '1', "first_name": 'my', "last_name": 'BIG',
                                      "email": 'my@big.org', 'groups': '1', 'user_permissions': '7;9;11'}, False)

        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        self.assert_count_equal('CONTEXT/PARAM', 8)
        self.assert_xml_equal('CONTEXT/PARAM[@name="username"]', 'newuser')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_staff"]', '0')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_superuser"]', '1')
        self.assert_xml_equal('CONTEXT/PARAM[@name="first_name"]', 'my')
        self.assert_xml_equal('CONTEXT/PARAM[@name="last_name"]', 'BIG')
        self.assert_xml_equal('CONTEXT/PARAM[@name="email"]', 'my@big.org')
        self.assert_xml_equal('CONTEXT/PARAM[@name="groups"]', '1')
        self.assert_xml_equal(
            'CONTEXT/PARAM[@name="user_permissions"]', '7;9;11')

        self.assertEqual(
            5, len(LucteriosUser.objects.all()))

        user = LucteriosUser.objects.get(id=5)
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'user_actif': '5'}, False)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(
            user.date_joined.strftime('%d %m %Y'), date.today().strftime('%d %m %Y'))
        self.assertEqual(
            user.last_login.strftime('%d %m %Y'), date.today().strftime('%d %m %Y'))
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.first_name, 'my')
        self.assertEqual(user.last_name, 'BIG')
        self.assertEqual(user.email, 'my@big.org')
        groups = user.groups.all().order_by('id')
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].id, 1)
        perms = user.user_permissions.all().order_by(
            'id')
        self.assertEqual(len(perms), 3)
        self.assertEqual(perms[0].id, 7)
        self.assertEqual(perms[1].id, 9)
        self.assertEqual(perms[2].id, 11)

    def test_userdeldisabled(self):

        user = add_user("user1")
        user.is_active = False
        user.save()
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_inactif"]/RECORD', 1)

        self.factory.xfer = UsersDelete()
        self.call('/CORE/usersDelete', {'user_inactif': '3'}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'usersDelete')
        self.assert_xml_equal(
            'TEXT', "Voulez-vous supprimer cet enregistrement de 'utilisateur'?")
        self.assert_count_equal('CONTEXT/PARAM', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_inactif"]', '3')

        self.factory.xfer = UsersDelete()
        self.call(
            '/CORE/usersDelete', {'user_inactif': '3', "CONFIRME": 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersDelete')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)

    def test_userpassword(self):
        user = add_user("user1")
        user.set_password('user')
        user.save()

        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('user'), 'init')

        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
                                      'password_change': 'o', 'password1': 'abc', 'password2': '132'}, False)
        self.assert_observer('core.exception', 'CORE', 'usersEdit')
        self.assert_xml_equal(
            'EXCEPTION/MESSAGE', 'Les mots de passes sont différents!')
        self.assert_xml_equal('EXCEPTION/CODE', '3')

        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('user'), 'after different')

        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
                                      'password_change': 'n', 'password1': '', 'password2': ''}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('user'), 'after empty')

        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
                                      'password_change': 'o', 'password1': 'abc', 'password2': 'abc'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'usersEdit')
        user = LucteriosUser.objects.get(id=3)
        self.assertTrue(user.check_password('abc'), 'success after change')
        self.assertFalse(user.check_password('user'), 'wrong after change')

        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'SAVE': 'YES', 'user_actif': '3',
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

        self.call(
            '/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/usersEdit', {'user_actif': '3'})
        self.assert_observer('core.custom', 'CORE', 'usersEdit')
        self.assert_count_equal('CLOSE_ACTION/ACTION', 1)
        self.assert_action_equal(
            'CLOSE_ACTION/ACTION', ('unlock', None, "CORE", "unlock", 1, 1, 1))
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3')
        self.assert_xml_equal(
            'CONTEXT/PARAM[@name="LOCK_IDENT"]', 'lucterios.CORE.models-LucteriosUser-3')

        new_test = LucteriosTest("setUp")
        new_test.setUp()
        new_test.call(
            '/CORE/authentification', {'username': 'user1', 'password': 'user1'})
        new_test.assert_observer('core.auth', 'CORE', 'authentification')
        new_test.assert_xml_equal('', 'OK')

        new_test.call('/CORE/usersEdit', {'user_actif': '3'})
        new_test.assert_observer('core.exception', 'CORE', 'usersEdit')
        new_test.assert_xml_equal(
            'EXCEPTION/MESSAGE', six.text_type("Enregistrement verrouillé par 'admin'!"))
        new_test.assert_xml_equal('EXCEPTION/CODE', '3')

        self.call(
            '/CORE/unlock', {'user_actif': '3', "LOCK_IDENT": 'lucterios.CORE.models-LucteriosUser-3'})
        self.assert_observer('core.acknowledge', 'CORE', 'unlock')

        new_test.call('/CORE/usersEdit', {'user_actif': '3'})
        new_test.assert_observer('core.custom', 'CORE', 'usersEdit')


class GroupTest(LucteriosTest):

    def setUp(self):
        tools.WrapAction.mode_connect_notfree = None
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        signal_and_lock.unlocker_view_class = Unlock
        signal_and_lock.RecordLocker.clear()
        add_empty_user()

    def tearDown(self):
        LucteriosTest.tearDown(self)
        tools.WrapAction.mode_connect_notfree = parameters.notfree_mode_connect

    def test_grouplist(self):
        self.factory.xfer = GroupsList()
        self.call('/CORE/groupsList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'groupsList')
        self.assert_xml_equal('TITLE', 'Les groupes')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal(
            'ACTIONS/ACTION', ('Fermer', 'images/close.png'))
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_comp_equal(
            'COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/group.png', ('0', '0', '1', '1'))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="title"]', '{[br/]}{[center]}{[u]}{[b]}Les groupes{[/b]}{[/u]}{[/center]}',
                               ('1', '0', '1', '1'))
        self.assert_coordcomp_equal(
            'COMPONENTS/GRID[@name="group"]', ('0', '1', '2', '1'))
        self.assert_count_equal(
            'COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION', 3)
        self.assert_action_equal(
            'COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION[position()=1]', ('Modifier', 'images/edit.png', 'CORE', 'groupsEdit', 0, 1, 0))
        self.assert_action_equal(
            'COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION[position()=2]', ('Supprimer', 'images/delete.png', 'CORE', 'groupsDelete', 0, 1, 2))
        self.assert_action_equal(
            'COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION[position()=3]', ('Ajouter', 'images/add.png', 'CORE', 'groupsEdit', 0, 1, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="group"]/HEADER', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="group"]/HEADER[@name="name"]', "nom")
        self.assert_count_equal('COMPONENTS/GRID[@name="group"]/RECORD', 0)
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="nb_group"]', "Nombre total de groupes: 0", (0, 2, 2, 1))

    def test_groupadd(self):
        self.factory.xfer = GroupsEdit()
        self.call('/CORE/groupsEdit', {}, False)
        self.assert_observer('core.custom', 'CORE', 'groupsEdit')
        self.assert_xml_equal('TITLE', 'Ajouter un groupe')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal(
            'ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'groupsEdit', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal(
            'ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))

        self.assert_count_equal('COMPONENTS/*', 12)
        self.assert_comp_equal(
            'COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/group.png', (0, 0, 1, 6))

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_name"]', "{[b]}nom{[/b]}", (1, 0, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/EDIT[@name="name"]', None, (2, 0, 1, 1))

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_permissions"]', "{[b]}permissions{[/b]}", (1, 1, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="hd_permissions_available"]', "{[center]}{[i]}Permissions disponibles{[/i]}{[/center]}", (2, 1, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/CHECKLIST[@name="permissions_available"]', (2, 2, 1, 5))
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="hd_permissions_chosen"]', "{[center]}{[i]}Permissions choisies{[/i]}{[/center]}", (4, 1, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/CHECKLIST[@name="permissions_chosen"]', (4, 2, 1, 5))

        self.assert_coordcomp_equal(
            'COMPONENTS/BUTTON[@name="permissions_addall"]', (3, 2, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/BUTTON[@name="permissions_add"]', (3, 3, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/BUTTON[@name="permissions_del"]', (3, 4, 1, 1))
        self.assert_coordcomp_equal(
            'COMPONENTS/BUTTON[@name="permissions_delall"]', (3, 5, 1, 1))
        self.assert_action_equal(
            'COMPONENTS/BUTTON[@name="permissions_addall"]/ACTIONS/ACTION', ('>>', None, None, None, 0, 1, 1))
        self.assert_action_equal(
            'COMPONENTS/BUTTON[@name="permissions_add"]/ACTIONS/ACTION', ('>', None, None, None, 0, 1, 1))
        self.assert_action_equal(
            'COMPONENTS/BUTTON[@name="permissions_del"]/ACTIONS/ACTION', ('<', None, None, None, 0, 1, 1))
        self.assert_action_equal(
            'COMPONENTS/BUTTON[@name="permissions_delall"]/ACTIONS/ACTION', ('<<', None, None, None, 0, 1, 1))

    def test_useraddsave(self):
        groups = LucteriosGroup.objects.all()
        self.assertEqual(len(groups), 0)

        self.factory.xfer = GroupsEdit()
        self.call('/CORE/groupsEdit',
                  {'SAVE': 'YES', 'name': 'newgroup', "permissions": '1;3;5;7'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'groupsEdit')
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="name"]', 'newgroup')
        self.assert_xml_equal('CONTEXT/PARAM[@name="permissions"]', '1;3;5;7')

        groups = LucteriosGroup.objects.all()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, "newgroup")
        perm = groups[0].permissions.all().order_by(
            'id')
        self.assertEqual(len(perm), 4)
        self.assertEqual(perm[0].id, 1)
        self.assertEqual(perm[1].id, 3)
        self.assertEqual(perm[2].id, 5)
        self.assertEqual(perm[3].id, 7)

    def test_groupedit(self):
        group = LucteriosGroup.objects.create(
            name="my_group")
        group.permissions = Permission.objects.filter(
            id__in=[1, 3])
        group.save()

        self.factory.xfer = GroupsEdit()
        self.call('/CORE/groupsEdit', {'group': '1'}, False)
        self.assert_observer('core.custom', 'CORE', 'groupsEdit')
        self.assert_xml_equal('TITLE', 'Modifier un groupe')

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_name"]', "{[b]}nom{[/b]}", (1, 0, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/EDIT[@name="name"]', 'my_group', (2, 0, 1, 1))

    def test_groupedit_notexist(self):
        self.factory.xfer = GroupsEdit()
        self.call('/CORE/groupsEdit', {'group': '50'}, False)
        self.assert_observer('core.exception', 'CORE', 'groupsEdit')
        self.assert_xml_equal('EXCEPTION/MESSAGE', six.text_type(
            "Cet enregistrement n'existe pas!\nVeuillez rafraichir votre application."))
        self.assert_xml_equal('EXCEPTION/CODE', '3')

    def test_groupadd_same(self):
        grp = LucteriosGroup.objects.create(
            name="mygroup")
        grp.save()

        self.factory.xfer = GroupsEdit()
        self.call('/CORE/groupsEdit',
                  {'SAVE': 'YES', 'name': 'mygroup', "permissions": '1;3;5;7'}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'groupsEdit')
        self.assert_count_equal('CONTEXT/PARAM', 3)
        self.assert_xml_equal('CONTEXT/PARAM[@name="name"]', 'mygroup')
        self.assert_xml_equal('CONTEXT/PARAM[@name="permissions"]', '1;3;5;7')
        self.assert_attrib_equal('TEXT', 'type', '3')
        self.assert_xml_equal(
            'TEXT', six.text_type('Cet enregistrement existe déjà!'))
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal(
            'ACTIONS/ACTION', ('Recommencer', None, "CORE", "groupsEdit", 1, 1, 1))

    def test_groupedit_fornew(self):
        self.factory.xfer = GroupsEdit()
        self.call(
            '/CORE/groupsEdit', {'name': 'mygroup', "permissions": '1;3;5;7'}, False)
        self.assert_xml_equal('TITLE', 'Ajouter un groupe')
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="name"]', 'mygroup')
        self.assert_xml_equal('CONTEXT/PARAM[@name="permissions"]', '1;3;5;7')
        self.assert_count_equal('ACTIONS/ACTION', 2)

        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="lbl_name"]', "{[b]}nom{[/b]}", (1, 0, 1, 1))
        self.assert_comp_equal(
            'COMPONENTS/EDIT[@name="name"]', 'mygroup', (2, 0, 1, 1))

    def test_concurentedit(self):
        user1 = add_user("user1")
        user1.is_superuser = True
        user1.save()
        grp = LucteriosGroup.objects.create(
            name="mygroup")
        grp.save()

        self.call(
            '/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/groupsEdit', {'group': '1'})
        self.assert_observer('core.custom', 'CORE', 'groupsEdit')
        self.assert_count_equal('CLOSE_ACTION/ACTION', 1)
        self.assert_action_equal(
            'CLOSE_ACTION/ACTION', ('unlock', None, "CORE", "unlock", 1, 1, 1))
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="group"]', '1')
        self.assert_xml_equal(
            'CONTEXT/PARAM[@name="LOCK_IDENT"]', 'lucterios.CORE.models-LucteriosGroup-1')

        new_test = LucteriosTest("setUp")
        new_test.setUp()
        new_test.call(
            '/CORE/authentification', {'username': 'user1', 'password': 'user1'})
        new_test.assert_observer('core.auth', 'CORE', 'authentification')
        new_test.assert_xml_equal('', 'OK')

        new_test.call('/CORE/groupsEdit', {'group': '1'})
        new_test.assert_observer('core.exception', 'CORE', 'groupsEdit')
        new_test.assert_xml_equal(
            'EXCEPTION/MESSAGE', six.text_type("Enregistrement verrouillé par 'admin'!"))
        new_test.assert_xml_equal('EXCEPTION/CODE', '3')

        self.call('/CORE/exitConnection', {})

        new_test.call('/CORE/groupsEdit', {'group': '1'})
        new_test.assert_observer('core.custom', 'CORE', 'groupsEdit')


class SessionTest(LucteriosTest):

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        add_empty_user()

    def test_sessionlist(self):
        self.call(
            '/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/sessionList', {})
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assert_xml_equal('TITLE', 'Sessions')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal(
            'ACTIONS/ACTION', ('Fermer', 'images/close.png'))
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_xml_equal(
            'COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.CORE/images/session.png')
        self.assert_coordcomp_equal(
            'COMPONENTS/IMAGE[@name="img"]', ('0', '0', '1', '1'))
        self.assert_xml_equal(
            'COMPONENTS/LABELFORM[@name="title"]', '{[br/]}{[center]}{[u]}{[b]}Sessions{[/b]}{[/u]}{[/center]}')
        self.assert_coordcomp_equal(
            'COMPONENTS/LABELFORM[@name="title"]', ('1', '0', '1', '1'))
        self.assert_coordcomp_equal(
            'COMPONENTS/GRID[@name="session"]', ('0', '1', '2', '1'))

        self.assert_count_equal('COMPONENTS/GRID[@name="session"]/HEADER', 2)

        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="session"]/HEADER[@name="username"]', "nom d'utilisateur")
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="session"]/HEADER[@name="expire_date"]', "date d'expiration")
        self.assert_count_equal('COMPONENTS/GRID[@name="session"]/RECORD', 1)
        self.assert_xml_equal(
            'COMPONENTS/GRID[@name="session"]/RECORD[1]/VALUE[@name="username"]', 'admin')
        self.assert_comp_equal(
            'COMPONENTS/LABELFORM[@name="nb_session"]', "Nombre total de sessions: 1", (0, 2, 2, 1))

    def test_sessiondel(self):
        self.call('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_xml_equal('', 'OK')

        self.call('/CORE/sessionList', {})
        self.assert_count_equal('COMPONENTS/GRID[@name="session"]/RECORD', 1)
        session_id = self.response_xml.xpath('COMPONENTS/GRID[@name="session"]/RECORD')[0].get("id")

        self.call('/CORE/sessionDelete', {'session': session_id, 'CONFIRME': 'YES'})
        self.assert_observer('core.acknowledge', 'CORE', 'sessionDelete')

        self.call('/CORE/sessionList', {})
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assert_count_equal('COMPONENTS/GRID[@name="session"]/RECORD', 1)
        self.assert_attrib_equal('COMPONENTS/GRID[@name="session"]/RECORD[1]', 'id', session_id)
