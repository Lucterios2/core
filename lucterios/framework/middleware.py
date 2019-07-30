# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
'''
Django middleware for Lucterios

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
import time

from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import curry
from django.db.models.signals import pre_save
from django.conf import settings
from django.apps import apps

from lucterios.framework.xferbasic import XferContainerException
from lucterios.framework.error import LucteriosRedirectException
from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_YES
from lucterios.framework.models import LucteriosLogEntry
from django.utils import six


class LucteriosErrorMiddleware(XferContainerException):

    def __init__(self, get_response):
        self.get_origin_response = get_response
        XferContainerException.__init__(self)

    def __call__(self, request):
        response = self.get_origin_response(request)
        return response

    def process_exception(self, request, exception):
        self.request = request
        self.set_except(exception)
        self.closeaction = None
        if isinstance(exception, LucteriosRedirectException) and (exception.redirectclassview is not None):
            redirectaction = exception.redirectclassview.get_action()
            if self.check_action_permission(redirectaction):
                self.closeaction = (redirectaction, FORMTYPE_MODAL, CLOSE_YES, None)
        self.responsejson = {}
        self._initialize(request)
        self.fillresponse()
        self._finalize()
        return self.get_response()


threadlocal = threading.local()


def is_authenticated(user):
    """Return whether or not a User is authenticated.

    Function provides compatibility following deprecation of method call to
    `is_authenticated()` in Django 2.0.

    This is *only* required to support Django < v1.10 (i.e. v1.9 and earlier),
    as `is_authenticated` was introduced as a property in v1.10.s
    """
    if not hasattr(user, 'is_authenticated'):
        return False
    if callable(user.is_authenticated):
        # Will be callable if django.version < 2.0, but is only necessary in
        # v1.9 and earlier due to change introduced in v1.10 making
        # `is_authenticated` a property instead of a callable.
        return user.is_authenticated()
    else:
        return user.is_authenticated


class AuditlogMiddleware(MiddlewareMixin):
    """
    Middleware to couple the request's user to log items. This is accomplished by currying the signal receiver with the
    user from the request (or None if the user is not authenticated).
    """

    def process_request(self, request):
        """
        Gets the current user from the request and prepares and connects a signal receiver with the user already
        attached to it.
        """
        # Initialize thread local storage
        threadlocal.auditlog = {
            'signal_duid': (self.__class__, time.time()),
            'remote_addr': request.META.get('REMOTE_ADDR'),
        }

        # In case of proxy, set 'original' address
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            threadlocal.auditlog['remote_addr'] = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]

        # Connect signal for automatic logging
        if hasattr(request, 'user') and is_authenticated(request.user):
            set_actor = curry(self.set_actor, user=request.user, signal_duid=threadlocal.auditlog['signal_duid'])
            pre_save.connect(set_actor, sender=LucteriosLogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'], weak=False)

    def process_response(self, request, response):
        """
        Disconnects the signal receiver to prevent it from staying active.
        """
        if hasattr(threadlocal, 'auditlog'):
            pre_save.disconnect(sender=LucteriosLogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'])

        return response

    def process_exception(self, request, exception):
        """
        Disconnects the signal receiver to prevent it from staying active in case of an exception.
        """
        if hasattr(threadlocal, 'auditlog'):
            pre_save.disconnect(sender=LucteriosLogEntry, dispatch_uid=threadlocal.auditlog['signal_duid'])

        return None

    @staticmethod
    def set_actor(user, sender, instance, signal_duid, **kwargs):
        """
        Signal receiver with an extra, required 'user' kwarg. This method becomes a real (valid) signal receiver when
        it is curried with the actor.
        """
        if hasattr(threadlocal, 'auditlog'):
            if signal_duid != threadlocal.auditlog['signal_duid']:
                return
            try:
                app_label, model_name = settings.AUTH_USER_MODEL.split('.')
                auth_user_model = apps.get_model(app_label, model_name)
            except ValueError:
                auth_user_model = apps.get_model('auth', 'user')
            if sender == LucteriosLogEntry and isinstance(user, auth_user_model) and instance.username is None:
                instance.username = six.text_type(user)

            instance.remote_addr = threadlocal.auditlog['remote_addr']
