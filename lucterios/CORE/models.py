# -*- coding: utf-8 -*-
'''
Describe database model for Django

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
from os.path import dirname, join, exists, isfile
from os import walk, makedirs, unlink
from shutil import rmtree
from zipfile import ZipFile, BadZipFile
from imp import load_source

from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _, ugettext_lazy

from lucterios.framework.models import LucteriosModel, LucteriosVirtualField,\
    LucteriosLogEntry
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.xfersearch import get_search_query_from_criteria
from lucterios.framework.signal_and_lock import Signal
from lucterios.framework.filetools import get_tmp_dir, get_user_dir
from lucterios.framework.tools import set_locale_lang
from lucterios.framework.auditlog import auditlog, LucteriosAuditlogModelRegistry
from django.db.models.query import QuerySet


class AbstractSetting(LucteriosModel):
    TYPE_STRING = 0
    TYPE_INTEGER = 1
    TYPE_REAL = 2
    TYPE_BOOL = 3
    TYPE_SELECT = 4
    TYPE_PASSWORD = 5
    TYPE_META = 6
    LIST_TYPES = ((TYPE_STRING, _('String')), (TYPE_INTEGER, _('Integer')), (TYPE_REAL, _('Real')),
                  (TYPE_BOOL, _('Boolean')), (TYPE_SELECT, _('Select')), (TYPE_PASSWORD, _('Password')), (TYPE_META, _('Meta')))

    typeparam = models.IntegerField(choices=LIST_TYPES, default=0)
    args = models.CharField(_('arguments'), max_length=200, default="{}")
    value = models.TextField(_('value'), blank=True)
    metaselect = models.TextField('meta', blank=True)

    value_txt = LucteriosVirtualField(verbose_name=_('value'), compute_from='get_value_text')
    title = LucteriosVirtualField(verbose_name=_('name'), compute_from='__str__')

    def __str__(self):
        return str(ugettext_lazy(self.name))

    @classmethod
    def _check_and_change(self, created, typeparam, title, args, value, param_titles, meta, param):
        if created:
            param.title = title
            param.typeparam = typeparam
            param.param_titles = param_titles
            param.args = args
            param.value = value
            if meta is not None:
                param.metaselect = meta
            param.save()
        elif param.typeparam != typeparam:
            param.typeparam = typeparam
            param.param_titles = param_titles
            if meta is not None:
                param.metaselect = meta
            param.args = args
            param.save()
        elif meta is not None:
            param.metaselect = meta
            param.save()
        elif param.args != args:
            param.args = args
            param.save()

    def _value_to_int(self):
        try:
            return int(self.value)
        except ValueError:
            if self.value == 'False':
                return 0
            if self.value == 'True':
                return 1
            return int('0' + self.value)

    def _value_to_float(self):
        try:
            return float(self.value)
        except ValueError:
            return float('0' + self.value)

    def _get_text_for_meta(self):
        if ('Multi' in self._correct_args) and self._correct_args['Multi']:
            selection = dict(self._selection_from_object())
            try:
                value_text = "{[br/]}".join([selection[value] if value in selection else value for value in self._correct_value])
            except TypeError:
                value_text = "{[br/]}".join(self._correct_value)
        elif self.meta_info[3] == "id":
            db_obj = self.get_value_object()
            if db_obj is not None:
                value_text = str(db_obj)
            else:
                value_text = "---"
        else:
            selection = dict(self._selection_from_object())
            value_text = selection[self._correct_value] if self._correct_value in selection else self._correct_value
        return value_text

    def _selection_from_object(self):
        from django.apps import apps
        selection = []
        if self.correct_type == Parameter.TYPE_META:  # select in object
            if (self.meta_info[0] != "") and (self.meta_info[1] != ""):
                db_mdl = apps.get_model(self.meta_info[0], self.meta_info[1])
            else:
                db_mdl = None
            if not self.meta_info[4] and not (('Multi' in self._correct_args) and self._correct_args['Multi']):
                if (self.typeparam == Parameter.TYPE_INTEGER) or (self.typeparam == Parameter.TYPE_REAL):
                    selection.append((0, None))
                else:
                    selection.append(('', None))
            if db_mdl is None:
                selection = self.meta_info[2]
            else:
                for obj_item in db_mdl.objects.filter(self.meta_info[2]):
                    selection.append((getattr(obj_item, self.meta_info[3]), str(obj_item)))
        return selection

    def _get_meta_comp(self):
        from lucterios.framework.xfercomponents import XferCompSelect, XferCompCheckList
        if ('Multi' in self._correct_args) and self._correct_args['Multi']:
            param_cmp = XferCompCheckList(self.name)
            param_cmp.simple = 2
        else:
            param_cmp = XferCompSelect(self.name)
        return param_cmp

    def _meta_from_script(self):
        import importlib
        import sys
        self._meta_info = list(self._meta_info)
        sys_modules = dict(sys.modules)
        last = None
        for item_val in self._meta_info[2].split(';'):
            if item_val.startswith('import '):
                module_name = item_val[7:]
                mod_imported = importlib.import_module(module_name)
                sys_modules[module_name] = mod_imported
            else:
                last = eval(item_val, sys_modules)
        self._meta_info[2] = last

    @property
    def meta_info(self):
        if not hasattr(self, "_meta_info"):
            from django.db.models import Q
            self._meta_info = None
            if self.metaselect != "":
                self._meta_info = eval(self.metaselect)
                if (len(self._meta_info) == 5) and isinstance(self._meta_info[0], str) and isinstance(self._meta_info[1], str) and isinstance(self._meta_info[3], str) and isinstance(self._meta_info[4], bool):
                    if isinstance(self._meta_info[2], str):
                        self._meta_from_script()
                    elif not isinstance(self._meta_info[2], Q) and not isinstance(self._meta_info[2], list):
                        self._meta_info = None
                else:
                    self._meta_info = None
        return self._meta_info

    @property
    def correct_type(self):
        if not hasattr(self, "_correct_type"):
            self._correct_type = self.typeparam
            if self.meta_info is not None:  # select in object
                self._correct_type = Parameter.TYPE_META
        return self._correct_type

    def correct_args_value(self):
        if hasattr(self, "_correct_args") and hasattr(self, "_correct_value"):
            return
        self._correct_args = {}
        self._correct_value = None
        try:
            current_args = eval(self.args)
        except Exception:
            current_args = {}
        if self.correct_type == Parameter.TYPE_STRING:  # String
            self._correct_value = str(self.value)
            self._correct_args.update({'Multi': False, 'HyperText': False})
        elif self.typeparam == Parameter.TYPE_INTEGER:  # Integer
            if (self.correct_type == Parameter.TYPE_META) and ('Multi' in current_args) and current_args['Multi']:
                self._correct_value = [int(val) for val in self.value.split(';') if val.strip() != '']
            else:
                self._correct_args.update({'Min': 0, 'Max': 10000000})
                self._correct_value = self._value_to_int()
        elif self.typeparam == Parameter.TYPE_REAL:  # Real
            self._correct_value = self._value_to_float()
            self._correct_args.update({'Min': 0, 'Max': 10000000, 'Prec': 2})
        elif self.correct_type == Parameter.TYPE_BOOL:  # Boolean
            self._correct_value = self.value == 'True'
        elif self.correct_type == Parameter.TYPE_SELECT:  # Select
            self._correct_value = self._value_to_int()
            self._correct_args.update({'Enum': 0})
        else:
            self._correct_value = str(self.value)
        if self.correct_type == Parameter.TYPE_META:
            self._correct_args.update({'Multi': False})
        for arg_key in self._correct_args.keys():
            if arg_key in current_args.keys():
                self._correct_args[arg_key] = current_args[arg_key]

    def get_value_typed(self):
        self.correct_args_value()
        return self._correct_value

    def get_value_text(self):
        value_text = ""
        self.correct_args_value()
        if self.correct_type == Parameter.TYPE_BOOL:  # Boolean
            if self._correct_value:
                value_text = ugettext_lazy("Yes")
            else:
                value_text = ugettext_lazy("No")
        elif self.correct_type == Parameter.TYPE_SELECT:  # Select
            value_text = ugettext_lazy(self.name + ".%d" % self._correct_value)
        elif self.correct_type == Parameter.TYPE_META:  # selected
            value_text = self._get_text_for_meta()
        else:
            value_text = self._correct_value
        return value_text

    def get_value_object(self):
        from json import loads
        from django.apps import apps
        self.correct_args_value()
        if self.correct_type == Parameter.TYPE_STRING:  # String
            try:
                db_obj = loads(self._correct_value)
            except Exception:
                db_obj = None
            return db_obj
        elif (self.correct_type == Parameter.TYPE_META):
            try:
                if ('Multi' in self._correct_args) and self._correct_args['Multi']:
                    query = {self.meta_info[3] + '__in': self._correct_value.split(';')}
                else:
                    query = {self.meta_info[3]: self._correct_value}
                db_mdl = apps.get_model(self.meta_info[0], self.meta_info[1])
                db_obj = db_mdl.objects.filter(**query).first()
            except Exception:
                db_obj = None
            return db_obj
        else:
            return None

    def get_label_comp(self):
        from lucterios.framework.xfercomponents import XferCompLabelForm
        lbl = XferCompLabelForm('lbl_' + self.name)
        lbl.set_value_as_name(ugettext_lazy(self.name))
        return lbl

    def get_write_comp(self):
        from lucterios.framework.xfercomponents import XferCompMemo, XferCompEdit, XferCompFloat, XferCompCheck, XferCompSelect, XferCompPassword
        param_cmp = None
        self.correct_args_value()
        if self.correct_type == Parameter.TYPE_STRING:  # String
            if self._correct_args['Multi']:
                param_cmp = XferCompMemo(self.name)
                param_cmp.with_hypertext = self._correct_args['HyperText']
            else:
                param_cmp = XferCompEdit(self.name)
            param_cmp.set_value(self._correct_value)
        elif self.correct_type == Parameter.TYPE_INTEGER:  # Integer
            param_cmp = XferCompFloat(self.name, minval=self._correct_args['Min'], maxval=self._correct_args['Max'], precval=0)
            param_cmp.set_value(self._correct_value)
            param_cmp.set_needed(True)
        elif self.correct_type == Parameter.TYPE_REAL:  # Real
            param_cmp = XferCompFloat(self.name, minval=self._correct_args['Min'], maxval=self._correct_args['Max'], precval=self._correct_args['Prec'])
            param_cmp.set_value(self._correct_value)
            param_cmp.set_needed(True)
        elif self.correct_type == Parameter.TYPE_BOOL:  # Boolean
            param_cmp = XferCompCheck(self.name)
            param_cmp.set_value(str(self._correct_value))
            param_cmp.set_needed(True)
        elif self.correct_type == Parameter.TYPE_SELECT:  # Select
            param_cmp = XferCompSelect(self.name)
            selection = [(sel_idx, ugettext_lazy(self.name + ".%d" % sel_idx)) for sel_idx in range(0, self._correct_args['Enum'])]
            param_cmp.set_select(selection)
            param_cmp.set_value(self._correct_value)
            param_cmp.set_needed(True)
        elif self.correct_type == Parameter.TYPE_PASSWORD:  # password
            param_cmp = XferCompPassword(self.name)
            param_cmp.security = 0
            param_cmp.set_value('')
        elif self.correct_type == Parameter.TYPE_META:  # select in object
            param_cmp = self._get_meta_comp()
            param_cmp.set_needed(self.meta_info[4])
            param_cmp.set_select(self._selection_from_object())
            param_cmp.set_value(self._correct_value)
        param_cmp.description = str(ugettext_lazy(self.name))
        return param_cmp

    def get_read_comp(self):
        from lucterios.framework.xfercomponents import XferCompLabelForm
        param_cmp = XferCompLabelForm(self.name)
        self.correct_args_value()
        if self.correct_type == Parameter.TYPE_PASSWORD:  # password
            param_cmp.set_value(''.ljust(len(self._correct_value), '*'))
        else:
            param_cmp.set_value(self.get_value_text())
        return param_cmp

    class Meta(object):
        abstract = True


class Parameter(AbstractSetting):

    name = models.CharField(_('name'), max_length=100, unique=True)

    @classmethod
    def check_and_create(cls, name, typeparam, title, args, value, param_titles=None, meta=None):
        param, created = Parameter.objects.get_or_create(name=name)
        cls._check_and_change(created, typeparam, title, args, value, param_titles, meta, param)
        return created

    @classmethod
    def change_value(cls, pname, pvalue):
        db_param = cls.objects.get(name=pname)
        if (db_param.typeparam == cls.TYPE_BOOL) and isinstance(pvalue, str):
            db_param.value = str((pvalue == '1') or (pvalue == 'o'))
        else:
            db_param.value = pvalue
        db_param.save()

    class Meta(object):
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        default_permissions = ['add', 'change']


class Preference(AbstractSetting):

    name = models.CharField(_('name'), max_length=100, unique=False)
    user = models.ForeignKey("LucteriosUser", verbose_name=_('user'), null=True, default=None, on_delete=models.CASCADE)

    @classmethod
    def get_default_fields(cls):
        return ['title', 'value_txt']

    @classmethod
    def get_edit_fields(cls):
        return []

    @classmethod
    def check_and_create(cls, name, typeparam, title, args, value, param_titles=None, meta=None):
        param, created = Preference.objects.get_or_create(name=name, user=None)
        cls._check_and_change(created, typeparam, title, args, value, param_titles, meta, param)
        return created

    @classmethod
    def change_value(cls, pname, pvalue, user=None):
        if isinstance(user, int):
            user = LucteriosUser.objects.get(id=user) if user != 0 else None
        if (user is None) or user.is_anonymous:
            user = None
        try:
            db_param = cls.objects.get(name=pname, user=user)
            if (pvalue is None) and (user is not None):
                db_param.delete()
                return
        except ObjectDoesNotExist:
            if user is None:
                raise LucteriosException(GRAVE, "Preference %s unknown!" % pname)
            elif pvalue is None:
                return
            init_param = cls.objects.get(name=pname, user=None)
            db_param = cls.objects.create(name=pname, user=user, typeparam=init_param.typeparam, args=init_param.args, metaselect=init_param.metaselect)
        if (db_param.typeparam == cls.TYPE_BOOL) and isinstance(pvalue, str):
            db_param.value = str((pvalue == '1') or (pvalue == 'o'))
        else:
            db_param.value = pvalue
        db_param.save()

    @classmethod
    def get_value(cls, pname, user=None):
        if isinstance(user, int):
            user = LucteriosUser.objects.get(id=user)
        if (user is None) or user.is_anonymous:
            user = None
        try:
            query = models.Q(name=pname) & (models.Q(user=user) | models.Q(user=None))
            db_param = None
            for param_item in cls.objects.filter(query).order_by('name', '-user'):
                if (db_param is None) or (param_item.user is not None):
                    db_param = param_item
            if db_param is None:
                raise LucteriosException(GRAVE, "Preference %s unknown!" % pname)
        except Exception:
            raise LucteriosException(GRAVE, "Preference %s not found!" % pname)
        return db_param.get_value_typed()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.name != '':
            AbstractSetting.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        ordering = ['name']
        verbose_name = _('preference')
        verbose_name_plural = _('preferences')
        default_permissions = ['add', 'change']


class LucteriosUser(User, LucteriosModel):

    class PreferenceUser(QuerySet):

        def __init__(self, model=None, query=None, using=None, hints=None):
            QuerySet.__init__(self, model=Preference, query=query, using=using, hints=hints)
            self._result_cache = None
            self.pt_id = 0
            self.model._meta.pk = Preference()._meta.pk
            self.user = self._hints['user']

        def add_pref(self, new_pref):
            if new_pref.user is None:
                self._result_cache.append(Preference(id=new_pref.name, name=new_pref.name, user=self.user,
                                                     value=new_pref.value, typeparam=new_pref.typeparam,
                                                     args=new_pref.args, metaselect=new_pref.metaselect))
            else:
                new_pref.id = new_pref.name
                self._result_cache.append(new_pref)

        def _fetch_all(self):
            if self._result_cache is None:
                self._result_cache = []
                last_pref = None
                for pref in Preference.objects.filter(models.Q(user=self.user) | models.Q(user=None)).order_by('name', '-user'):
                    if last_pref is None:
                        last_pref = pref
                    elif last_pref.name != pref.name:
                        self.add_pref(last_pref)
                        last_pref = pref
                    elif pref.user is not None:
                        last_pref = pref
            if last_pref is not None:
                self.add_pref(last_pref)

    @classmethod
    def get_default_fields(cls):
        return ['username', 'first_name', 'last_name', 'last_login']

    @classmethod
    def get_edit_fields(cls):
        return {'': ['username'],
                _('Informations'): ['is_active', 'is_staff', 'is_superuser', 'first_name', 'last_name', 'email'],
                _('Permissions'): ['groups', 'user_permissions'],
                _('Preferences'): ['preferences_set']}

    @classmethod
    def get_show_fields(cls):
        return ['username', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser', 'first_name', 'last_name', 'email']

    @classmethod
    def get_print_fields(cls):
        return ['username']

    def generate_password(self):
        import random
        letter_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@$#%&*+='
        password = ''.join(random.choice(letter_string)
                           for _ in range(random.randint(8, 12)))
        if Signal.call_signal("send_connection", self.email, self.username, password) > 0:
            self.set_password(password)
            self.save()
            return True
        else:
            return False

    @property
    def preferences_set(self):
        return self.PreferenceUser(hints={'user': self})

    class Meta(User.Meta):

        proxy = True
        default_permissions = []


class LucteriosGroup(Group, LucteriosModel):

    @classmethod
    def get_edit_fields(cls):
        return ['name', 'permissions']

    @classmethod
    def get_default_fields(cls):
        return ['name']

    @classmethod
    def redefine_generic(cls, name, *args):
        generic_group, _created = LucteriosGroup.objects.get_or_create(name=name)
        generic_group.permissions.clear()
        for premission_set in args:
            for perm_item in premission_set:
                generic_group.permissions.add(perm_item)
        return generic_group

    class Meta(object):

        proxy = True
        default_permissions = []
        verbose_name = _('group')
        verbose_name_plural = _('groups')


class Label(LucteriosModel):
    name = models.CharField(_('name'), max_length=100, unique=True)

    page_width = models.IntegerField(
        _('page width'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    page_height = models.IntegerField(
        _('page height'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    cell_width = models.IntegerField(
        _('cell width'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    cell_height = models.IntegerField(
        _('cell height'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    columns = models.IntegerField(
        _('number of columns'), validators=[MinValueValidator(1), MaxValueValidator(99)])
    rows = models.IntegerField(
        _('number of rows'), validators=[MinValueValidator(1), MaxValueValidator(99)])
    left_marge = models.IntegerField(
        _('left marge'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    top_marge = models.IntegerField(
        _('top marge'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    horizontal_space = models.IntegerField(
        _('horizontal space'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    vertical_space = models.IntegerField(
        _('vertical space'), validators=[MinValueValidator(1), MaxValueValidator(9999)])

    def __str__(self):
        return self.name

    @classmethod
    def get_show_fields(cls):
        return ['name', ('columns', 'rows'), ('page_width', 'page_height'), ('cell_width', 'cell_height'), ('left_marge', 'top_marge'), ('horizontal_space', 'vertical_space')]

    @classmethod
    def get_default_fields(cls):
        return ["name", 'columns', 'rows']

    @classmethod
    def get_print_selector(cls):
        selection = []
        for dblbl in cls.objects.all():
            selection.append((dblbl.id, dblbl.name))
        return [('LABEL', _('label'), selection), ('FIRSTLABEL', _('# of first label'), (1, 100, 0))]

    @classmethod
    def get_label_selected(cls, xfer):
        label_id = xfer.getparam('LABEL')
        first_label = xfer.getparam('FIRSTLABEL')
        return cls.objects.get(id=label_id), int(first_label)

    class Meta(object):

        verbose_name = _('label')
        verbose_name_plural = _('labels')


class PrintModel(LucteriosModel):
    KIND_LISTING = 0
    KIND_LABEL = 1
    KIND_REPORT = 2
    KIND_LIST = ((KIND_LISTING, _('Listing')), (KIND_LABEL, _('Label')), (KIND_REPORT, _('Report')))

    MODE_SIMPLE = 0
    MODE_ADVANCED = 1
    MODE_LIST = ((MODE_SIMPLE, _('Simple')), (MODE_ADVANCED, _('Advanced')))

    name = models.CharField(_('name'), max_length=100, unique=False)
    kind = models.IntegerField(_('kind'), choices=KIND_LIST)
    modelname = models.CharField(_('model'), max_length=100)
    value = models.TextField(_('value'), blank=True)
    mode = models.IntegerField(_('mode'), choices=MODE_LIST, default=MODE_SIMPLE)
    is_default = models.BooleanField(verbose_name=_('default'), default=False)

    def __str__(self):
        return self.name

    @classmethod
    def get_show_fields(cls):
        return ['name', 'kind', 'mode', 'modelname', 'value']

    @classmethod
    def get_search_fields(cls):
        return['name', 'kind', 'mode', 'modelname', 'value']

    @classmethod
    def get_default_fields(cls):
        return ["name"]

    def can_delete(self):
        items = PrintModel.objects.filter(kind=self.kind, modelname=self.modelname)
        if len(items) <= 1:
            return _('Last model of this kind!')
        return ''

    @classmethod
    def get_print_selector(cls, kind, model):
        selection = []
        for dblbl in cls.objects.filter(kind=kind, modelname=model.get_long_name()):
            selection.append((dblbl.id, dblbl.name))
        if len(selection) == 0:
            raise LucteriosException(IMPORTANT, _('No model!'))
        return [('MODEL', _('model'), selection)]

    @classmethod
    def get_print_default(cls, kind, model, raiseerror=True):
        models = cls.objects.filter(kind=kind, modelname=model.get_long_name(), is_default=True)
        if len(models) > 0:
            return models[0].id
        if raiseerror:
            raise LucteriosException(IMPORTANT, _('No default model for %s!') % model._meta.verbose_name)
        return 0

    @classmethod
    def get_model_selected(cls, xfer):
        try:
            model_id = xfer.getparam('MODEL')
            return cls.objects.get(id=model_id)
        except ValueError:
            raise LucteriosException(IMPORTANT, _('No model selected!'))

    def clone(self):
        self.name = _("copy of %s") % self.name
        self.id = None
        self.is_default = False
        self.save()

    def change_has_default(self):
        if not self.is_default:
            all_model = PrintModel.objects.filter(kind=self.kind, modelname=self.modelname)
            for model_item in all_model:
                model_item.is_default = False
                model_item.save()
            self.is_default = True
            self.save()

    def model_associated(self):
        from django.apps import apps
        return apps.get_model(self.modelname)

    def model_associated_title(self):
        return str(self.model_associated()._meta.verbose_name)

    @property
    def page_width(self):
        model_values = self.value.split('\n')
        return int(model_values[0])

    @property
    def page_height(self):
        model_values = self.value.split('\n')
        return int(model_values[1])

    @property
    def columns(self):
        columns = []
        model_values = self.value.split('\n')
        del model_values[0]
        del model_values[0]
        for col_value in model_values:
            if col_value != '':
                new_col = col_value.split('//')
                new_col[0] = int(new_col[0])
                columns.append(new_col)
        return columns

    def change_listing(self, page_width, page_heigth, columns):
        self.value = "%d\n%d\n" % (page_width, page_heigth)
        for column in columns:
            self.value += "%d//%s//%s\n" % column

    def load_model(self, module, name=None, check=False, is_default=False):
        from django.utils.module_loading import import_module
        try:
            if name is None:
                print_mod = load_source('modelprint', module)
            else:
                print_mod = import_module("%s.printmodel.%s" % (module, name))
            if self.id is None:
                self.name = getattr(print_mod, "name")
            elif check and (self.kind != getattr(print_mod, "kind")) and (self.modelname != getattr(print_mod, "modelname")):
                return False
            if is_default is not None:
                self.is_default = is_default
            self.kind = getattr(print_mod, "kind")
            self.modelname = getattr(print_mod, "modelname")
            self.value = getattr(print_mod, "value", "")
            self.mode = getattr(print_mod, "mode", 0)
            self.save()
            return True
        except ImportError:
            return False

    def import_file(self, file):
        content = ''
        try:
            try:
                with ZipFile(file, 'r') as zip_ref:
                    content = zip_ref.extract('printmodel', path=get_tmp_dir())
            except (KeyError, BadZipFile):
                raise LucteriosException(IMPORTANT, _('Model file is invalid!'))
            return self.load_model(content, check=True)
        finally:
            if isfile(content):
                unlink(content)

    def extract_file(self):
        tmp_dir = join(get_tmp_dir(), 'zipfile')
        download_file = join(get_user_dir(), 'extract-%d.mdl' % self.id)
        if exists(tmp_dir):
            rmtree(tmp_dir)
        makedirs(tmp_dir)
        try:
            content_model = "# -*- coding: utf-8 -*-\n\n"
            content_model += "from __future__ import unicode_literals\n\n"
            content_model += 'name = "%s"\n' % self.name
            content_model += 'kind = %d\n' % int(self.kind)
            content_model += 'modelname = "%s"\n' % self.modelname
            content_model += 'value = """%s"""\n' % self.value
            content_model += 'mode = %d\n' % int(self.mode)
            with ZipFile(download_file, 'w') as zip_ref:
                zip_ref.writestr('printmodel', content_model)
        finally:
            if exists(tmp_dir):
                rmtree(tmp_dir)
        return 'extract-%d.mdl' % self.id

    @classmethod
    def get_default_model(cls, module, modelname=None, kind=None):
        models = []
        from django.utils.module_loading import import_module
        try:
            dir_pack = dirname(import_module("%s.printmodel" % module).__file__)
            for _dir, _dirs, filenames in walk(dir_pack):
                for filename in filenames:
                    if (filename[-3:] == ".py") and not filename.startswith('_'):
                        mod_name = filename[:-3]
                        print_mod = import_module("%s.printmodel.%s" % (module, mod_name))
                        if ((modelname is None) or (getattr(print_mod, "modelname") == modelname)) and ((kind is None) or (getattr(print_mod, "kind") == kind)):
                            models.append((mod_name, getattr(print_mod, "name")))
        except ImportError:
            pass
        return models

    class Meta(object):
        verbose_name = _('model')
        verbose_name_plural = _('models')


class SavedCriteria(LucteriosModel):
    name = models.CharField(_('name'), max_length=100, unique=False)
    modelname = models.CharField(_('model'), max_length=100)
    criteria = models.TextField(_('criteria'), blank=True)

    def __str__(self):
        return self.name

    @property
    def model_title(self):
        from django.apps import apps
        return apps.get_model(self.modelname)._meta.verbose_name.title()

    @property
    def criteria_desc(self):
        from django.apps import apps
        result_criteria = get_search_query_from_criteria(
            self.criteria, apps.get_model(self.modelname))
        return "{[br/]}".join(tuple(result_criteria[1].values()))

    @classmethod
    def get_show_fields(cls):
        return ['modelname', 'name', 'criteria']

    @classmethod
    def get_edit_fields(cls):
        return ['modelname', 'name', 'criteria']

    @classmethod
    def get_default_fields(cls):
        return ['name', (_('model'), 'model_title'), (_('criteria'), 'criteria_desc')]

    class Meta(object):
        verbose_name = _('Saved criteria')
        verbose_name_plural = _('Saved criterias')
        default_permissions = []


@Signal.decorate('checkparam')
def core_checkparam():
    Parameter.check_and_create(name='CORE-GUID', typeparam=0, title=_("CORE-GUID"), args="{'Multi':False}", value='')
    Parameter.check_and_create(name='CORE-connectmode', typeparam=4, title=_("CORE-connectmode"), args="{'Enum':3}", value='0',
                               param_titles=(_("CORE-connectmode.0"), _("CORE-connectmode.1"), _("CORE-connectmode.2")))
    Parameter.check_and_create(name='CORE-Wizard', typeparam=3, title=_("CORE-Wizard"), args="{}", value='True')
    Parameter.check_and_create(name='CORE-MessageBefore', typeparam=0, title=_("CORE-MessageBefore"), args="{'Multi':True, 'HyperText':True}", value='')
    Parameter.check_and_create(name='CORE-AuditLog', typeparam=0, title=_("CORE-AuditLog"), args="{'Multi':True, 'HyperText':True}", value='')
    Parameter.check_and_create(name='CORE-PluginPermission', typeparam=0, title=_("CORE-PluginPermission"), args="{'Multi':True, 'HyperText':False}", value='{}')

    LucteriosGroup.redefine_generic(_("# Core (administrator)"), Parameter.get_permission(True, True, True), SavedCriteria.get_permission(True, True, True), LucteriosLogEntry.get_permission(True, True, True),
                                    LucteriosGroup.get_permission(True, True, True), LucteriosUser.get_permission(True, True, True),
                                    Label.get_permission(True, True, True), PrintModel.get_permission(True, True, True))


def set_auditlog_states():
    from lucterios.CORE.parameters import Params
    try:
        LucteriosAuditlogModelRegistry.set_state_packages(Params.getvalue('CORE-AuditLog').split())
    except LucteriosException:
        pass


@Signal.decorate('auditlog_register')
def core_auditlog_register():
    auditlog.register(Parameter, include_fields=['value_txt'])
    auditlog.register(LucteriosUser)
    auditlog.register(LucteriosGroup)
    set_auditlog_states()


def post_after_migrate(sender, **kwargs):
    if ('exception' not in kwargs) and ('app_config' in kwargs) and (kwargs['app_config'].name == 'lucterios.CORE'):
        from django.conf import settings
        set_locale_lang(settings.LANGUAGE_CODE)
        print('check parameters')
        Signal.call_signal("checkparam")
        print('convert data')
        Signal.call_signal("convertdata")


post_migrate.connect(post_after_migrate)
