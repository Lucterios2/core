# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.db import IntegrityError

from lucterios.framework.error import LucteriosException, GRAVE, IMPORTANT
from lucterios.framework.tools import icon_path, ifplural, CLOSE_NO, StubAction, \
    ActionsManage
from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm, XferCompGrid
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom

def get_items_from_filter(model, filter_desc):
    if isinstance(filter_desc, dict):
        items = model.objects.filter(**filter_desc)  # pylint: disable=no-member
    elif isinstance(filter_desc, list):
        items = model.objects.filter(*filter_desc)  # pylint: disable=no-member
    else:
        items = model.objects.all()  # pylint: disable=no-member
    return items

class XferListEditor(XferContainerCustom):
    filter = None

    def fillresponse_header(self):
        # pylint: disable=unused-argument,no-self-use
        return

    def fillresponse(self):
        # pylint: disable=not-callable
        img = XferCompImage('img')
        img.set_value(icon_path(self))
        img.set_location(0, 0)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0)
        self.add_component(lbl)
        self.fillresponse_header()
        row = self.get_max_row()
        items = get_items_from_filter(self.model, self.filter)
        grid = XferCompGrid(self.field_id)
        grid.set_model(items, None, self)
        grid.add_actions(self)
        grid.set_location(0, row + 1, 2)
        grid.set_size(200, 500)
        self.add_component(grid)
        lbl = XferCompLabelForm("nb")
        lbl.set_location(0, row + 2, 2)
        lbl.set_value(_("Total number of %(name)s: %(count)d") % {'name':self.model._meta.verbose_name_plural, 'count':grid.nb_lines})  # pylint: disable=protected-access
        self.add_component(lbl)
        action_list = [('listing', _("Listing"), "images/print.png"), ('label', _("Label"), "images/print.png")]
        for act_type, title, icon in action_list:
            self.add_action(ActionsManage.get_act_changed(self.model.__name__, act_type, title, icon), {'close':CLOSE_NO})

        self.add_action(StubAction(_('Close'), 'images/close.png'), {})

class XferAddEditor(XferContainerCustom):
    caption_add = ''
    caption_modify = ''
    fieldnames = []
    redirect_to_show = True

    def fillresponse(self):
        if self.is_new:
            self.caption = self.caption_add
        else:
            self.caption = self.caption_modify
        img = XferCompImage('img')
        img.set_value(icon_path(self))
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, 0, False)
        self.add_action(self.get_changed(_('Ok'), 'images/ok.png'), {'params':{"SAVE":"YES"}})
        self.add_action(StubAction(_('Cancel'), 'images/cancel.png'), {})

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        if self.getparam("SAVE") != "YES":
            self.fillresponse()
            self._finalize()
            return self.get_response()
        else:
            save = XferSave()
            save.is_view_right = self.is_view_right
            save.model = self.model
            save.field_id = self.field_id
            save.caption = self.caption
            save.raise_except_class = self.__class__
            save.closeaction = self.closeaction
            if self.redirect_to_show:
                save.redirect_action(ActionsManage.get_act_changed(self.model.__name__, 'show', '', ''))
            return save.get(request, *args, **kwargs)

class XferShowEditor(XferContainerCustom):

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(icon_path(self))
        img.set_location(0, 0, 1, 5)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0)
        self.add_component(lbl)
        self.fill_from_model(1, 0, True)
        action_list = [('modify', _("Modify"), "images/edit.png"), ('print', _("Print"), "images/print.png")]
        for act_type, title, icon in action_list:
            self.add_action(ActionsManage.get_act_changed(self.model.__name__, act_type, title, icon), {'close':CLOSE_NO})
        self.add_action(StubAction(_('Close'), 'images/close.png'), {})

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        self.fillresponse()
        self._finalize()
        return self.get_response()

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
        self.items = self.model.objects.filter(pk__in=ids)

    def fillresponse(self):
        # pylint: disable=protected-access
        for item in self.items:
            cant_del_msg = item.can_delete()

            if cant_del_msg != '':
                raise LucteriosException(IMPORTANT, cant_del_msg)

        if self.confirme(ifplural(len(self.items), _("Do you want delete this %(name)s ?") % {'name':self.model._meta.verbose_name}, \
                                    _("Do you want delete those %(nb)s %(name)s ?") % {'nb':len(self.items), 'name':self.model._meta.verbose_name_plural})):
            for item in self.items:
                item.delete()

class XferSave(XferContainerAcknowledge):

    raise_except_class = None

    def fillresponse(self):
        if self.has_changed:
            try:
                self.item.save()
                self.has_changed = False
                if self.fill_manytomany_fields():
                    self.item.save()
            except IntegrityError:
                self.raise_except(_("This record exists yet!"), self.raise_except_class)
        if self.except_msg == '':
            self.item.saving(self)
