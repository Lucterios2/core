# -*- coding: utf-8 -*-
'''
from_v1 for lucterios.CORE

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

from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
from django.contrib.auth.models import Permission

from lucterios.install.lucterios_migration import MigrateAbstract
from lucterios.CORE.models import LucteriosUser
from lucterios.CORE.models import LucteriosGroup
from django.utils import six


PERMISSION_CODENAMES = {'add_label': ('Impression', 'CORE'), 'change_label': ('Impression', 'CORE'), 'delete_label': ('Impression', 'CORE'),
                        'add_parameter': ('Modifier les paramètres généraux', 'CORE'), 'change_parameter': ('Consulter les paramètres généreaux', 'CORE'),
                        'add_printmodel': ('Impression', 'CORE'), 'change_printmodel': ('Impression', 'CORE'), 'delete_printmodel': ('Impression', 'CORE'),
                        'add_logentry': ('Paramètres généraux (avancé)', 'CORE'), 'change_logentry': ('Paramètres généraux (avancé)', 'CORE'), 'delete_logentry': ('Paramètres généraux (avancé)', 'CORE'),
                        'add_group': ('Ajouter/Modifier un groupe', 'CORE'), 'change_group': ('Ajouter/Modifier un groupe', 'CORE'), 'delete_group': ('Ajouter/Modifier un groupe', 'CORE'),
                        'add_permission': ('Ajouter/Modifier un groupe', 'CORE'), 'change_permission': ('Ajouter/Modifier un groupe', 'CORE'), 'delete_permission': ('Ajouter/Modifier un groupe', 'CORE'),
                        'add_contenttype': ('Paramètres généraux (avancé)', 'CORE'), 'change_contenttype': ('Paramètres généraux (avancé)', 'CORE'), 'delete_contenttype': ('Paramètres généraux (avancé)', 'CORE'),
                        'add_session': ('Consultation de session de connexion', 'CORE'), 'change_session': ('Consultation de session de connexion', 'CORE'), 'delete_session': ('Consultation de session de connexion', 'CORE'),
                        'add_user': ('Ajouter/modifier un utilisateur', 'CORE'), 'change_user': ('Ajouter/modifier un utilisateur', 'CORE'), 'delete_user': ('Ajouter/modifier un utilisateur', 'CORE'),

                        'add_abstractcontact': ('Ajouter/Modifier', 'org_lucterios_contacts'), 'change_abstractcontact': ('Voir/Lister', 'org_lucterios_contacts'), 'delete_abstractcontact': ('Suppression/Fusion', 'org_lucterios_contacts'),
                        'add_postalcode': ('Gestion des paramètres', 'org_lucterios_contacts'), 'change_postalcode': ('Gestion des paramètres', 'org_lucterios_contacts'),
                        'add_responsability': ('Ajouter/Modifier', 'org_lucterios_contacts'), 'change_responsability': ('Voir/Lister', 'org_lucterios_contacts'), 'delete_responsability': ('Suppression/Fusion', 'org_lucterios_contacts'),

                        'add_folder': ('Parametrages', 'org_lucterios_documents'), 'change_folder': ('Parametrages', 'org_lucterios_documents'), 'delete_folder': ('Parametrages', 'org_lucterios_documents'),
                        'add_document': ('Ajout/modification', 'org_lucterios_documents'), 'change_document': ('Visualisation', 'org_lucterios_documents'), 'delete_document': ('Supression', 'org_lucterios_documents'),

                        'add_third': ('Ajouter/Modifier les tiers', 'fr_sdlibre_compta'), 'change_third': ('Voir/Consulter les tiers', 'fr_sdlibre_compta'), 'delete_third': ('Ajouter/Modifier les tiers', 'fr_sdlibre_compta'),
                        'add_fiscalyear': ('Paramètrages', 'fr_sdlibre_compta'), 'change_fiscalyear': ('Paramètrages', 'fr_sdlibre_compta'), 'delete_fiscalyear': ('Paramètrages', 'fr_sdlibre_compta'),
                        'add_chartsaccount': ('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta'), 'change_chartsaccount': ('Voir/Consulter la comptabilité', 'fr_sdlibre_compta'), 'delete_chartsaccount': ('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta')}


class CoreMigrate(MigrateAbstract):

    def __init__(self, old_db):
        MigrateAbstract.__init__(self, old_db)
        self.permission_relation = []
        self.group_list = {}
        self.user_list = {}

    def _permissions(self):
        permissions = Permission.objects.all()
        self.permission_relation = []
        for permission in permissions:
            if permission.codename in PERMISSION_CODENAMES.keys():
                rigth_name, ext_name = PERMISSION_CODENAMES[
                    permission.codename]
                cur = self.old_db.open()
                sql_text = six.text_type("SELECT R.id FROM CORE_extension_rights R,CORE_extension E WHERE R.extension=E.id AND R.description='%s' AND E.extensionId='%s'") % (
                    six.text_type(rigth_name), ext_name)
                try:
                    cur.execute(sql_text)
                except:
                    self.print_log("SQL error:%s", sql_text)
                rigth_id = cur.fetchone()
                if rigth_id is not None:
                    self.permission_relation.append(
                        (permission.id, rigth_id[0]))
                else:
                    self.print_log("=> not found %s", (sql_text,))

    def _groups(self):
        LucteriosGroup.objects.all().delete()
        cur = self.old_db.open()
        cur.execute("SELECT id, groupName FROM CORE_groups")
        for groupid, group_name in cur.fetchall():
            premission_ref = []
            for perm_id, perm_oldright in self.permission_relation:
                rigthcur = self.old_db.open()
                rigthcur.execute("SELECT value FROM CORE_group_rights WHERE rightref=%d AND groupref=%d" % (
                    perm_oldright, groupid))
                rightvalue, = rigthcur.fetchone()
                if rightvalue == 'o':
                    premission_ref.append(perm_id)
            new_grp = LucteriosGroup.objects.create(
                name=group_name)
            new_grp.permissions = Permission.objects.filter(
                id__in=premission_ref)
            self.print_log("=> Group %s (%s)", (group_name, premission_ref))
            self.group_list[groupid] = new_grp

    def _users(self):
        LucteriosUser.objects.all().delete()
        cur = self.old_db.open()
        cur.execute(
            "SELECT id,login,pass,realName,groupId,actif FROM CORE_users")
        for userid, login, password, real_name, group_id, actif in cur.fetchall():
            if login != '':
                self.print_log("=> User %s [%s]", (login, real_name))
                try:
                    new_user = LucteriosUser.objects.create_user(
                        username=login)
                    if (login == "admin") and (password[0] == '*'):
                        new_user.set_password('admin')
                    else:
                        new_user.password = password
                    new_user.first_name = real_name.split(' ')[0]
                    new_user.last_name = ''.join(real_name.split(' ')[1:])
                    new_user.is_active = actif == 'o'
                    new_user.is_superuser = login == 'admin'
                    if group_id in self.group_list.keys():
                        new_user.groups = Group.objects.filter(
                            id__in=[self.group_list[group_id].pk])
                    new_user.save()
                    self.user_list[userid] = new_user
                except IntegrityError:
                    self.print_log("*** User %s doubled", (login,))

    def run(self):
        try:
            self._permissions()
            self._groups()
            self._users()
        finally:
            self.old_db.close()
        self.old_db.objectlinks['groups'] = self.group_list
        self.old_db.objectlinks['users'] = self.user_list
