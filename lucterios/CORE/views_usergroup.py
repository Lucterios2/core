# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from lucterios.framework.xferadvance import XferDelete, XferAddEditor
from lucterios.framework.xfergraphic import XferContainerCustom, XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage, XferCompGrid
from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, FORMTYPE_MODAL, SELECT_SINGLE, SELECT_MULTI
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.signal_and_lock import LucteriosSession
from lucterios.CORE.models import LucteriosGroup, LucteriosUser

MenuManage.add_sub("core.right", 'core.admin', "images/gestionDroits.png", _("_Rights manage"), _("To manage users, groups and permissions."), 40)

@MenuManage.describ('auth.change_group', FORMTYPE_NOMODAL, 'core.right', _("To manage permissions groupes."))
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
        lbl.set_value_as_title(_('Existing groups'))
        lbl.set_location(1, 0)
        self.add_component(lbl)

        group = LucteriosGroup.objects.filter()  # pylint: disable=no-member
        grid = XferCompGrid('group')
        grid.set_location(0, 1, 2)
        grid.set_model(group, ['name'])
        grid.add_action(self.request, GroupsEdit().get_changed(_("Modify"), "images/edit.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, GroupsDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, GroupsEdit().get_changed(_("Add"), "images/add.png"), {'modal':FORMTYPE_MODAL})
        self.add_component(grid)

        self.add_action(XferContainerAcknowledge().get_changed(_('Close'), 'images/close.png'), {})

@MenuManage.describ('auth.add_group')
class GroupsEdit(XferAddEditor):
    # pylint: disable=too-many-public-methods
    caption_add = _("Add a group")
    caption_modify = _("Modify a group")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'
    locked = True

@MenuManage.describ('auth.delete_group')
class GroupsDelete(XferDelete):
    caption = _("Delete group")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'

@MenuManage.describ('auth.change_user', FORMTYPE_NOMODAL, 'core.right', _("To manage users."))
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
        lbl.set_value_as_title(_('Users of the software'))
        lbl.set_location(1, 0)
        self.add_component(lbl)

        lbl = XferCompLabelForm('lbl_actifs')
        lbl.set_value_as_name(_("List of active users"))
        lbl.set_location(0, 1, 2)
        self.add_component(lbl)

        users = LucteriosUser.objects.filter(is_active=True)  # pylint: disable=no-member
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
        lbl.set_value_as_name(_("List of inactive users"))
        lbl.set_location(0, 4, 2)
        self.add_component(lbl)

        users = LucteriosUser.objects.filter(is_active=False)  # pylint: disable=no-member
        grid = XferCompGrid('user_inactif')
        grid.set_location(0, 5, 2)
        grid.set_model(users, ['username', 'first_name', 'last_name'])
        grid.add_action(self.request, UsersEnabled().get_changed(_("Enabled"), "images/ok.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        grid.add_action(self.request, UsersDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_MULTI})
        self.add_component(grid)

        self.add_action(XferContainerAcknowledge().get_changed(_('Close'), 'images/close.png'), {})

@MenuManage.describ('auth.delete_user')
class UsersDelete(XferDelete):
    caption = _("Delete users")
    icon = "user.png"
    model = LucteriosUser
    field_id = ('user_actif', 'user_inactif')

    def fillresponse(self):
        for item in self.items:
            if item == self.request.user:
                raise LucteriosException(IMPORTANT, _("You can delete yourself!"))
        XferDelete.fillresponse(self)

@MenuManage.describ('auth.add_user')
class UsersDisabled(XferContainerAcknowledge):
    caption = _("Disabled an user")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_actif'

    def fillresponse(self):
        if self.item == self.request.user:
            raise LucteriosException(IMPORTANT, _("You can disabled yourself!"))
        self.item.is_active = False
        self.item.save()

@MenuManage.describ('auth.add_user')
class UsersEnabled(XferContainerAcknowledge):
    caption = _("Enabled an user")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_inactif'

    def fillresponse(self):
        self.item.is_active = True
        self.item.save()

@MenuManage.describ('auth.add_user')
class UsersEdit(XferAddEditor):
    # pylint: disable=too-many-public-methods
    caption_add = _("Add an users")
    caption_modify = _("Modify an user")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_actif'
    locked = True

    def fillreponse_forsave(self):
        password1 = self.getparam('password1')
        password2 = self.getparam('password2')
        if password1 != password2:
            raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
        if (password1 is not None) and (password1 != ''):
            self.item.set_password(password1)
            self.item.save()

@MenuManage.describ('sessions.change_session', FORMTYPE_NOMODAL, 'core.right', _("To manage session."))
class SessionList(XferContainerCustom):
    # pylint: disable=too-many-public-methods
    caption = _("Sessions")
    icon = "extensions.png"

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value('images/extensions.png')
        img.set_location(0, 0)
        self.add_component(img)

        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(_('Existing sessions'))
        lbl.set_location(1, 0)
        self.add_component(lbl)

        session = LucteriosSession.objects.filter()  # pylint: disable=no-member
        grid = XferCompGrid('session')
        grid.set_location(0, 1, 2)
        grid.set_model(session, [(_('username'), 'username'), 'expire_date'])
        grid.add_action(self.request, SessionDelete().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        self.add_component(grid)

        self.add_action(XferContainerAcknowledge().get_changed(_('Close'), 'images/close.png'), {})

@MenuManage.describ('sessions.delete_session')
class SessionDelete(XferDelete):
    caption = _("Delete session")
    icon = "extensions.png"
    model = LucteriosSession
    field_id = 'session'
