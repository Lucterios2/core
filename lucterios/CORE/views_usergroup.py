# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import describ_action, add_sub_menu, FORMTYPE_NOMODAL, FORMTYPE_MODAL, SELECT_SINGLE, SELECT_MULTI
from lucterios.framework.xfergraphic import XferContainerCustom, XferContainerAcknowledge, XferDelete, XferSave
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage, XferCompGrid, XferCompPassword

from django.contrib.auth.models import User, Group
from django.utils import six
from lucterios.framework.error import LucteriosException, IMPORTANT

add_sub_menu("core.right", 'core.admin', "images/gestionDroits.png", _("_Rights manage"), _("To manage users, groups and permissions."), 40)

@describ_action('auth.change_group', FORMTYPE_NOMODAL, 'core.right', _("To manage permissions groupes."))
class GroupsList(XferContainerCustom):
    # pylint: disable=too-many-public-methods
    caption = _("_Groups")
    icon = "group.png"

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value('images/group.png')
        img.set_location(0, 0)
        self.add_component(img)

        lbl = XferCompLabelForm('title')
        lbl.set_value('{[center]}{[underline]}{[bold]}%s{[/bold]}{[/underline]}{[/center]}' % _('Existing groups'))
        lbl.set_location(1, 0)
        self.add_component(lbl)

        group = Group.objects.filter()  # pylint: disable=no-member
        grid = XferCompGrid('group')
        grid.set_location(0, 1, 2)
        grid.set_model(group, ['name'])
        grid.add_action(self.request, GroupsEdit().get_changed(_("Modify"), "images/edit.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, GroupsDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, GroupsEdit().get_changed(_("Add"), "images/add.png"), {'modal':FORMTYPE_MODAL})
        self.add_component(grid)

        self.add_action(XferContainerAcknowledge().get_changed(_('Close'), 'images/close.png'), {})

@describ_action('auth.add_group')
class GroupsEdit(XferContainerCustom):
    # pylint: disable=too-many-public-methods
    caption = _("Modify a group")
    icon = "group.png"
    model = Group
    field_id = 'group'

    def fillresponse(self):
        if self.is_new:
            self.caption = _("Add a group")
        else:
            self.caption = _("Modify a group")
        img = XferCompImage('img')
        img.set_value('images/group.png')
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, 0, False, ['name'])
        self.selector_from_model(1, 1, 'permissions', _("Available permissions"), _("Chosen permissions"))

        self.add_action(GroupsModify().get_changed(_('Ok'), 'images/ok.png'), {})
        self.add_action(XferContainerAcknowledge().get_changed(_('Cancel'), 'images/cancel.png'), {})

@describ_action('auth.delete_group')
class GroupsDelete(XferDelete):
    caption = _("Delete group")
    icon = "group.png"
    model = Group
    field_id = 'group'

@describ_action('auth.add_group')
class GroupsModify(XferSave):
    caption = _("Modify a group")
    icon = "group.png"
    model = Group
    field_id = 'group'

@describ_action('auth.change_user', FORMTYPE_NOMODAL, 'core.right', _("To manage users."))
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

@describ_action('auth.delete_user')
class UsersDelete(XferDelete):
    caption = _("Delete users")
    icon = "user.png"
    model = User
    field_id = ('user_actif', 'user_inactif')

    def fillresponse(self):
        for item in self.items:
            if item == self.request.user:
                raise LucteriosException(IMPORTANT, _("You can delete yourself!"))
        XferDelete.fillresponse(self)

@describ_action('auth.add_user')
class UsersDisabled(XferContainerAcknowledge):
    caption = _("Disabled an user")
    icon = "user.png"
    model = User
    field_id = 'user_actif'

    def fillresponse(self):
        if self.item == self.request.user:
            raise LucteriosException(IMPORTANT, _("You can disabled yourself!"))
        self.item.is_active = False
        self.item.save()

@describ_action('auth.add_user')
class UsersEnabled(XferContainerAcknowledge):
    caption = _("Enabled an user")
    icon = "user.png"
    model = User
    field_id = 'user_inactif'

    def fillresponse(self):
        self.item.is_active = True
        self.item.save()

@describ_action('auth.add_user')
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
        img.set_location(0, 0, 1, 3)
        self.add_component(img)
        if self.is_new:
            self.fill_from_model(1, 0, False, ['username'])
        else:
            self.fill_from_model(1, 0, True, ['username', 'date_joined', 'last_login'])

        self.new_tab(_('Informations'))
        self.fill_from_model(0, 0, False, ['is_staff', 'is_superuser', 'first_name', 'last_name', 'email'])
        lbl = XferCompLabelForm('lbl_password1')
        lbl.set_location(0, 5, 1, 1)
        lbl.set_value(six.text_type('{[bold]}%s{[/bold]}') % _("password"))
        self.add_component(lbl)
        lbl = XferCompLabelForm('lbl_password2')
        lbl.set_location(0, 6, 1, 1)
        lbl.set_value(six.text_type('{[bold]}%s{[/bold]}') % _("password (again)"))
        self.add_component(lbl)
        pwd = XferCompPassword('password1')
        pwd.set_location(1, 5, 1, 1)
        self.add_component(pwd)
        pwd = XferCompPassword('password2')
        pwd.set_location(1, 6, 1, 1)
        self.add_component(pwd)

        self.new_tab(_('Permissions'))
        self.selector_from_model(0, 0, 'groups', _("Available groups"), _("Chosen groups"))
        self.selector_from_model(0, 5, 'user_permissions', _("Available permissions"), _("Chosen permissions"))
        # 'password''groups''user_permissions'

        self.add_action(UsersModify().get_changed(_('Ok'), 'images/ok.png'), {})
        self.add_action(XferContainerAcknowledge().get_changed(_('Cancel'), 'images/cancel.png'), {})

@describ_action('auth.add_user')
class UsersModify(XferSave):
    caption = _("Modify an user")
    icon = "user.png"
    model = User
    field_id = 'user_actif'

    def fillresponse(self, password1='', password2=''):
        XferSave.fillresponse(self)
        if password1 != password2:
            raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
        if password1 != '':
            self.item.set_password(password1)
            self.item.save()
