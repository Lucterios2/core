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
from os.path import join, exists, dirname, basename
from os import makedirs
from pkgutil import walk_packages
from importlib import import_module
from lucterios.framework.tools import MenuManage, WrapAction
from logging import getLogger
from lucterios.framework.error import LucteriosException


class PluginItem(object):

    def __init__(self, module):
        self.module = module
        self._views = None

    @property
    def name(self):
        return self.module.__name__

    @property
    def title(self):
        return getattr(self.module, "TITLE", self.module.__name__)

    @property
    def version(self):
        return getattr(self.module, "VERSION", '0.0.1')

    @property
    def views(self):
        if self._views is None:
            self._views = []
            try:
                import_module('.views', package=self.module.__name__)
            except Exception:
                getLogger('lucterios.plugin').exception("import of %s", self.module.__name__)
                raise
        return self._views

    def add_view(self, xferview, menu_parent, menu_desc, right_admin):
        if self._views is not None:
            xferview.__module__ = "%s.%s" % (PluginManager.setting_name(), xferview.__module__)
            self._views.append(MenuManage.describ(lambda request: self.permission(right_admin, request), menu_parent=menu_parent, menu_desc=menu_desc)(xferview))

    def permission(self, right_admin, request):
        getLogger('lucterios.plugin').debug("right_admin='%s' request='%s'", right_admin, request)
        if WrapAction.mode_connect_notfree():
            if request.user.is_authenticated:
                if request.user.is_superuser:
                    return True
                elif not right_admin and (request.user.id is not None):
                    plugin_permissions = PluginManager.get_param() if PluginManager.get_param is not None else {}
                    if self.name in plugin_permissions:
                        permsgroups = request.user.groups.filter(id__in=plugin_permissions[self.name])
                        return len(permsgroups) > 0
            return False
        else:
            return True


class PluginManager(object):

    _SINGLETON = None

    get_param = None
    set_param = None

    def __init__(self):
        self._plugin_buffer = None
        if not exists(self.plugins_dir()):
            makedirs(self.plugins_dir())
            with open(join(self.plugins_dir(), '__init__.py'), "w") as file_py:
                file_py.write('\n')

    @classmethod
    def get_instance(cls):
        if cls._SINGLETON is None:
            cls._SINGLETON = cls()
        return cls._SINGLETON

    @classmethod
    def free_instance(cls):
        cls._SINGLETON = None

    @classmethod
    def setting_name(cls):
        from django.conf import settings
        return basename(dirname(settings.SETUP.__file__))

    @classmethod
    def plugins_dir(cls):
        from django.conf import settings
        return join(dirname(settings.SETUP.__file__), 'plugins')

    @classmethod
    def describ(cls, menu_parent=None, right_admin=False, menu_desc=None):
        def wrapper(item):
            plugin = cls.get_instance().find(".".join(item.__module__.split('.')[:-1]))
            if plugin is not None:
                plugin.add_view(item, menu_parent, menu_desc, right_admin)
            return item
        return wrapper

    @property
    def count(self):
        return len(list(self))

    def find(self, name):
        if self.count > 0:
            for item in self:
                if item.name == name:
                    return item
        return None

    def _append_plugin(self, plugin_permission, importer, module_name):
        module_found = importer.find_module(module_name)
        if module_found is not None:
            new_plugin = PluginItem(module_found.load_module(module_name))
            if new_plugin.name not in plugin_permission:
                plugin_permission[new_plugin.name] = []
            self._plugin_buffer.append(new_plugin)

    def _reload(self):
        try:
            plugin_permission = self.get_param() if self.get_param is not None else {}
        except LucteriosException:
            plugin_permission = {}
        self._plugin_buffer = []
        for importer, module_name, is_pkg in walk_packages(path=[self.plugins_dir()]):
            if is_pkg:
                self._append_plugin(plugin_permission, importer, module_name)
        self._plugin_buffer.sort(key=lambda item: item.name)
        if (plugin_permission is not None) and (self.set_param is not None):
            try:
                self.set_param({permitem[0]: permitem[1] for permitem in plugin_permission.items() if self.find(permitem[0]) is not None})
            except LucteriosException:
                plugin_permission = {}

    def __iter__(self):
        if self._plugin_buffer is None:
            self._reload()
        for plugin_item in self._plugin_buffer:
            yield plugin_item

    def __getitem__(self, index):
        if (index >= 0) and (self.count > index):
            return self._plugin_buffer[index]
        else:
            return None
