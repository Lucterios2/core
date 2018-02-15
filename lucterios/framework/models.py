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
import logging
from datetime import datetime, date, time
from django_fsm.signals import post_transition

from django.db import models, transaction
from django.db.models import Transform, Count, Q
from django.db.models.deletion import ProtectedError
from django.db.models.lookups import RegisterLookupMixin
from django.core.exceptions import FieldDoesNotExist, ValidationError, ObjectDoesNotExist
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import six, formats, timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.module_loading import import_module

from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.editors import LucteriosEditor


class AbsoluteValue(Transform):
    lookup_name = 'abs'

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "ABS(%s)" % lhs, params


RegisterLookupMixin.register_lookup(AbsoluteValue)


def get_value_converted(value, bool_textual=False, convert_datetime=True):
    if hasattr(value, 'all'):
        values = []
        for val_item in value.all():
            values.append(six.text_type(val_item))
        return "{[br/]}".join(values)
    elif isinstance(value, datetime) and convert_datetime:
        return formats.date_format(value, "DATETIME_FORMAT")
    elif isinstance(value, date) and convert_datetime:
        return formats.date_format(value, "DATE_FORMAT")
    elif isinstance(value, time) and convert_datetime:
        return formats.date_format(value, "TIME_FORMAT")
    elif isinstance(value, bool):
        if bool_textual:
            if value:
                return _("Yes")
            else:
                return _("No")
        else:
            if value:
                return six.text_type("1")
            else:
                return six.text_type("0")
    elif value is None:
        return six.text_type("---")
    elif isinstance(value, LucteriosModel):
        return value.get_final_child()
    else:
        return value


def get_value_if_choices(value, dep_field):
    if hasattr(dep_field, 'choices') and (dep_field.choices is not None) and (len(dep_field.choices) > 0):
        for choices_key, choices_value in dep_field.choices:
            if choices_key == int(value):
                value = six.text_type(choices_value)
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
            field_val.append("%s=%s" % (key, six.text_type(val).replace('{[br/]}', "\n").strip().replace("\n", '<br/>')))
    return field_val


class LucteriosModel(models.Model):

    TO_EVAL_FIELD = re.compile(r"#[A-Za-z_0-9\.]+")

    @classmethod
    def get_default_fields(cls):
        fields = [f.name for f in cls._meta.get_fields(
        )]
        if cls._meta.has_auto_field and (cls._meta.auto_field.attname in fields):
            fields.remove(
                cls._meta.auto_field.attname)
        fields.sort()
        return fields

    @classmethod
    def get_long_name(cls):
        instance = cls()
        return "%s.%s" % (instance._meta.app_label, instance._meta.object_name)

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
    def convert_field_for_search(cls, fieldname, fieldsearched):
        def convertQ(query):
            if isinstance(query, Q):
                for q_idx in range(len(query.children)):
                    query.children[q_idx] = convertQ(query.children[q_idx])
                return query
            elif isinstance(query, tuple) and (len(query) == 2):
                return (field_name + '__' + query[0], query[1])
            else:
                return None
        if isinstance(fieldsearched, six.text_type):
            return fieldname + "." + fieldsearched
        elif len(fieldsearched) == 4:
            if fieldname[-4:] == '_set':
                field_name = fieldname[:-4]
            else:
                field_name = fieldname
            field = cls.get_field_by_name(field_name)
            if hasattr(field, 'verbose_name'):
                fieldsearched[1].verbose_name = field.verbose_name + ' > ' + fieldsearched[1].verbose_name
            else:
                fieldsearched[1].verbose_name = field.related_model._meta.verbose_name + ' > ' + fieldsearched[1].verbose_name
            return (fieldname + "." + fieldsearched[0], fieldsearched[1], field_name + "__" + fieldsearched[2], convertQ(fieldsearched[3]))

    @classmethod
    def get_print_fields(cls):
        return cls.get_default_fields()

    def set_context(self, xfer):
        pass

    def get_color_ref(self):
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
    def import_data(cls, rowdata, dateformat):
        from django.db.models.fields import IntegerField, FloatField, DecimalField, DateField, TimeField, DateTimeField, BooleanField
        from django.db.models.fields.related import ForeignKey
        try:
            new_item = cls()
            if cls._meta.ordering is not None:
                query = {}
                for order_fd in cls._meta.ordering:
                    if order_fd[0] == '-':
                        order_fd = order_fd[1:]
                    if order_fd in rowdata.keys():
                        query[order_fd] = rowdata[order_fd]
            if len(query) > 0:
                search = cls.objects.filter(**query)
                if len(search) > 0:
                    new_item = search[0]
            for fieldname, fieldvalue in rowdata.items():
                dep_field = cls.get_field_by_name(fieldname)
                value_to_saved = (dep_field is not None) and not (dep_field.is_relation and dep_field.many_to_many)
                if isinstance(dep_field, IntegerField):
                    if (dep_field.choices is not None) and (len(dep_field.choices) > 0):
                        for choice in dep_field.choices:
                            if fieldvalue == choice[1]:
                                fieldvalue = choice[0]
                    try:
                        fieldvalue = int(fieldvalue)
                    except ValueError:
                        fieldvalue = 0
                elif isinstance(dep_field, FloatField) or isinstance(dep_field, DecimalField):
                    try:
                        fieldvalue = float(fieldvalue.replace(',', '.'))
                    except ValueError:
                        fieldvalue = 0.0
                elif isinstance(dep_field, DateField) and isinstance(fieldvalue, six.text_type):
                    try:
                        fieldvalue = datetime.strptime(fieldvalue, dateformat).date()
                    except ValueError:
                        fieldvalue = datetime.now().date()
                elif isinstance(dep_field, TimeField) and isinstance(fieldvalue, six.text_type):
                    try:
                        fieldvalue = datetime.strptime(fieldvalue, "%H:%M").time()
                    except ValueError:
                        fieldvalue = datetime.now().time()
                elif isinstance(dep_field, DateTimeField) and isinstance(fieldvalue, six.text_type):
                    try:
                        fieldvalue = datetime.strptime(fieldvalue, dateformat + " %H:%M")
                    except ValueError:
                        fieldvalue = datetime.now()
                elif isinstance(dep_field, BooleanField):
                    fieldvalue = (six.text_type(fieldvalue) == 'True') or (six.text_type(fieldvalue).lower() == 'yes') or (six.text_type(fieldvalue).lower() == 'oui') or (fieldvalue != 0)
                elif not fieldname.endswith('_id') and isinstance(dep_field, ForeignKey):
                    sub_value = fieldvalue
                    fieldvalue = None
                    for sub_item in dep_field.remote_field.model.objects.all():
                        if six.text_type(sub_item.get_final_child()) == six.text_type(sub_value):
                            fieldvalue = sub_item
                            break
                    if fieldvalue is None:
                        base_dep_field = cls.get_field_by_name(fieldname.split('.')[0])
                        if not base_dep_field.null:
                            return None
                if value_to_saved:
                    setattr(new_item, fieldname, fieldvalue)

            for fieldname in cls.get_edit_fields():
                if isinstance(fieldname, tuple):
                    fieldname = fieldname[1]
                dep_field = cls.get_field_by_name(fieldname)
                if (dep_field is not None) and not dep_field.null and not dep_field.blank:
                    val = getattr(new_item, fieldname)
                    if val in [None, '']:
                        return None
            new_item.save()
            return new_item
        except ValidationError:
            logging.getLogger('lucterios.framwork').exception("import_data")
            raise LucteriosException(GRAVE, "Data error in this line:<br/> %s" % "<br/>".join(get_obj_contains(new_item)))
        except Exception:
            logging.getLogger('lucterios.framwork').exception("import_data")
            raise

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

    @transaction.atomic
    def merge_objects(self, alias_objects=[]):
        from django.contrib.contenttypes.fields import GenericForeignKey
        from django.apps import apps
        if not isinstance(alias_objects, list):
            alias_objects = [alias_objects]

        primary_class = self.__class__
        for alias_object in alias_objects:
            if not isinstance(alias_object, primary_class):
                raise TypeError('Only models of same class can be merged')

        generic_fields = []
        for model in apps.get_models():
            generic_fields.extend(
                filter(lambda x: isinstance(x, GenericForeignKey), model.__dict__.values()))

        blank_local_fields = set([field.attname for field in self._meta.local_fields if getattr(
            self, field.attname) in [None, '']])

        for alias_object in alias_objects:
            for related_object in alias_object._meta.get_fields(include_hidden=False):
                if related_object.one_to_many and related_object.auto_created:
                    alias_varname = related_object.get_accessor_name()
                    obj_varname = related_object.field.name
                    related_objects = getattr(alias_object, alias_varname)
                    for obj in related_objects.all():
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
                        setattr(self, obj_varname, mergedlist)

            for field in generic_fields:
                filter_kwargs = {}
                filter_kwargs[field.fk_field] = alias_object._get_pk_val()
                filter_kwargs[field.ct_field] = field.get_content_type(
                    alias_object)
                for generic_related_object in field.model.objects.filter(**filter_kwargs):
                    setattr(generic_related_object, field.name, self)
                    generic_related_object.save()

            filled_up = set()
            for field_name in blank_local_fields:
                val = getattr(alias_object, field_name)
                if val not in [None, '']:
                    setattr(self, field_name, val)
                    filled_up.add(field_name)
            blank_local_fields -= filled_up

            alias_object.delete()
        self.save()

    @classmethod
    def get_field_by_name(cls, fieldname):
        try:
            fieldnames = fieldname.split('.')
            current_meta = cls._meta
            for field_name in fieldnames:
                dep_field = current_meta.get_field(field_name)
                if hasattr(dep_field, 'remote_field') and (dep_field.remote_field is not None):
                    current_meta = dep_field.remote_field.model._meta
        except FieldDoesNotExist:
            dep_field = None
        return dep_field

    def evaluate(self, text):
        def eval_sublist(field_list, field_value):
            field_val = []
            for sub_model in field_value.all():
                field_val.append(
                    sub_model.evaluate("#" + ".".join(field_list[1:])))
            return "{[br/]}".join(field_val)
        if text == '#':
            return six.text_type(self)
        value = text
        if text is not None:
            for field in self.TO_EVAL_FIELD.findall(text):
                field_list = field[1:].split('.')
                if hasattr(self, field_list[0]):
                    field_value = getattr(self, field_list[0])
                else:
                    field_value = ""
                if PrintFieldsPlugIn.is_plugin(field_list[0]):
                    field_val = PrintFieldsPlugIn.get_plugin(
                        field_list[0]).evaluate("#" + ".".join(field_list[1:]))
                elif field_list[0][-4:] == '_set':
                    field_val = eval_sublist(field_list, field_value)
                else:
                    try:
                        dep_field = self._meta.get_field(field_list[0])
                    except FieldDoesNotExist:
                        dep_field = None
                    if (dep_field is None or is_simple_field(dep_field)) and not isinstance(field_value, LucteriosModel):
                        field_val = get_value_converted(field_value, True)
                        field_val = get_value_if_choices(field_val, dep_field)
                    else:
                        if field_value is None:
                            field_val = ""
                        elif isinstance(field_value, LucteriosModel) and not hasattr(field_value, "all"):
                            field_val = field_value.evaluate("#" + ".".join(field_list[1:]))
                        else:
                            field_val = eval_sublist(field_list, field_value)
                value = value.replace(field, six.text_type(field_val))
        return value

    @classmethod
    def get_field_for_print(cls, with_plugin, field_name):
        def add_sub_field(field_name, field_title, model):
            for sub_title, sub_name in model.get_all_print_fields(False):
                fields.append(
                    ("%s > %s" % (field_title, sub_title), "%s.%s" % (field_name, sub_name)))
        fields = []
        item = cls()
        if PrintFieldsPlugIn.is_plugin(field_name):
            if with_plugin:
                fields.extend(PrintFieldsPlugIn.get_plugin(field_name).get_all_print_fields())
        elif field_name[-4:] == '_set':
            child = getattr(item, field_name)
            field_title = child.model._meta.verbose_name
            add_sub_field(field_name, field_title, child.model)
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
            try:
                dep_field = item._meta.get_field(field_name)
                field_title = dep_field.verbose_name
                if is_simple_field(dep_field):
                    fields.append((field_title, field_name))
                else:
                    add_sub_field(field_name, field_title, dep_field.remote_field.model)
            except (FieldDoesNotExist, AttributeError):
                if hasattr(item, field_name):
                    fields.append((field_name, field_name))
        return fields

    @classmethod
    def get_all_print_fields(cls, with_plugin=True):
        fields = []
        for field_name in cls.get_print_fields():
            fields.extend(cls.get_field_for_print(with_plugin, field_name))
        return fields

    def get_final_child(self):
        final_child = self
        rel_objs = self._meta.get_fields(
        )
        for rel_obj in rel_objs:
            if hasattr(rel_obj, 'field') and (rel_obj.field.name == (self.__class__.__name__.lower() + '_ptr')):
                try:
                    final_child = getattr(
                        self, rel_obj.get_accessor_name()).get_final_child()
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

    class Meta(object):
        abstract = True


class LucteriosSession(Session, LucteriosModel):

    def __init__(self, *args, **kwargs):
        Session.__init__(self, *args, **kwargs)
        self._data = None

    @classmethod
    def get_default_fields(cls):
        return [(_('is active'), 'is_active'), (_('username'), 'username'), 'expire_date']

    def _get_data(self):
        if self._data is None:
            self._data = self.get_decoded()
        return self._data

    @property
    def username(self):
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

    @property
    def is_active(self):
        return get_value_converted(self.get_is_active(), bool_textual=True)

    @classmethod
    def clean_anonymous(cls):
        dt_now = timezone.now()
        for sess in LucteriosSession.objects.filter(expire_date__lt=dt_now):
            if sess.username == '---':
                sess.delete()

    def flush(self):
        try:
            if hasattr(Session, "flush"):
                Session.flush(self)
        except Exception:
            pass

    class Meta(object):
        proxy = True
        default_permissions = []
        verbose_name = _('session')
        verbose_name_plural = _('sessions')
        ordering = ['-expire_date']


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


PrintFieldsPlugIn.add_plugin(GeneralPrintPlugin)


def post_after_transition(sender, **kwargs):
    if 'exception' not in kwargs:
        instance = kwargs['instance']
        instance.save()


post_transition.connect(post_after_transition)
