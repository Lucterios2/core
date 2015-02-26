# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from datetime import date

from lucterios.framework.test import LucteriosTest, add_admin_user, add_empty_user, add_user
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.views_usergroup import UsersList, UsersDelete, UsersDisabled, UsersEnabled, UsersEdit, UsersModify, \
    GroupsModify
from lucterios.CORE.views_usergroup import GroupsList, GroupsEdit
from django.contrib.auth.models import Group, Permission

class UserTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        add_admin_user()
        add_empty_user()

    def test_userlist(self):
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'usersList')
        self.assert_xml_equal('TITLE', 'Utilisateurs')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal('ACTIONS/ACTION', ('Fermer', 'images/close.png'))
        self.assert_count_equal('COMPONENTS/*', 7)
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img"]', 'images/user.png')
        self.assert_coordcomp_equal('COMPONENTS/IMAGE[@name="img"]', ('0', '0', '1', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="title"]', '{[center]}{[underline]}{[bold]}Utilisateurs du logiciel{[/bold]}{[/underline]}{[/center]}')
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="title"]', ('1', '0', '1', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_actifs"]', '{[bold]}Liste des utilisateurs actifs{[/bold]}{[newline]}{[newline]}')
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="lbl_actifs"]', ('0', '1', '2', '1'))
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="user_actif"]', ('0', '2', '2', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="separator"]', None)
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="separator"]', ('0', '3', '1', '1'))
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="lbl_inactif"]', '{[bold]}Liste des utilisateurs inactifs{[/bold]}{[newline]}{[newline]}')
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="lbl_inactif"]', ('0', '4', '2', '1'))
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="user_inactif"]', ('0', '5', '2', '1'))

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
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="last_login"]', date.today().strftime('%d'), True)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="last_login"]', date.today().strftime('%d'), True)

        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION', 4)
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=1]', ('Modifier', 'images/edit.png', 'CORE', 'usersEdit', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=2]', ('Désactiver', 'images/suppr.png', 'CORE', 'usersDisabled', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=3]', ('Supprimer', 'images/suppr.png', 'CORE', 'usersDelete', 0, 1, 2))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=4]', ('Ajouter', 'images/add.png', 'CORE', 'usersEdit', 0, 1, 1))

        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER', 3)

        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="username"]', "nom d'utilisateur")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="first_name"]', "prénom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="last_name"]', "nom")
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION', 2)
        self.assert_action_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION[position()=1]', ('Réactiver', 'images/ok.png', 'CORE', 'usersEnabled', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION[position()=2]', ('Supprimer', 'images/suppr.png', 'CORE', 'usersDelete', 0, 1, 2))

    def test_userdelete(self):
        add_user("user1")
        add_user("user2")
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=4]/VALUE[@name="username"]', 'user2')

        self.factory.xfer = UsersDelete()
        self.call('/CORE/usersDelete', {'user_actif':'3;4'}, False)
        self.assert_observer('Core.DialogBox', 'CORE', 'usersDelete')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CONFIRME"]', 'YES')
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3;4')
        self.assert_attrib_equal('TEXT', 'type', '2')
        # self.assert_xml_equal('TEXT', 'Voulez-vous supprimer ces 2 utilisateurs?')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_xml_equal('ACTIONS/ACTION[1]', 'Oui')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'icon', 'images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'extension', 'CORE')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'action', 'usersDelete')
        self.assert_xml_equal('ACTIONS/ACTION[2]', 'Non')
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'icon', 'images/cancel.png')
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'action', None)

        self.factory.xfer = UsersDelete()
        self.call('/CORE/usersDelete', {'user_actif':'3;4', 'CONFIRME':'YES'}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'usersDelete')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CONFIRME"]', 'YES')
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3;4')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')

    def test_userdisabledenabled(self):
        add_user("user1")
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')

        self.factory.xfer = UsersDisabled()
        self.call('/CORE/usersDisabled', {'user_actif':'3'}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'usersDisabled')
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')

        self.factory.xfer = UsersEnabled()
        self.call('/CORE/usersEnabled', {'user_inactif':'3'}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'usersEnabled')
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_inactif"]', '3')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 3)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=3]/VALUE[@name="username"]', 'user1')

    def test_useredit(self):
        add_user("user1")
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'user_actif':'3'}, False)
        self.assert_observer('Core.Custom', 'CORE', 'usersEdit')
        self.assert_xml_equal('TITLE', 'Modifier un utilisateur')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'usersModify', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))

        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img"]', 'images/user.png')
        self.assert_coordcomp_equal('COMPONENTS/IMAGE[@name="img"]', ('0', '0', '1', '6'))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_username"]', "{[bold]}nom d'utilisateur{[/bold]}", (1, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_date_joined"]', "{[bold]}date d'inscription{[/bold]}", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_last_login"]', "{[bold]}dernière connexion{[/bold]}", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_is_active"]', "{[bold]}actif{[/bold]}", (1, 3, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_is_staff"]', "{[bold]}statut équipe{[/bold]}", (1, 4, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_is_superuser"]', "{[bold]}statut super-utilisateur{[/bold]}", (1, 5, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_first_name"]', "{[bold]}prénom{[/bold]}", (1, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_last_name"]', "{[bold]}nom{[/bold]}", (1, 7, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_email"]', "{[bold]}adresse électronique{[/bold]}", (1, 8, 1, 1))

        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="username"]', (2, 0, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="date_joined"]', (2, 1, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="last_login"]', (2, 2, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/LABELFORM[@name="is_active"]', (2, 3, 1, 1))

        self.assert_coordcomp_equal('COMPONENTS/CHECK[@name="is_staff"]', (2, 4, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECK[@name="is_superuser"]', (2, 5, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/EDIT[@name="first_name"]', (2, 6, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/EDIT[@name="last_name"]', (2, 7, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/EDIT[@name="email"]', (2, 8, 1, 1))

        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="username"]', 'user1')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="date_joined"]', date.today().strftime('%d'), True)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="last_login"]', date.today().strftime('%d'), True)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="is_active"]', 'Oui')

        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_staff"]', '0')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_superuser"]', '0')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="first_name"]', 'user1')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="last_name"]', 'USER1')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="email"]', None)

    def test_usermodif(self):
        add_user("user1")
        self.factory.xfer = UsersModify()
        self.call('/CORE/usersModify', {'user_actif':'3', "is_staff":'1', "is_superuser":'o', "first_name":'foo', "last_name":'SUPER', "email":'foo@super.com'}, False)

        self.assert_observer('Core.Acknowledge', 'CORE', 'usersModify')
        self.assert_count_equal('CONTEXT/PARAM', 6)
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_actif"]', '3')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_staff"]', '1')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_superuser"]', 'o')
        self.assert_xml_equal('CONTEXT/PARAM[@name="first_name"]', 'foo')
        self.assert_xml_equal('CONTEXT/PARAM[@name="last_name"]', 'SUPER')
        self.assert_xml_equal('CONTEXT/PARAM[@name="email"]', 'foo@super.com')

        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'user_actif':'3'}, False)
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_staff"]', '1')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_superuser"]', '1')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="first_name"]', 'foo')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="last_name"]', 'SUPER')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="email"]', 'foo@super.com')

    def test_useradd(self):
        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'usersEdit')
        self.assert_xml_equal('TITLE', 'Ajouter un utilisateur')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'usersModify', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))

        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img"]', 'images/user.png')
        self.assert_coordcomp_equal('COMPONENTS/IMAGE[@name="img"]', ('0', '0', '1', '6'))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_username"]', "{[bold]}nom d'utilisateur{[/bold]}", (1, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_is_staff"]', "{[bold]}statut équipe{[/bold]}", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_is_superuser"]', "{[bold]}statut super-utilisateur{[/bold]}", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_first_name"]', "{[bold]}prénom{[/bold]}", (1, 3, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_last_name"]', "{[bold]}nom{[/bold]}", (1, 4, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_email"]', "{[bold]}adresse électronique{[/bold]}", (1, 5, 1, 1))

        self.assert_coordcomp_equal('COMPONENTS/EDIT[@name="username"]', (2, 0, 1, 1))

        self.assert_coordcomp_equal('COMPONENTS/CHECK[@name="is_staff"]', (2, 1, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECK[@name="is_superuser"]', (2, 2, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/EDIT[@name="first_name"]', (2, 3, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/EDIT[@name="last_name"]', (2, 4, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/EDIT[@name="email"]', (2, 5, 1, 1))

        self.assert_xml_equal('COMPONENTS/EDIT[@name="username"]', None)
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_staff"]', '0')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_superuser"]', '0')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="first_name"]', None)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="last_name"]', None)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="email"]', None)

    def test_useraddsave(self):
        add_user("user1")
        add_user("user2")
        self.factory.xfer = UsersModify()
        self.call('/CORE/usersModify', {'username':'newuser', "is_staff":'0', "is_superuser":'1', "first_name":'my', "last_name":'BIG', "email":'my@big.org'}, False)

        self.assert_observer('Core.Acknowledge', 'CORE', 'usersModify')
        self.assert_count_equal('CONTEXT/PARAM', 6)
        self.assert_xml_equal('CONTEXT/PARAM[@name="username"]', 'newuser')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_staff"]', '0')
        self.assert_xml_equal('CONTEXT/PARAM[@name="is_superuser"]', '1')
        self.assert_xml_equal('CONTEXT/PARAM[@name="first_name"]', 'my')
        self.assert_xml_equal('CONTEXT/PARAM[@name="last_name"]', 'BIG')
        self.assert_xml_equal('CONTEXT/PARAM[@name="email"]', 'my@big.org')

        self.factory.xfer = UsersEdit()
        self.call('/CORE/usersEdit', {'user_actif':'5'}, False)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="username"]', 'newuser')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="date_joined"]', date.today().strftime('%d'), True)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="last_login"]', date.today().strftime('%d'), True)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="is_active"]', 'Oui')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_staff"]', '0')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="is_superuser"]', '1')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="first_name"]', 'my')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="last_name"]', 'BIG')
        self.assert_xml_equal('COMPONENTS/EDIT[@name="email"]', 'my@big.org')

    def test_userdeldisabled(self):

        user = add_user("user1")
        user.is_active = False
        user.save()
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 1)

        self.factory.xfer = UsersDelete()
        self.call('/CORE/usersDelete', {'user_inactif':'3'}, False)
        self.assert_observer('Core.DialogBox', 'CORE', 'usersDelete')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_xml_equal('CONTEXT/PARAM[@name="CONFIRME"]', 'YES')
        self.assert_xml_equal('CONTEXT/PARAM[@name="user_inactif"]', '3')

        self.factory.xfer = UsersDelete()
        self.call('/CORE/usersDelete', {'user_inactif':'3', "CONFIRME":'YES'}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'usersDelete')

        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)

class GroupTest(LucteriosTest):
    # pylint: disable=too-many-public-methods,too-many-statements

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        add_admin_user()
        add_empty_user()

    def test_grouplist(self):
        self.factory.xfer = GroupsList()
        self.call('/CORE/groupsList', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'groupsList')
        self.assert_xml_equal('TITLE', 'Groupes')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal('ACTIONS/ACTION', ('Fermer', 'images/close.png'))
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', 'images/group.png', ('0', '0', '1', '1'))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="title"]', '{[center]}{[underline]}{[bold]}Groupes éxistants{[/bold]}{[/underline]}{[/center]}', \
                               ('1', '0', '1', '1'))
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="group"]', ('0', '1', '2', '1'))
        self.assert_count_equal('COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION', 3)
        self.assert_action_equal('COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION[position()=1]', ('Modifier', 'images/edit.png', 'CORE', 'groupsEdit', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION[position()=2]', ('Supprimer', 'images/suppr.png', 'CORE', 'groupsDelete', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="group"]/ACTIONS/ACTION[position()=3]', ('Ajouter', 'images/add.png', 'CORE', 'groupsEdit', 0, 1, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="group"]/HEADER', 1)
        self.assert_xml_equal('COMPONENTS/GRID[@name="group"]/HEADER[@name="name"]', "nom")
        self.assert_count_equal('COMPONENTS/GRID[@name="group"]/RECORD', 0)

    def test_groupadd(self):
        self.factory.xfer = GroupsEdit()
        self.call('/CORE/groupsEdit', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'groupsEdit')
        self.assert_xml_equal('TITLE', 'Ajouter un groupe')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'CORE', 'groupsModify', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))

        self.assert_count_equal('COMPONENTS/*', 12)
        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', 'images/group.png', (0, 0, 1, 6))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_name"]', "{[bold]}nom{[/bold]}", (1, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/EDIT[@name="name"]', None, (2, 0, 1, 1))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_permissions"]', "{[bold]}permissions{[/bold]}", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="hd_permissions_available"]', "{[center]}{[italic]}Permissions disponibles{[/italic]}{[/center]}", (2, 1, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECKLIST[@name="permissions_available"]', (2, 2, 1, 5))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="hd_permissions_chosen"]', "{[center]}{[italic]}Permissions choisies{[/italic]}{[/center]}", (4, 1, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/CHECKLIST[@name="permissions_chosen"]', (4, 2, 1, 5))

        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="permissions_addall"]', (3, 2, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="permissions_add"]', (3, 3, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="permissions_del"]', (3, 4, 1, 1))
        self.assert_coordcomp_equal('COMPONENTS/BUTTON[@name="permissions_delall"]', (3, 5, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="permissions_addall"]/ACTIONS/ACTION', ('>>', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="permissions_add"]/ACTIONS/ACTION', ('>', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="permissions_del"]/ACTIONS/ACTION', ('<', None, None, None, 0, 1, 1))
        self.assert_action_equal('COMPONENTS/BUTTON[@name="permissions_delall"]/ACTIONS/ACTION', ('<<', None, None, None, 0, 1, 1))

    def test_useraddsave(self):
        groups = Group.objects.all()
        self.assertEqual(len(groups), 0)

        self.factory.xfer = GroupsModify()
        self.call('/CORE/groupsModify', {'name':'newgroup', "permissions":'1;3;5;7'}, False)

        self.assert_observer('Core.Acknowledge', 'CORE', 'groupsModify')
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="name"]', 'newgroup')
        self.assert_xml_equal('CONTEXT/PARAM[@name="permissions"]', '1;3;5;7')

        groups = Group.objects.all()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].name, "newgroup")
        perm = groups[0].permissions.all().order_by('id')
        self.assertEqual(len(perm), 4)
        self.assertEqual(perm[0].id, 1)
        self.assertEqual(perm[1].id, 3)
        self.assertEqual(perm[2].id, 5)
        self.assertEqual(perm[3].id, 7)

    def test_groupedit(self):
        group = Group.objects.create(name="my_group")
        group.permissions = Permission.objects.filter(id__in=[1, 3])
        group.save()

        self.factory.xfer = GroupsEdit()
        self.call('/CORE/groupsEdit', {'group':'1'}, False)
        self.assert_observer('Core.Custom', 'CORE', 'groupsEdit')
        self.assert_xml_equal('TITLE', 'Modifier un groupe')

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lbl_name"]', "{[bold]}nom{[/bold]}", (1, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/EDIT[@name="name"]', 'my_group', (2, 0, 1, 1))
