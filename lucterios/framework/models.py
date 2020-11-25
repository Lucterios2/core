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
import re
import json
import logging
from datetime import datetime
from copy import deepcopy

from django_fsm.signals import post_transition

from django.db import models, transaction
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.db.models.deletion import ProtectedError
from django.db.models.fields import BooleanField, DateTimeField, TimeField, DateField, IntegerField
from django.apps.registry import apps
from django.core.exceptions import FieldDoesNotExist, ValidationError, ObjectDoesNotExist
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, Permission
from django.utils import timezone
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_module

from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.tools import adapt_value, format_to_string, extract_format, get_format_from_field, get_format_value
from lucterios.framework.model_fields import get_obj_contains, PrintFieldsPlugIn,\
    is_simple_field, LucteriosVirtualField


def add_sub_field_for_print(fields, field_name, field_title, model):
    for sub_title, sub_name in model.get_all_print_fields(False):
        fields.append(("%s > %s" % (field_title, sub_title), "%s.%s" % (field_name, sub_name)))


def eval_sublist(field_list, field_value):
    field_val = []
    for sub_model in field_value.all():
        field_val.append(sub_model.evaluate("#" + ".".join(field_list[1:])))
    return "{[br/]}".join(field_val)


class LucteriosModel(models.Model):

    TO_EVAL_FIELD = re.compile(r"#[A-Za-z_0-9\.]+")

    @classmethod
    def get_default_fields(cls):
        fields = [f.name for f in cls._meta.get_fields()]
        if (cls._meta.auto_field is not None) and (cls._meta.auto_field.attname in fields):
            fields.remove(cls._meta.auto_field.attname)
        fields.sort()
        return fields

    @classmethod
    def get_long_name(cls):
        return "%s.%s" % (cls._meta.app_label, cls._meta.object_name)

    @classmethod
    def get_edit_fields(cls):
        return cls.get_show_fields()

    @classmethod
    def get_show_fields(cls):
        return cls.get_default_fields()

    @classmethod
    def get_search_fields(cls):
        return cls.get_default_fields()

    @classmethod
    def convert_field_for_search(cls, fieldname, fieldsearched, add_verbose=True):
        def convertQ(query):
            if isinstance(query, Q):
                for q_idx in range(len(query.children)):
                    query.children[q_idx] = convertQ(query.children[q_idx])
                return query
            elif isinstance(query, tuple) and (len(query) == 2):
                return (field_name + '__' + query[0], query[1])
            else:
                return None
        if isinstance(fieldsearched, str):
            return fieldname + "." + fieldsearched
        elif len(fieldsearched) == 4:
            if fieldname[-4:] == '_set':
                field_name = fieldname[:-4]
            else:
                field_name = fieldname
            field = cls.get_field_by_name(field_name)
            newfielddb = deepcopy(fieldsearched[1])
            if isinstance(add_verbose, str):
                newfielddb.verbose_name = str(add_verbose) + ' > ' + str(fieldsearched[1].verbose_name)
            elif hasattr(field, 'verbose_name'):
                newfielddb.verbose_name = str(field.verbose_name) + ' > ' + str(fieldsearched[1].verbose_name)
            elif add_verbose:
                newfielddb.verbose_name = str(field.related_model._meta.verbose_name) + ' > ' + str(fieldsearched[1].verbose_name)
            return (fieldname + "." + fieldsearched[0], newfielddb, field_name + "__" + fieldsearched[2], convertQ(fieldsearched[3]))

    @classmethod
    def get_print_fields(cls):
        return cls.get_default_fields()

    def set_context(self, xfer):
        pass

    def get_color_ref(self):
        return None

    def get_auditlog_object(self):
        return None

    @classmethod
    def get_select_contact_type(cls, with_current=True):
        select_list = []
        if with_current:
            select_list.append(
                (cls.get_long_name(), cls._meta.verbose_name.title()))
        for sub_class in cls.__subclasses__():
            select_list.extend(sub_class.get_select_contact_type())
        return select_list

    @classmethod
    def get_import_fields(cls):
        fields = []
        for field in cls.get_edit_fields():
            if isinstance(field, tuple):
                fields.extend(field)
            else:
                fields.append(field)
        return fields

    @classmethod
    def get_import_logs(cls):
        return getattr(cls, 'import_logs', [])

    @classmethod
    def initialize_import(cls):
        cls.import_logs = []

    @classmethod
    def _convert_field_integerfield(cls, fieldvalue, dep_field, **_args):
        if (dep_field.choices is not None) and (len(dep_field.choices) > 0):
            for choice in dep_field.choices:
                if fieldvalue == choice[1]:
                    fieldvalue = choice[0]
        try:
            fieldvalue = int(fieldvalue)
        except ValueError:
            fieldvalue = 0
        return fieldvalue

    @classmethod
    def _convert_field_floatfield(cls, fieldvalue, **_args):
        try:
            if isinstance(fieldvalue, str):
                fieldvalue = fieldvalue.replace(',', '.')
            fieldvalue = float(fieldvalue)
        except ValueError:
            fieldvalue = 0.0
        return fieldvalue

    @classmethod
    def _convert_field_decimalfield(cls, fieldvalue, **_args):
        return cls._convert_field_floatfield(fieldvalue, **_args)

    @classmethod
    def _convert_field_datefield(cls, fieldvalue, dateformat, **_args):
        try:
            if isinstance(fieldvalue, str):
                fieldvalue = datetime.strptime(fieldvalue, dateformat).date()
        except ValueError:
            fieldvalue = datetime.now().date()
        return fieldvalue

    @classmethod
    def _convert_field_timefield(cls, fieldvalue, dateformat, **_args):
        try:
            if isinstance(fieldvalue, str):
                fieldvalue = datetime.strptime(fieldvalue, "%H:%M").time()
        except ValueError:
            fieldvalue = datetime.now().time()
        return fieldvalue

    @classmethod
    def _convert_field_datetimefield(cls, fieldvalue, dateformat, **_args):
        try:
            if isinstance(fieldvalue, str):
                fieldvalue = datetime.strptime(fieldvalue, dateformat + " %H:%M")
        except ValueError:
            fieldvalue = datetime.now()
        return fieldvalue

    @classmethod
    def _convert_field_booleanfield(cls, fieldvalue, **_args):
        fieldvalue = (str(fieldvalue) == 'True') or (str(fieldvalue).lower() == 'yes') or (str(fieldvalue).lower() == 'oui') or (fieldvalue != 0)
        return fieldvalue

    @classmethod
    def _convert_field_foreignkey(cls, fieldvalue, dep_field, fieldname, **_args):
        if not fieldname.endswith('_id'):
            sub_value = fieldvalue
            fieldvalue = None
            for sub_item in dep_field.remote_field.model.objects.all():
                if str(sub_item.get_final_child()) == str(sub_value):
                    fieldvalue = sub_item
                    break
            if fieldvalue is None:
                base_dep_field = cls.get_field_by_name(fieldname.split('.')[0])
                if not base_dep_field.null:
                    raise LucteriosException(GRAVE, _("%(name)s '%(value)s' unknown !") % {'name': base_dep_field.verbose_name, 'value': sub_value})
        return fieldvalue

    @classmethod
    def _get_from_data(cls, rowdata):
        new_item = cls()
        if cls._meta.ordering is not None:
            query = {}
            for order_fd in cls._meta.ordering:
                if order_fd[0] == '-':
                    order_fd = order_fd[1:]
                if order_fd in rowdata.keys():
                    query[order_fd + '__iexact'] = rowdata[order_fd]
        if len(query) > 0:
            search = cls.objects.filter(**query)
            if len(search) > 0:
                new_item = search[0]
        return new_item

    def set_attribute(self, fieldname, fieldvalue, dateformat):
        from django.db.models.fields import FloatField, DecimalField
        from django.db.models.fields.related import ForeignKey
        dep_field = self.get_field_by_name(fieldname)
        if (dep_field is not None) and not (dep_field.is_relation and dep_field.many_to_many):
            for field_type in (IntegerField, FloatField, DecimalField, DateField, TimeField, DateTimeField, BooleanField, ForeignKey):
                if isinstance(dep_field, field_type):
                    fct = getattr(self, "_convert_field_%s" % field_type.__name__.lower(), None)
                    if fct is not None:
                        fieldvalue = fct(fieldvalue, dep_field=dep_field, dateformat=dateformat, fieldname=fieldname)
                        break
            setattr(self, fieldname, fieldvalue)

    def is_needed_attribute(self, fieldname):
        if isinstance(fieldname, tuple):
            fieldname = fieldname[1]
        dep_field = self.get_field_by_name(fieldname)
        if (dep_field is not None) and not dep_field.null and not dep_field.blank:
            val = getattr(self, fieldname)
            if val in [None, '']:
                return True
        return False

    @classmethod
    def import_data(cls, rowdata, dateformat):
        try:
            new_item = cls._get_from_data(rowdata)
            for fieldname, fieldvalue in rowdata.items():
                new_item.set_attribute(fieldname, fieldvalue, dateformat)
            for fieldname in cls.get_edit_fields():
                if new_item.is_needed_attribute(fieldname):
                    return None
            new_item.save()
            return new_item
        except LucteriosException as import_error:
            cls.import_logs.append(str(import_error))
            return None
        except ValidationError:
            logging.getLogger('lucterios.framwork').exception("import_data")
            raise LucteriosException(GRAVE, "Data error in this line:<br/> %s" % "<br/>".join(get_obj_contains(new_item)))
        except Exception:
            logging.getLogger('lucterios.framwork').exception("import_data")
            raise

    @classmethod
    def finalize_import(cls):
        return None

    @classmethod
    def get_query_for_duplicate(cls):
        query = Q()
        for ident in cls.objects.values(*cls._meta.ordering).annotate(Count('id')).values(*cls._meta.ordering).order_by().filter(id__count__gt=1):
            query |= Q(**ident)
        if len(query) == 0:
            empty_val = {}
            for item in cls._meta.ordering:
                empty_val[item] = ''
            query = Q(**empty_val)
        return query

    def _merge_fields_object(self, alias_object):
        for related_object in alias_object._meta.get_fields(include_hidden=False):
            if related_object.one_to_many and related_object.auto_created:
                alias_varname = related_object.get_accessor_name()
                obj_varname = related_object.field.name
                related_objects = getattr(alias_object, alias_varname)
                for obj in related_objects.all():
                    if hasattr(obj, "get_final_child"):
                        obj = obj.get_final_child()
                    setattr(obj, obj_varname, self)
                    obj.save()
            if related_object.many_to_many:
                if related_object.auto_created:
                    alias_varname = related_object.get_accessor_name()
                    obj_varname = related_object.field.name
                    if alias_varname is not None:
                        related_many_objects = getattr(alias_object, alias_varname).all()
                    else:
                        related_many_objects = getattr(alias_object, obj_varname).all()
                    for obj in related_many_objects.all():
                        getattr(obj, obj_varname).remove(alias_object)
                        getattr(obj, obj_varname).add(self)
                else:
                    obj_varname = related_object.name
                    mergedlist = []
                    mergedlist.extend(getattr(self, obj_varname).all())
                    mergedlist.extend(getattr(alias_object, obj_varname).all())
                    getattr(self, obj_varname).set(mergedlist)

    def _merge_genericfield_object(self, alias_object, generic_fields):
        for field in generic_fields:
            filter_kwargs = {}
            filter_kwargs[field.fk_field] = alias_object._get_pk_val()
            filter_kwargs[field.ct_field] = field.get_content_type(alias_object)
            for generic_related_object in field.model.objects.filter(**filter_kwargs):
                setattr(generic_related_object, field.name, self)
                generic_related_object.save()

    def _merge_blankfield_object(self, alias_object, blank_local_fields):
        filled_up = set()
        for field_name in blank_local_fields:
            val = getattr(alias_object, field_name)
            if val not in [None, '']:
                setattr(self, field_name, val)
                filled_up.add(field_name)
        blank_local_fields -= filled_up

    @transaction.atomic
    def merge_objects(self, alias_objects=[]):
        from django.contrib.contenttypes.fields import GenericForeignKey
        from lucterios.framework.signal_and_lock import Signal
        if not isinstance(alias_objects, list):
            alias_objects = [alias_objects]
        if len(alias_objects) == 0:
            return
        primary_class = self.__class__
        for alias_object in alias_objects:
            if not isinstance(alias_object, primary_class):
                raise TypeError('Only models of same class can be merged')

        Signal.call_signal("pre_merge", self, alias_objects)
        generic_fields = []
        for model in apps.get_models():
            generic_fields.extend(filter(lambda x: isinstance(x, GenericForeignKey), model.__dict__.values()))
        blank_local_fields = set([field.attname for field in self._meta.local_fields if getattr(self, field.attname) in [None, '']])
        for alias_object in alias_objects:
            self._merge_fields_object(alias_object)
            self._merge_genericfield_object(alias_object, generic_fields)
            self._merge_blankfield_object(alias_object, blank_local_fields)
            alias_object.delete()
        self.save()
        Signal.call_signal("post_merge", self)

    @classmethod
    def get_field_by_name(cls, fieldname):
        try:
            fieldnames = fieldname.split('.')
            current_meta = cls._meta
            dep_field = current_meta.get_field(fieldnames[0])
            if (len(fieldnames) > 1) and hasattr(dep_field, 'remote_field') and (dep_field.remote_field is not None):
                dep_field = dep_field.remote_field.model.get_field_by_name('.'.join(fieldnames[1:]))
        except FieldDoesNotExist:
            dep_field = None
        return dep_field

    def get_value_for_evaluate(self, field_list, field_value):
        dep_field = self.get_field_by_name(field_list[0])
        if (dep_field is None or is_simple_field(dep_field)) and not isinstance(field_value, LucteriosModel):
            field_value = adapt_value(field_value)
            formatnum, formatstr = extract_format(get_format_from_field(dep_field))
            field_val = format_to_string(field_value, formatnum, formatstr)
        elif field_value is None:
            field_val = ""
        elif isinstance(field_value, LucteriosModel) and not hasattr(field_value, "all"):
            field_val = field_value.evaluate("#" + ".".join(field_list[1:]))
        else:
            field_val = eval_sublist(field_list, field_value)
        return field_val

    def evaluate_with_formating(self, text):
        value, formatnum, formatstr = None, None, None
        matchfield = self.TO_EVAL_FIELD.match(text)
        if (matchfield is not None) and (matchfield.span() == (0, len(text))):
            field_list = text[1:].split('.')
            if hasattr(self, field_list[0]):
                field_value = getattr(self, field_list[0])
                dep_field = self.get_field_by_name(field_list[0])
                if (dep_field is None or is_simple_field(dep_field)) and not isinstance(field_value, LucteriosModel):
                    value = adapt_value(field_value)
                    formatnum, formatstr = extract_format(get_format_from_field(dep_field))
                elif isinstance(field_value, LucteriosModel) and not hasattr(field_value, "all"):
                    value, formatnum, formatstr = field_value.evaluate_with_formating("#" + ".".join(field_list[1:]))
        return value, formatnum, formatstr

    def evaluate(self, text):
        if text == '#':
            return str(self)
        value = text
        if text is not None:
            for field in self.TO_EVAL_FIELD.findall(text):
                field_list = field[1:].split('.')
                if hasattr(self, field_list[0]):
                    field_value = getattr(self, field_list[0])
                else:
                    field_value = ""
                if PrintFieldsPlugIn.is_plugin(field_list[0]):
                    field_val = PrintFieldsPlugIn.get_plugin(field_list[0]).evaluate("#" + ".".join(field_list[1:]))
                elif field_list[0][-4:] == '_set':
                    field_val = eval_sublist(field_list, field_value)
                else:
                    field_val = self.get_value_for_evaluate(field_list, field_value)
                value = value.replace(field, str(field_val))
        return value

    def _append_sub_field_for_print(self, field_name, with_plugin):
        fields = []
        sub_fields = field_name.split('.')
        try:
            dep_field = self._meta.get_field(sub_fields[0])
            field_title = dep_field.verbose_name
            if len(sub_fields) == 1:
                if is_simple_field(dep_field):
                    fields.append((field_title, field_name))
                else:
                    add_sub_field_for_print(fields, field_name, field_title, dep_field.remote_field.model)
            else:
                for sub_title, __new_field in dep_field.remote_field.model.get_field_for_print(with_plugin, ".".join(sub_fields[1:])):
                    if sub_title != '':
                        fields.append(("%s > %s" % (field_title, sub_title), field_name))
                    else:
                        fields.append((field_title, field_name))

        except (FieldDoesNotExist, AttributeError):
            if (field_name == 'str'):
                fields.append(("", field_name))
            elif hasattr(self, field_name):
                fields.append((field_name, field_name))
        return fields

    @classmethod
    def get_field_for_print(cls, with_plugin, field_name):
        fields = []
        item = cls()
        if PrintFieldsPlugIn.is_plugin(field_name):
            if with_plugin:
                fields.extend(PrintFieldsPlugIn.get_plugin(field_name).get_all_print_fields())
        elif field_name[-4:] == '_set':
            child = getattr(item, field_name)
            field_title = child.model._meta.verbose_name
            add_sub_field_for_print(fields, field_name, field_title, child.model)
        elif isinstance(field_name, tuple):
            sub_title, field_name = field_name
            if field_name.split('.')[0][-4:] == '_set':
                mother_field_name = field_name.split('.')[0]
                child = getattr(item, mother_field_name)
                field_title = child.model._meta.verbose_name
                fields.append(("%s > %s" % (field_title, sub_title), field_name))
            else:
                fields.append((sub_title, field_name))
        elif field_name.split('.')[0][-4:] == '_set':
            mother_field_name = field_name.split('.')[0]
            child = getattr(item, mother_field_name)
            field_title = child.model._meta.verbose_name
            last_field_name = ".".join(field_name.split('.')[1:])
            for (sub_title, __new_field) in child.model.get_field_for_print(with_plugin, last_field_name):
                fields.append(("%s > %s" % (field_title, sub_title), field_name))
        else:
            fields.extend(item._append_sub_field_for_print(field_name, with_plugin))
        return fields

    @classmethod
    def get_all_print_fields(cls, with_plugin=True):
        fields = []
        for field_name in cls.get_print_fields():
            fields.extend(cls.get_field_for_print(with_plugin, field_name))
        return fields

    def get_final_child(self):
        final_child = self
        rel_objs = self._meta.get_fields()
        for rel_obj in rel_objs:
            if hasattr(rel_obj, 'field') and (rel_obj.field.name == (self.__class__.__name__.lower() + '_ptr')):
                try:
                    final_child = getattr(self, rel_obj.get_accessor_name()).get_final_child()
                except AttributeError:
                    pass
        return final_child

    def can_delete(self):

        return ''

    def delete(self, using=None):
        try:
            models.Model.delete(self, using=using)
        except ProtectedError:
            logging.getLogger('lucterios.framwork').debug("delete", exc_info=True)
            raise LucteriosException(IMPORTANT, _(
                'Cannot delete this record: there are associated with some sub-record'))

    @property
    def editor(self):
        try:
            root_module_name = ".".join(self.__module__.split('.')[:-1])
            module_editor = import_module(root_module_name + ".editors")
            class_name = self.__class__.__name__ + "Editor"
            class_editor = getattr(module_editor, class_name)
            return class_editor(self)
        except (ImportError, AttributeError):
            return LucteriosEditor(self)

    @classmethod
    def _get_sub_class(cls):
        current_class = cls
        while current_class._meta.proxy is True:
            for sub_class in current_class.__mro__:
                if (sub_class != current_class) and hasattr(current_class, '_meta'):
                    current_class = sub_class
                    break
        return current_class

    @classmethod
    def get_permission(cls, show=False, add=False, delete=False):
        perm_filter = Q()
        perm_filter |= Q(codename__istartswith="change_") if show else ~Q(codename__istartswith="change_")
        perm_filter |= Q(codename__istartswith="add_") if add else ~Q(codename__istartswith="add_")
        perm_filter |= Q(codename__istartswith="delete_") if delete else ~Q(codename__istartswith="delete_")
        current_class = cls._get_sub_class()
        perm_filter &= Q(content_type__app_label=current_class._meta.app_label) & Q(content_type__model=current_class._meta.object_name.lower())
        for item in Permission.objects.filter(perm_filter):
            if (item.codename.startswith("change_") and show) or (item.codename.startswith("add_") and add) or (item.codename.startswith("delete_") and delete):
                yield item

    class Meta(object):
        abstract = True


class LucteriosSession(Session, LucteriosModel):

    username = LucteriosVirtualField(verbose_name=_('username'), compute_from='get_username')
    is_active = LucteriosVirtualField(verbose_name=_('is active'), compute_from='get_is_active', format_string="B")

    def __init__(self, *args, **kwargs):
        Session.__init__(self, *args, **kwargs)
        self._data = None

    @classmethod
    def get_default_fields(cls):
        return ['is_active', 'username', 'expire_date']

    def _get_data(self):
        if self._data is None:
            self._data = self.get_decoded()
        return self._data

    def get_username(self):
        data = self._get_data()
        user_id = data.get('_auth_user_id', None)
        if user_id is None:
            return "---"
        else:
            try:
                return User.objects.get(id=user_id).username
            except ObjectDoesNotExist:
                return "---"

    def get_is_active(self):
        dt_now = timezone.now()
        return self.expire_date > dt_now

    @classmethod
    def clean_anonymous(cls):
        dt_now = timezone.now()
        for sess in LucteriosSession.objects.filter(expire_date__lt=dt_now):
            if sess.username == '---':
                sess.delete()

    class Meta(object):
        proxy = True
        default_permissions = []
        verbose_name = _('session')
        verbose_name_plural = _('sessions')
        ordering = ['-expire_date']


class LogEntryManager(models.Manager):
    """
    Custom manager for the :py:class:`LogEntry` model.
    """

    def log_create(self, instance, **kwargs):
        """
        Helper method to create a new log entry. This method automatically populates some fields when no explicit value
        is given.

        :param instance: The model instance to log a change for.
        :type instance: Model
        :param kwargs: Field overrides for the :py:class:`LogEntry` object.
        :return: The new log entry or `None` if there were no changes.
        :rtype: LogEntry
        """
        changes = kwargs.get('changes', None)
        pk = self._get_pk_value(instance)

        if changes is not None:
            kwargs.setdefault('modelname', instance.__class__.get_long_name())
            kwargs.setdefault('object_pk', pk)
            kwargs.setdefault('object_repr', smart_text(instance))

            if isinstance(pk, int):
                kwargs.setdefault('object_id', pk)

            get_additional_data = getattr(instance, 'get_additional_data', None)
            if callable(get_additional_data):
                kwargs.setdefault('additional_data', get_additional_data())

            # Delete log entries with the same pk as a newly created model. This should only be necessary when an pk is
            # used twice.
            if kwargs.get('action', None) is LucteriosLogEntry.Action.CREATE:
                if kwargs.get('object_id', None) is not None and self.filter(modelname=kwargs.get('modelname'), object_id=kwargs.get('object_id')).exists():
                    self.filter(modelname=kwargs.get('modelname'), object_id=kwargs.get('object_id')).delete()
                else:
                    self.filter(modelname=kwargs.get('modelname'), object_pk=kwargs.get('object_pk', '')).delete()
            # save LogEntry to same database instance is using
            db = instance._state.db
            return self.create(**kwargs) if db is None or db == '' else self.using(db).create(**kwargs)
        return None

    def get_for_object(self, instance):
        """
        Get log entries for the specified model instance.

        :param instance: The model instance to get log entries for.
        :type instance: Model
        :return: QuerySet of log entries for the given model instance.
        :rtype: QuerySet
        """
        # Return empty queryset if the given model instance is not a model instance.
        if not isinstance(instance, models.Model):
            return self.none()

        pk = self._get_pk_value(instance)

        if isinstance(pk, int):
            return self.filter(modelname=instance.__class__.get_long_name(), object_id=pk)
        else:
            return self.filter(modelname=instance.__class__.get_long_name(), object_pk=smart_text(pk))

    def get_for_objects(self, queryset):
        """
        Get log entries for the objects in the specified queryset.

        :param queryset: The queryset to get the log entries for.
        :type queryset: QuerySet
        :return: The LogEntry objects for the objects in the given queryset.
        :rtype: QuerySet
        """
        if not isinstance(queryset, QuerySet) or queryset.count() == 0:
            return self.none()

        modelname = queryset.model.get_long_name()
        primary_keys = list(queryset.values_list(queryset.model._meta.pk.name, flat=True))

        if isinstance(primary_keys[0], int):
            return self.filter(modelname=modelname).filter(Q(object_id__in=primary_keys)).distinct()
        elif isinstance(queryset.model._meta.pk, models.UUIDField):
            primary_keys = [smart_text(pk) for pk in primary_keys]
            return self.filter(modelname=modelname).filter(Q(object_pk__in=primary_keys)).distinct()
        else:
            return self.filter(modelname=modelname).filter(Q(object_pk__in=primary_keys)).distinct()

    def get_for_model(self, model):
        """
        Get log entries for all objects of a specified type.

        :param model: The model to get log entries for.
        :type model: class
        :return: QuerySet of log entries for the given model.
        :rtype: QuerySet
        """
        if not hasattr(model, "get_long_name"):
            return self.none()

        return self.filter(modelname=model.get_long_name())

    def _get_pk_value(self, instance):
        """
        Get the primary key field value for a model instance.

        :param instance: The model instance to get the primary key for.
        :type instance: Model
        :return: The primary key value of the given model instance.
        """
        pk_field = instance._meta.pk.name
        pk = getattr(instance, pk_field, None)

        # Check to make sure that we got an pk not a model object.
        if isinstance(pk, models.Model):
            pk = self._get_pk_value(pk)
        return pk


def get_format_value_ex(*args):
    return get_format_value(*args).replace("{[p", "{[span").replace("{[/p]}", "{[/span]}")


class LucteriosLogEntry(LucteriosModel):
    TEXT_TITLEFIELD = '{[th style="text-align: left;width: 25%%;vertical-align: top;"]}%s{[/th]}'
    TEXT_FIRSTVALUE = '{[td style="border: none;width: 20%%;vertical-align: top;"]}%s{[/td]}'
    TEXT_VALUE = '{[td style="border: none;vertical-align: top;"]}%s{[/td]}'
    TEXT_LINE = "{[tr]}%s{[/tr]}"

    class Action:
        CREATE = 0
        UPDATE = 1
        DELETE = 2
        REMOVE = 3
        ADD = 4
        choices = (
            (CREATE, _("create")),
            (UPDATE, _("update")),
            (DELETE, _("delete")),
            (REMOVE, _("remove")),
            (ADD, _("add"))
        )

        @classmethod
        def get_action_title(cls, action_id):
            for choices_id, choices_val in cls.choices:
                if str(choices_id) == str(action_id):
                    return str(choices_val)
            return str(action_id)

    messagetxt = LucteriosVirtualField(verbose_name=_('change message'), compute_from='get_message')
    modelname = models.CharField(db_index=True, max_length=255, blank=False, null=False, verbose_name=_("content type"))
    username = models.CharField(max_length=255, blank=True, null=True, default=None, verbose_name=_("actor"))
    object_pk = models.CharField(db_index=True, max_length=255, verbose_name=_("object pk"))
    object_id = models.BigIntegerField(blank=True, db_index=True, null=True, verbose_name=_("object id"))
    object_repr = models.TextField(verbose_name=_("object representation"))
    action = models.IntegerField(choices=Action.choices, verbose_name=_("action"))
    changes = models.TextField(blank=True, verbose_name=_("change message"))
    remote_addr = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("remote address"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("date"))
    additional_data = models.TextField(blank=True, null=True, verbose_name=_("additional data"))

    objects = LogEntryManager()

    def __str__(self):
        if self.action == self.Action.CREATE:
            fstring = _("Created {repr:s}")
        elif self.action == self.Action.UPDATE:
            fstring = _("Updated {repr:s}")
        elif self.action == self.Action.DELETE:
            fstring = _("Deleted {repr:s}")
        else:
            fstring = _("Logged {repr:s}")

        return fstring.format(repr=self.object_repr)

    @classmethod
    def get_default_fields(cls):
        return ['timestamp',
                'username',
                'action',
                'object_repr',
                'messagetxt',
                ]

    @classmethod
    def get_typeselection(cls):
        res = []
        for modelname in cls.objects.values_list('modelname', flat=True).distinct():
            model_item = apps.get_model(modelname)
            res.append((modelname, str(model_item._meta.verbose_name)))
        return sorted(list(set(res)), key=lambda item: item[1])

    def get_field(self, name):
        try:
            model = apps.get_model(self.modelname)
            return model._meta.get_field(name)
        except FieldDoesNotExist:
            return None

    def get_new_line(self, action, dep_field, value):
        if value[0] == 'None':
            value[0] = None
        if value[1] == 'None':
            value[1] = None
        if hasattr(dep_field, 'verbose_name'):
            title = dep_field.verbose_name
        else:
            title = dep_field.name
        if action in (self.Action.CREATE, self.Action.ADD) or (value[0] == value[1]):
            return (self.TEXT_TITLEFIELD + self.TEXT_VALUE) % (title, get_format_value_ex(dep_field, value[1]))
        elif action == self.Action.UPDATE:
            return (self.TEXT_TITLEFIELD + self.TEXT_FIRSTVALUE + self.TEXT_VALUE) % (title, get_format_value_ex(dep_field, value[0]), get_format_value_ex(dep_field, value[1]))
        else:
            return (self.TEXT_TITLEFIELD + self.TEXT_VALUE) % (title, get_format_value_ex(dep_field, value[0]))

    def _append_additional_data(self):
        res = []
        additional_data = json.loads(self.additional_data)
        for field_title, values in additional_data.items():
            for action_id, value_data in values.items():
                action_id = int(action_id)
                res_data = []
                for value_item in value_data:
                    if isinstance(value_item, dict) and ('modelname' in value_item) and ('changes' in value_item):
                        sub_model = apps.get_model(value_item['modelname'])
                        for sub_fieldname, diff_value in value_item['changes'].items():
                            sub_dep_field = sub_model._meta.get_field(sub_fieldname)
                            if (sub_dep_field is None) or (not sub_dep_field.editable or sub_dep_field.primary_key):
                                continue
                            new_line = self.get_new_line(action_id, sub_dep_field, diff_value)
                            res_data.append(self.TEXT_LINE % new_line)
                    else:

                        new_line = self.TEXT_VALUE % value_item
                        res_data.append(self.TEXT_LINE % new_line)

                new_line = (self.TEXT_TITLEFIELD + self.TEXT_FIRSTVALUE + self.TEXT_VALUE) % (field_title,
                                                                                              '{[i]}%s{[/i]}' % LucteriosLogEntry.Action.get_action_title(action_id),
                                                                                              '{[table]}%s{[/table]}' % ''.join(res_data))
                res.append(self.TEXT_LINE % new_line)
        return res

    def get_message(self):
        changes = json.loads(self.changes)
        res = ["{[table width='100%']}"]
        for key, value in changes.items():
            dep_field = self.get_field(key)
            if (dep_field is None) or (not dep_field.editable or dep_field.primary_key):
                continue
            new_line = self.get_new_line(self.action, dep_field, value)
            res.append(self.TEXT_LINE % new_line)
        if self.additional_data is not None:
            res.extend(self._append_additional_data())
        res.append("{[/table]}")
        return "".join(res)

    def change_additional_data(self, sender_ident, log_action, addon_data):
        if self.additional_data is None:
            additional_data = {}
        else:
            additional_data = json.loads(self.additional_data)
        if sender_ident not in additional_data:
            additional_data[sender_ident] = {}
        if log_action not in additional_data[sender_ident]:
            additional_data[sender_ident][log_action] = []
        if isinstance(addon_data, list):
            additional_data[sender_ident][log_action].extend(addon_data)
        else:
            additional_data[sender_ident][log_action].append(addon_data)
        self.additional_data = json.dumps(additional_data, default=str)
        self.save()

    class Meta(object):
        default_permissions = []
        get_latest_by = 'timestamp'
        ordering = ['-timestamp']
        verbose_name = _("log entry")
        verbose_name_plural = _("log entries")


def post_after_transition(sender, **kwargs):
    if 'exception' not in kwargs:
        instance = kwargs['instance']
        instance.save()


post_transition.connect(post_after_transition)


def correct_db_field(fields):
    def check_ret(val):
        if isinstance(val, int):
            return val
        elif hasattr(val, "rowcount"):
            return val.rowcount
        return 0
    from django.db import connection
    if connection.vendor == 'sqlite':
        query = "UPDATE %s SET %s=0 WHERE typeof(%s)='text'"
    else:
        query = "UPDATE %s SET %s=0 WHERE %s='NaN'"
    ret = 0
    try:
        with connection.cursor() as cursor:
            for tablename, fieldname in fields.items():
                ret += check_ret(cursor.execute(query % (tablename, fieldname, fieldname)))
    except Exception:
        logging.getLogger('lucterios.framwork').exception("correct_db_field")
    if ret > 0:
        print("%s DB corrections" % ret)
