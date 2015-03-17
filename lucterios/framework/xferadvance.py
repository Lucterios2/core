# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom
from django.db import IntegrityError
from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework.tools import icon_path, ifplural, CLOSE_NO, \
    FORMTYPE_MODAL, SELECT_SINGLE, SELECT_NONE, SubAction
from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm, \
    XferCompGrid

class XferListEditor(XferContainerCustom):
    field_names = []
    filter = None
    show_class = None
    edit_class = None
    add_class = None
    del_class = None

    def fillresponse_header(self):
        # pylint: disable=unused-argument,no-self-use
        return

    def fillresponse_footer(self):
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
        if isinstance(self.filter, dict):
            items = self.model.objects.filter(**self.filter)  # pylint: disable=no-member
        elif isinstance(self.filter, list):
            items = self.model.objects.filter(*self.filter)  # pylint: disable=no-member
        else:
            items = self.model.objects.all()  # pylint: disable=no-member
        grid = XferCompGrid(self.field_id)
        grid.set_model(items, self.field_names, self)
        if self.show_class is not None:
            grid.add_action(self.request, self.show_class().get_changed(_("Edit"), "images/edit.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        if self.edit_class is not None:
            grid.add_action(self.request, self.edit_class().get_changed(_("Modify"), "images/edit.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        if self.del_class is not None:
            grid.add_action(self.request, self.del_class().get_changed(_("Delete"), "images/suppr.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_SINGLE})
        if self.add_class is not None:
            grid.add_action(self.request, self.add_class().get_changed(_("Add"), "images/add.png"), {'modal':FORMTYPE_MODAL, 'unique':SELECT_NONE})
        grid.set_location(0, row + 1, 2)
        grid.set_size(200, 500)
        self.add_component(grid)
        lbl = XferCompLabelForm("nb")
        lbl.set_location(0, row + 2, 2)
        lbl.set_value(_("Total number of %(name)s: %(count)d") % {'name':self.model._meta.verbose_name_plural, 'count':grid.nb_lines})  # pylint: disable=protected-access
        self.add_component(lbl)
        self.fillresponse_footer()

        self.add_action(SubAction(_('Close'), 'images/close.png'), {})

class XferAddEditor(XferContainerCustom):
    caption_add = ''
    caption_modify = ''
    fieldnames = []

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        if self.getparam("SAVE") != "YES":
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
            self.add_action(SubAction(_('Cancel'), 'images/cancel.png'), {})
            return self._finalize()
        else:
            save = XferSave()
            save.is_view_right = self.is_view_right
            save.model = self.model
            save.field_id = self.field_id
            save.caption = self.caption
            save.raise_except_class = self.__class__
            save.closeaction = self.closeaction
            return save.get(request, *args, **kwargs)

class XferShowEditor(XferContainerCustom):

    modify_class = None

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        img = XferCompImage('img')
        img.set_value(icon_path(self))
        img.set_location(0, 0, 1, 1)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0)
        self.add_component(lbl)
        self.fill_from_model(1, 0, True)
        if self.modify_class is not None:
            self.add_action(self.modify_class().get_changed(_('Modify'), 'images/edit.png'), {'close':CLOSE_NO})  # pylint: disable=not-callable
        self.add_action(SubAction(_('Close'), 'images/close.png'), {})
        return self._finalize()

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
