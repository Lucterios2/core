# -*- coding: utf-8 -*-
'''
Tools to manage signal and lock in Lucterios

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
import threading
import logging

from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django.core.exceptions import ObjectDoesNotExist

from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.models import LucteriosSession
from importlib import import_module


class Signal(object):

    _SIGNAL_LIST = {}

    _signlock = threading.RLock()

    @classmethod
    def decorate(cls, name):
        def wrapper(item):
            logging.getLogger("lucterios.core.signal").debug(">> decorate %s", name)
            cls._signlock.acquire()
            try:
                if name not in cls._SIGNAL_LIST.keys():
                    cls._SIGNAL_LIST[name] = []
                cls._SIGNAL_LIST[name].append(item)
                return item
            finally:
                cls._signlock.release()
                logging.getLogger("lucterios.core.signal").debug("<< decorate %s", name)
        return wrapper

    @classmethod
    def call_signal(cls, name, *args):
        nb_call = 0
        logging.getLogger("lucterios.core.signal").debug(">> call_signal %s", name)
        cls._signlock.acquire()
        try:
            if name in cls._SIGNAL_LIST.keys():
                for sign_fct in cls._SIGNAL_LIST[name]:
                    if sign_fct(*args):
                        nb_call += 1
        finally:
            cls._signlock.release()
        logging.getLogger("lucterios.core.signal").debug("<< call_signal %s", name)
        return nb_call

    @classmethod
    def get_packages_of_signal(cls, name):
        packages = {}
        logging.getLogger("lucterios.core.signal").debug(">> call_signal %s", name)
        cls._signlock.acquire()
        try:
            if name in cls._SIGNAL_LIST.keys():
                for sign_fct in cls._SIGNAL_LIST[name]:
                    new_package = sign_fct.__module__.split('.')[:-1]
                    appmodule = import_module('.'.join(new_package))
                    if hasattr(appmodule, '__title__'):
                        try:
                            app_title = appmodule.__title__()
                        except TypeError:
                            app_title = six.text_type(appmodule.__title__)
                    else:
                        app_title = six.text_type(appmodule)
                    packages[new_package[-1]] = app_title
        finally:
            cls._signlock.release()
        logging.getLogger("lucterios.core.signal").debug("<< call_signal %s", name)
        return packages


unlocker_view_class = None


class RecordLocker(object):

    _lock_list = {}

    _lock = threading.RLock()

    @classmethod
    def clear(cls):
        logging.getLogger("lucterios.core.record").debug(">> clear")
        cls._lock.acquire()
        try:
            cls._lock_list = {}
        finally:
            cls._lock.release()
        logging.getLogger("lucterios.core.record").debug("<< clear")

    @classmethod
    def lock(cls, request, model_item):
        logging.getLogger("lucterios.core.record").debug(">> lock [%s] %s", request.user, model_item)
        cls._lock.acquire()
        try:
            params = {}
            from django.conf import settings
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if session_key is not None:
                lock_ident = "-".join((six.text_type(model_item.__module__),
                                       six.text_type(model_item.__class__.__name__), six.text_type(model_item.pk)))
                params['LOCK_IDENT'] = lock_ident
                if lock_ident in cls._lock_list.keys():
                    old_session_key = cls._lock_list[lock_ident]
                    if old_session_key != session_key:
                        try:
                            old_session = LucteriosSession.objects.get(pk=old_session_key)
                            if old_session.get_is_active():
                                raise LucteriosException(IMPORTANT, _("Record locked by '%s'!") % old_session.username)
                            else:
                                del cls._lock_list[lock_ident]
                                old_session.flush()
                        except ObjectDoesNotExist:
                            pass
                cls._lock_list[lock_ident] = session_key
            return params
        finally:
            cls._lock.release()
            logging.getLogger("lucterios.core.record").debug("<< lock [%s] %s %s", request.user, model_item, session_key)

    @classmethod
    def is_lock(cls, model_item):
        logging.getLogger("lucterios.core.record").debug(">> is_lock %s", model_item)
        cls._lock.acquire()
        try:
            lock_ident = "-".join((six.text_type(model_item.__module__),
                                   six.text_type(model_item.__class__.__name__), six.text_type(model_item.pk)))
            return lock_ident in cls._lock_list.keys()
        finally:
            cls._lock.release()
            logging.getLogger("lucterios.core.record").debug("<< is_lock %s", model_item)

    @classmethod
    def has_item_lock(cls, model_class):
        logging.getLogger("lucterios.core.record").debug(">> has_item_lock %s", model_class)
        cls._lock.acquire()
        try:
            lock_root = "-".join((six.text_type(model_class.__module__), six.text_type(model_class.__name__)))
            for lock_ident in cls._lock_list.keys():
                if lock_ident.startswith(lock_root):
                    return True
            return False
        finally:
            cls._lock.release()
            logging.getLogger("lucterios.core.record").debug("<< has_item_lock %s", model_class)

    @classmethod
    def unlock(cls, request, params=None):
        logging.getLogger("lucterios.core.record").debug(">> unlock [%s] %s", request.user, params)
        cls._lock.acquire()
        try:
            from django.conf import settings
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if (session_key is not None) and (params is None):
                lock_ident_list = list(cls._lock_list.keys())
                for lock_ident in lock_ident_list:
                    if (lock_ident in cls._lock_list) and (cls._lock_list[lock_ident] == session_key):
                        del cls._lock_list[lock_ident]
            elif (session_key is not None) and ('LOCK_IDENT' in params.keys()):
                lock_ident = params['LOCK_IDENT']
                if (lock_ident in cls._lock_list.keys()) and (cls._lock_list[lock_ident] == session_key):
                    del cls._lock_list[lock_ident]
        finally:
            cls._lock.release()
            logging.getLogger("lucterios.core.record").debug(">> unlock [%s]", request.user)
