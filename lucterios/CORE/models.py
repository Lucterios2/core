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

    groups__titles = [_("Available groups"), _("Chosen groups")]
    user_permissions__titles = [_("Available permissions"), _("Chosen permissions")]

    def edit(self, xfer):
        from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompPassword
        if self.id is not None: # pylint: disable=no-member
            obj_username = xfer.get_components('username')
            xfer.remove_component('username')
            xfer.tab = obj_username.tab
            lbl_un = XferCompLabelForm('username')
            lbl_un.set_value(obj_username.value)
            lbl_un.col = obj_username.col
            lbl_un.row = obj_username.row
            lbl_un.vmin = obj_username.vmin
            lbl_un.hmin = obj_username.hmin
            lbl_un.colspan = obj_username.colspan
            lbl_un.rowspan = obj_username.rowspan
            xfer.add_component(lbl_un)
            xfer.filltab_from_model(lbl_un.col - 1, lbl_un.row + 1, True, ['date_joined', 'last_login'])
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
        return LucteriosModel.edit(self, xfer)

    class Meta(User.Meta):
        # pylint: disable=no-init
        proxy = True
        default_permissions = []

class LucteriosGroup(Group, LucteriosModel):

    lucteriosgroup__editfields = ['name', 'permissions']

    permissions__titles = [_("Available permissions"), _("Chosen permissions")]

    class Meta(Group.Meta):
        # pylint: disable=no-init
        proxy = True
        default_permissions = []
