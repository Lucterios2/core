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

from django.db import models
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import six, formats

def get_value_converted(value, bool_textual=False):
    # pylint: disable=too-many-return-statements, too-many-branches
    import datetime
    if hasattr(value, 'all'):
        values = []
        for val_item in value.all():
            values.append(six.text_type(val_item))
        return "{[br/]}".join(values)
    elif isinstance(value, datetime.datetime):
        return formats.date_format(value, "DATETIME_FORMAT")
    elif isinstance(value, datetime.date):
        return formats.date_format(value, "DATE_FORMAT")
    elif isinstance(value, datetime.time):
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
    if hasattr(dep_field[0], 'choices') and (dep_field[0].choices is not None) and (len(dep_field[0].choices) > 0):
        for choices_key, choices_value in dep_field[0].choices:
            if choices_key == int(value):
                value = six.text_type(choices_value)
                break
    return value

class LucteriosModel(models.Model):

    TO_EVAL_FIELD = re.compile(r"#[A-Za-z_0-9\.]+")

    @classmethod
    def get_default_fields(cls):
        fields = cls._meta.get_all_field_names()  # pylint: disable=no-member,protected-access
        if cls._meta.has_auto_field and (cls._meta.auto_field.attname in fields):  # pylint: disable=no-member,protected-access
            fields.remove(cls._meta.auto_field.attname)  # pylint: disable=no-member,protected-access
        return fields

    @classmethod
    def get_long_name(cls):
        instance = cls()
        return "%s.%s" % (instance._meta.app_label, instance._meta.object_name)  # pylint: disable=no-member,protected-access

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
    def get_print_fields(cls):
        return cls.get_default_fields()

    @classmethod
    def get_field_by_name(cls, fieldname):
        fieldnames = fieldname.split('.')
        current_meta = cls._meta  # pylint: disable=protected-access,no-member
        for field_name in fieldnames:
            dep_field = current_meta.get_field_by_name(field_name)
            if hasattr(dep_field[0], 'rel') and (dep_field[0].rel is not None):
                current_meta = dep_field[0].rel.to._meta  # pylint: disable=protected-access
        return dep_field

    def evaluate(self, text):
        def eval_sublist(field_list, field_value):
            field_val = []
            for sub_model in field_value.all():
                field_val.append(sub_model.evaluate("#" + ".".join(field_list[1:])))
            return  "{[br/]}".join(field_val)
        from django.db.models.fields import FieldDoesNotExist
        from django.db.models.fields.related import ForeignKey
        value = text
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
                try:
                    dep_field = self._meta.get_field_by_name(field_list[0])  # pylint: disable=no-member,protected-access
                except FieldDoesNotExist:
                    dep_field = None
                if (dep_field is None) or (dep_field[2] and not dep_field[3] and not isinstance(dep_field[0], ForeignKey)):
                    field_val = get_value_converted(field_value, True)
                else:
                    if field_value is None:
                        field_val = ""
                    elif isinstance(dep_field[0], ForeignKey):
                        field_val = field_value.evaluate("#" + ".".join(field_list[1:]))  # pylint: disable=no-member
                    else:
                        field_val = eval_sublist(field_list, field_value)
            value = value.replace(field, six.text_type(field_val))
        return value

    @classmethod
    def get_all_print_fields(cls, with_plugin=True):
        def add_sub_field(field_name, field_title, model):
            for sub_title, sub_name in model.get_all_print_fields(False):
                fields.append(("%s > %s" % (field_title, sub_title), "%s.%s" % (field_name, sub_name)))
        from django.db.models.fields.related import ForeignKey
        fields = []
        item = cls()
        for field_name in cls.get_print_fields():
            if PrintFieldsPlugIn.is_plugin(field_name):
                if with_plugin:
                    fields.extend(PrintFieldsPlugIn.get_plugin(field_name).get_all_print_fields())
            elif field_name[-4:] == '_set':
                child = getattr(item, field_name)
                field_title = child.model._meta.verbose_name  # pylint: disable=protected-access
                add_sub_field(field_name, field_title, child.model)
            else:
                dep_field = item._meta.get_field_by_name(field_name)  # pylint: disable=no-member,protected-access
                field_title = dep_field[0].verbose_name
                if dep_field[2] and not dep_field[3] and not isinstance(dep_field[0], ForeignKey):
                    fields.append((field_title, field_name))
                else:
                    add_sub_field(field_name, field_title, dep_field[0].rel.to)
        return fields

    def get_final_child(self):
        final_child = self
        rel_objs = self._meta.get_all_related_objects()  # pylint: disable=no-member,protected-access
        for rel_obj in rel_objs:
            if (rel_obj.model != type(self)) and (rel_obj.field.name == (self.__class__.__name__.lower() + '_ptr')):
                try:
                    final_child = getattr(self, rel_obj.get_accessor_name()).get_final_child()
                except AttributeError:
                    pass
        return final_child

    def can_delete(self):
        # pylint: disable=unused-argument,no-self-use
        return ''

    def edit(self, xfer):
        # pylint: disable=unused-argument,no-self-use
        return

    def show(self, xfer):
        # pylint: disable=unused-argument,no-self-use
        return

    def before_save(self, xfer):
        # pylint: disable=unused-argument,no-self-use
        return

    def saving(self, xfer):
        # pylint: disable=unused-argument,no-self-use
        return

    class Meta(object):
        # pylint: disable=no-init
        abstract = True

class LucteriosSession(Session, LucteriosModel):

    @classmethod
    def get_default_fields(cls):
        return [(_('username'), 'username'), 'expire_date']

    @property
    def username(self):
        data = self.get_decoded()
        user_id = data.get('_auth_user_id', None)
        if user_id is None:
            return "---"
        else:
            return User.objects.get(id=user_id).username  # pylint: disable=no-member

    class Meta(object):
        # pylint: disable=no-init
        proxy = True
        default_permissions = []
        verbose_name = _('session')
        verbose_name_plural = _('sessions')

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
        # pylint: disable=no-self-use
        return []

    def evaluate(self, text_to_evaluate):
        # pylint: disable=unused-argument,no-self-use
        return ""
