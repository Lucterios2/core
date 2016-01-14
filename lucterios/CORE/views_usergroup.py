# -*- coding: utf-8 -*-
'''
Views for manage user, group, permission and session in Lucterios

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

from django.utils.translation import ugettext_lazy as _

from lucterios.framework.xferadvance import XferDelete, XferAddEditor, XferListEditor
from lucterios.framework.xfergraphic import XferContainerCustom, XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompImage, XferCompGrid
from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, FORMTYPE_MODAL, SELECT_SINGLE, SELECT_MULTI, \
    WrapAction, ActionsManage, SELECT_NONE
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.signal_and_lock import LucteriosSession
from lucterios.CORE.models import LucteriosGroup, LucteriosUser

MenuManage.add_sub("core.right", 'core.admin', "images/permissions.png",
                   _("_Rights manage"), _("To manage users, groups and permissions."), 40)


@ActionsManage.affect('LucteriosGroup', 'edit', 'add')
@MenuManage.describ('auth.add_group')
class GroupsEdit(XferAddEditor):
    caption_add = _("Add a group")
    caption_modify = _("Modify a group")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'
    locked = True


@ActionsManage.affect('LucteriosGroup', 'delete')
@MenuManage.describ('auth.delete_group')
class GroupsDelete(XferDelete):
    caption = _("Delete group")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'


@MenuManage.describ('auth.change_group', FORMTYPE_NOMODAL, 'core.right', _("To manage permissions groupes."))
class GroupsList(XferListEditor):
    caption = _("Groups")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'


@MenuManage.describ('auth.change_user', FORMTYPE_NOMODAL, 'core.right', _("To manage users."))
class UsersList(XferContainerCustom):
    caption = _("_Users")
    icon = "user.png"
    model = LucteriosUser

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
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

        users = LucteriosUser.objects.filter(
            is_active=True)
        grid = XferCompGrid('user_actif')
        grid.set_location(0, 2, 2)
        grid.set_model(users, None)
        grid.add_action(self.request, UsersEdit.get_action(
            _("Modify"), "images/edit.png"), {'modal': FORMTYPE_MODAL, 'unique': SELECT_SINGLE})
        grid.add_action(self.request, UsersDisabled.get_action(
            _("Disabled"), "images/delete.png"), {'modal': FORMTYPE_MODAL, 'unique': SELECT_SINGLE})
        grid.add_action(self.request, UsersDelete.get_action(
            _("Delete"), "images/delete.png"), {'modal': FORMTYPE_MODAL, 'unique': SELECT_MULTI})
        grid.add_action(self.request, UsersEdit.get_action(
            _("Add"), "images/add.png"), {'modal': FORMTYPE_MODAL, 'unique': SELECT_NONE})
        self.add_component(grid)

        lbl = XferCompLabelForm('separator')
        lbl.set_value('')
        lbl.set_location(0, 3)
        self.add_component(lbl)

        lbl = XferCompLabelForm('lbl_inactif')
        lbl.set_value_as_name(_("List of inactive users"))
        lbl.set_location(0, 4, 2)
        self.add_component(lbl)

        users = LucteriosUser.objects.filter(
            is_active=False)
        grid = XferCompGrid('user_inactif')
        grid.set_location(0, 5, 2)
        grid.set_model(users, ['username', 'first_name', 'last_name'])
        grid.add_action(self.request, UsersEnabled.get_action(
            _("Enabled"), "images/ok.png"), {'modal': FORMTYPE_MODAL, 'unique': SELECT_SINGLE})
        grid.add_action(self.request, UsersDelete.get_action(
            _("Delete"), "images/delete.png"), {'modal': FORMTYPE_MODAL, 'unique': SELECT_MULTI})
        self.add_component(grid)

        self.add_action(WrapAction(_('Close'), 'images/close.png'), {})


@ActionsManage.affect('LucteriosUser', 'delete')
@MenuManage.describ('auth.delete_user')
class UsersDelete(XferDelete):
    caption = _("Delete users")
    icon = "user.png"
    model = LucteriosUser
    field_id = ('user_actif', 'user_inactif')

    def fillresponse(self):
        for item in self.items:
            if item == self.request.user:
                raise LucteriosException(
                    IMPORTANT, _("You can delete yourself!"))
        XferDelete.fillresponse(self)


@MenuManage.describ('auth.add_user')
class UsersDisabled(XferContainerAcknowledge):
    caption = _("Disabled an user")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_actif'

    def fillresponse(self):
        if self.item == self.request.user:
            raise LucteriosException(
                IMPORTANT, _("You can disabled yourself!"))
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


@ActionsManage.affect('LucteriosUser', 'add', 'edit')
@MenuManage.describ('auth.add_user')
class UsersEdit(XferAddEditor):
    caption_add = _("Add an users")
    caption_modify = _("Modify an user")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_actif'


@ActionsManage.affect('LucteriosSession', 'delete')
@MenuManage.describ('sessions.delete_session')
class SessionDelete(XferDelete):
    caption = _("Delete session")
    icon = "session.png"
    model = LucteriosSession
    field_id = 'session'


@MenuManage.describ('sessions.change_session', FORMTYPE_NOMODAL, 'core.right', _("To manage session."))
class SessionList(XferListEditor):
    caption = _("Sessions")
    icon = "session.png"
    model = LucteriosSession
    field_id = 'session'
