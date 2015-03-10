# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from lucterios.framework.error import LucteriosException, GRAVE, IMPORTANT
from django.utils import six
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

_SIGNAL_LIST = {}

def signal(name):
    def wrapper(item):
        if not name in _SIGNAL_LIST.keys():
            _SIGNAL_LIST[name] = []
        _SIGNAL_LIST[name].append(item)
        return item
    return wrapper

def call_signal(name, *args):
    if not name in _SIGNAL_LIST.keys():
        raise LucteriosException(GRAVE, _("Unknown signal %s") % name)
    for sign_fct in _SIGNAL_LIST[name]:
        sign_fct(*args)

unlocker_action_class = None # pylint: disable=invalid-name

class RecordLocker(object):

    _lock_list = {}

    @classmethod
    def clear(cls):
        cls._lock_list = {}

    @classmethod
    def lock(cls, request, model_item):
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
                    old_session = Session.objects.get(pk=old_session_key) # pylint: disable=no-member
                    user_id = old_session.get_decoded().get('_auth_user_id', None)
                    if user_id is None:
                        user_name = _("Anonymous user")
                    else:
                        user_name = User.objects.get(id=user_id).username  # pylint: disable=no-member
                    raise LucteriosException(IMPORTANT, _("Record locked by '%s'!") % user_name)
                except ObjectDoesNotExist:
                    pass
            cls._lock_list[lock_ident] = session_key
        return params

    @classmethod
    def unlock(cls, request, params):
        from django.conf import settings
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        if (session_key is not None) and ('LOCK_IDENT' in params.keys()):
            lock_ident = params['LOCK_IDENT']
            if (lock_ident in cls._lock_list.keys()) and (cls._lock_list[lock_ident] == session_key):
                del cls._lock_list[lock_ident]
