# -*- coding: utf-8 -*-
'''
Abstract and proxy model for Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2019 sd-libre.fr
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

from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from auditlog.registry import AuditlogModelRegistry
from auditlog.models import LogEntry

from lucterios.framework.tools import get_dico_from_setquery
import threading


def lct_log_create(sender, instance, created, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        from auditlog.receivers import log_create
        log_create(sender, instance, created, **kwargs)


def lct_log_update(sender, instance, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        from auditlog.receivers import log_update
        log_update(sender, instance, **kwargs)


def lct_log_delete(sender, instance, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        from auditlog.receivers import log_delete
        log_delete(sender, instance, **kwargs)


def lct_log_m2m(sender, instance, action, model, pk_set, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        import json
        if not hasattr(instance, '_last_log'):
            instance._last_log = LogEntry.objects.log_create(instance, action=LogEntry.Action.UPDATE, changes='{}', additional_data='{}')
        log_action = None
        if action == 'post_remove':
            log_action = six.text_type(_("remove"))
        elif action == 'pre_add':
            log_action = six.text_type(_("add"))
        if log_action is not None:
            additional_data = json.loads(instance._last_log.additional_data)
            sender_ident = six.text_type(sender)
            for m2m_property in LucteriosAuditlogModelRegistry.get_m2m_property(instance.__class__):
                if m2m_property.through == sender:
                    sender_ident = six.text_type(m2m_property.field.verbose_name)
            if sender_ident not in additional_data:
                additional_data[sender_ident] = {}
            if log_action not in additional_data[sender_ident]:
                additional_data[sender_ident][log_action] = []
            additional_data[sender_ident][log_action].extend(get_dico_from_setquery(model.objects.filter(pk__in=pk_set)).values())
            instance._last_log.additional_data = json.dumps(additional_data)
            instance._last_log.save()


class LucteriosAuditlogModelRegistry(AuditlogModelRegistry):

    _main_state = False
    _state_packages = []
    _statelock = threading.RLock()

    @classmethod
    def main_disabled(cls):
        cls._statelock.acquire()
        try:
            cls._main_state = False
        finally:
            cls._statelock.release()

    @classmethod
    def main_enabled(cls):
        cls._statelock.acquire()
        try:
            cls._main_state = True
        finally:
            cls._statelock.release()

    @classmethod
    def set_state_packages(cls, state_packages):
        cls._statelock.acquire()
        try:
            cls._state_packages = state_packages
        finally:
            cls._statelock.release()

    @classmethod
    def get_state(cls, package_name):
        cls._statelock.acquire()
        try:
            return cls._main_state and (package_name in cls._state_packages)
        finally:
            cls._statelock.release()

    @classmethod
    def get_m2m_property(cls, model):
        res = []
        for m2m_field in model._meta.get_fields():
            if hasattr(model, m2m_field.name):
                m2m_property = getattr(model, m2m_field.name)
                if hasattr(m2m_property, 'through'):
                    res.append(m2m_property)
        return res

    def _connect_signals(self, model):
        """
        Connect signals for the model.
        """
        for signal in self._signals:
            receiver = self._signals[signal]
            if signal == m2m_changed:
                for m2m_property in self.get_m2m_property(model):
                    m2m_model = m2m_property.through
                    signal.connect(receiver, sender=m2m_model, dispatch_uid=self._dispatch_uid(signal, m2m_model))
            else:
                signal.connect(receiver, sender=model, dispatch_uid=self._dispatch_uid(signal, model))


def audit_log():
    from auditlog import registry
    if m2m_changed not in registry.auditlog._signals:
        registry.auditlog = LucteriosAuditlogModelRegistry(custom={post_save: lct_log_create,
                                                                   pre_save: lct_log_update,
                                                                   post_delete: lct_log_delete,
                                                                   m2m_changed: lct_log_m2m})
    return registry.auditlog
