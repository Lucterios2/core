# -*- coding: utf-8 -*-
#!/usr/bin/env python
# pylint: disable=invalid-name
'''
Created on avr. 2015

@author: sd-libre
'''

from django.utils import six

INSTANCE_PATH = '.'

def dict_factory(cursor, row):
    dictdb = {}
    for idx, col in enumerate(cursor.description):
        dictdb[col[0]] = row[idx]
    return dictdb

def extract_archive(name, archive):
    from shutil import rmtree
    from os import mkdir
    from os.path import join, isdir, abspath
    tmp_path = join(abspath(INSTANCE_PATH), name, 'tmp_resore')
    if isdir(tmp_path):
        rmtree(tmp_path)
    mkdir(tmp_path)
    import tarfile
    tar = tarfile.open(archive, 'r:gz')
    for item in tar:
        tar.extract(item, tmp_path)
    return tmp_path

def initial_olddb(name, debug):
    from os import unlink
    from os.path import join, isfile, abspath
    old_db_path = join(abspath(INSTANCE_PATH), name, 'old_database.sqlite3')
    if isfile(old_db_path) and (debug == ''):
        unlink(old_db_path)
    return old_db_path

def read_sqlfile(sql_file_path):
    # pylint: disable=too-many-branches
    import re
    with open(sql_file_path, 'r', encoding='iso 8859-15') as sqlf:
        create_script = []
        insert_script = []
        new_create_script = None
        new_insert_script = None
        for line in sqlf.readlines():
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

def import_in_olddb(old_db_path, create_script, insert_script):
    import sqlite3
    con = sqlite3.connect(old_db_path)
    cur = con.cursor()
    for item_script in create_script:
        try:
            cur.execute(item_script)
        except (sqlite3.IntegrityError, sqlite3.OperationalError):
            six.print_('error:' + item_script)
            raise
    last_begin = ""
    for item_script in insert_script:
        try:
            if last_begin != item_script[:70]:
                con.commit()
                last_begin = item_script[:70]
            cur.execute(item_script)
        except (sqlite3.IntegrityError, sqlite3.OperationalError):
            six.print_('error:' + item_script)
            raise
    con.commit()
    con.close()

def restore_usergroup(old_db_path):
    # pylint: disable=too-many-locals
    import sqlite3
    from django.contrib.auth.models import User, Group
    con = sqlite3.connect(old_db_path)
    try:
        Group.objects.all().delete()  # pylint: disable=no-member
        group_list = {}
        cur = con.cursor()
        cur.execute("SELECT id, groupName FROM CORE_groups")
        for groupid, group_name in cur.fetchall():
            new_grp = Group.objects.create(name=group_name)  # pylint: disable=no-member
            six.print_("=> Group %s" % (group_name,))
            group_list[groupid] = new_grp

        User.objects.all().delete()  # pylint: disable=no-member
        user_list = {}
        cur = con.cursor()

        cur.execute("SELECT id,login,pass,real_name,group_id,actif FROM CORE_users")
        for userid, login, password, real_name, group_id, actif in cur.fetchall():
            if login != '':
                six.print_("=> User %s [%s]" % (login, real_name))
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
    finally:
        con.close()
    return user_list

def read_personne_abstacte(con, abstract_id):
    con.row_factory = dict_factory
    super_cur = con.cursor()
    super_cur.execute("SELECT * FROM org_lucterios_contacts_personneAbstraite WHERE id=%d" % abstract_id)
    abst_val = super_cur.fetchone()
    return abst_val

def assign_abstact_values(new_legalentity, abst_val):
    for old_field, new_field in [['adresse', 'address'], ['codePostal', 'postal_code'], \
                                 ['ville', 'city'], ['pays', 'country'], ['fixe', 'tel1'], \
                                 ['portable', 'tel2'], ['mail', 'email'], ['commentaire', 'comment']]:
        if abst_val[old_field] is not None:
            setattr(new_legalentity, new_field, abst_val[old_field])

def restore_contact(old_db_path, user_list):
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    import sqlite3
    from django.apps import apps
    function_mdl = apps.get_model("contacts", "Function")
    structuretype_mdl = apps.get_model("contacts", "StructureType")
    legalentity_mdl = apps.get_model("contacts", "LegalEntity")
    individual_mdl = apps.get_model("contacts", "Individual")
    responsability_mdl = apps.get_model("contacts", "Responsability")
    con = sqlite3.connect(old_db_path)
    try:
        function_mdl.objects.all().delete()
        function_list = {}
        cur = con.cursor()

        cur.execute("SELECT id, nom FROM org_lucterios_contacts_fonctions")
        for functionid, function_name in cur.fetchall():
            six.print_("=> Function %s" % (function_name,))
            function_list[functionid] = function_mdl.objects.create(name=function_name)

        structuretype_mdl.objects.all().delete()
        structuretype_list = {}
        cur = con.cursor()

        cur.execute("SELECT id, nom FROM org_lucterios_contacts_typesMorales")
        for structuretypeid, structuretype_name in cur.fetchall():
            six.print_("=> StructureType %s" % (structuretype_name,))
            structuretype_list[structuretypeid] = structuretype_mdl.objects.create(name=structuretype_name)

        legalentity_mdl.objects.all().delete()
        legalentity_list = {}

        con.row_factory = None
        cur = con.cursor()
        cur.execute("SELECT id, superId, raisonSociale, type, siren FROM org_lucterios_contacts_personneMorale")
        for legalentityid, legalentity_super, legalentity_name, legalentity_type, legalentity_siren in cur.fetchall():
            abst_val = read_personne_abstacte(con, legalentity_super)
            six.print_("=> LegalEntity[%d] %s (siren=%s) %s" % (legalentityid, legalentity_name, legalentity_siren, six.text_type(abst_val)))
            if legalentityid == 1:
                new_legalentity = legalentity_mdl.objects.create(id=1, name=legalentity_name)
            else:
                new_legalentity = legalentity_mdl.objects.create(name=legalentity_name)
            assign_abstact_values(new_legalentity, abst_val)
            if legalentity_type in structuretype_list.keys():
                new_legalentity.structure_type = structuretype_list[legalentity_type]
            if legalentity_siren is not None:

                new_legalentity.identify_number = legalentity_siren
            new_legalentity.save()
            legalentity_list[legalentityid] = new_legalentity

        individual_mdl.objects.all().delete()
        individual_list = {}
        con.row_factory = None
        cur = con.cursor()
        cur.execute("SELECT id, superId, nom, prenom, sexe, user FROM org_lucterios_contacts_personnePhysique")
        for individualid, individual_super, individual_firstname, individual_lastname, individual_sexe, individual_user in cur.fetchall():
            abst_val = read_personne_abstacte(con, individual_super)
            six.print_("=> Individual %s %s (user=%s) %s" % (individual_firstname, individual_lastname, individual_user, six.text_type(abst_val)))
            new_individual = individual_mdl.objects.create(firstname=individual_firstname, lastname=individual_lastname)
            assign_abstact_values(new_individual, abst_val)
            new_individual.genre = individual_sexe + 1
            if individual_user in user_list.keys():
                new_individual.user = user_list[individual_user]
            new_individual.save()
            individual_list[individualid] = new_individual

        responsability_mdl.objects.all().delete()
        con.row_factory = None
        cur = con.cursor()
        cur.execute("SELECT DISTINCT physique, morale FROM org_lucterios_contacts_liaison")
        for physique, morale in cur.fetchall():
            if (morale in legalentity_list.keys()) and (physique in individual_list.keys()):
                new_resp = responsability_mdl.objects.create(individual=individual_list[physique], legal_entity=legalentity_list[morale])
                ids = []
                fctcur = con.cursor()
                fctcur.execute('SELECT fonction FROM org_lucterios_contacts_liaison WHERE physique=%d AND morale=%d' % (physique, morale))
                for (fonction,) in fctcur.fetchall():
                    if fonction in function_list.keys():

                        ids.append(function_list[fonction].pk)
                six.print_("=> Responsability %s %s =%s" % (six.text_type(individual_list[physique]), six.text_type(legalentity_list[morale]), six.text_type(ids)))

                new_resp.functions = function_mdl.objects.filter(id__in=ids)
                new_resp.save()
    finally:
        con.close()

def restore(name, archive, debug):
    import os, sys
    from os.path import join, isfile, abspath
    sys.path.insert(0, abspath(INSTANCE_PATH))

    os.environ["DJANGO_SETTINGS_MODULE"] = "%s.settings" % name
    from django import setup
    setup()

    old_db_path = initial_olddb(name, debug)
    tmp_path = extract_archive(name, archive)
    if not isfile(old_db_path):
        for filename in ['data_CORE.sql', 'data_org_lucterios_contacts.sql']:
            create_script, insert_script = read_sqlfile(join(tmp_path, filename))
            import_in_olddb(old_db_path, create_script, insert_script)

    users = restore_usergroup(old_db_path)
    restore_contact(old_db_path, users)

def main():
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 0.1")
    parser.add_option("-n", "--name",
                      dest="name",
                      help="Instance to restore")
    parser.add_option("-a", "--archive",
                      dest="archive",
                      help="Archive to restore",)
    parser.add_option("-d", "--debug",
                      dest="debug",
                      default="",
                      help="Debug option",)
    (options, _) = parser.parse_args()
    restore(options.name, options.archive, options.debug)

if __name__ == '__main__':
    main()
