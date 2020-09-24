# -*- coding: utf-8 -*-
'''
Tools to manage Lucterios parameters

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
from json import dumps
import threading

from django.utils.translation import ugettext_lazy
from django.core.exceptions import ObjectDoesNotExist

from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework import tools, signal_and_lock
from lucterios.framework.plugins import PluginManager

from lucterios.CORE.models import Parameter


class Params(object):

    _PARAM_CACHE_LIST = {}

    _paramlock = threading.RLock()

    @classmethod
    def clear(cls):
        cls._paramlock.acquire()
        try:
            cls._PARAM_CACHE_LIST.clear()
        finally:
            cls._paramlock.release()

    @classmethod
    def _get(cls, name):
        if name not in cls._PARAM_CACHE_LIST.keys():
            try:
                cls._PARAM_CACHE_LIST[name] = Parameter.objects.get(name=name)
            except ObjectDoesNotExist:
                raise LucteriosException(GRAVE, "Parameter %s unknown!" % name)
            except Exception:
                raise LucteriosException(GRAVE, "Parameter %s not found!" % name)
        return cls._PARAM_CACHE_LIST[name]

    @classmethod
    def getvalue(cls, name):
        cls._paramlock.acquire()
        try:
            return cls._get(name).get_value_typed()
        finally:
            cls._paramlock.release()

    @classmethod
    def setvalue(cls, name, value):
        Parameter.change_value(name, value)
        cls.clear()

    @classmethod
    def getobject(cls, name):
        cls._paramlock.acquire()
        try:
            return cls._get(name).get_value_object()
        finally:
            cls._paramlock.release()

    @classmethod
    def gettext(cls, name):
        cls._paramlock.acquire()
        try:
            return str(cls._get(name).get_value_text())
        finally:
            cls._paramlock.release()

    @classmethod
    def fill(cls, xfer, names, col, row, readonly=True, nb_col=1):
        cls._paramlock.acquire()
        try:
            coloffset = 0
            titles = {}
            signal_and_lock.Signal.call_signal('get_param_titles', names, titles)
            param_cmp = None
            for name in names:
                param = cls._get(name)
                if param is not None:
                    if readonly:
                        param_cmp = param.get_read_comp()
                    else:
                        param_cmp = param.get_write_comp()
                    param_cmp.set_location(col + coloffset, row, 1, 1)
                    if param.name in titles:
                        param_cmp.description = titles[param.name]
                    else:
                        param_cmp.description = ugettext_lazy(param.name)
                    xfer.add_component(param_cmp)
                    coloffset += 1
                    if coloffset == nb_col:
                        coloffset = 0
                        row += 1
            if (param_cmp is not None) and (coloffset != 0):
                param_cmp.colspan = nb_col - coloffset + 1
        finally:
            cls._paramlock.release()


def notfree_mode_connect(*args):
    mode_connection = Params.getvalue("CORE-connectmode")
    return mode_connection != 2


def secure_mode_connect():
    mode_connection = Params.getvalue("CORE-connectmode")
    return mode_connection == 0


def get_param_plugin():
    try:
        return Params.getobject("CORE-PluginPermission")
    except Exception:
        return {}


def set_param_plugin(value):
    try:
        Params.setvalue("CORE-PluginPermission", dumps(value))
    except Exception:
        pass


tools.WrapAction.mode_connect_notfree = notfree_mode_connect
PluginManager.get_param = lambda *_args: get_param_plugin()
PluginManager.set_param = lambda *args: set_param_plugin(args[-1])
