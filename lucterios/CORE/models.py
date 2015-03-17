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

    class Meta(object):
        # pylint: disable=no-init
        proxy = True
        default_permissions = []
        verbose_name = _('group')
        verbose_name_plural = _('groups')
