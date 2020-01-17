# -*- coding: utf-8 -*-
'''
Unit test class for connection and login in Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2020 sd-libre.fr
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
from os.path import join, isdir, isfile
from os import makedirs
from shutil import rmtree

from lucterios.framework.test import LucteriosTest
from lucterios.framework.plugins import PluginManager
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser
from lucterios.CORE.models import LucteriosUser, LucteriosGroup
from lucterios.CORE.parameters import Params
from lucterios.CORE.views_usergroup import GroupsEdit


class PluginTest(LucteriosTest):

    def _del_plugin_dir(self):
        rmtree(PluginManager.plugins_dir(), True)

    def setUp(self):
        LucteriosTest.setUp(self)
        self._del_plugin_dir()
        PluginManager.free_instance()
        self.plugins = PluginManager.get_instance()

    def tearDown(self):
        self._del_plugin_dir()
        self.plugins = None
        PluginManager.free_instance()
        LucteriosTest.tearDown(self)

    def _add_plugin(self, name, add_view=False, **args):
        print("PluginManager", PluginManager.plugins_dir(), PluginManager.setting_name())
        new_plugins_dir = join(PluginManager.plugins_dir(), name)
        makedirs(new_plugins_dir)
        with open(join(new_plugins_dir, '__init__.py'), "w") as file_py:
            file_py.write('# -*- coding: utf8 -*-\n')
            for key, val in args.items():
                file_py.write('\n')
                file_py.write('%s = "%s"\n' % (key.upper(), val))
        if add_view:
            with open(join(new_plugins_dir, 'views.py'), "w") as file_py:
                file_py.write('# -*- coding: utf8 -*-\n')
                file_py.write('\n')
                file_py.write('from django.utils.translation import ugettext_lazy as _\n')
                file_py.write('from lucterios.framework.plugins import PluginManager\n')
                file_py.write('from lucterios.framework.xfergraphic import XferContainerCustom\n')
                file_py.write('\n')
                file_py.write('\n')
                file_py.write('@PluginManager.describ(menu_parent="core.plugins", right_admin=True, menu_desc="Administration")\n')
                file_py.write('class Admin(XferContainerCustom):\n')
                file_py.write('    caption = _("Admin")\n')
                file_py.write('    icon = "images/config.png"\n')
                file_py.write('\n')
                file_py.write('\n')
                file_py.write('@PluginManager.describ(menu_parent="core.general", menu_desc="Visu")\n')
                file_py.write('class Show(XferContainerCustom):\n')
                file_py.write('    caption = _("Show")\n')
                file_py.write('    icon = "images/edit.png"\n')
                file_py.write('\n')
                file_py.write('\n')
                file_py.write('@PluginManager.describ(right_admin=True)\n')
                file_py.write('class Config(XferContainerCustom):\n')
                file_py.write('    caption = _("Config")\n')
                file_py.write('    icon = "images/config_ex.png"\n')
                file_py.write('\n')

    def testEmpty(self):
        self.assertTrue(isdir(self.plugins.plugins_dir()))
        self.assertTrue(isfile(join(self.plugins.plugins_dir(), '__init__.py')))
        self.assertEqual(self.plugins.count, 0)
        self.assertEqual(list(self.plugins), [])
        self.assertEqual(Params.getobject("CORE-PluginPermission"), {})

    def testBasicPlugin(self):
        self._add_plugin('basic')
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(self.plugins[0].name, 'basic')
        self.assertEqual(self.plugins[0].title, 'basic')
        self.assertEqual(self.plugins[0].version, '0.0.1')
        self.assertEqual(Params.getobject("CORE-PluginPermission"), {"basic": []})

    def testAdvancePlugin(self):
        Params.setvalue("CORE-PluginPermission", '{"basic": []}')
        self._add_plugin('advance', title='Advance tool', version='1.2.3')
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(self.plugins[0].name, 'advance')
        self.assertEqual(self.plugins[0].title, 'Advance tool')
        self.assertEqual(self.plugins[0].version, '1.2.3')
        self.assertEqual(Params.getobject("CORE-PluginPermission"), {"advance": []})

    def testViewPlugin(self):
        self._add_plugin('view', add_view=True)
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(self.plugins[0].name, 'view')
        self.assertEqual(len(self.plugins[0].views), 3)
        self.assertEqual(self.plugins[0].views[0].url_text, '%s.view/admin' % PluginManager.setting_name())
        self.assertEqual(self.plugins[0].views[1].url_text, '%s.view/show' % PluginManager.setting_name())
        self.assertEqual(self.plugins[0].views[2].url_text, '%s.view/config' % PluginManager.setting_name())

    def set_mode(self, mode):
        Params.setvalue('CORE-connectmode', mode)

    def testPermissionPlugin_free(self):
        self.set_mode(2)
        self._add_plugin('free', add_view=True)

        request = RequestFactory().post('/')
        request.user = AnonymousUser()
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(len(self.plugins[0].views), 3)
        self.assertTrue(self.plugins[0].views[0].get_action().check_permission(request))
        self.assertTrue(self.plugins[0].views[1].get_action().check_permission(request))
        self.assertTrue(self.plugins[0].views[2].get_action().check_permission(request))

    def testPermissionPlugin_anonymoous(self):
        self.set_mode(1)
        self._add_plugin('anonymoous', add_view=True)

        request = RequestFactory().post('/')
        request.user = AnonymousUser()
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(len(self.plugins[0].views), 3)
        self.assertFalse(self.plugins[0].views[0].get_action().check_permission(request))
        self.assertFalse(self.plugins[0].views[1].get_action().check_permission(request))
        self.assertFalse(self.plugins[0].views[2].get_action().check_permission(request))

    def testPermissionPlugin_logon_admin(self):
        self.set_mode(0)
        self._add_plugin('admin', add_view=True)

        request = RequestFactory().post('/')
        request.user = LucteriosUser()
        request.user.is_superuser = True
        request.user.is_staff = True
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(len(self.plugins[0].views), 3)
        self.assertTrue(self.plugins[0].views[0].get_action().check_permission(request))
        self.assertTrue(self.plugins[0].views[1].get_action().check_permission(request))
        self.assertTrue(self.plugins[0].views[2].get_action().check_permission(request))

    def testPermissionPlugin_logon_usersimple(self):
        self.set_mode(0)
        self._add_plugin('usersimple', add_view=True)

        request = RequestFactory().post('/')
        request.user = LucteriosUser()
        request.user.is_superuser = False
        request.user.is_staff = False
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(len(self.plugins[0].views), 3)
        self.assertFalse(self.plugins[0].views[0].get_action().check_permission(request))
        self.assertFalse(self.plugins[0].views[1].get_action().check_permission(request))
        self.assertFalse(self.plugins[0].views[2].get_action().check_permission(request))

    def testPermissionPlugin_logon_useraccess(self):
        group = LucteriosGroup.objects.create(name="plugin")
        Params.setvalue("CORE-PluginPermission", '{"useraccess": [%d]}' % group.id)
        self.set_mode(0)
        self._add_plugin('useraccess', add_view=True)

        request = RequestFactory().post('/')
        request.user = LucteriosUser.objects.create(username="user", is_superuser=False, is_staff=False)
        self.assertEqual(self.plugins.count, 1)
        self.assertEqual(len(self.plugins[0].views), 3)
        self.assertFalse(self.plugins[0].views[0].get_action().check_permission(request))
        self.assertFalse(self.plugins[0].views[1].get_action().check_permission(request))
        self.assertFalse(self.plugins[0].views[2].get_action().check_permission(request))

        request.user.groups.set(LucteriosGroup.objects.filter(id=group.id))
        request.user.save()
        self.assertFalse(self.plugins[0].views[0].get_action().check_permission(request))
        self.assertTrue(self.plugins[0].views[1].get_action().check_permission(request))
        self.assertFalse(self.plugins[0].views[2].get_action().check_permission(request))

    def test_groupedit(self):
        group = LucteriosGroup.objects.create(name="plugin")
        Params.setvalue("CORE-PluginPermission", '{"useraccess": [%d]}' % group.id)
        self._add_plugin('useraccess', add_view=True)
        self._add_plugin('view', add_view=True)
        self._add_plugin('advance', title='Advance tool', version='1.2.3')

        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'group': group.id}, False)
        self.assert_observer('core.custom', 'CORE', 'groupsEdit')
        self.assert_count_equal('', 4)
        self.assert_json_equal('EDIT', "name", 'plugin',)
        self.assert_json_equal('CHECKLIST', "permissions", [])
        self.assert_select_equal("plugins", {'advance': 'Advance tool', 'useraccess': 'useraccess', 'view': 'view'}, True)
        self.assert_json_equal('CHECKLIST', "plugins", ['useraccess'])

        self.factory.xfer = GroupsEdit()
        self.calljson('/CORE/groupsEdit', {'SAVE': 'YES', 'group': group.id, 'name': 'plugin', "plugins": 'advance;view'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'groupsEdit')
        self.assertEqual(Params.getobject("CORE-PluginPermission"), {"advance": [group.id], 'useraccess': [], 'view': [group.id]})

    def test_connect(self):
        self._add_plugin('view', add_view=True)
        self._add_plugin('advance', title='Advance tool', version='1.2.3')
        self.calljson('/CORE/authentification', {'username': 'admin', 'password': 'admin'})
        self.assert_observer('core.auth', 'CORE', 'authentification')
        self.assert_json_equal('', '', 'OK')
        self.assertEqual(len(self.response_json['connexion']['INFO_SERVER']), 3 + 3 + 2)
        self.assertEqual(self.response_json['connexion']['INFO_SERVER'][4], "Advance tool=1.2.3")
        self.assertEqual(self.response_json['connexion']['INFO_SERVER'][5], "view=0.0.1")
