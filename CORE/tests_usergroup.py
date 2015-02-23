# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest, add_admin_user, add_empty_user
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.CORE.views_usergroup import UsersList

class UserGroupTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        add_admin_user()
        add_empty_user()

    def test_userlist(self):
        self.factory.xfer = UsersList()
        self.call('/CORE/usersList', {}, False)
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'CORE')
        self.assert_attrib_equal('', 'source_action', 'usersList')
        self.assert_xml_equal('TITLE', 'Utilisateurs')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_xml_equal('ACTIONS/ACTION', 'Fermer')
        self.assert_attrib_equal('ACTIONS/ACTION', 'icon', 'images/close.png')
        self.assert_attrib_equal('ACTIONS/ACTION', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION', 'action', None)
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
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/HEADER[@name="is_staff"]', "statut équipe")
        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=1]/VALUE[@name="username"]', 'admin')
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_actif"]/RECORD[@id=2]/VALUE[@name="username"]', 'empty')

        self.assert_count_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION', 4)
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=1]', ('Modifier', 'images/edit.png', 'CORE', 'usersModify', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=2]', ('Désactiver', 'images/suppr.png', 'CORE', 'usersDisabled', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=3]', ('Supprimer', 'images/suppr.png', 'CORE', 'usersDelete', 0, 1, 2))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_actif"]/ACTIONS/ACTION[position()=4]', ('Ajouter', 'images/add.png', 'CORE', 'usersAdd', 0, 1, 1))

        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER', 3)

        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="username"]', "nom d'utilisateur")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="first_name"]', "prénom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="user_inactif"]/HEADER[@name="last_name"]', "nom")
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/RECORD', 0)
        self.assert_count_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION', 2)
        self.assert_action_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION[position()=1]', ('Réactiver', 'images/ok.png', 'CORE', 'usersEnabled', 0, 1, 0))
        self.assert_action_equal('COMPONENTS/GRID[@name="user_inactif"]/ACTIONS/ACTION[position()=2]', ('Supprimer', 'images/suppr.png', 'CORE', 'usersDelete', 0, 1, 2))
