# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from lucterios.framework.error import LucteriosException, GRAVE, IMPORTANT
from django.utils import six
from django.core.exceptions import ObjectDoesNotExist
import threading
from lucterios.framework.models import LucteriosSession

class Signal(object):

    _SIGNAL_LIST = {}

    _signlock = threading.RLock()

    @classmethod
    def decorate(cls, name):
        def wrapper(item):
            cls._signlock.acquire()
            try:
                if not name in cls._SIGNAL_LIST.keys():
                    cls._SIGNAL_LIST[name] = []
                cls._SIGNAL_LIST[name].append(item)
                return item
            finally:
                cls._signlock.release()
        return wrapper

    @classmethod
    def call_signal(cls, name, *args):
        cls._signlock.acquire()
        try:
            if not name in cls._SIGNAL_LIST.keys():
                raise LucteriosException(GRAVE, _("Unknown signal %s") % name)
            for sign_fct in cls._SIGNAL_LIST[name]:
                sign_fct(*args)
        finally:
            cls._signlock.release()

unlocker_action_class = None # pylint: disable=invalid-name

class RecordLocker(object):

    _lock_list = {}

    _lock = threading.RLock()

    @classmethod
    def clear(cls):
        cls._lock.acquire()
        try:
            cls._lock_list = {}
        finally:
            cls._lock.release()

    @classmethod
    def lock(cls, request, model_item):
        cls._lock.acquire()
        try:
            params = {}
            from django.conf import settings
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if session_key is not None:
                lock_ident = "-".join((six.text_type(model_item.__module__), \
                    six.text_type(model_item.__class__.__name__), six.text_type(model_item.pk)))
                params['LOCK_IDENT'] = lock_ident
                if lock_ident in cls._lock_list.keys():
                    old_session_key = cls._lock_list[lock_ident]
                    try:
                        old_session = LucteriosSession.objects.get(pk=old_session_key) # pylint: disable=no-member
                        raise LucteriosException(IMPORTANT, _("Record locked by '%s'!") % old_session.username)
                    except ObjectDoesNotExist:
                        pass
                cls._lock_list[lock_ident] = session_key
            return params
        finally:
            cls._lock.release()

    @classmethod
    def unlock(cls, request, params):
        cls._lock.acquire()
        try:
            from django.conf import settings
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if (session_key is not None) and ('LOCK_IDENT' in params.keys()):
                lock_ident = params['LOCK_IDENT']
                if (lock_ident in cls._lock_list.keys()) and (cls._lock_list[lock_ident] == session_key):
                    del cls._lock_list[lock_ident]
        finally:
            cls._lock.release()