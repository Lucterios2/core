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
from lucterios.framework.tools import icon_path, ifplural
from lucterios.framework.xfercomponents import XferCompImage


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
            self.params["SAVE"] = "YES"
            self.add_action(self.__class__().get_changed(_('Ok'), 'images/ok.png'), {})
            self.add_action(XferContainerAcknowledge().get_changed(_('Cancel'), 'images/cancel.png'), {})
            return self._finalize()
        else:
            del self.params["SAVE"]
            save = XferSave()
            save.model = self.model
            save.field_id = self.field_id
            save.caption = self.caption
            save.raise_except_class = self.__class__

            save.closeaction = self.closeaction
            return save.get(request, *args, **kwargs)

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
