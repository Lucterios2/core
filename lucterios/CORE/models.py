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
from zipfile import ZipFile
try:
    from zipfile import BadZipFile
except:
    from zipfile import BadZipfile as BadZipFile
from imp import load_source

from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _
from django.utils import six, translation

from lucterios.framework.models import LucteriosModel
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.xfersearch import get_search_query_from_criteria
from lucterios.framework.signal_and_lock import Signal
from lucterios.framework.filetools import get_tmp_dir, get_user_dir


class Parameter(LucteriosModel):

    name = models.CharField(_('name'), max_length=100, unique=True)
    typeparam = models.IntegerField(choices=((0, _('String')), (1, _(
        'Integer')), (2, _('Real')), (3, _('Boolean')), (4, _('Select'))))
    args = models.CharField(_('arguments'), max_length=200, default="{}")
    value = models.TextField(_('value'), blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def check_and_create(cls, name, typeparam, title, args, value, param_titles=None):
        param, created = Parameter.objects.get_or_create(name=name, typeparam=typeparam)
        if created:
            param.title = title
            param.param_titles = param_titles
            param.args = args
            param.value = value
            param.save()
        return created

    @classmethod
    def change_value(cls, pname, pvalue):
        db_param = cls.objects.get(name=pname)
        if (db_param.typeparam == 3) and isinstance(pvalue, six.text_type):
            db_param.value = six.text_type((pvalue == '1') or (pvalue == 'o'))
        else:
            db_param.value = pvalue
        db_param.save()

    class Meta(object):

        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        default_permissions = ['add', 'change']


class LucteriosUser(User, LucteriosModel):

    @classmethod
    def get_default_fields(cls):
        return ['username', 'first_name', 'last_name', 'last_login']

    @classmethod
    def get_edit_fields(cls):
        return {'': ['username'],
                _('Informations'): ['is_active', 'is_staff', 'is_superuser', 'first_name', 'last_name', 'email'],
                _('Permissions'): ['groups', 'user_permissions']}

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

    groups__titles = [_("Available groups"), _("Chosen groups")]
    user_permissions__titles = [
        _("Available permissions"), _("Chosen permissions")]

    class Meta(User.Meta):

        proxy = True
        default_permissions = []


class LucteriosGroup(Group, LucteriosModel):

    @classmethod
    def get_edit_fields(cls):
        return ['name', 'permissions']

    permissions__titles = [_("Available permissions"), _("Chosen permissions")]

    @classmethod
    def get_default_fields(cls):
        return ['name']

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
    name = models.CharField(_('name'), max_length=100, unique=False)
    kind = models.IntegerField(
        _('kind'), choices=((0, _('Listing')), (1, _('Label')), (2, _('Report'))))
    modelname = models.CharField(_('model'), max_length=100)
    value = models.TextField(_('value'), blank=True)
    mode = models.IntegerField(
        _('mode'), choices=((0, _('Simple')), (1, _('Advanced'))), default=0)
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
        items = PrintModel.objects.filter(
            kind=self.kind, modelname=self.modelname)
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
        return six.text_type(self.model_associated()._meta.verbose_name)

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


def post_after_migrate(sender, **kwargs):
    if ('exception' not in kwargs) and ('app_config' in kwargs) and (kwargs['app_config'].name == 'lucterios.CORE'):
        from django.conf import settings
        translation.activate(settings.LANGUAGE_CODE)
        six.print_('check parameters')
        Signal.call_signal("checkparam")

post_migrate.connect(post_after_migrate)
