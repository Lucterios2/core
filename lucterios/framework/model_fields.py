# -*- coding: utf-8 -*-
'''
Abstract and proxy model for Lucterios

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
import logging
from datetime import datetime
from types import FunctionType

from django.db import models
from django.db.models import Transform
from django.db.models.lookups import RegisterLookupMixin
from django.db.models.signals import pre_save
from django.core.exceptions import ImproperlyConfigured
from django.utils import formats
from django.utils.translation import ugettext_lazy as _

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import ConflictingIdError


class AbsoluteValue(Transform):
    lookup_name = 'abs'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "ABS(%s)" % lhs, params


RegisterLookupMixin.register_lookup(AbsoluteValue)


def get_value_if_choices(value, dep_field):
    if hasattr(dep_field, 'choices') and (dep_field.choices is not None) and (len(dep_field.choices) > 0):
        for choices_key, choices_value in dep_field.choices:
            if choices_key == int(value):
                value = str(choices_value)
                break
    elif hasattr(dep_field, 'decimal_places'):
        format_txt = "%%.%df" % dep_field.decimal_places
        value = format_txt % float(value)
    return value


def is_simple_field(dep_field):
    from django.db.models.fields.related import ForeignKey
    return (not dep_field.auto_created or dep_field.concrete) and not (dep_field.is_relation and dep_field.many_to_many) and not isinstance(dep_field, ForeignKey)


def get_obj_contains(new_item):
    field_val = []
    for key, val in new_item.__dict__.items():
        if (key != 'id') and (key[0] != '_'):
            field_val.append("%s=%s" % (key, str(val).replace('{[br/]}', "\n").strip().replace("\n", '<br/>')))
    return field_val


def get_subfield_show(initial_fields, subtable):
    fields = []
    for item in initial_fields:
        if isinstance(item, str):
            fields.append("%s.%s" % (subtable, item))
        if isinstance(item, tuple):
            colres = []
            for colitem in item:
                if isinstance(colitem, tuple):
                    colitem = (colitem[0], "%s.%s" % (subtable, colitem[1]))
                else:
                    colitem = "%s.%s" % (subtable, colitem)
                colres.append(colitem)
            fields.append(tuple(colres))
    return fields


def generic_format_string(self):
    if hasattr(self, '_format_string'):
        if isinstance(self._format_string, str):
            return self._format_string
        elif isinstance(self._format_string, FunctionType):
            return self._format_string()
        elif hasattr(self, 'decimal_places'):
            return "N%d" % self.decimal_places
    return None


class LucteriosDecimalField(models.DecimalField):

    def __init__(self, verbose_name=None, name=None, format_string=None, **kwargs):
        models.DecimalField.__init__(self, verbose_name, name, **kwargs)
        self._format_string = format_string

    @property
    def format_string(self):
        return generic_format_string(self)


class LucteriosVirtualField(models.Field):

    virtual_disabled = False

    def __init__(self, compute_from=None, format_string=None, *args, **kwargs):
        kwargs['editable'] = False
        if compute_from is None:
            raise ImproperlyConfigured('%s requires setting compute_from' % self.__class__)
        super(LucteriosVirtualField, self).__init__(*args, **kwargs)
        self.compute_from = compute_from
        self._format_string = format_string

    @property
    def format_string(self):
        return generic_format_string(self)

    def get_attname_column(self):
        return self.get_attname(), None

    class ObjectProxy(object):
        def __init__(self, field):
            self.field = field

        def __get__(self, instance, cls=None):
            if instance is None:
                return self
            value = self.field.calculate_value(instance)
            instance.__dict__[self.field.name] = value
            return value

        def __set__(self, obj, value):
            pass

    def contribute_to_class(self, cls, name, **kwargs):
        """Add field to class using ObjectProxy so that
        calculate_value can access the model instance."""
        self.set_attributes_from_name(name)
        cls._meta.add_field(self, private=True)
        self.model = cls
        setattr(cls, name, LucteriosVirtualField.ObjectProxy(self))
        pre_save.connect(self.resolve_computed_field, sender=cls)

    def resolve_computed_field(self, sender, instance, raw, **kwargs):
        """Pre-save signal receiver to compute new field value."""
        value = self.calculate_value(instance)
        setattr(instance, self.get_attname(), value)
        return value

    def calculate_value(self, instance):
        """
        Retrieve or call function to obtain value for this field.
        Args:
            instance: Parent model instance to reference
        """
        if LucteriosVirtualField.virtual_disabled:
            return None
        try:
            if callable(self.compute_from):
                value = self.compute_from(instance)
            else:
                instance_compute_object = getattr(instance, self.compute_from)
                if callable(instance_compute_object):
                    value = instance_compute_object()
                else:
                    value = instance_compute_object
        except Exception as err:
            logging.getLogger('lucterios.framwork').warning("LucteriosVirtualField.calculate_value(%s.%s) : %s", instance.__class__.__name__, self.compute_from, err)
            value = None
        return self.to_python(value)

    def deconstruct(self):
        name, path, args, kwargs = super(LucteriosVirtualField, self).deconstruct()
        kwargs['compute_from'] = self.compute_from
        return name, path, args, kwargs

    def to_python(self, value):
        return super(LucteriosVirtualField, self).to_python(value)

    def get_prep_value(self, value):
        return super(LucteriosVirtualField, self).get_prep_value(value)


class PrintFieldsPlugIn(object):
    _plug_ins = {}
    name = "EMPTY"
    title = ""

    @classmethod
    def get_plugin(cls, name):
        if name in cls._plug_ins.keys():
            return cls._plug_ins[name]()
        else:
            return PrintFieldsPlugIn()

    @classmethod
    def is_plugin(cls, name):
        return name in cls._plug_ins.keys()

    @classmethod
    def add_plugin(cls, pluginclass):
        cls._plug_ins[pluginclass.name] = pluginclass

    def get_all_print_fields(self):
        return []

    def evaluate(self, text_to_evaluate):
        return ""


class GeneralPrintPlugin(PrintFieldsPlugIn):
    name = "GENERAL"
    title = _('General')

    def get_all_print_fields(self):
        fields = []
        fields.append(("%s > %s" % (self.title, _('current date')), "%s.%s" % (self.name, 'today_short')))
        fields.append(("%s > %s" % (self.title, _('current date')), "%s.%s" % (self.name, 'today_long')))
        fields.append(("%s > %s" % (self.title, _('current hour')), "%s.%s" % (self.name, 'hour')))
        return fields

    def evaluate(self, text_to_evaluate):
        current_datetime = datetime.now()
        res = text_to_evaluate
        res = res.replace('#today_short', formats.date_format(current_datetime, "SHORT_DATE_FORMAT"))
        res = res.replace('#today_long', formats.date_format(current_datetime, "DATE_FORMAT"))
        res = res.replace('#hour', formats.date_format(current_datetime, "TIME_FORMAT"))
        return res


class LucteriosScheduler(object):

    _scheduler = None

    @classmethod
    def get_scheduler(cls):
        if LucteriosScheduler._scheduler is None:
            LucteriosScheduler._scheduler = BackgroundScheduler()
            LucteriosScheduler._scheduler.start()
        return LucteriosScheduler._scheduler

    @classmethod
    def stop_scheduler(cls):
        if LucteriosScheduler._scheduler is not None:
            LucteriosScheduler._scheduler.shutdown()
            LucteriosScheduler._scheduler = None

    @classmethod
    def add_task(cls, callback, minutes, **kwargs):
        scheduler = cls.get_scheduler()
        try:
            scheduler.add_job(callback, 'interval', minutes=minutes, id=callback.__name__, kwargs=kwargs)
        except ConflictingIdError:
            pass

    @classmethod
    def add_date(cls, callback, datetime, **kwargs):
        scheduler = cls.get_scheduler()
        try:
            scheduler.add_job(callback, 'date', run_date=datetime, id=callback.__name__, kwargs=kwargs)
        except ConflictingIdError:
            pass

    @classmethod
    def remove(cls, callback):
        scheduler = cls.get_scheduler()
        if scheduler.get_job(callback.__name__) is not None:
            scheduler.remove_job(callback.__name__)

    @classmethod
    def get_list(cls):
        job_list = []
        scheduler = cls.get_scheduler()
        for job in scheduler.get_jobs():
            if hasattr(job, 'next_run_time'):
                status = job.next_run_time
            else:
                status = 'pending'
            job_list.append((job.name, job.func.__doc__, job.trigger, status))
        return job_list


PrintFieldsPlugIn.add_plugin(GeneralPrintPlugin)
