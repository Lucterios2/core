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
from logging import getLogger

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields import DateTimeField, NOT_PROVIDED
from django.db.models.base import Model
from django.utils.encoding import smart_text
from django.utils import six, timezone
from django.conf import settings


def track_field(field):
    """
    Returns whether the given field should be tracked by Auditlog.

    Untracked fields are many-to-many relations and relations to the Auditlog LogEntry model.

    :param field: The field to check.
    :type field: Field
    :return: Whether the given field should be tracked.
    :rtype: bool
    """
    from lucterios.framework.models import LucteriosLogEntry

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
    try:
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
    except Exception as err:
        getLogger('lucterios.framwork').error("auditlog:get_field_value(%s,%s) : %s", obj, field.name, err)
        raise
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
    from lucterios.framework.auditlog import auditlog

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
    else:
        for field in fields:
            if (field.name in model_fields['mapping_fields']) and (field.name not in diff.keys()):
                diff[field.name] = (smart_text(get_field_value(old, field)), smart_text(get_field_value(new, field)))

    return diff


def get_sender_ident_for_m2m(sender, instance):
    from lucterios.framework.auditlog import LucteriosAuditlogModelRegistry
    sender_ident = six.text_type(sender)
    attrname = six.text_type(instance._meta.verbose_name),
    for m2m_property in LucteriosAuditlogModelRegistry.get_m2m_property(instance.__class__):
        if m2m_property.through == sender:
            sender_ident = six.text_type(m2m_property.field.verbose_name)
            attrname = m2m_property.field.name
    return sender_ident, attrname
