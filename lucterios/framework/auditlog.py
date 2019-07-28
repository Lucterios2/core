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

from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.utils.translation import ugettext_lazy as _
from django.utils import six, timezone

from django.utils.encoding import smart_text
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import DateTimeField, NOT_PROVIDED
from django.db.models.base import Model
from django.conf import settings

from lucterios.framework.tools import get_dico_from_setquery
from lucterios.framework.models import LucteriosLogEntry


def track_field(field):
    """
    Returns whether the given field should be tracked by Auditlog.

    Untracked fields are many-to-many relations and relations to the Auditlog LogEntry model.

    :param field: The field to check.
    :type field: Field
    :return: Whether the given field should be tracked.
    :rtype: bool
    """
    # Do not track many to many relations
    if field.many_to_many:
        return False

    # Do not track relations to LogEntry
    if getattr(field, 'remote_field', None) is not None and field.remote_field.model == LucteriosLogEntry:
        return False

    # 1.8 check
    elif getattr(field, 'rel', None) is not None and field.rel.to == LucteriosLogEntry:
        return False

    return True


def get_fields_in_model(instance):
    """
    Returns the list of fields in the given model instance. Checks whether to use the official _meta API or use the raw
    data. This method excludes many to many fields.

    :param instance: The model instance to get the fields for
    :type instance: Model
    :return: The list of fields for the given model (instance)
    :rtype: list
    """
    assert isinstance(instance, Model)

    # Check if the Django 1.8 _meta API is available
    use_api = hasattr(instance._meta, 'get_fields') and callable(instance._meta.get_fields)

    if use_api:
        return [f for f in instance._meta.get_fields() if track_field(f)]
    return instance._meta.fields


def get_field_value(obj, field):
    """
    Gets the value of a given model instance field.
    :param obj: The model instance.
    :type obj: Model
    :param field: The field you want to find the value of.
    :type field: Any
    :return: The value of the field as a string.
    :rtype: str
    """
    if isinstance(field, DateTimeField):
        # DateTimeFields are timezone-aware, so we need to convert the field
        # to its naive form before we can accuratly compare them for changes.
        try:
            value = field.to_python(getattr(obj, field.name, None))
            if value is not None and settings.USE_TZ and not timezone.is_naive(value):
                value = timezone.make_naive(value, timezone=timezone.utc)
        except ObjectDoesNotExist:
            value = field.default if field.default is not NOT_PROVIDED else None
    else:
        try:
            value = smart_text(getattr(obj, field.name, None))
        except ObjectDoesNotExist:
            value = field.default if field.default is not NOT_PROVIDED else None

    return value


def model_instance_diff(old, new):
    """
    Calculates the differences between two model instances. One of the instances may be ``None`` (i.e., a newly
    created model or deleted model). This will cause all fields with a value to have changed (from ``None``).

    :param old: The old state of the model instance.
    :type old: Model
    :param new: The new state of the model instance.
    :type new: Model
    :return: A dictionary with the names of the changed fields as keys and a two tuple of the old and new field values
             as value.
    :rtype: dict
    """
    from auditlog.registry import auditlog

    if not(old is None or isinstance(old, Model)):
        raise TypeError("The supplied old instance is not a valid model instance.")
    if not(new is None or isinstance(new, Model)):
        raise TypeError("The supplied new instance is not a valid model instance.")

    diff = {}

    if old is not None and new is not None:
        fields = set(old._meta.fields + new._meta.fields)
        model_fields = auditlog.get_model_fields(new._meta.model)
    elif old is not None:
        fields = set(get_fields_in_model(old))
        model_fields = auditlog.get_model_fields(old._meta.model)
    elif new is not None:
        fields = set(get_fields_in_model(new))
        model_fields = auditlog.get_model_fields(new._meta.model)
    else:
        fields = set()
        model_fields = None

    # Check if fields must be filtered
    if model_fields and (model_fields['include_fields'] or model_fields['exclude_fields']) and fields:
        filtered_fields = []
        if model_fields['include_fields']:
            filtered_fields = [field for field in fields
                               if field.name in model_fields['include_fields']]
        else:
            filtered_fields = fields
        if model_fields['exclude_fields']:
            filtered_fields = [field for field in filtered_fields
                               if field.name not in model_fields['exclude_fields']]
        fields = filtered_fields

    for field in fields:
        old_value = get_field_value(old, field)
        new_value = get_field_value(new, field)

        if old_value != new_value:
            diff[field.name] = (smart_text(old_value), smart_text(new_value))

    if len(diff) == 0:
        diff = None

    return diff


def log_create(sender, instance, created, **kwargs):
    if created:
        changes = model_instance_diff(None, instance)

        LucteriosLogEntry.objects.log_create(
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
                LucteriosLogEntry.objects.log_create(
                    instance,
                    action=LucteriosLogEntry.Action.UPDATE,
                    changes=json.dumps(changes),
                )


def log_delete(sender, instance, **kwargs):
    if instance.pk is not None:
        changes = model_instance_diff(instance, None)

        LucteriosLogEntry.objects.log_create(
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
