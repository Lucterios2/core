'''
Created on 10 juil. 2025

@author: lag
'''
from os.path import join
from unittest.mock import patch, call, Mock
from io import BytesIO, StringIO
from os import getenv
from datetime import datetime, timedelta
import sys

from django.conf import settings

from lucterios.framework.test import LucteriosTest
from lucterios.CORE.views_archive import VirtualArchiveList, VirtualArchiveDel,\
    VirtualArchiveRename, VirtualArchiveExport, VirtualArchiveImport,\
    VirtualArchiveImportAct, VirtualArchiveAddModify, VirtualArchiveRestore
from lucterios.CORE.models import VirtualArchive


class ArchiveTest(LucteriosTest):

    MY_BACKUP_DIR = '/tmp/backup'

    def setUp(self):
        LucteriosTest.setUp(self)
        self.instance_name = getenv("DJANGO_SETTINGS_MODULE", "???.???").split('.')[0]
        settings.BACKUP_DIRECTORY = self.MY_BACKUP_DIR
        settings.BACKUP_POST_RESTORE_SCRIPT = join(settings.BACKUP_DIRECTORY, 'script.py')
        settings.BACKUP_READONLY = False

    def tearDown(self)->None:
        settings.BACKUP_READONLY = False
        settings.BACKUP_DIRECTORY = ''
        settings.BACKUP_POST_RESTORE_SCRIPT = ''
        LucteriosTest.tearDown(self)

    @patch("os.path.getmtime", side_effect=[1433714400.0, 1411164000.0])
    @patch("os.path.getsize", side_effect=[67 * 1024 * 1024, 45 * 1024 * 1024])
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("glob.iglob", return_value=[join(MY_BACKUP_DIR, "aaa.lbk"), join(MY_BACKUP_DIR, "bbb.lbk")])
    def test_list(self, mock_glob, mock_isdir, mock_isfile, mock_getsize, mock_getmtime):
        self.factory.xfer = VirtualArchiveList()
        self.calljson('/CORE/virtualArchiveList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'virtualArchiveList')
        self.assert_count_equal('virtualarchive', 2)
        self.assert_json_equal('', 'virtualarchive/@0/id', join(settings.BACKUP_DIRECTORY, "aaa.lbk"))
        self.assert_json_equal('', 'virtualarchive/@0/name', "aaa")
        self.assert_json_equal('', 'virtualarchive/@0/file_size', 67)
        self.assert_json_equal('', 'virtualarchive/@0/modify_date', "2015-06-07T22:00:00")
        self.assert_json_equal('', 'virtualarchive/@1/id', join(settings.BACKUP_DIRECTORY, "bbb.lbk"))
        self.assert_json_equal('', 'virtualarchive/@1/name', "bbb")
        self.assert_json_equal('', 'virtualarchive/@1/file_size', 45)
        self.assert_json_equal('', 'virtualarchive/@1/modify_date', "2014-09-19T22:00:00")
        self.assert_count_equal('#virtualarchive/actions', 6)
        self.assert_action_equal('DELETE', '#virtualarchive/actions/@0', ('Supprimer', 'mdi:mdi-delete-outline', 'CORE', 'virtualArchiveDel', 0, 1, 2))
        self.assert_action_equal('POST', '#virtualarchive/actions/@1', ('Archive', 'mdi:mdi-pencil-plus-outline', 'CORE', 'virtualArchiveAddModify', 0, 1, 1))
        self.assert_action_equal('POST', '#virtualarchive/actions/@2', ('Import', 'mdi:mdi-upload', 'CORE', 'virtualArchiveImport', 0, 1, 1))
        self.assert_action_equal('POST', '#virtualarchive/actions/@3', ('Export', 'mdi:mdi-download', 'CORE', 'virtualArchiveExport', 0, 1, 0))
        self.assert_action_equal('POST', '#virtualarchive/actions/@4', ('Restauration', 'mdi:mdi-check', 'CORE', 'virtualArchiveRestore', 0, 1, 0))
        self.assert_action_equal('POST', '#virtualarchive/actions/@5', ('Renomer', 'mdi:mdi-pencil-outline', 'CORE', 'virtualArchiveRename', 0, 1, 0))

        self.assertEqual(mock_isdir.call_count, 7)
        self.assertEqual(mock_glob.call_count, 1)
        self.assertEqual(mock_isfile.call_count, 3)
        self.assertEqual(mock_getsize.call_count, 2)
        self.assertEqual(mock_getmtime.call_count, 2)
        self.assertEqual(mock_glob.call_args.args, (join(self.MY_BACKUP_DIR, "*.lbk"),))

    @patch("os.path.getmtime", side_effect=[1433714400.0, 1411164000.0, 1433714400.0, 1411164000.0, 1433714400.0, 1411164000.0, 1433714400.0, 1411164000.0])
    @patch("os.path.getsize", side_effect=[67 * 1024 * 1024, 45 * 1024 * 1024, 67 * 1024 * 1024, 45 * 1024 * 1024, 67 * 1024 * 1024, 45 * 1024 * 1024, 67 * 1024 * 1024, 45 * 1024 * 1024])
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("glob.iglob", return_value=[join(MY_BACKUP_DIR, "aaa.lbk"), join(MY_BACKUP_DIR, "bbb.lbk")])
    def test_list_order(self, mock_glob, mock_isdir, mock_isfile, mock_getsize, mock_getmtime):
        settings.BACKUP_READONLY = True
        self.factory.xfer = VirtualArchiveList()
        self.calljson('/CORE/virtualArchiveList', {'GRID_ORDER%virtualarchive': 'file_size'}, False)
        self.assert_observer('core.custom', 'CORE', 'virtualArchiveList')
        self.assert_count_equal('virtualarchive', 2)
        self.assert_json_equal('', 'virtualarchive/@0/id', join(settings.BACKUP_DIRECTORY, "bbb.lbk"))
        self.assert_json_equal('', 'virtualarchive/@0/name', "bbb")
        self.assert_json_equal('', 'virtualarchive/@0/file_size', 45)
        self.assert_json_equal('', 'virtualarchive/@0/modify_date', "2014-09-19T22:00:00")
        self.assert_json_equal('', 'virtualarchive/@1/id', join(settings.BACKUP_DIRECTORY, "aaa.lbk"))
        self.assert_json_equal('', 'virtualarchive/@1/name', "aaa")
        self.assert_json_equal('', 'virtualarchive/@1/file_size', 67)
        self.assert_json_equal('', 'virtualarchive/@1/modify_date', "2015-06-07T22:00:00")
        self.assert_count_equal('#virtualarchive/actions', 2)
        self.assert_action_equal('POST', '#virtualarchive/actions/@0', ('Export', 'mdi:mdi-download', 'CORE', 'virtualArchiveExport', 0, 1, 0))
        self.assert_action_equal('POST', '#virtualarchive/actions/@1', ('Restauration', 'mdi:mdi-check', 'CORE', 'virtualArchiveRestore', 0, 1, 0))

        self.factory.xfer = VirtualArchiveList()
        self.calljson('/CORE/virtualArchiveList', {'GRID_ORDER%virtualarchive': '-name'}, False)
        self.assert_observer('core.custom', 'CORE', 'virtualArchiveList')
        self.assert_count_equal('virtualarchive', 2)
        self.assert_json_equal('', 'virtualarchive/@0/id', join(settings.BACKUP_DIRECTORY, "bbb.lbk"))
        self.assert_json_equal('', 'virtualarchive/@0/name', "bbb")
        self.assert_json_equal('', 'virtualarchive/@0/file_size', 45)
        self.assert_json_equal('', 'virtualarchive/@0/modify_date', "2014-09-19T22:00:00")
        self.assert_json_equal('', 'virtualarchive/@1/id', join(settings.BACKUP_DIRECTORY, "aaa.lbk"))
        self.assert_json_equal('', 'virtualarchive/@1/name', "aaa")
        self.assert_json_equal('', 'virtualarchive/@1/file_size', 67)
        self.assert_json_equal('', 'virtualarchive/@1/modify_date', "2015-06-07T22:00:00")
        self.assert_count_equal('#virtualarchive/actions', 2)

        self.assertEqual(mock_isdir.call_count, 6)
        self.assertEqual(mock_glob.call_count, 4)
        self.assertEqual(mock_isfile.call_count, 10)
        self.assertEqual(mock_getsize.call_count, 8)
        self.assertEqual(mock_getmtime.call_count, 8)

    @patch("os.unlink", return_value=True)
    @patch("os.path.getmtime", side_effect=[1433714400.0, 1411164000.0, 1433714400.0, 1411164000.0])
    @patch("os.path.getsize", side_effect=[67 * 1024 * 1024, 45 * 1024 * 1024, 67 * 1024 * 1024, 45 * 1024 * 1024])
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("glob.iglob", return_value=[join(MY_BACKUP_DIR, "aaa.lbk"), join(MY_BACKUP_DIR, "bbb.lbk")])
    def test_delete(self, mock_glob, mock_isdir, mock_isfile, mock_getsize, mock_getmtime, mock_unlink):
        self.factory.xfer = VirtualArchiveDel()
        self.calljson('/CORE/virtualArchiveDel', {'virtualarchive': join(self.MY_BACKUP_DIR, "aaa.lbk")}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'virtualArchiveDel')
        self.assert_json_equal('', 'type', '2')
        self.assert_json_equal('', 'text', "Voulez-vous supprimer cet enregistrement de 'archive'?")
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('DELETE', self.json_actions[0], ('Oui', 'mdi:mdi-check', 'CORE', 'virtualArchiveDel', 1, 1, 1))
        self.assert_action_equal('POST', self.json_actions[1], ('Non', 'mdi:mdi-cancel'))

        self.factory.xfer = VirtualArchiveDel()
        self.calljson('/CORE/virtualArchiveDel', {'virtualarchive': join(self.MY_BACKUP_DIR, "aaa.lbk"), 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'virtualArchiveDel')

        self.assertEqual(mock_isdir.call_count, 3)
        self.assertEqual(mock_glob.call_count, 2)
        self.assertEqual(mock_isfile.call_count, 4)
        self.assertEqual(mock_getsize.call_count, 4)
        self.assertEqual(mock_getmtime.call_count, 4)
        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_unlink.call_args.args, (join(self.MY_BACKUP_DIR, "aaa.lbk"),))

    @patch("os.rename", return_value=True)
    @patch("os.path.getmtime", side_effect=[1433714400.0, 1411164000.0, 1433714400.0, 1411164000.0])
    @patch("os.path.getsize", side_effect=[67 * 1024 * 1024, 45 * 1024 * 1024, 67 * 1024 * 1024, 45 * 1024 * 1024])
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("glob.iglob", return_value=[join(MY_BACKUP_DIR, "aaa.lbk"), join(MY_BACKUP_DIR, "bbb.lbk")])
    def test_rename(self, mock_glob, mock_isdir, mock_isfile, mock_getsize, mock_getmtime, mock_rename):
        self.factory.xfer = VirtualArchiveRename()
        self.calljson('/CORE/virtualArchiveRename', {'virtualarchive': join(self.MY_BACKUP_DIR, "bbb.lbk")}, False)
        self.assert_observer('core.custom', 'CORE', 'virtualArchiveRename')
        self.assert_json_equal('EDIT', 'new_name', 'bbb')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('POST', self.json_actions[0], ('Ok', 'mdi:mdi-check', 'CORE', 'virtualArchiveRename', 1, 1, 1))
        self.assert_action_equal('POST', self.json_actions[1], ('Annuler', 'mdi:mdi-cancel'))

        self.factory.xfer = VirtualArchiveRename()
        self.calljson('/CORE/virtualArchiveRename', {'virtualarchive': join(self.MY_BACKUP_DIR, "bbb.lbk"), 'new_name': 'ccc', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'virtualArchiveRename')

        self.assertEqual(mock_isdir.call_count, 3)
        self.assertEqual(mock_glob.call_count, 2)
        self.assertEqual(mock_isfile.call_count, 4)
        self.assertEqual(mock_getsize.call_count, 4)
        self.assertEqual(mock_getmtime.call_count, 4)
        self.assertEqual(mock_rename.call_count, 1)
        self.assertEqual(mock_rename.call_args.args, (join(self.MY_BACKUP_DIR, "bbb.lbk"), join(self.MY_BACKUP_DIR, "ccc.lbk")))

    @patch("os.path.getmtime", side_effect=[1433714400.0, 1411164000.0, 1433714400.0, 1411164000.0])
    @patch("os.path.getsize", side_effect=[67 * 1024 * 1024, 45 * 1024 * 1024, 67 * 1024 * 1024, 45 * 1024 * 1024])
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("glob.iglob", return_value=[join(MY_BACKUP_DIR, "aaa.lbk"), join(MY_BACKUP_DIR, "bbb.lbk")])
    def test_download(self, mock_glob, mock_isdir, mock_isfile, mock_getsize, mock_getmtime):
        self.factory.xfer = VirtualArchiveExport()
        self.calljson('/CORE/virtualArchiveExport', {'virtualarchive': join(self.MY_BACKUP_DIR, "bbb.lbk")}, False)
        self.assert_observer('core.custom', 'CORE', 'virtualArchiveExport')
        self.assert_json_equal('LINK', 'filename', 'bbb.lbk')
        self.assert_attrib_equal('filename', 'link', '/CORE/download?filename=L3RtcC9iYWNrdXAvYmJiLmxiaw==&sign=d41d8cd98f00b204e9800998ecf8427e&name=bbb.lbk')
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal('POST', self.json_actions[0], ('Fermer', 'mdi:mdi-close'))

        self.assertEqual(mock_isdir.call_count, 1)
        self.assertEqual(mock_glob.call_count, 1)
        self.assertEqual(mock_isfile.call_count, 2)
        self.assertEqual(mock_getsize.call_count, 2)
        self.assertEqual(mock_getmtime.call_count, 2)

    @patch("builtins.open")
    @patch("os.path.isdir", return_value=True)
    def test_upload(self, mock_isdir, mock_open):
        mock_open.side_effect = [BytesIO(b''), BytesIO(b'')]
        self.factory.xfer = VirtualArchiveImport()
        self.calljson('/CORE/virtualArchiveImport', {}, False)
        self.assert_observer('core.custom', 'CORE', 'virtualArchiveImport')
        self.assert_json_equal('UPLOAD', 'filename', '')
        self.assert_attrib_equal('filename', 'filter', ['.lbk'])
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('POST', self.json_actions[0], ('Ok', 'mdi:mdi-check', 'CORE', 'virtualArchiveImportAct', 1, 1, 1))
        self.assert_action_equal('POST', self.json_actions[1], ('Fermer', 'mdi:mdi-close'))

        file_to_load = BytesIO(b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.' * 100)
        file_to_load.name = 'zzz.lbk'
        self.factory.xfer = VirtualArchiveImportAct()
        self.calljson('/CORE/virtualArchiveImportAct', {'filename': file_to_load, 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'virtualArchiveImportAct')

        self.assertEqual(mock_isdir.call_count, 3)
        self.assertEqual(mock_open.call_args.args, ('/tmp/backup/zzz.lbk', 'wb'))

    @patch("lucterios.framework.model_fields.LucteriosScheduler.add_date", return_value=None)
    @patch("os.path.isdir", return_value=True)
    def test_add(self, mock_isdir, mock_add_date):
        self.factory.xfer = VirtualArchiveAddModify()
        self.calljson('/CORE/virtualArchiveAddModify', {}, False)
        self.assert_observer('core.custom', 'CORE', 'virtualArchiveAddModify')
        self.assert_json_equal('EDIT', 'name', '')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('POST', self.json_actions[0], ('Ok', 'mdi:mdi-check', 'CORE', 'virtualArchiveAddModify', 1, 1, 1))
        self.assert_action_equal('POST', self.json_actions[1], ('Annuler', 'mdi:mdi-cancel'))

        current_date = datetime.now()
        self.factory.xfer = VirtualArchiveAddModify()
        self.calljson('/CORE/virtualArchiveAddModify', {'name': 'uuu', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'virtualArchiveAddModify')

        self.assertEqual(mock_isdir.call_count, 4)
        self.assertEqual(mock_add_date.call_count, 1)
        self.assertEqual(len(mock_add_date.call_args.args), 1)
        self.assertEqual(len(mock_add_date.call_args.kwargs), 2)
        self.assertEqual(mock_add_date.call_args.args[0].__name__, 'create_new_archive')
        self.assertLess(current_date.date() - mock_add_date.call_args.kwargs['datetime'].date(), timedelta(seconds=15))
        self.assertEqual(mock_add_date.call_args.kwargs['new_name'], 'uuu')

    @patch("lucterios.CORE.models.get_date_formating", return_value="Gredi 26 Thermidor 124")
    @patch("builtins.open")
    @patch('lucterios.CORE.models.Popen')
    @patch("os.unlink", return_value=True)
    @patch("os.path.isfile", return_value=True)
    def test_create_archive(self, mock_isfile, mock_unlink, mock_popen, mock_open, mock_formating):
        mock_open.return_value = StringIO('')
        mock_open.return_value.close = lambda: None
        mocked_pipe = Mock()
        attrs = {'wait.return_value': None, 'stdout': BytesIO(b'out of create archive'), 'returncode': 0}
        mocked_pipe.configure_mock(**attrs)
        mock_popen.return_value = mocked_pipe

        VirtualArchive.create_new_archive(new_name='uuu')

        self.assertEqual(mock_isfile.call_count, 1)
        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_open.call_count, 1)
        self.assertEqual(mock_formating.call_count, 2)

        self.assertEqual(mock_popen.call_args.args, (sys.executable + " -m lucterios.install.lucterios_admin archive -n " + self.instance_name + " -f '/tmp/backup/uuu.lbk' -i " + settings.BASE_DIR,))
        self.assertEqual(mock_open.call_args.args, ('%s/tmp/last_backup.log' % join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0]), 'a'))
        self.assertEqual(mock_open.return_value.getvalue(), "Command: " + sys.executable + """ -m lucterios.install.lucterios_admin archive -n """ + self.instance_name + """ -f '/tmp/backup/uuu.lbk' -i """ + settings.BASE_DIR + """
Begin: Gredi 26 Thermidor 124
End: Gredi 26 Thermidor 124
Duration: 0 min 0 sec
Result: OK

out of create archive

""")

    @patch("lucterios.framework.model_fields.LucteriosScheduler.add_date", return_value=None)
    @patch("os.path.getmtime", side_effect=[1433714400.0, 1411164000.0, 1433714400.0, 1411164000.0])
    @patch("os.path.getsize", side_effect=[67 * 1024 * 1024, 45 * 1024 * 1024, 67 * 1024 * 1024, 45 * 1024 * 1024])
    @patch("os.path.isfile", return_value=True)
    @patch("os.path.isdir", return_value=True)
    @patch("glob.iglob", return_value=[join(MY_BACKUP_DIR, "aaa.lbk"), join(MY_BACKUP_DIR, "bbb.lbk")])
    def test_restore(self, mock_glob, mock_isdir, mock_isfile, mock_getsize, mock_getmtime, mock_add_date):
        self.factory.xfer = VirtualArchiveRestore()
        self.calljson('/CORE/virtualArchiveRestore', {'virtualarchive': join(self.MY_BACKUP_DIR, "bbb.lbk")}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'virtualArchiveRestore')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal('POST', self.json_actions[0], ('Oui', 'mdi:mdi-check', 'CORE', 'virtualArchiveRestore', 1, 1, 1))
        self.assert_action_equal('POST', self.json_actions[1], ('Non', 'mdi:mdi-cancel'))

        current_date = datetime.now()
        self.factory.xfer = VirtualArchiveRestore()
        self.calljson('/CORE/virtualArchiveRestore', {'virtualarchive': join(self.MY_BACKUP_DIR, "bbb.lbk"), 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'virtualArchiveRestore')
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal('POST', self.json_actions[0], ('Ok', 'mdi:mdi-check'))

        self.assertEqual(mock_isdir.call_count, 3)
        self.assertEqual(mock_glob.call_count, 2)
        self.assertEqual(mock_isfile.call_count, 4)
        self.assertEqual(mock_getsize.call_count, 4)
        self.assertEqual(mock_getmtime.call_count, 4)

        self.assertEqual(mock_add_date.call_count, 1)
        self.assertEqual(len(mock_add_date.call_args.args), 1)
        self.assertEqual(len(mock_add_date.call_args.kwargs), 2)
        self.assertEqual(mock_add_date.call_args.args[0].__name__, 'restore_old_archive')
        self.assertLess(current_date.date() - mock_add_date.call_args.kwargs['datetime'].date(), timedelta(seconds=15))
        self.assertEqual(mock_add_date.call_args.kwargs['filename'], join(self.MY_BACKUP_DIR, "bbb.lbk"))

    @patch("lucterios.CORE.models.get_date_formating", return_value="Gredi 26 Thermidor 124")
    @patch("builtins.open")
    @patch('lucterios.CORE.models.Popen')
    @patch("os.unlink", return_value=True)
    @patch("os.path.isfile", return_value=True)
    def test_restore_archive(self, mock_isfile, mock_unlink, mock_popen, mock_open, mock_formating):
        mock_open.return_value = StringIO('')
        mock_open.return_value.close = lambda: None
        mocked_pipe1 = Mock()
        mocked_pipe1.configure_mock(**{'wait.return_value': None, 'stdout': BytesIO(b'out of restore archive'), 'returncode': 0})
        mocked_pipe2 = Mock()
        mocked_pipe2.configure_mock(**{'wait.return_value': None, 'stdout': BytesIO(b'out of script'), 'returncode': 1})
        mock_popen.side_effect = [mocked_pipe1, mocked_pipe2]

        VirtualArchive.restore_old_archive(filename=join(self.MY_BACKUP_DIR, "bbb.lbk"))

        self.assertEqual(mock_isfile.call_count, 2)
        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_popen.call_count, 2)
        self.assertEqual(mock_open.call_count, 2)
        self.assertEqual(mock_formating.call_count, 4)

        self.assertEqual(mock_popen.call_args_list, [
            call(sys.executable + " -m lucterios.install.lucterios_admin restore -n " + self.instance_name + " -f '/tmp/backup/bbb.lbk' -i " + settings.BASE_DIR, stdout=-1, stderr=-2, shell=True, executable="/bin/bash"),
            call(sys.executable + " " + settings.BASE_DIR + "/manage_" + self.instance_name + ".py shell < '/tmp/backup/script.py'", stdout=-1, stderr=-2, shell=True, executable="/bin/bash")
        ])
        self.assertEqual(mock_open.call_args_list, [
            call('%s/tmp/last_backup.log' % join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0]), 'a', encoding='utf-8'),
            call('%s/tmp/last_backup.log' % join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0]), 'a', encoding='utf-8')
        ])
        self.assertEqual(mock_open.return_value.getvalue(), "Command: " + sys.executable + """ -m lucterios.install.lucterios_admin restore -n """ + self.instance_name + """ -f '/tmp/backup/bbb.lbk' -i """ + settings.BASE_DIR + """
Begin: Gredi 26 Thermidor 124
End: Gredi 26 Thermidor 124
Duration: 0 min 0 sec
Result: OK

out of restore archive

Command: """ + sys.executable + " " + settings.BASE_DIR + """/manage_""" + self.instance_name + """.py shell < '/tmp/backup/script.py'
Begin: Gredi 26 Thermidor 124
End: Gredi 26 Thermidor 124
Duration: 0 min 0 sec
Result: Failure

out of script

""")

    @patch("lucterios.CORE.models.get_date_formating", return_value="Gredi 26 Thermidor 124")
    @patch("builtins.open")
    @patch('lucterios.CORE.models.Popen')
    @patch("os.unlink", return_value=True)
    @patch("os.path.isfile", side_effect=[True, False])
    def test_restore_archive_noscript(self, mock_isfile, mock_unlink, mock_popen, mock_open, mock_formating):
        mock_open.return_value = StringIO('')
        mock_open.return_value.close = lambda: None
        mocked_pipe1 = Mock()
        mocked_pipe1.configure_mock(**{'wait.return_value': None, 'stdout': BytesIO(b'out of restore archive'), 'returncode': 0})
        mock_popen.side_effect = [mocked_pipe1]

        VirtualArchive.restore_old_archive(filename=join(self.MY_BACKUP_DIR, "bbb.lbk"))

        self.assertEqual(mock_isfile.call_count, 2)
        self.assertEqual(mock_unlink.call_count, 1)
        self.assertEqual(mock_popen.call_count, 1)
        self.assertEqual(mock_open.call_count, 1)
        self.assertEqual(mock_formating.call_count, 2)

        self.assertEqual(mock_popen.call_args_list, [
            call(sys.executable + " -m lucterios.install.lucterios_admin restore -n " + self.instance_name + " -f '/tmp/backup/bbb.lbk' -i " + settings.BASE_DIR, stdout=-1, stderr=-2, shell=True, executable="/bin/bash"),
        ])
        self.assertEqual(mock_open.call_args_list, [
            call('%s/tmp/last_backup.log' % join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0]), 'a', encoding='utf-8'),
        ])
        self.assertEqual(mock_open.return_value.getvalue(), "Command: " + sys.executable + """ -m lucterios.install.lucterios_admin restore -n """ + self.instance_name + """ -f '/tmp/backup/bbb.lbk' -i """ + settings.BASE_DIR + """
Begin: Gredi 26 Thermidor 124
End: Gredi 26 Thermidor 124
Duration: 0 min 0 sec
Result: OK

out of restore archive

""")
