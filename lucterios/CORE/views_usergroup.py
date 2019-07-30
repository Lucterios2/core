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
from django.apps.registry import apps
from django.db.models import Q

from lucterios.framework.xferadvance import XferDelete, XferAddEditor, XferListEditor, TITLE_MODIFY, TITLE_DELETE, TITLE_CREATE
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom
from lucterios.framework.xfercomponents import XferCompGrid, XferCompSelect,\
    XferCompCheckList, XferCompButton, XferCompImage, XferCompLabelForm
from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, SELECT_SINGLE, SELECT_MULTI, ActionsManage,\
    FORMTYPE_REFRESH, CLOSE_NO, SELECT_NONE, FORMTYPE_MODAL
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.signal_and_lock import LucteriosSession, Signal
from lucterios.framework.models import LucteriosScheduler, LucteriosLogEntry

from lucterios.CORE.models import LucteriosGroup, LucteriosUser, Parameter, set_auditlog_states
from lucterios.CORE.parameters import Params
from django.contrib.contenttypes.models import ContentType
from django.utils import six

MenuManage.add_sub("core.right", 'core.admin', "images/permissions.png", _("_Rights manage"), _("To manage users, groups and permissions."), 40)


@MenuManage.describ('auth.change_group', FORMTYPE_NOMODAL, 'core.right', _("To manage permissions groupes."))
class GroupsList(XferListEditor):
    caption = _("Groups")
    icon = "group.png"
    model = LucteriosGroup
    field_id = 'group'


@ActionsManage.affect_grid(TITLE_CREATE, "images/new.png")
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
    caption = _('Users of the software')
    icon = "user.png"
    model = LucteriosUser
    field_id = 'user_actif'

    def fillresponse_header(self):
        self.filter = Q(is_active=True)

    def fillresponse_body(self):
        XferListEditor.fillresponse_body(self)
        row = self.get_max_row()
        self.fieldnames = ['username', 'first_name', 'last_name']
        self.fill_grid(row + 1, self.model, 'user_inactif', LucteriosUser.objects.filter(is_active=False))
        self.get_components('user_actif').vmin = -1
        self.get_components('user_actif').description = _("List of active users")
        self.get_components('user_inactif').vmin = 200
        self.get_components('user_inactif').description = _("List of inactive users")


@ActionsManage.affect_grid(TITLE_CREATE, "images/new.png", condition=lambda xfer, gridname='user_actif': gridname == 'user_actif')
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


@MenuManage.describ('sessions.change_session', FORMTYPE_NOMODAL, 'core.right', _("To manage session and tasks."))
class SessionList(XferListEditor):
    caption = _("Sessions & tasks")
    icon = "session.png"
    model = LucteriosSession
    field_id = 'session'

    def fillresponse_header(self):
        self.new_tab(_("Sessions"))

    def fill_tasks(self):
        self.new_tab(_('Tasks'))
        grid = XferCompGrid('tasks')
        grid.no_pager = True
        grid.add_header('name', _('name'))
        grid.add_header('trigger', _('trigger'))
        grid.add_header('nextdate', _('next date'), 'datetime')
        for job_desc in LucteriosScheduler.get_list():
            grid.set_value(job_desc[0], 'name', job_desc[1])
            grid.set_value(job_desc[0], 'trigger', '%s' % job_desc[2])
            grid.set_value(job_desc[0], 'nextdate', job_desc[3])

        grid.set_location(0, self.get_max_row() + 1, 2)
        grid.set_size(200, 500)
        self.add_component(grid)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.fill_tasks()


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
                new_sess_ids.append(sess_item.pk)
        self.items = self.model.objects.filter(pk__in=new_sess_ids)


@MenuManage.describ('sessions.change_session')
@ActionsManage.affect_other(_("Show log"), "images/auditlog.png")
class AuditLogShow(XferContainerCustom):
    caption = _("Show log")
    icon = "auditlog.png"
    model = LucteriosLogEntry
    field_id = 'lucterioslogentry'

    def fillresponse(self, model='', objid=0):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.model = apps.get_model(model)
        if objid != 0:
            self.item = self.model.objects.get(id=objid)
            fieldnames = []
            for fieldname in self.model.get_default_fields():
                if isinstance(fieldname, tuple):
                    fieldnames.append(fieldname[1])
                else:
                    fieldnames.append(fieldname)
            self.fill_from_model(1, 0, True, desc_fields=fieldnames)
            log_items = LucteriosLogEntry.objects.get_for_object(self.item)
        else:
            content_type = ContentType.objects.get_for_model(self.model)
            lbl = XferCompLabelForm('ModelName')
            lbl.set_value_as_header(six.text_type(content_type))
            lbl.description = _("content type")
            lbl.set_location(1, 0, 2)
            self.add_component(lbl)
            log_items = LucteriosLogEntry.objects.get_for_model(self.model)
        grid = XferCompGrid(self.field_id)
        grid.set_model(log_items, None, self)
        grid.set_location(1, self.get_max_row() + 1, 2)
        grid.set_size(200, 500)
        self.add_component(grid)


@MenuManage.describ('sessions.change_session', FORMTYPE_NOMODAL, 'core.right', _("To manage audit logs."))
class AudiLogConfig(XferListEditor):
    caption = _("Log configuration")
    icon = "auditlog.png"
    model = LucteriosLogEntry
    field_id = 'lucterioslogentry'

    def fillresponse_header(self):
        self.new_tab(_("Log entries"))
        row = self.get_max_row() + 1
        type_selected = self.getparam('type_selected', '')
        sel = XferCompSelect('type_selected')
        sel.set_select(LucteriosLogEntry.get_typeselection())
        sel.set_needed(True)
        sel.set_value(type_selected)
        sel.set_location(1, row)
        sel.description = _("content type")
        sel._check_case()
        sel.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(sel)
        self.filter = Q(modelname=sel.value)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        self.new_tab(_("Log setting"))
        row = self.get_max_row() + 1
        sel = XferCompCheckList('AuditLogSetting')
        sel.simple = 2
        sel.set_select(Signal.get_packages_of_signal('auditlog_register'))
        sel.set_value(Params.getvalue('CORE-AuditLog').split())
        sel.set_location(1, row, 3)
        sel.description = _('settings')
        self.add_component(sel)
        btn = XferCompButton('ChangeAL')
        btn.set_action(self.request, AudiLogChange.get_action(TITLE_MODIFY, "images/edit.png"), modal=FORMTYPE_MODAL, close=CLOSE_NO)
        btn.set_location(2, row + 1)
        self.add_component(btn)


@MenuManage.describ('CORE.add_parameter')
class AudiLogChange(XferContainerAcknowledge):
    caption = _("Log setting")
    icon = "auditlog.png"
    model = LucteriosLogEntry
    field_id = 'lucterioslogentry'

    def fillresponse(self, AuditLogSetting=[]):
        Parameter.change_value('CORE-AuditLog', "\n".join(AuditLogSetting))
        Params.clear()
        set_auditlog_states()


@ActionsManage.affect_grid(_('purge'), "images/delete.png", unique=SELECT_NONE)
@MenuManage.describ('CORE.add_parameter')
class AudiLogPurge(XferContainerAcknowledge):
    caption = _("Purge log")
    icon = "auditlog.png"
    model = LucteriosLogEntry
    field_id = 'lucterioslogentry'

    def fillresponse(self, type_selected=''):
        if self.confirme(_('Do you want to purge those logs ?')):
            for log_entry in LucteriosLogEntry.objects.filter(modelname=type_selected):
                log_entry.delete()
