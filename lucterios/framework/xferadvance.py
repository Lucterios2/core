# -*- coding: utf-8 -*-
'''
Advance abstract viewer classes for Lucterios

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
from logging import getLogger

from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError
from django.db.models import Q
from django.utils import six

from lucterios.framework.error import LucteriosException, GRAVE, IMPORTANT
from lucterios.framework.tools import ifplural, WrapAction, ActionsManage,\
    FORMTYPE_MODAL, CLOSE_NO
from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm, XferCompGrid,\
    XferCompButton
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom
from django_fsm import TransitionNotAllowed
from lucterios.framework.models import LucteriosLogEntry


TITLE_OK = _("Ok")
TITLE_CANCEL = _("Cancel")
TITLE_CLOSE = _("Close")
TITLE_EDIT = _("Edit")
TITLE_MODIFY = _("Modify")
TITLE_DELETE = _("Delete")
TITLE_ADD = _("Add")
TITLE_CREATE = _("Create")
TITLE_SAVE = _("Save")
TITLE_CLONE = _('clone')
TITLE_PRINT = _("Print")
TITLE_LISTING = _("Listing")
TITLE_LABEL = _("Label")

TEXT_TOTAL_NUMBER = _("Total number of %(name)s: %(count)d")


def action_list_sorted(item):
    if item[0].caption == TITLE_EDIT:
        return 1
    if item[0].caption == TITLE_MODIFY:
        return 2
    if item[0].caption == TITLE_DELETE:
        return 3
    if item[0].caption == TITLE_CREATE:
        return 4
    if item[0].caption == TITLE_ADD:
        return 4
    if item[0].caption == TITLE_CLONE:
        return 5
    if item[0].caption == TITLE_PRINT:
        return 6
    if item[0].caption == TITLE_LISTING:
        return 7
    if item[0].caption == TITLE_LABEL:
        return 8
    if ('intop' in item[1].keys()) and item[1]['intop']:
        return 0
    else:
        return 100


def add_auditlog_button(xfer, instance, posx, posy):
    if xfer.with_auditlog_btn and LucteriosLogEntry.objects.get_for_object(instance).count() > 0:
        btn = XferCompButton('auditlogbtn')
        btn.set_action(xfer.request, ActionsManage.get_action_url(LucteriosLogEntry.get_long_name(), 'Show', xfer),
                       modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'model': instance.__class__.get_long_name(),
                                                                     'objid': instance.id})
        btn.set_is_mini(True)
        btn.set_location(posx, posy)
        xfer.add_component(btn)


def add_auditlogs_button(xfer, model, posx, posy):
    if xfer.with_auditlog_btn and LucteriosLogEntry.objects.get_for_model(model).count() > 0:
        btn = XferCompButton('auditlogbtn')
        btn.set_action(xfer.request, ActionsManage.get_action_url(LucteriosLogEntry.get_long_name(), 'Show', xfer),
                       modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'model': model.get_long_name()})
        btn.set_is_mini(True)
        btn.set_location(posx, posy)
        xfer.add_component(btn)


class XferListEditor(XferContainerCustom):
    multi_page = True
    with_auditlog_btn = True

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        self.fieldnames = None
        self.filter = None
        self.size_by_page = None

    def fillresponse_header(self):
        return

    def get_items_from_filter(self):
        if isinstance(self.filter, Q) and (len(self.filter.children) > 0):
            items = self.model.objects.filter(self.filter).distinct()
        else:
            items = self.model.objects.all()
        return items

    def fill_grid(self, row, model, field_id, items):
        grid = XferCompGrid(field_id)
        if self.size_by_page is not None:
            grid.size_by_page = self.size_by_page
        if self.multi_page:
            xfer = self
        else:
            xfer = None
        grid.set_model(items, self.fieldnames, xfer)
        grid.add_action_notified(self, model=model)
        grid.set_location(0, row + 1, 2)
        grid.set_size(350, 500)
        self.add_component(grid)

    def fillresponse_body(self):
        self.items = self.get_items_from_filter()
        self.fill_grid(self.get_max_row(), self.model, self.field_id, self.items)

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0)
        self.add_component(lbl)
        self.fillresponse_header()
        self.fillresponse_body()
        add_auditlogs_button(self, self.model, 0, self.get_max_row() + 20)
        if self.model is not None:
            for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_LIST, self, key=action_list_sorted):
                self.add_action(act, **opt)
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


class XferAddEditor(XferContainerCustom):
    caption_add = ''
    caption_modify = ''
    redirect_to_show = 'Show'
    locked = True
    with_auditlog_btn = True

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        if isinstance(self.redirect_to_show, six.text_type):
            self.with_auditlog_btn = (ActionsManage.get_action_url(self.model.get_long_name(), self.redirect_to_show, self) is None)

    def fillresponse(self):
        if self.is_new:
            self.caption = self.caption_add
        else:
            self.caption = self.caption_modify
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, 0, False)
        if len(self.actions) == 0:
            self.add_action(self.get_action(TITLE_OK, 'images/ok.png'), params={"SAVE": "YES"})
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_EDIT, self, key=action_list_sorted):
            self.add_action(act, **opt)
        self.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        add_auditlog_button(self, self.item, 0, max(6, self.get_max_row()) + 20)

    def get_post(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(
            ">> get %s [%s]", request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            if self.getparam("SAVE") != "YES":
                self.fillresponse()
                self._finalize()
                return self.get_response()
            else:
                return self.run_save(request, *args, **kwargs)
        finally:
            getLogger("lucterios.core.request").debug(
                "<< get %s [%s]", request.path, request.user)

    def run_save(self, request, *args, **kwargs):
        save = XferSave()
        save.is_view_right = self.is_view_right
        save.locked = self.locked
        save.model = self.model
        save.field_id = self.field_id
        save.caption = self.caption
        save.raise_except_class = self.__class__
        save.closeaction = self.closeaction
        save.redirect_to_show = self.redirect_to_show
        return save.get(request, *args, **kwargs)


class XferShowEditor(XferContainerCustom):

    locked = True
    readonly = True
    with_auditlog_btn = True

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)

    def fillresponse(self):
        if self.item.id is None:
            raise LucteriosException(IMPORTANT, _("This record not exist!\nRefresh your application."))
        max_row = self.get_max_row() + 1
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, max_row, True)
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_SHOW, self, key=action_list_sorted):
            self.add_action(act, **opt)
        self.add_action(WrapAction(_('Close'), 'images/close.png'))
        add_auditlog_button(self, self.item, 0, max(6, self.get_max_row()) + 20)


class XferDelete(XferContainerAcknowledge):

    def _search_model(self):
        if self.model is None:
            raise LucteriosException(GRAVE, _("No model"))
        if isinstance(self.field_id, tuple):
            for field_id in self.field_id:
                ids = self.getparam(field_id)
                if ids is not None:
                    self.field_id = field_id
                    break
        else:
            ids = self.getparam(self.field_id)
        if ids is None:
            raise LucteriosException(GRAVE, _("No selection"))
        ids = ids.split(';')
        self.items = self.model.objects.filter(pk__in=ids).distinct()

    def fillresponse(self):

        for item in self.items:
            cant_del_msg = item.get_final_child().can_delete()
            if cant_del_msg != '':
                raise LucteriosException(IMPORTANT, cant_del_msg)

        if self.confirme(ifplural(len(self.items), _("Do you want delete this %(name)s ?") % {'name': self.model._meta.verbose_name},
                                  _("Do you want delete those %(nb)s %(name)s ?") % {'nb': len(self.items), 'name': self.model._meta.verbose_name_plural})):
            for item in self.items:
                item.get_final_child().delete()


class XferSave(XferContainerAcknowledge):
    raise_except_class = None
    redirect_to_show = 'Show'

    def fillresponse(self):
        if "SAVE" in self.params.keys():
            del self.params["SAVE"]
        if self.has_changed:
            self.item.editor.before_save(self)
            try:
                self.item.save()
                self.has_changed = False
                if self.fill_manytomany_fields():
                    self.item.save()
            except IntegrityError as err:
                getLogger("lucterios.core.container").info("%s", err)
                six.print_(err)
                self.raise_except(
                    _("This record exists yet!"), self.raise_except_class)
        if self.except_msg == '':
            self.item.editor.saving(self)
        if self.getparam('URL_TO_REDIRECT') is not None:
            url_text = self.getparam('URL_TO_REDIRECT')
            self.redirect_action(WrapAction('', '', url_text=url_text), params={self.field_id: self.item.id})
        elif isinstance(self.redirect_to_show, six.text_type):
            self.redirect_action(ActionsManage.get_action_url(self.model.get_long_name(), self.redirect_to_show, self),
                                 params={self.field_id: self.item.id})


class XferTransition(XferContainerAcknowledge):

    def __init__(self, **kwargs):
        XferContainerAcknowledge.__init__(self, **kwargs)
        self.trans_result = None

    def _confirmed(self, transition):
        try:
            self.trans_result = []
            for item in self.items:
                transit_function = getattr(item, transition)
                setattr(item, 'xfer', self)
                self.trans_result.append(transit_function())
            if len(self.trans_result) == 0:
                self.trans_result = None
            elif len(self.trans_result) == 1:
                self.trans_result = self.trans_result[0]
        except TransitionNotAllowed:
            raise LucteriosException(IMPORTANT, _('Transaction impossible!{[br/]}A condition should not be verified.'))

    def fill_confirm(self, transition, trans):
        if self.confirme(_("Do you want to change this %(name)s to '%(state)s'?") % {'name': self.model._meta.verbose_name, 'state': trans[3]}):
            self._confirmed(transition)

    def fillresponse(self):
        transition = self.getparam('TRANSITION', '')
        if transition in self.trans_list:
            trans = self.trans_list[transition]
            self.caption = trans[5]
            self.fill_confirm(transition, trans)
        else:
            raise LucteriosException(GRAVE, _("Bad transition"))
