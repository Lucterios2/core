#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
'''
Created on avr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from os.path import join, isfile, isdir
from os import mkdir, unlink
from shutil import rmtree, copyfile
import sqlite3

from lucterios.install.lucterios_admin import LucteriosInstance
from django.utils import six

INSTANCE_PATH = '.'

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

                        'add_individual':('Ajouter/Modifier', 'org_lucterios_contacts'), 'change_individual':('Voir/Lister', 'org_lucterios_contacts'), 'delete_individual':('Suppression/Fusion', 'org_lucterios_contacts'), \
                        'add_legalentity':('Ajouter/Modifier', 'org_lucterios_contacts'), 'change_legalentity':('Voir/Lister', 'org_lucterios_contacts'), 'delete_legalentity':('Suppression/Fusion', 'org_lucterios_contacts'), \
                        'add_postalcode':('Gestion des paramètres', 'org_lucterios_contacts'), 'change_postalcode':('Gestion des paramètres', 'org_lucterios_contacts'), \
                        'add_responsability':('Ajouter/Modifier', 'org_lucterios_contacts'), 'change_responsability':('Voir/Lister', 'org_lucterios_contacts'), 'delete_responsability':('Suppression/Fusion', 'org_lucterios_contacts')}

def dict_factory(cursor, row):
    dictdb = {}
    for idx, col in enumerate(cursor.description):
        dictdb[col[0]] = row[idx]
    return dictdb

class MigrateFromV1(LucteriosInstance):

    def __init__(self, name, instance_path, debug):
        LucteriosInstance.__init__(self, name, instance_path)
        self.read()
        self.debug = debug
        self.old_db_path = ""
        self.tmp_path = ""
        self.con = None

    def print_log(self, msg, arg):
        # pylint: disable=no-self-use
        try:
            six.print_(six.text_type(msg) % arg)
        except UnicodeEncodeError:
            six.print_("*** UnicodeEncodeError ***")
            six.print_(msg)
            six.print_(arg)

    def clear_current(self):
        self.clear()
        self.refresh()

    def extract_archive(self, archive):
        import tarfile
        self.tmp_path = join(self.instance_path, self.name, 'tmp_resore')
        if isdir(self.tmp_path):
            rmtree(self.tmp_path)
        mkdir(self.tmp_path)
        tar = tarfile.open(archive, 'r:gz')
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
        # pylint: disable=too-many-branches
        import re
        try:
            sqlf = open(join(self.tmp_path, sql_file_path), 'r', encoding='iso 8859-15')
        except TypeError:
            sqlf = open(join(self.tmp_path, sql_file_path), 'r')
        with sqlf:
            create_script = []
            insert_script = []
            new_create_script = None
            new_insert_script = None
            for line in sqlf.readlines():
                try:
                    line = line.decode('iso 8859-15').strip()
                except AttributeError:
                    line = line.strip()
                if new_insert_script is not None:
                    if line[-1:] == ";":
                        new_insert_script.append(line)
                        insert_script.append("\n".join(new_insert_script))
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
        from django.contrib.auth.models import User, Group, Permission
        from django.db.utils import IntegrityError
        try:
            permissions = Permission.objects.all()  # pylint: disable=no-member
            permission_relation = []
            for permission in permissions:
                if permission.codename in PERMISSION_CODENAMES.keys():
                    rigth_name, ext_name = PERMISSION_CODENAMES[permission.codename]
                    cur = self.open_olddb()
                    try:
                        rigth_name = rigth_name.decode('utf-8')
                    except AttributeError:
                        pass
                    sql_text = six.text_type("SELECT R.id FROM CORE_extension_rights R,CORE_extension E WHERE R.extension=E.id AND R.description='%s' AND E.extensionId='%s'") % (rigth_name, ext_name)
                    cur.execute(sql_text)
                    rigth_id = cur.fetchone()
                    if rigth_id is not None:
                        permission_relation.append((permission.id, rigth_id[0]))
                    else:
                        self.print_log("=> not found %s", (sql_text,))
            Group.objects.all().delete()  # pylint: disable=no-member
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
                new_grp = Group.objects.create(name=group_name)  # pylint: disable=no-member
                new_grp.permissions = Permission.objects.filter(id__in=premission_ref)  # pylint: disable=no-member
                self.print_log("=> Group %s (%s)", (group_name, premission_ref))
                group_list[groupid] = new_grp

            User.objects.all().delete()  # pylint: disable=no-member
            user_list = {}
            cur = self.open_olddb()

            cur.execute("SELECT id,login,pass,realName,groupId,actif FROM CORE_users")
            for userid, login, password, real_name, group_id, actif in cur.fetchall():
                if login != '':
                    self.print_log("=> User %s [%s]", (login, real_name))
                    try:
                        new_user = User.objects.create_user(username=login)  # pylint: disable=no-member
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
        return user_list

    def restore_contact(self, user_list):
        # pylint: disable=too-many-locals,too-many-branches,too-many-statements
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
        try:
            apps.get_app_config("contacts")
        except LookupError:
            self.print_log("=> No contacts module", ())
            return
        function_mdl = apps.get_model("contacts", "Function")
        structuretype_mdl = apps.get_model("contacts", "StructureType")
        legalentity_mdl = apps.get_model("contacts", "LegalEntity")
        individual_mdl = apps.get_model("contacts", "Individual")
        responsability_mdl = apps.get_model("contacts", "Responsability")
        try:
            function_mdl.objects.all().delete()
            function_list = {}
            cur = self.open_olddb()

            cur.execute("SELECT id, nom FROM org_lucterios_contacts_fonctions")
            for functionid, function_name in cur.fetchall():
                self.print_log("=> Function %s", (function_name,))
                function_list[functionid] = function_mdl.objects.create(name=function_name)

            structuretype_mdl.objects.all().delete()
            structuretype_list = {}
            cur = self.open_olddb()

            cur.execute("SELECT id, nom FROM org_lucterios_contacts_typesMorales")
            for structuretypeid, structuretype_name in cur.fetchall():
                self.print_log("=> StructureType %s", (structuretype_name,))
                structuretype_list[structuretypeid] = structuretype_mdl.objects.create(name=structuretype_name)

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

            individual_mdl.objects.all().delete()
            individual_list = {}
            cur = self.open_olddb()

            cur.execute("SELECT id, superId, nom, prenom, sexe, user FROM org_lucterios_contacts_personnePhysique")
            for individualid, individual_super, individual_firstname, individual_lastname, individual_sexe, individual_user in cur.fetchall():
                self.print_log("=> Individual %s %s (user=%s)", (individual_firstname, individual_lastname, individual_user))
                new_individual = individual_mdl.objects.create(firstname=individual_firstname, lastname=individual_lastname)
                assign_abstact_values(new_individual, individual_super)
                new_individual.genre = individual_sexe + 1
                if individual_user in user_list.keys():
                    new_individual.user = user_list[individual_user]
                new_individual.save()
                individual_list[individualid] = new_individual

            responsability_mdl.objects.all().delete()
            cur = self.open_olddb()

            cur.execute("SELECT DISTINCT physique, morale FROM org_lucterios_contacts_liaison")
            for physique, morale in cur.fetchall():
                if (morale in legalentity_list.keys()) and (physique in individual_list.keys()):
                    new_resp = responsability_mdl.objects.create(individual=individual_list[physique], legal_entity=legalentity_list[morale])
                    ids = []
                    fctcur = self.open_olddb()
                    fctcur.execute('SELECT fonction FROM org_lucterios_contacts_liaison WHERE physique=%d AND morale=%d' % (physique, morale))
                    for (fonction,) in fctcur.fetchall():
                        if fonction in function_list.keys():
                            ids.append(function_list[fonction].pk)
                    self.print_log("=> Responsability %s %s =%s", (six.text_type(individual_list[physique]), six.text_type(legalentity_list[morale]), six.text_type(ids)))
                    new_resp.functions = function_mdl.objects.filter(id__in=ids)
                    new_resp.save()
        finally:
            self.close_olddb()

    def restore(self, archive):
        self.initial_olddb()
        self.extract_archive(archive)
        if not isfile(self.old_db_path):
            for filename in ['data_CORE.sql', 'data_org_lucterios_contacts.sql']:
                create_script, insert_script = self.read_sqlfile(filename)
                self.import_in_olddb(create_script, insert_script)
        self.clear_current()
        users = self.restore_usergroup()
        self.restore_contact(users)
        self.clear_old_archive()

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
    mirg.restore(options.archive)

if __name__ == '__main__':
    main()
