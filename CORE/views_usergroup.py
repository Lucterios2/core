# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import describ_action, add_sub_menu, FORMTYPE_NOMODAL, FORMTYPE_MODAL, SELECT_SINGLE, SELECT_MULTI
from lucterios.framework.xfergraphic import XferContainerAbstract, XferContainerCustom
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage, XferCompGrid

from django.contrib.auth.models import User

add_sub_menu("core.right", 'core.admin', "images/gestionDroits.png", _("_Rights manage"), _("To manage users, groups and permissions."), 40)

@describ_action('', FORMTYPE_NOMODAL, 'core.right', _("To manage permissions groupes."))
class GroupList(XferContainerCustom):
    caption = _("_Groups")
    icon = "group.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.right', _("To manage users."))
class UsersList(XferContainerCustom):
    caption = _("_Users")
    icon = "user.png"

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value('images/user.png')
        img.set_location(0, 0)
        self.add_component(img)

        lbl = XferCompLabelForm('title')
        lbl.set_value('{[center]}{[underline]}{[bold]}%s{[/bold]}{[/underline]}{[/center]}' % _('Users of the software'))
        lbl.set_location(1, 0)
        self.add_component(lbl)

        lbl = XferCompLabelForm('lbl_actifs')
        lbl.set_value('{[bold]}%s{[/bold]}{[newline]}{[newline]}' % _("List of active users"))
        lbl.set_location(0, 1, 2)
        self.add_component(lbl)

        users = User.objects.filter(is_active=True) # pylint: disable=no-member
        grid = XferCompGrid('user_actif')
        grid.set_location(0, 2, 2)
        grid.set_model(users, ['username', 'first_name', 'last_name', 'is_staff'])
        grid.add_action(self.request, UsersModify().get_changed(_("Modify"), "images/edit.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, UsersDisabled().get_changed(_("Disabled"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, UsersDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_MULTI})
        grid.add_action(self.request, UsersAdd().get_changed(_("Add"), "images/add.png"), {'modal':FORMTYPE_MODAL})
        self.add_component(grid)

        lbl = XferCompLabelForm('separator')
        lbl.set_value('')
        lbl.set_location(0, 3)
        self.add_component(lbl)

        lbl = XferCompLabelForm('lbl_inactif')
        lbl.set_value('{[bold]}%s{[/bold]}{[newline]}{[newline]}' % _("List of inactive users"))
        lbl.set_location(0, 4, 2)
        self.add_component(lbl)

        users = User.objects.filter(is_active=False) # pylint: disable=no-member
        grid = XferCompGrid('user_inactif')
        grid.set_location(0, 5, 2)
        grid.set_model(users, ['username', 'first_name', 'last_name'])
        grid.add_action(self.request, UsersEnabled().get_changed(_("Enabled"), "images/ok.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, UsersDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_MULTI})
        self.add_component(grid)

        self.add_action(XferContainerAbstract().get_changed(_('Close'), 'images/close.png'), {})

@describ_action('')
class UsersModify(XferContainerCustom):
    caption = _("Modify an user")
    icon = "user.png"

@describ_action('')
class UsersDisabled(XferContainerCustom):
    caption = _("Disabled an user")
    icon = "user.png"

@describ_action('')
class UsersDelete(XferContainerCustom):
    caption = _("Delete users")
    icon = "user.png"

@describ_action('')
class UsersAdd(XferContainerCustom):
    caption = _("Add an users")
    icon = "user.png"

@describ_action('')
class UsersEnabled(XferContainerCustom):
    caption = _("Enabled an user")
    icon = "user.png"
