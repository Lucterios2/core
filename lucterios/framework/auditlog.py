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
import threading
import json

from django.db.models.base import Model
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from lucterios.framework.models import LucteriosLogEntry
from lucterios.framework.auditlog_tools import model_instance_diff, add_m2m_modification


def log_create(sender, instance, created, **kwargs):
    if created:
        changes = model_instance_diff(None, instance)

        instance._last_log = LucteriosLogEntry.objects.log_create(
            instance,
            action=LucteriosLogEntry.Action.CREATE,
            changes=json.dumps(changes),
        )


def log_update(sender, instance, **kwargs):
    if instance.pk is not None:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            new = instance

            changes = model_instance_diff(old, new)

            # Log an entry only if there are changes
            if changes:
                instance._last_log = LucteriosLogEntry.objects.log_create(
                    instance,
                    action=LucteriosLogEntry.Action.UPDATE,
                    changes=json.dumps(changes),
                )


def log_delete(sender, instance, **kwargs):
    if instance.pk is not None:
        changes = model_instance_diff(instance, None)

        instance._last_log = LucteriosLogEntry.objects.log_create(
            instance,
            action=LucteriosLogEntry.Action.DELETE,
            changes=json.dumps(changes),
        )


def lct_log_create(sender, instance, created, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        log_create(sender, instance, created, **kwargs)


def lct_log_update(sender, instance, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        log_update(sender, instance, **kwargs)


def lct_log_delete(sender, instance, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        log_delete(sender, instance, **kwargs)


def lct_log_m2m(sender, instance, action, model, pk_set, **kwargs):
    if LucteriosAuditlogModelRegistry.get_state(instance._meta.app_label):
        if not hasattr(instance, '_last_log'):
            instance._last_log = LucteriosLogEntry.objects.log_create(instance, action=LucteriosLogEntry.Action.UPDATE, changes='{}', additional_data='{}')
        log_action = None
        if action == 'post_remove':
            log_action = six.text_type(_("remove"))
        elif action == 'pre_add':
            log_action = six.text_type(_("add"))
        if log_action is not None:
            if instance._last_log.additional_data is None:
                additional_data = {}
            else:
                additional_data = json.loads(instance._last_log.additional_data)
            add_m2m_modification(sender, instance, model, pk_set, log_action, additional_data)
            instance._last_log.additional_data = json.dumps(additional_data)
            instance._last_log.save()


class LucteriosAuditlogModelRegistry(object):

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

    """
    A registry that keeps track of the models that use Auditlog to track changes.
    """

    def __init__(self):
        self._registry = {}
        self._signals = {}
        self._signals[post_save] = lct_log_create
        self._signals[pre_save] = lct_log_update
        self._signals[m2m_changed] = lct_log_m2m
        self._signals[post_delete] = lct_log_delete

    def register(self, model=None, include_fields=[], exclude_fields=[], mapping_fields={}):
        """
        Register a model with auditlog. Auditlog will then track mutations on this model's instances.

        :param model: The model to register.
        :type model: Model
        :param include_fields: The fields to include. Implicitly excludes all other fields.
        :type include_fields: list
        :param exclude_fields: The fields to exclude. Overrides the fields to include.
        :type exclude_fields: list
        """
        def registrar(cls):
            """Register models for a given class."""
            if not issubclass(cls, Model):
                raise TypeError("Supplied model is not a valid model.")

            self._registry[cls] = {
                'include_fields': include_fields,
                'exclude_fields': exclude_fields,
                'mapping_fields': mapping_fields,
            }
            self._connect_signals(cls)

            # We need to return the class, as the decorator is basically
            # syntactic sugar for:
            # MyClass = auditlog.register(MyClass)
            return cls

        if model is None:
            # If we're being used as a decorator, return a callable with the
            # wrapper.
            return lambda cls: registrar(cls)
        else:
            # Otherwise, just register the model.
            registrar(model)

    def contains(self, model):
        """
        Check if a model is registered with auditlog.

        :param model: The model to check.
        :type model: Model
        :return: Whether the model has been registered.
        :rtype: bool
        """
        return model in self._registry

    def unregister(self, model):
        """
        Unregister a model with auditlog. This will not affect the database.

        :param model: The model to unregister.
        :type model: Model
        """
        try:
            del self._registry[model]
        except KeyError:
            pass
        else:
            self._disconnect_signals(model)

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

    def _disconnect_signals(self, model):
        """
        Disconnect signals for the model.
        """
        for signal, _receiver in self._signals.items():
            signal.disconnect(sender=model, dispatch_uid=self._dispatch_uid(signal, model))

    def _dispatch_uid(self, signal, model):
        """
        Generate a dispatch_uid.
        """
        return (self.__class__, model, signal)

    def get_model_fields(self, model):
        return {
            'include_fields': self._registry[model]['include_fields'],
            'exclude_fields': self._registry[model]['exclude_fields'],
            'mapping_fields': self._registry[model]['mapping_fields'],
        }


auditlog = LucteriosAuditlogModelRegistry()
