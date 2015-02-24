# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import describ_action, add_sub_menu, FORMTYPE_NOMODAL, FORMTYPE_MODAL, SELECT_SINGLE, SELECT_MULTI
from lucterios.framework.xfergraphic import XferContainerCustom, XferContainerAcknowledge, XferDelete, XferSave
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage, XferCompGrid

from django.contrib.auth.models import User

add_sub_menu("core.right", 'core.admin', "images/gestionDroits.png", _("_Rights manage"), _("To manage users, groups and permissions."), 40)

@describ_action('', FORMTYPE_NOMODAL, 'core.right', _("To manage permissions groupes."))
class GroupList(XferContainerCustom):
    # pylint: disable=too-many-public-methods
    caption = _("_Groups")
    icon = "group.png"

@describ_action('', FORMTYPE_NOMODAL, 'core.right', _("To manage users."))
class UsersList(XferContainerCustom):
    # pylint: disable=too-many-public-methods
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

        users = User.objects.filter(is_active=True)  # pylint: disable=no-member
        grid = XferCompGrid('user_actif')
        grid.set_location(0, 2, 2)
        grid.set_model(users, ['username', 'first_name', 'last_name', 'last_login'])
        grid.add_action(self.request, UsersEdit().get_changed(_("Modify"), "images/edit.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, UsersDisabled().get_changed(_("Disabled"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, UsersDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_MULTI})
        grid.add_action(self.request, UsersEdit().get_changed(_("Add"), "images/add.png"), {'modal':FORMTYPE_MODAL})
        self.add_component(grid)

        lbl = XferCompLabelForm('separator')
        lbl.set_value('')
        lbl.set_location(0, 3)
        self.add_component(lbl)

        lbl = XferCompLabelForm('lbl_inactif')
        lbl.set_value('{[bold]}%s{[/bold]}{[newline]}{[newline]}' % _("List of inactive users"))
        lbl.set_location(0, 4, 2)
        self.add_component(lbl)

        users = User.objects.filter(is_active=False)  # pylint: disable=no-member
        grid = XferCompGrid('user_inactif')
        grid.set_location(0, 5, 2)
        grid.set_model(users, ['username', 'first_name', 'last_name'])
        grid.add_action(self.request, UsersEnabled().get_changed(_("Enabled"), "images/ok.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, UsersDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_MULTI})
        self.add_component(grid)

        self.add_action(XferContainerAcknowledge().get_changed(_('Close'), 'images/close.png'), {})

@describ_action('')
class UsersDelete(XferDelete):
    caption = _("Delete users")
    icon = "user.png"
    model = User
    field_id = ('user_actif', 'user_inactif')

@describ_action('')
class UsersDisabled(XferContainerAcknowledge):
    caption = _("Disabled an user")
    icon = "user.png"
    model = User
    field_id = 'user_actif'

    def fillresponse(self):
        self.item.is_active = False
        self.item.save()

@describ_action('')
class UsersEnabled(XferContainerAcknowledge):
    caption = _("Enabled an user")
    icon = "user.png"
    model = User
    field_id = 'user_inactif'

    def fillresponse(self):
        self.item.is_active = True
        self.item.save()

@describ_action('')
class UsersEdit(XferContainerCustom):
    # pylint: disable=too-many-public-methods
    caption = _("Modify an user")
    icon = "user.png"
    model = User
    field_id = 'user_actif'

    def fillresponse(self):
        if self.is_new:
            self.caption = _("Add an users")
        else:
            self.caption = _("Modify an user")
        img = XferCompImage('img')
        img.set_value('images/user.png')
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        if self.is_new:
            self.fill_from_model(1, 0, False, ['username', 'is_staff', 'is_superuser', 'first_name', 'last_name', 'email'])
        else:
            self.fill_from_model(1, 0, True, ['username', 'date_joined', 'last_login', 'is_active'])
            self.fill_from_model(1, 4, False, ['is_staff', 'is_superuser', 'first_name', 'last_name', 'email'])
        # 'password''groups''user_permissions'

        self.add_action(UsersModify().get_changed(_('Ok'), 'images/ok.png'), {})
        self.add_action(XferContainerAcknowledge().get_changed(_('Cancel'), 'images/cancel.png'), {})

@describ_action('')
class UsersModify(XferSave):
    caption = _("Modify an user")
    icon = "user.png"
    model = User
    field_id = 'user_actif'
