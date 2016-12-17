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

PERMISSION_CODENAMES = {
    'CORE.add_label': ('Impression', 'CORE'),
    'CORE.delete_label': ('Impression', 'CORE'),
    'CORE.change_label': ('Impression', 'CORE'),
    'CORE.add_parameter': ('Modifier les paramètres généraux', 'CORE'),
    'CORE.change_parameter': ('Modifier les paramètres généraux', 'CORE'),
    'CORE.add_printmodel': ('Impression', 'CORE'),
    'CORE.change_printmodel': ('Impression', 'CORE'),
    'CORE.delete_printmodel': ('Impression', 'CORE'),
    'auth.add_group': ('Ajouter/Modifier un groupe', 'CORE'),
    'auth.change_group': ('Ajouter/Modifier un groupe', 'CORE'),
    'auth.delete_group': ('Ajouter/Modifier un groupe', 'CORE'),
    'auth.add_user': ('Ajouter/modifier un utilisateur', 'CORE'),
    'auth.change_user': ('Ajouter/modifier un utilisateur', 'CORE'),
    'auth.delete_user': ('Ajouter/modifier un utilisateur', 'CORE'),
    'sessions.delete_session': ('Consultation de session de connexion', 'CORE'),
    'sessions.change_session': ('Consultation de session de connexion', 'CORE'),

    'contacts.add_abstractcontact': ('Ajouter/Modifier', 'org_lucterios_contacts'),
    'contacts.change_abstractcontact': ('Voir/Lister', 'org_lucterios_contacts'),
    'contacts.delete_abstractcontact': ('Suppression/Fusion', 'org_lucterios_contacts'),
    'contacts.add_postalcode': ('Gestion des paramètres', 'org_lucterios_contacts'),
    'contacts.change_postalcode': ('Gestion des paramètres', 'org_lucterios_contacts'),
    'contacts.add_responsability': ('Ajouter/Modifier', 'org_lucterios_contacts'),
    'contacts.change_responsability': ('Voir/Lister', 'org_lucterios_contacts'),
    'contacts.delete_responsability': ('Suppression/Fusion', 'org_lucterios_contacts'),

    'documents.add_document': ('Ajout/modification', 'org_lucterios_documents'),
    'documents.change_document': ('Visualisation', 'org_lucterios_documents'),
    'documents.delete_document': ('Supression', 'org_lucterios_documents'),
    'documents.add_folder': ('Parametrages', 'org_lucterios_documents'),
    'documents.change_folder': ('Parametrages', 'org_lucterios_documents'),
    'documents.delete_folder': ('Parametrages', 'org_lucterios_documents'),

    'mailing.add_message': ('Ajouter/Modifier', 'org_lucterios_contacts'),
    'mailing.change_message': ('Voir/Lister', 'org_lucterios_contacts'),
    'mailing.delete_message': ('Suppression/Fusion', 'org_lucterios_contacts'),

    'accounting.add_chartsaccount': ('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta'),
    'accounting.change_chartsaccount': ('Voir/Consulter la comptabilité', 'fr_sdlibre_compta'),
    'accounting.delete_chartsaccount': ('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta'),
    'accounting.add_entryaccount': ('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta'),
    'accounting.change_entryaccount': ('Voir/Consulter la comptabilité', 'fr_sdlibre_compta'),
    'accounting.delete_entryaccount': ('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta'),
    'accounting.add_fiscalyear': ('Paramètrages', 'fr_sdlibre_compta'),
    'accounting.change_fiscalyear': ('Paramètrages', 'fr_sdlibre_compta'),
    'accounting.delete_fiscalyear': ('Paramètrages', 'fr_sdlibre_compta'),
    'accounting.add_third': ('Ajouter/Modifier les tiers', 'fr_sdlibre_compta'),
    'accounting.change_third': ('Voir/Consulter les tiers', 'fr_sdlibre_compta'),
    'accounting.delete_third': ('Ajouter/Modifier les tiers', 'fr_sdlibre_compta'),

    'invoice.add_article': ('Ajout/Modification articles', 'fr_sdlibre_facture'),
    'invoice.change_article': ('Ajout/Modification articles', 'fr_sdlibre_facture'),
    'invoice.delete_article': ('Ajout/Modification articles', 'fr_sdlibre_facture'),
    'invoice.add_bill': ('Modification factures', 'fr_sdlibre_facture'),
    'invoice.change_bill': ('Consultation factures', 'fr_sdlibre_facture'),
    'invoice.delete_bill': ('Suppression factures', 'fr_sdlibre_facture'),
    'invoice.add_vat': ('Configuration', 'fr_sdlibre_facture'),
    'invoice.change_vat': ('Configuration', 'fr_sdlibre_facture'),
    'invoice.delete_vat': ('Configuration', 'fr_sdlibre_facture'),

    'payoff.add_bankaccount': [('Parametrage', 'fr_sdlibre_copropriete'), ('Configuration', 'fr_sdlibre_facture')],
    'payoff.change_bankaccount': [('Parametrage', 'fr_sdlibre_copropriete'), ('Configuration', 'fr_sdlibre_facture')],
    'payoff.delete_bankaccount': [('Parametrage', 'fr_sdlibre_copropriete'), ('Configuration', 'fr_sdlibre_facture')],
    'payoff.add_depositslip': [('Parametrage', 'fr_sdlibre_copropriete'), ('Gestion des remises de chèques', 'fr_sdlibre_facture')],
    'payoff.change_depositslip': [('Parametrage', 'fr_sdlibre_copropriete'), ('Gestion des remises de chèques', 'fr_sdlibre_facture')],
    'payoff.delete_depositslip': [('Parametrage', 'fr_sdlibre_copropriete'), ('Gestion des remises de chèques', 'fr_sdlibre_facture')],
    'payoff.add_payoff': [('Parametrage', 'fr_sdlibre_copropriete'), ('Modification factures', 'fr_sdlibre_facture')],
    'payoff.change_payoff': [('Parametrage', 'fr_sdlibre_copropriete'), ('Consultation factures', 'fr_sdlibre_facture')],
    'payoff.delete_payoff': [('Parametrage', 'fr_sdlibre_copropriete'), ('Modification factures', 'fr_sdlibre_facture')],

    'condominium.add_callfunds': ('Ajout/Modification', 'fr_sdlibre_copropriete'),
    'condominium.change_callfunds': ('Visualisation', 'fr_sdlibre_copropriete'),
    'condominium.delete_callfunds': ('Suppression', 'fr_sdlibre_copropriete'),
    'condominium.add_expense': ('Ajout/Modification', 'fr_sdlibre_copropriete'),
    'condominium.change_expense': ('Visualisation', 'fr_sdlibre_copropriete'),
    'condominium.delete_expense': ('Suppression', 'fr_sdlibre_copropriete'),
    'condominium.add_owner': ('Ajout/Modification', 'fr_sdlibre_copropriete'),
    'condominium.change_owner': ('Visualisation', 'fr_sdlibre_copropriete'),
    'condominium.delete_owner': ('Suppression', 'fr_sdlibre_copropriete'),
    'condominium.add_set': ('Ajout/Modification', 'fr_sdlibre_copropriete'),
    'condominium.change_set': ('Visualisation', 'fr_sdlibre_copropriete'),
    'condominium.delete_set': ('Suppression', 'fr_sdlibre_copropriete'),

    'member.add_activity': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.delete_activity': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.add_age': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.delete_age': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.delete_age': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.add_season': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.change_season': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.add_team': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.delete_team': ('Gestion des paramètres', 'fr_sdlibre_membres'),
    'member.add_subscription': ('Ajouter une licence', 'fr_sdlibre_membres'),
    'member.change_subscription': ('Ajouter une licence', 'fr_sdlibre_membres'),
    'member.delete_subscription': ('Ajouter une licence', 'fr_sdlibre_membres'),
    'member.add_adherent': ('Modifier/Ajouter un adhérent', 'fr_sdlibre_membres'),
    'member.change_adherent': ('Consulter les adhérents', 'fr_sdlibre_membres'),
    'member.delete_adherent': ('Modifier/Ajouter un adhérent', 'fr_sdlibre_membres'),

    'event.add_degreetype': ('Gestion des paramètres', 'fr_sdlibre_FormationSport'),
    'event.change_degreetype': ('Gestion des paramètres', 'fr_sdlibre_FormationSport'),
    'event.delete_degreetype': ('Gestion des paramètres', 'fr_sdlibre_FormationSport'),
    'event.add_degree': ('Gestion des paramètres', 'fr_sdlibre_FormationSport'),
    'event.change_degree': ('Consultation', 'fr_sdlibre_FormationSport'),
    'event.delete_degree': ('Gestion des paramètres', 'fr_sdlibre_FormationSport'),
    'event.add_event': ('Modifier/Ajouter une formation', 'fr_sdlibre_FormationSport'),
    'event.change_event': ('Consultation', 'fr_sdlibre_FormationSport'),
    'event.delete_event': ('Modifier/Ajouter une formation', 'fr_sdlibre_FormationSport'),
}


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
            right_name = "%s.%s" % (
                permission.content_type.app_label, permission.codename)
            if right_name in PERMISSION_CODENAMES.keys():
                perm_value = PERMISSION_CODENAMES[right_name]
                if isinstance(perm_value[0], six.text_type):
                    perm_value = [perm_value]
                rigth_id = None
                for rigth_name, ext_name in perm_value:
                    cur = self.old_db.open()
                    sql_text = six.text_type("SELECT R.id FROM CORE_extension_rights R,CORE_extension E WHERE R.extension=E.id AND R.description='%s' AND E.extensionId='%s'") % (
                        six.text_type(rigth_name), ext_name)
                    try:
                        cur.execute(sql_text)
                    except:
                        self.print_debug("SQL error:%s", sql_text)
                    rigth_id = cur.fetchone()
                    if rigth_id is not None:
                        break
                if rigth_id is not None:
                    self.permission_relation.append(
                        (permission.id, rigth_id[0]))
                else:
                    self.print_debug("=> not found %s", (sql_text,))

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
            self.print_debug("=> Group %s (%s)", (group_name, premission_ref))
            self.group_list[groupid] = new_grp

    def _users(self):
        LucteriosUser.objects.all().delete()
        cur = self.old_db.open()
        cur.execute(
            "SELECT id,login,pass,realName,groupId,actif FROM CORE_users")
        for userid, login, password, real_name, group_id, actif in cur.fetchall():
            if login != '':
                self.print_debug("=> User %s [%s]", (login, real_name))
                try:
                    new_user = LucteriosUser.objects.create_user(
                        username=login)
                    if (login == "admin") and (password[0] == '*'):
                        new_user.set_password('admin')
                    else:
                        new_user.password = "md5$$%s" % password
                    new_user.first_name = real_name.split(' ')[0]
                    new_user.last_name = ''.join(real_name.split(' ')[1:])
                    new_user.is_active = actif == 'o'
                    new_user.is_superuser = login == 'admin'
                    new_user.is_staff = login == 'admin'
                    if group_id in self.group_list.keys():
                        new_user.groups = Group.objects.filter(
                            id__in=[self.group_list[group_id].pk])
                    new_user.save()
                    self.user_list[userid] = new_user
                except IntegrityError:
                    self.print_debug("*** User %s doubled", (login,))

    def run(self):
        try:
            self._permissions()
            self._groups()
            self._users()
        finally:
            self.old_db.close()
        self.print_info("Nb groups:%d", len(self.group_list))
        self.print_info("Nb users:%d", len(self.user_list))
        self.old_db.objectlinks['groups'] = self.group_list
        self.old_db.objectlinks['users'] = self.user_list
