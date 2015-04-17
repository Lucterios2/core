# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.models import LucteriosModel
from lucterios.framework.error import LucteriosException, IMPORTANT
from django.core.validators import MinValueValidator, MaxValueValidator

class Parameter(LucteriosModel):

    name = models.CharField(_('name'), max_length=100, unique=True)
    typeparam = models.IntegerField(choices=((0, _('String')), (1, _('Integer')), (2, _('Real')), (3, _('Boolean')), (4, _('Select'))))
    args = models.CharField(_('arguments'), max_length=200, default="{}")
    value = models.TextField(_('value'), blank=True)

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        default_permissions = ['add', 'change']

class LucteriosUser(User, LucteriosModel):

    lucteriosuser__editfields = {'':['username'], \
                                 _('Informations'):['is_staff', 'is_superuser', 'first_name', 'last_name', 'email'], \
                                 _('Permissions'):['groups', 'user_permissions']}

    lucteriosuser__showfields = ['username', 'date_joined', 'last_login', 'is_staff', 'is_superuser', 'first_name', 'last_name', 'email']

    default_fields = ['username', 'first_name', 'last_name', 'last_login']
    print_fields = ['username']

    groups__titles = [_("Available groups"), _("Chosen groups")]
    user_permissions__titles = [_("Available permissions"), _("Chosen permissions")]

    def edit(self, xfer):
        from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompPassword
        if self.id is not None:  # pylint: disable=no-member
            xfer.change_to_readonly('username')
            obj_username = xfer.get_components('username')
            xfer.filltab_from_model(obj_username.col - 1, obj_username.row + 1, True, ['date_joined', 'last_login'])
        obj_email = xfer.get_components('email')
        xfer.tab = obj_email.tab
        new_row = obj_email.row
        lbl1 = XferCompLabelForm('lbl_password1')
        lbl1.set_location(0, new_row + 1, 1, 1)
        lbl1.set_value_as_name(_("password"))
        xfer.add_component(lbl1)
        lbl2 = XferCompLabelForm('lbl_password2')
        lbl2.set_location(0, new_row + 2, 1, 1)
        lbl2.set_value_as_name(_("password (again)"))
        xfer.add_component(lbl2)
        pwd1 = XferCompPassword('password1')
        pwd1.set_location(1, new_row + 1, 1, 1)
        xfer.add_component(pwd1)
        pwd2 = XferCompPassword('password2')
        pwd2.set_location(1, new_row + 2, 1, 1)
        xfer.add_component(pwd2)
        if xfer.getparam("IDENT_READ") is not None:
            xfer.change_to_readonly('first_name')
            xfer.change_to_readonly('last_name')
            xfer.change_to_readonly('email')
        return LucteriosModel.edit(self, xfer)

    def saving(self, xfer):
        password1 = xfer.getparam('password1')
        password2 = xfer.getparam('password2')
        if password1 != password2:
            raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
        if (password1 is not None) and (password1 != ''):
            self.set_password(password1)
            self.save()

    class Meta(User.Meta):
        # pylint: disable=no-init
        proxy = True
        default_permissions = []

class LucteriosGroup(Group, LucteriosModel):

    lucteriosgroup__editfields = ['name', 'permissions']

    permissions__titles = [_("Available permissions"), _("Chosen permissions")]

    default_fields = ['name']

    class Meta(object):
        # pylint: disable=no-init
        proxy = True
        default_permissions = []
        verbose_name = _('group')
        verbose_name_plural = _('groups')

class Label(LucteriosModel):
    name = models.CharField(_('name'), max_length=100, unique=True)

    page_width = models.IntegerField(_('page width'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    page_height = models.IntegerField(_('page height'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    cell_width = models.IntegerField(_('cell width'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    cell_height = models.IntegerField(_('cell height'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    columns = models.IntegerField(_('number of columns'), validators=[MinValueValidator(1), MaxValueValidator(99)])
    rows = models.IntegerField(_('number of rows'), validators=[MinValueValidator(1), MaxValueValidator(99)])
    left_marge = models.IntegerField(_('left marge'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    top_marge = models.IntegerField(_('top marge'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    horizontal_space = models.IntegerField(_('horizontal space'), validators=[MinValueValidator(1), MaxValueValidator(9999)])
    vertical_space = models.IntegerField(_('vertical space'), validators=[MinValueValidator(1), MaxValueValidator(9999)])

    def __str__(self):
        return self.name

    label__showfields = ['name', ('page_width', 'page_height'), ('cell_width', 'cell_height'), ('columns', 'rows'), ('left_marge', 'top_marge'), ('horizontal_space', 'vertical_space')]
    label__editfields = ['name', ('page_width', 'page_height'), ('cell_width', 'cell_height'), ('columns', 'rows'), ('left_marge', 'top_marge'), ('horizontal_space', 'vertical_space')]
    label__searchfields = ["name", 'columns', 'rows']
    default_fields = ["name", 'columns', 'rows']

    @classmethod
    def get_print_selector(cls):
        selection = []
        for dblbl in cls.objects.all():  # pylint: disable=no-member
            selection.append((dblbl.id, dblbl.name))
        return [('LABEL', _('label'), selection), ('FIRSTLABEL', _('# of first label'), (1, 100, 0))]

    @classmethod
    def get_label_selected(cls, xfer):
        label_id = xfer.getparam('LABEL')
        first_label = xfer.getparam('FIRSTLABEL')
        return cls.objects.get(id=label_id), int(first_label)  # pylint: disable=no-member

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('label')
        verbose_name_plural = _('labels')

class PrintModel(LucteriosModel):
    name = models.CharField(_('name'), max_length=100, unique=False)
    kind = models.IntegerField(_('kind'), choices=((0, _('Listing')), (1, _('Label')), (2, _('Report'))))
    modelname = models.CharField(_('model'), max_length=100)
    value = models.TextField(_('value'), blank=True)

    def __str__(self):
        return self.name

    printmdodel__showfields = ['name', 'kind', 'modelname', 'value']
    printmdodel__editfields = ['name', 'kind', 'modelname', 'value']
    printmdodel__searchfields = ['name', 'kind', 'modelname', 'value']
    default_fields = ["name"]

    def can_delete(self):
        items = PrintModel.objects.filter(kind=self.kind, modelname=self.modelname) # pylint: disable=no-member
        if len(items) <= 1:
            return _('Last model of this kind!')
        return ''

    @classmethod
    def get_print_selector(cls, kind, model):
        selection = []
        for dblbl in cls.objects.filter(kind=kind, modelname=model.get_long_name()):  # pylint: disable=no-member
            selection.append((dblbl.id, dblbl.name))
        if len(selection) == 0:
            raise LucteriosException(IMPORTANT, _('No model!'))
        return [('MODEL', _('model'), selection)]

    @classmethod
    def get_model_selected(cls, xfer):
        try:
            model_id = xfer.getparam('MODEL')
            return cls.objects.get(id=model_id)  # pylint: disable=no-member
        except ValueError:
            raise LucteriosException(IMPORTANT, _('No model selected!'))

    def model_associated(self):
        from django.apps import apps
        return apps.get_model(self.modelname)

    def model_associated_title(self):
        self.model_associated()._meta.verbose_name.title() # pylint: disable=protected-access

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

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('model')
        verbose_name_plural = _('models')
