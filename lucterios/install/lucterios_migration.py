#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
# -*- coding: utf-8 -*-
'''
Migration tools to import old Lucterios backup

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

from os.path import join, isfile, isdir
from os import mkdir, unlink
from shutil import rmtree, copyfile
import sqlite3

from lucterios.install.lucterios_admin import LucteriosInstance, INSTANCE_PATH
from django.utils import six
from time import time

# pylint: disable=line-too-long
PERMISSION_CODENAMES = {'add_label':('Impression', 'CORE'), 'change_label':('Impression', 'CORE'), 'delete_label':('Impression', 'CORE'), \
                        'add_parameter':('Modifier les paramètres généraux', 'CORE'), 'change_parameter':('Consulter les paramètres généreaux', 'CORE'), \
                        'add_printmodel':('Impression', 'CORE'), 'change_printmodel':('Impression', 'CORE'), 'delete_printmodel':('Impression', 'CORE'), \
                        'add_logentry':('Paramètres généraux (avancé)', 'CORE'), 'change_logentry':('Paramètres généraux (avancé)', 'CORE'), 'delete_logentry':('Paramètres généraux (avancé)', 'CORE'), \
                        'add_group':('Ajouter/Modifier un groupe', 'CORE'), 'change_group':('Ajouter/Modifier un groupe', 'CORE'), 'delete_group':('Ajouter/Modifier un groupe', 'CORE'), \
                        'add_permission':('Ajouter/Modifier un groupe', 'CORE'), 'change_permission':('Ajouter/Modifier un groupe', 'CORE'), 'delete_permission':('Ajouter/Modifier un groupe', 'CORE'), \
                        'add_contenttype':('Paramètres généraux (avancé)', 'CORE'), 'change_contenttype':('Paramètres généraux (avancé)', 'CORE'), 'delete_contenttype':('Paramètres généraux (avancé)', 'CORE'), \
                        'add_session':('Consultation de session de connexion', 'CORE'), 'change_session':('Consultation de session de connexion', 'CORE'), 'delete_session':('Consultation de session de connexion', 'CORE'),
                        'add_user':('Ajouter/modifier un utilisateur', 'CORE'), 'change_user':('Ajouter/modifier un utilisateur', 'CORE'), 'delete_user':('Ajouter/modifier un utilisateur', 'CORE'), \

                        'add_abstractcontact':('Ajouter/Modifier', 'org_lucterios_contacts'), 'change_abstractcontact':('Voir/Lister', 'org_lucterios_contacts'), 'delete_abstractcontact':('Suppression/Fusion', 'org_lucterios_contacts'), \
                        'add_postalcode':('Gestion des paramètres', 'org_lucterios_contacts'), 'change_postalcode':('Gestion des paramètres', 'org_lucterios_contacts'), \
                        'add_responsability':('Ajouter/Modifier', 'org_lucterios_contacts'), 'change_responsability':('Voir/Lister', 'org_lucterios_contacts'), 'delete_responsability':('Suppression/Fusion', 'org_lucterios_contacts'), \

                        'add_folder':('Parametrages', 'org_lucterios_documents'), 'change_folder':('Parametrages', 'org_lucterios_documents'), 'delete_folder':('Parametrages', 'org_lucterios_documents'), \
                        'add_document':('Ajout/modification', 'org_lucterios_documents'), 'change_document':('Visualisation', 'org_lucterios_documents'), 'delete_document':('Supression', 'org_lucterios_documents'), \

                        'add_third':('Ajouter/Modifier les tiers', 'fr_sdlibre_compta'), 'change_third':('Voir/Consulter les tiers', 'fr_sdlibre_compta'), 'delete_third':('Ajouter/Modifier les tiers', 'fr_sdlibre_compta'), \
                        'add_fiscalyear':('Paramètrages', 'fr_sdlibre_compta'), 'change_fiscalyear':('Paramètrages', 'fr_sdlibre_compta'), 'delete_fiscalyear':('Paramètrages', 'fr_sdlibre_compta'), \
                        'add_chartsaccount':('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta'), 'change_chartsaccount':('Voir/Consulter la comptabilité', 'fr_sdlibre_compta'), 'delete_chartsaccount':('Ajouter/Modifier la comptabilité', 'fr_sdlibre_compta')}

def dict_factory(cursor, row):
    dictdb = {}
    for idx, col in enumerate(cursor.description):
        dictdb[col[0]] = row[idx]
    return dictdb

class MigrateFromV1(LucteriosInstance):

    def __init__(self, name, instance_path=INSTANCE_PATH, debug=''):
        LucteriosInstance.__init__(self, name, instance_path)
        self.read()
        self.debug = debug
        self.old_db_path = ""
        self.tmp_path = ""
        self.filename = ""
        self.con = None

    def print_log(self, msg, arg):
        # pylint: disable=no-self-use
        try:
            six.print_(six.text_type(msg) % arg)
        except UnicodeEncodeError:
            six.print_("*** UnicodeEncodeError ***")
            try:
                six.print_(msg)
                six.print_(arg)
            except UnicodeEncodeError:
                pass

    def clear_current(self):
        self.clear()
        self.refresh()

    def extract_archive(self):
        import tarfile
        self.tmp_path = join(self.instance_path, self.name, 'tmp_resore')
        if isdir(self.tmp_path):
            rmtree(self.tmp_path)
        mkdir(self.tmp_path)
        tar = tarfile.open(self.filename, 'r:gz')
        for item in tar:
            tar.extract(item, self.tmp_path)

    def initial_olddb(self):
        self.old_db_path = join(self.instance_path, self.name, 'old_database.sqlite3')
        if isfile(self.old_db_path) and (self.debug == ''):
            unlink(self.old_db_path)

    def clear_old_archive(self):
        if self.debug == '':
            if isfile(self.old_db_path):
                unlink(self.old_db_path)
            if isdir(self.tmp_path):
                rmtree(self.tmp_path)

    def read_sqlfile(self, sql_file_path):
        # pylint: disable=too-many-branches, too-many-statements
        import re
        import codecs
        rigth_insert_script = []
        create_script = []
        insert_script = []
        sql_file = join(self.tmp_path, sql_file_path)
        if isfile(sql_file):
            with codecs.open(sql_file, 'rb', encoding='ISO-8859-1') as sqlf:
                new_create_script = None
                new_insert_script = None
                for line in sqlf.readlines():
                    try:
                        line = line.strip()
                    except UnicodeEncodeError:
                        line = line.encode("ascii", 'replace').strip()
                    if new_insert_script is not None:
                        if line[-1:] == ";":
                            new_insert_script.append(six.text_type(line))
                            insert_script.append(six.text_type("\n").join(new_insert_script))
                            if 'CORE_extension_rights' in six.text_type("\n").join(new_insert_script):
                                rigth_insert_script.append(new_insert_script)
                            new_insert_script = None
                        else:
                            new_insert_script.append(line)
                    if new_create_script is not None:
                        if line[:8] == ') ENGINE':
                            new_create_script.append(')')
                            new_script = " ".join(new_create_script)
                            if new_script[-3:] == ", )":
                                new_script = new_script[:-3] + ")"
                            create_script.append(new_script)
                            new_create_script = None
                        elif (line[:11] != 'PRIMARY KEY') and (line[:3] != 'KEY') and (line[:10] != 'UNIQUE KEY'):
                            line = re.sub(r'int\([0-9]+\) unsigned', 'NUMERIC', line)
                            line = re.sub(r'tinyint\([0-9]+\)', 'NUMERIC', line)
                            line = re.sub(r'int\([0-9]+\)', 'NUMERIC', line)
                            line = re.sub(r'varchar\([0-9]+\)', 'TEXT', line)
                            line = re.sub(r'longtext', 'TEXT', line)
                            line = re.sub(r'enum\(.*\)', 'TEXT', line)
                            line = re.sub(r' AUTO_INCREMENT,', ' PRIMARY KEY,', line)
                            if (line.find('NOT NULL') != -1) and (line.find('DEFAULT') == -1):
                                line = re.sub(' NOT NULL,', ' NOT NULL DEFAULT "",', line)
                            new_create_script.append(line)
                    elif line[:12] == 'CREATE TABLE':
                        new_create_script = []
                        new_create_script.append(line)
                    elif line[:11] == 'INSERT INTO':
                        if line[-1:] == ";":
                            insert_script.append(line)
                            if 'CORE_extension_rights' in line:
                                rigth_insert_script.append(line)
                        else:
                            new_insert_script = []
                            new_insert_script.append(line)
        return create_script, insert_script

    def open_olddb(self, with_factory=False):
        if self.con is None:
            self.con = sqlite3.connect(self.old_db_path)
        if with_factory:
            self.con.row_factory = dict_factory
        else:

            self.con.row_factory = None
        return self.con.cursor()

    def close_olddb(self):
        if self.con is not None:
            self.con.close()
        self.con = None

    def import_in_olddb(self, create_script, insert_script):
        cur = self.open_olddb()
        try:
            for item_script in create_script:
                try:
                    cur.execute(item_script)
                except (sqlite3.IntegrityError, sqlite3.OperationalError):
                    self.print_log('error: %s', item_script)
                    raise
            last_begin = ""
            for item_script in insert_script:
                try:
                    if last_begin != item_script[:70]:
                        self.con.commit()
                        last_begin = item_script[:70]
                    cur.execute(item_script)
                except (sqlite3.IntegrityError, sqlite3.OperationalError):
                    self.print_log('error: %s', item_script)
                    raise
        finally:
            self.con.commit()
            self.close_olddb()

    def restore_usergroup(self):
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        from django.contrib.auth.models import Permission, Group
        from lucterios.CORE.models import LucteriosUser, LucteriosGroup
        from django.db.utils import IntegrityError
        try:
            permissions = Permission.objects.all()  # pylint: disable=no-member
            permission_relation = []
            for permission in permissions:
                if permission.codename in PERMISSION_CODENAMES.keys():
                    rigth_name, ext_name = PERMISSION_CODENAMES[permission.codename]
                    cur = self.open_olddb()
                    sql_text = six.text_type("SELECT R.id FROM CORE_extension_rights R,CORE_extension E WHERE R.extension=E.id AND R.description='%s' AND E.extensionId='%s'") % (six.text_type(rigth_name), ext_name)
                    try:
                        cur.execute(sql_text)
                    except:  # pylint: disable=bare-except
                        self.print_log("SQL error:%s", sql_text)
                    rigth_id = cur.fetchone()
                    if rigth_id is not None:
                        permission_relation.append((permission.id, rigth_id[0]))
                    else:
                        self.print_log("=> not found %s", (sql_text,))
            LucteriosGroup.objects.all().delete()  # pylint: disable=no-member
            group_list = {}
            cur = self.open_olddb()
            cur.execute("SELECT id, groupName FROM CORE_groups")
            for groupid, group_name in cur.fetchall():
                premission_ref = []
                for perm_id, perm_oldright in permission_relation:
                    rigthcur = self.open_olddb()
                    rigthcur.execute("SELECT value FROM CORE_group_rights WHERE rightref=%d AND groupref=%d" % (perm_oldright, groupid))
                    rightvalue, = rigthcur.fetchone()
                    if rightvalue == 'o':
                        premission_ref.append(perm_id)
                new_grp = LucteriosGroup.objects.create(name=group_name)  # pylint: disable=no-member
                new_grp.permissions = Permission.objects.filter(id__in=premission_ref)  # pylint: disable=no-member
                self.print_log("=> Group %s (%s)", (group_name, premission_ref))
                group_list[groupid] = new_grp

            LucteriosUser.objects.all().delete()  # pylint: disable=no-member
            user_list = {}
            cur = self.open_olddb()
            cur.execute("SELECT id,login,pass,realName,groupId,actif FROM CORE_users")
            for userid, login, password, real_name, group_id, actif in cur.fetchall():
                if login != '':
                    self.print_log("=> User %s [%s]", (login, real_name))
                    try:
                        new_user = LucteriosUser.objects.create_user(username=login)  # pylint: disable=no-member
                        if (login == "admin") and (password[0] == '*'):
                            new_user.set_password('admin')
                        else:
                            new_user.password = password
                        new_user.first_name = real_name.split(' ')[0]
                        new_user.last_name = ''.join(real_name.split(' ')[1:])
                        new_user.is_active = (actif == 'o')
                        new_user.is_superuser = (login == 'admin')
                        if group_id in group_list.keys():
                            new_user.groups = Group.objects.filter(id__in=[group_list[group_id].pk])  # pylint: disable=no-member
                        new_user.save()
                        user_list[userid] = new_user
                    except IntegrityError:
                        self.print_log("*** User %s doubled", (login,))
        finally:
            self.close_olddb()
        return user_list, group_list

    def _restore_contact_config(self):
        # pylint: disable=too-many-locals,too-many-statements
        from django.apps import apps
        function_mdl = apps.get_model("contacts", "Function")
        function_mdl.objects.all().delete()
        function_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id, nom FROM org_lucterios_contacts_fonctions")
        for functionid, function_name in cur.fetchall():
            self.print_log("=> Function %s", (function_name,))
            function_list[functionid] = function_mdl.objects.create(name=function_name)

        structuretype_mdl = apps.get_model("contacts", "StructureType")
        structuretype_mdl.objects.all().delete()
        structuretype_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id, nom FROM org_lucterios_contacts_typesMorales")
        for structuretypeid, structuretype_name in cur.fetchall():
            self.print_log("=> StructureType %s", (structuretype_name,))
            structuretype_list[structuretypeid] = structuretype_mdl.objects.create(name=structuretype_name)

        customfield_mdl = apps.get_model("contacts", "CustomField")
        customfield_mdl.objects.all().delete()
        customfield_list = {}
        cur = self.open_olddb()
        modelnames_relation = {}

        modelnames_relation["org_lucterios_contacts/personneAbstraite"] = "contacts.AbstractContact"
        modelnames_relation["org_lucterios_contacts/personneMorale"] = "contacts.LegalEntity"
        modelnames_relation["org_lucterios_contacts/personnePhysique"] = "contacts.Individual"
        # modelnames_relation["fr_sdlibre_membres/adherents"] = ""
        cur.execute("SELECT id, class, description, type, param FROM org_lucterios_contacts_champPerso")
        for customfield_val in cur.fetchall():
            self.print_log("=> CustomField %s", customfield_val[2])
            if customfield_val[1] in modelnames_relation.keys():
                old_args = ""
                args = {'min':0, 'max':0, 'prec':0, 'list':'', 'multi':False}
                try:
                    old_args = customfield_val[4].replace('array(', '{').replace(')', '}').replace('=>', ':')
                    old_args = old_args.replace('false', 'False').replace("true", 'True')
                    old_args_eval = eval(old_args)  # pylint: disable=eval-used
                    for arg_key, arg_val in old_args_eval.items():
                        if arg_key == "Multi":
                            args['multi'] = bool(arg_val)
                        if arg_key == "Min":
                            args['min'] = int(arg_val)
                        if arg_key == "Max":
                            args['max'] = int(arg_val)
                        if arg_key == "Prec":
                            args['prec'] = int(arg_val)
                        if arg_key == "Enum":
                            args['list'] = arg_val
                except:  # pylint: disable=bare-except
                    import sys, traceback
                    traceback.print_exc(file=sys.stdout)
                    self.print_log("--- CustomField: error args=%s/%s", (customfield_val[4], old_args))
                new_cf = customfield_mdl.objects.create(name=customfield_val[2], kind=customfield_val[3])
                new_cf.modelname = modelnames_relation[customfield_val[1]]
                new_cf.args = six.text_type(args)
                new_cf.save()
                customfield_list[customfield_val[0]] = new_cf
        return structuretype_list, function_list, customfield_list

    def _restore_contact_structure(self, user_list, structuretype_list):
        # pylint: disable=too-many-locals
        def assign_abstact_values(new_legalentity, abstract_id):
            from lucterios.framework.filetools import get_user_path
            super_cur = self.open_olddb(True)
            super_cur.execute("SELECT * FROM org_lucterios_contacts_personneAbstraite WHERE id=%d" % abstract_id)
            abst_val = super_cur.fetchone()
            for old_field, new_field in [['adresse', 'address'], ['codePostal', 'postal_code'], \
                                         ['ville', 'city'], ['pays', 'country'], ['fixe', 'tel1'], \
                                         ['portable', 'tel2'], ['mail', 'email'], ['commentaire', 'comment']]:
                if abst_val[old_field] is not None:
                    setattr(new_legalentity, new_field, abst_val[old_field])
            old_image_filename = join(self.tmp_path, "usr", "org_lucterios_contacts", "Image_%d.jpg" % abstract_id)
            if isfile(old_image_filename):
                new_image_filename = get_user_path("contacts", "Image_%s.jpg" % new_legalentity.abstractcontact_ptr_id)
                copyfile(old_image_filename, new_image_filename)
        from django.apps import apps
        abstract_list = {}
        legalentity_mdl = apps.get_model("contacts", "LegalEntity")
        legalentity_mdl.objects.all().delete()
        legalentity_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id, superId, raisonSociale, type, siren FROM org_lucterios_contacts_personneMorale")
        for legalentityid, legalentity_super, legalentity_name, legalentity_type, legalentity_siren in cur.fetchall():
            self.print_log("=> LegalEntity[%d] %s (siren=%s)", (legalentityid, legalentity_name, legalentity_siren))
            if legalentityid == 1:
                new_legalentity = legalentity_mdl.objects.create(id=1, name=legalentity_name)
            else:
                new_legalentity = legalentity_mdl.objects.create(name=legalentity_name)
            assign_abstact_values(new_legalentity, legalentity_super)
            if legalentity_type in structuretype_list.keys():
                new_legalentity.structure_type = structuretype_list[legalentity_type]
            if legalentity_siren is not None:
                new_legalentity.identify_number = legalentity_siren
            new_legalentity.save()
            legalentity_list[legalentityid] = new_legalentity
            abstract_list[legalentity_super] = new_legalentity

        individual_mdl = apps.get_model("contacts", "Individual")
        individual_mdl.objects.all().delete()
        individual_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id, superId, nom, prenom, sexe, user FROM org_lucterios_contacts_personnePhysique")
        for individualid, individual_super, individual_lastname, individual_firstname, individual_sexe, individual_user in cur.fetchall():
            self.print_log("=> Individual %s %s (user=%s)", (individual_firstname, individual_lastname, individual_user))
            new_individual = individual_mdl.objects.create(firstname=individual_firstname, lastname=individual_lastname)
            assign_abstact_values(new_individual, individual_super)
            new_individual.genre = individual_sexe + 1
            if individual_user in user_list.keys():
                new_individual.user = user_list[individual_user]
            new_individual.save()
            individual_list[individualid] = new_individual
            abstract_list[individual_super] = new_individual
        return legalentity_list, individual_list, abstract_list

    def _restore_contact_relations(self, legalentity_list, individual_list, abstract_list, function_list, customfield_list):
        # pylint: disable=too-many-locals
        from django.apps import apps
        function_mdl = apps.get_model("contacts", "Function")
        responsability_mdl = apps.get_model("contacts", "Responsability")
        responsability_mdl.objects.all().delete()
        cur = self.open_olddb()
        cur.execute("SELECT DISTINCT physique, morale FROM org_lucterios_contacts_liaison")
        for physique, morale in cur.fetchall():
            if (morale in legalentity_list.keys()) and (physique in individual_list.keys()):
                new_resp = responsability_mdl.objects.create(individual=individual_list[physique], legal_entity=legalentity_list[morale])
                ids = []
                fctcur = self.open_olddb()
                fctcur.execute('SELECT fonction FROM org_lucterios_contacts_liaison WHERE physique=%d AND morale=%d' % (physique, morale))
                for fonction, in fctcur.fetchall():
                    if fonction in function_list.keys():
                        ids.append(function_list[fonction].pk)

                self.print_log("=> Responsability %s %s =%s", (six.text_type(individual_list[physique]), six.text_type(legalentity_list[morale]), six.text_type(ids)))
                new_resp.functions = function_mdl.objects.filter(id__in=ids)
                new_resp.save()

        contactcustomfield_mdl = apps.get_model("contacts", "ContactCustomField")
        contactcustomfield_mdl.objects.all().delete()
        cur = self.open_olddb()
        cur.execute("SELECT contact, champ, value FROM org_lucterios_contacts_personneChamp")
        self.print_log("=> ContactCustomField %d", len(list(cur.fetchall())))
        for contactcustomfield_val in cur.fetchall():
            abs_contact = abstract_list[contactcustomfield_val[0]]
            if (contactcustomfield_val[2] != '') and (contactcustomfield_val[1] in customfield_list.keys()):
                cust_field = customfield_list[contactcustomfield_val[1]]
                contactcustomfield_mdl.objects.create(contact=abs_contact, field=cust_field, value=contactcustomfield_val[2])

    def restore_contact(self, user_list):
        from django.apps import apps
        try:
            apps.get_app_config("contacts")
        except LookupError:
            self.print_log("=> No contacts module", ())
            return
        try:
            structuretype_list, function_list, customfield_list = self._restore_contact_config()
            legalentity_list, individual_list, abstract_list = self._restore_contact_structure(user_list, structuretype_list)
            self._restore_contact_relations(legalentity_list, individual_list, abstract_list, function_list, customfield_list)
        finally:
            self.close_olddb()
        return abstract_list

    def _restore_document_folders(self, group_list):
        # pylint: disable=too-many-locals
        from django.apps import apps
        group_mdl = apps.get_model("CORE", "LucteriosGroup")
        folder_mdl = apps.get_model("documents", "Folder")
        folder_mdl.objects.all().delete()
        folder_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id, nom, description, parent FROM org_lucterios_documents_categorie ORDER BY parent,id")
        for folderid, folder_name, folder_description, folder_parent in cur.fetchall():
            self.print_log("=> Folder %s", (folder_name,))
            folder_list[folderid] = folder_mdl.objects.create(name=folder_name, description=folder_description)
            if folder_parent is not None:
                folder_list[folderid].parent = folder_list[folder_parent]
                folder_list[folderid].save()

            modif_group = []
            cur_mod = self.open_olddb()
            cur_mod.execute("SELECT groupe FROM org_lucterios_documents_modification WHERE categorie=%d" % folderid)
            for group_id in cur_mod.fetchall():
                modif_group.append(group_list[group_id[0]].id)

            visu_group = []
            cur_visu = self.open_olddb()
            cur_visu.execute("SELECT groupe FROM org_lucterios_documents_visualisation WHERE categorie=%d" % folderid)
            for group_id in cur_visu.fetchall():
                visu_group.append(group_list[group_id[0]].id)

            folder_list[folderid].modifier = group_mdl.objects.filter(id__in=modif_group)
            folder_list[folderid].viewer = group_mdl.objects.filter(id__in=visu_group)
        return folder_list

    def _restore_document_docs(self, folder_list, user_list):
        # pylint: disable=too-many-locals
        from lucterios.framework.filetools import get_user_path
        from django.apps import apps
        doc_mdl = apps.get_model("documents", "Document")
        doc_mdl.objects.all().delete()
        doc_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id, nom, description, categorie, modificateur, createur, dateModification, dateCreation FROM org_lucterios_documents_document")
        for docid, doc_name, doc_description, doc_folder, doc_modifier, doc_creator, doc_datemod, doc_datecreat in cur.fetchall():
            self.print_log("=> Document %s", (doc_name,))
            doc_list[docid] = doc_mdl.objects.create(name=doc_name, description=doc_description, date_modification=doc_datemod, date_creation=doc_datecreat)
            if doc_folder is not None:
                doc_list[docid].folder = folder_list[doc_folder]
            doc_list[docid].modifier = user_list[doc_modifier]
            doc_list[docid].creator = user_list[doc_creator]
            doc_list[docid].save()
            new_filename = get_user_path("documents", "document_%s" % six.text_type(doc_list[docid].id))
            old_filename = join(self.tmp_path, "usr", "org_lucterios_documents", "document%d" % docid)
            if isfile(old_filename):
                copyfile(old_filename, new_filename)
            else:
                with open(new_filename, 'wb') as newfl:
                    newfl.write('')

    def restore_document(self, group_list, user_list):
        from django.apps import apps
        try:
            apps.get_app_config("documents")
        except LookupError:
            self.print_log("=> No documents module", ())
            return
        folder_list = self._restore_document_folders(group_list)
        self._restore_document_docs(folder_list, user_list)

    def _restore_accounting_thirds(self, abstract_list):
        from django.apps import apps
        third_mdl = apps.get_model("accounting", "Third")
        third_mdl.objects.all().delete()
        accountthird_mdl = apps.get_model("accounting", "AccountThird")
        accountthird_mdl.objects.all().delete()
        third_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id,contact,compteFournisseur,compteClient,compteSalarie,compteSocietaire,etat FROM fr_sdlibre_compta_Tiers")
        for thirdid, abstractid, compte_fournisseur, compte_client, compte_salarie, compte_societaire, etat in cur.fetchall():
            self.print_log("=> Third of %s", (abstract_list[abstractid],))
            third_list[thirdid] = third_mdl.objects.create(contact=abstract_list[abstractid], status=etat)
            if (compte_fournisseur is not None) and (compte_fournisseur != ''):
                accountthird_mdl.objects.create(third=third_list[thirdid], code=compte_fournisseur)
            if (compte_client is not None) and (compte_client != ''):
                accountthird_mdl.objects.create(third=third_list[thirdid], code=compte_client)
            if (compte_salarie is not None) and (compte_salarie != ''):
                accountthird_mdl.objects.create(third=third_list[thirdid], code=compte_salarie)
            if (compte_societaire is not None) and (compte_societaire != ''):
                accountthird_mdl.objects.create(third=third_list[thirdid], code=compte_societaire)
        return third_list

    def _restore_accounting_years(self):
        from django.apps import apps
        year_mdl = apps.get_model("accounting", "FiscalYear")
        year_mdl.objects.all().delete()
        year_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id, debut,fin,etat,actif,lastExercice  FROM fr_sdlibre_compta_Exercices ORDER BY fin")
        for yearid, debut, fin, etat, actif, lastExercice in cur.fetchall():
            self.print_log("=> Year of %s => %s", (debut, fin))
            year_list[yearid] = year_mdl.objects.create(begin=debut, end=fin, status=etat, is_actif=(actif == 'o'))
            if lastExercice is not None:
                year_list[yearid].last_fiscalyear = year_list[lastExercice]
                year_list[yearid].save()
        return year_list

    def _restore_accounting_chartsaccount(self, year_list):
        from django.apps import apps
        chartsaccount_mdl = apps.get_model("accounting", "ChartsAccount")
        chartsaccount_mdl.objects.all().delete()
        chartsaccount_list = {}
        cur = self.open_olddb()
        cur.execute("SELECT id,numCpt,designation,exercice FROM fr_sdlibre_compta_Plan")
        for chartsaccountid, num_cpt, designation, exercice in cur.fetchall():
            self.print_log("=> charts of account %s - %d", (num_cpt, exercice))
            chartsaccount_list[chartsaccountid] = chartsaccount_mdl.objects.create(code=num_cpt, name=designation, year=year_list[exercice])
            if (num_cpt[0] == '2') or (num_cpt[0] == '3') or (num_cpt[0:2] == '41') or (num_cpt[0] == '5'):
                chartsaccount_list[chartsaccountid].type_of_account = 0  # Asset / 'actif'
            if (num_cpt[0] == '4') and (num_cpt[0:2] != '41'):
                chartsaccount_list[chartsaccountid].type_of_account = 1  # Liability / 'passif'
            if num_cpt[0] == '1':
                chartsaccount_list[chartsaccountid].type_of_account = 2  # Equity / 'capital'
            if num_cpt[0] == '7':
                chartsaccount_list[chartsaccountid].type_of_account = 3  # Revenue
            if num_cpt[0] == '6':
                chartsaccount_list[chartsaccountid].type_of_account = 4  # Expense
            if num_cpt[0] == '8':
                chartsaccount_list[chartsaccountid].type_of_account = 5  # Contra-accounts
            chartsaccount_list[chartsaccountid].save()
        return chartsaccount_list


    def _restore_accounting_extra(self):
        from django.apps import apps
        journal_mdl = apps.get_model("accounting", "Journal")
        accountlink_mdl = apps.get_model("accounting", "AccountLink")
        accountlink_mdl.objects.all().delete()
        journal_list = {}
        journal_list[1] = journal_mdl.objects.get(id=2)
        journal_list[2] = journal_mdl.objects.get(id=3)
        journal_list[3] = journal_mdl.objects.get(id=4)
        journal_list[4] = journal_mdl.objects.get(id=5)
        journal_list[5] = journal_mdl.objects.get(id=1)
        accountlink_list = {}
        cur_al = self.open_olddb()
        cur_al.execute("SELECT id FROM fr_sdlibre_compta_raprochement ORDER BY id")
        for (accountlinkid,) in cur_al.fetchall():
            accountlink_list[accountlinkid] = accountlink_mdl.objects.create()
        return journal_list, accountlink_list

    def _restore_accounting_entryaccount(self, year_list, third_list, account_list):
        # pylint: disable=too-many-locals
        from django.apps import apps
        entryaccount_mdl = apps.get_model("accounting", "EntryAccount")
        entryaccount_mdl.objects.all().delete()
        entrylineaccount_mdl = apps.get_model("accounting", "EntryLineAccount")
        entrylineaccount_mdl.objects.all().delete()
        entryaccount_list = {}
        entrylineaccount_list = {}
        journal_list, accountlink_list = self._restore_accounting_extra()
        cur_e = self.open_olddb()
        cur_e.execute("SELECT id, num, dateEcr, datePiece, designation, exercice, point, journal, opeRaproch, analytique FROM fr_sdlibre_compta_Operation")
        for entryaccountid, num, date_ecr, date_piece, designation, exercice, point, journal, operaproch, _ in cur_e.fetchall():
            self.print_log("=> entry account %s - %d", (six.text_type(num), exercice))
            entryaccount_list[entryaccountid] = entryaccount_mdl.objects.create(num=num, designation=designation, \
                                                        year=year_list[exercice], date_entry=date_ecr, date_value=date_piece, \
                                                        close=point == 'o', journal=journal_list[journal])
            if operaproch is not None:
                entryaccount_list[entryaccountid].link = accountlink_list[operaproch]
                entryaccount_list[entryaccountid].save()
        cur_l = self.open_olddb()
        cur_l.execute("SELECT id,numCpt,montant,reference,operation,tiers  FROM fr_sdlibre_compta_Ecriture")
        for entrylineaccountid, num_cpt, montant, reference, operation, tiers in cur_l.fetchall():
            self.print_log("=> line entry account %f - %d", (montant, num_cpt))
            entrylineaccount_list[entrylineaccountid] = entrylineaccount_mdl.objects.create(account=account_list[num_cpt], entry=entryaccount_list[operation], \
                                                                                amount=montant, reference=reference)
            if tiers is not None:
                entrylineaccount_list[entrylineaccountid].third = third_list[tiers]
                entrylineaccount_list[entrylineaccountid].save()

    def restore_compta(self, abstract_list):
        from django.apps import apps
        try:
            apps.get_app_config("accounting")
        except LookupError:
            self.print_log("=> No accounting module", ())
            return
        thirds = self._restore_accounting_thirds(abstract_list)
        years = self._restore_accounting_years()
        accounts = self._restore_accounting_chartsaccount(years)
        self._restore_accounting_entryaccount(years, thirds, accounts)

    def restore(self):
        begin_time = time()
        self.initial_olddb()
        self.extract_archive()
        if not isfile(self.old_db_path):
            for filename in ['data_CORE.sql', 'data_org_lucterios_contacts.sql', 'data_org_lucterios_documents.sql', 'data_fr_sdlibre_compta.sql']:
                create_script, insert_script = self.read_sqlfile(filename)
                self.import_in_olddb(create_script, insert_script)
        self.clear_current()
        users, groups = self.restore_usergroup()
        if isfile(join(self.tmp_path, 'data_org_lucterios_documents.sql')):
            self.restore_document(groups, users)
        if isfile(join(self.tmp_path, 'data_org_lucterios_contacts.sql')):
            abstracts = self.restore_contact(users)
            if isfile(join(self.tmp_path, 'data_fr_sdlibre_compta.sql')):
                self.restore_compta(abstracts)
        self.clear_old_archive()
        duration_sec = time() - begin_time
        duration_min = int(duration_sec / 60)
        duration_sec = duration_sec - duration_min * 60
        self.print_log("Migration duration: %d min %d sec", (duration_min, duration_sec))
        return True

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog --name <instance name> --archive <archive file>",
                          version="%prog 0.1")
    parser.add_option("-n", "--name",
                      dest="name",
                      help="Instance to restore")
    parser.add_option("-a", "--archive",
                      dest="archive",
                      default="",
                      help="Archive to restore",)
    parser.add_option("-i", "--instance_path",
                      dest="instance_path",
                      default=INSTANCE_PATH,
                      help="Directory of instance storage",)
    parser.add_option("-d", "--debug",
                      dest="debug",
                      default="",
                      help="Debug option",)
    (options, _) = parser.parse_args()
    if options.name is None:
        parser.error('Name needed!')
    if not isfile(options.archive):
        parser.error('Archive "%s" no found!' % options.archive)
    mirg = MigrateFromV1(options.name, options.instance_path, options.debug)
    mirg.filename = options.archive
    mirg.restore()

if __name__ == '__main__':
    main()
