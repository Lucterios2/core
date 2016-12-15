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
from django.db.models import Q

from lucterios.framework.xferadvance import XferDelete, XferAddEditor, XferListEditor, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.xfercomponents import XferCompLabelForm
from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, SELECT_SINGLE, SELECT_MULTI, ActionsManage
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.signal_and_lock import LucteriosSession
from lucterios.CORE.models import LucteriosGroup, LucteriosUser

MenuManage.add_sub("core.right", 'core.admin', "images/permissions.png",
                   _("_Rights manage"), _("To manage users, groups and permissions."), 40)


@MenuManage.describ('auth.change_group', FORMTYPE_NOMODAL, 'core.right', _("To manage permissions groupes."))
class GroupsList(XferListEditor):
    caption = _("Groups")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('auth.add_group')
class GroupsEdit(XferAddEditor):
    caption_add = _("Add a group")
    caption_modify = _("Modify a group")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'
    locked = True


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('auth.delete_group')
class GroupsDelete(XferDelete):
    caption = _("Delete group")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'


@MenuManage.describ('auth.change_user', FORMTYPE_NOMODAL, 'core.right', _("To manage users."))
class UsersList(XferListEditor):
    caption = _("_Users")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_actif'

    def fillresponse_header(self):
        lbl = XferCompLabelForm('lbl_actifs')
        lbl.set_value_as_name(_("List of active users"))
        lbl.set_location(0, 1, 2)
        self.add_component(lbl)
        self.filter = Q(is_active=True)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.get_components('title').set_value(_('Users of the software'))
        row = self.get_max_row() + 1
        lbl = XferCompLabelForm('separator')
        lbl.set_value('')
        lbl.set_location(0, row)
        self.add_component(lbl)

        lbl = XferCompLabelForm('lbl_inactif')
        lbl.set_value_as_name(_("List of inactive users"))
        lbl.set_location(0, row + 1, 2)
        self.add_component(lbl)
        self.fieldnames = ['username', 'first_name', 'last_name']
        self.fill_grid(row + 1, self.model, 'user_inactif', LucteriosUser.objects.filter(is_active=False))


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='user_actif': gridname == 'user_actif')
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", condition=lambda xfer, gridname='user_actif': gridname == 'user_actif', unique=SELECT_SINGLE)
@MenuManage.describ('auth.add_user')
class UsersEdit(XferAddEditor):
    caption_add = _("Add an users")
    caption_modify = _("Modify an user")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_actif'


@ActionsManage.affect_grid(_("Disabled"), "images/delete.png", condition=lambda xfer, gridname='user_actif': gridname == 'user_actif', unique=SELECT_SINGLE)
@ActionsManage.affect_edit(_("Disabled"), "images/delete.png", condition=lambda xfer: (xfer.item.id is not None) and xfer.item.is_active)
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


@ActionsManage.affect_grid(_("Enabled"), "images/ok.png", condition=lambda xfer, gridname='user_inactif': gridname == 'user_inactif', unique=SELECT_SINGLE, intop=True)
@ActionsManage.affect_edit(_("Enabled"), "images/ok.png", condition=lambda xfer: (xfer.item.id is not None) and not xfer.item.is_active)
@MenuManage.describ('auth.add_user')
class UsersEnabled(XferContainerAcknowledge):
    caption = _("Enabled an user")
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_inactif'

    def fillresponse(self, user_actif=0):
        if user_actif != 0:
            self.item = LucteriosUser.objects.get(id=user_actif)
        self.item.is_active = True
        self.item.save()


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
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


@MenuManage.describ('sessions.change_session', FORMTYPE_NOMODAL, 'core.right', _("To manage session."))
class SessionList(XferListEditor):
    caption = _("Sessions")
    icon = "session.png"
    model = LucteriosSession
    field_id = 'session'


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('sessions.delete_session')
class SessionDelete(XferDelete):
    caption = _("Delete session")
    icon = "session.png"
    model = LucteriosSession
    field_id = 'session'

    def _search_model(self):
        sess_items = self.model.objects.filter(pk__in=self.getparam(self.field_id, ()))
        new_sess_ids = []
        for sess_item in sess_items:
            if sess_item.session_key != self.request.session.session_key:
                new_sess_ids.append(sess_item.id)
        self.items = self.model.objects.filter(pk__in=new_sess_ids)
