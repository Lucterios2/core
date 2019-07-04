# -*- coding: utf-8 -*-
'''
Graphics abstract viewer classes for Lucterios

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
import datetime
from logging import getLogger
import warnings

from django.utils.translation import ugettext as _
from django.utils import six
from django.db.models.fields import EmailField, NOT_PROVIDED
from django.core.exceptions import ObjectDoesNotExist

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.xfercomponents import XferCompTab, XferCompImage, XferCompLabelForm, XferCompButton, \
    XferCompEdit, XferCompFloat, XferCompCheck, XferCompGrid, XferCompCheckList, \
    XferCompMemo, XferCompSelect, XferCompLinkLabel, XferCompDate, XferCompTime, XferCompDateTime
from lucterios.framework.tools import get_dico_from_setquery, WrapAction, SELECT_NONE, get_actions_json, adapt_value
from lucterios.framework.tools import get_corrected_setquery, FORMTYPE_MODAL, CLOSE_YES
from lucterios.framework.models import get_format_from_field


def get_range_value(model_field):
    from django.core.validators import MaxValueValidator, MinValueValidator
    min_value, max_value = 0, 10000
    for valid in model_field.validators:
        if isinstance(valid, MinValueValidator):
            min_value = valid.limit_value
        if isinstance(valid, MaxValueValidator):
            max_value = valid.limit_value
    return min_value, max_value


class XferContainerAcknowledge(XferContainerAbstract):

    observer_name = 'core.acknowledge'

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.title = ""
        self.msg = ""
        self.traitment_data = None
        self.typemsg = 1
        self.redirect_act = None
        self.except_msg = ""
        self.except_classact = None
        self.custom = None

    def create_custom(self, model=None):
        self.custom = XferContainerCustom()
        self.custom.model = model
        self.custom._initialize(self.request)
        self.custom.is_view_right = self.is_view_right
        self.custom.caption = self.caption
        self.custom.extension = self.extension
        self.custom.action = self.action
        self.custom.closeaction = self.closeaction
        return self.custom

    def confirme(self, title):
        self.title = title
        if self.title != "":
            if self.getparam("CONFIRME") is not None:
                return self.params["CONFIRME"] != ""
            else:
                return False
        else:
            return True

    def message(self, title, typemsg=1):
        self.msg = title
        self.typemsg = typemsg

    def traitment(self, icon, waiting_message, finish_message):
        self.traitment_data = [icon, waiting_message, finish_message]
        if self.getparam("RELOAD") is not None:
            return self.params["RELOAD"] != ""
        else:
            return False

    def redirect_action(self, action, modal=FORMTYPE_MODAL, close=CLOSE_YES, params=None):
        if self.check_action_permission(action):
            self.redirect_act = (action, modal, close, params)

    def raise_except(self, error_msg, action=None):
        self.except_msg = error_msg
        self.except_classact = action

    def fillresponse(self):
        pass

    def _get_from_custom(self, request, *args, **kwargs):
        dlg = XferContainerCustom()
        dlg.request = self.request
        dlg.is_view_right = self.is_view_right
        dlg.caption = self.caption
        dlg.extension = self.extension
        dlg.action = self.action
        img_title = XferCompImage('img_title')
        img_title.set_location(0, 0, 1, 2)
        img_title.set_value(self.traitment_data[0])
        dlg.add_component(img_title)

        lbl = XferCompLabelForm("info")
        lbl.set_location(1, 0)
        dlg.add_component(lbl)
        if self.getparam("RELOAD") is not None:
            lbl.set_value(
                "{[br/]}{[center]}" + six.text_type(self.traitment_data[2]) + "{[/center]}")
            dlg.add_action(WrapAction(_("Close"), "images/close.png"))
        else:
            lbl.set_value(
                "{[br/]}{[center]}" + six.text_type(self.traitment_data[1]) + "{[/center]}")
            btn = XferCompButton("Next")
            btn.set_location(1, 1)
            btn.set_size(50, 300)
            btn.set_action(self.request, self.get_action(_('Traitment...'), ""), params={"RELOAD": "YES"})
            btn.java_script = "parent.refresh()"
            dlg.params["RELOAD"] = "YES"
            dlg.add_component(btn)
            dlg.add_action(WrapAction(_("Cancel"), "images/cancel.png"))
        return dlg.get_post(request, *args, **kwargs)

    def get_post(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(
            ">> get %s [%s]", request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            self.fillresponse(**self._get_params())
            if self.custom is not None:
                return self.custom.get(request, *args, **kwargs)
            if (self.title != '') and (self.getparam("CONFIRME") != "YES"):
                dlg = XferContainerDialogBox()
                dlg.request = self.request
                dlg.is_view_right = self.is_view_right
                dlg.caption = "Confirmation"
                dlg.extension = self.extension
                dlg.action = self.action
                dlg.set_dialog(self.title, XFER_DBOX_CONFIRMATION)
                dlg.add_action(self.get_action(_("Yes"), "images/ok.png"), modal=FORMTYPE_MODAL, close=CLOSE_YES, params={"CONFIRME": "YES"})
                dlg.add_action(WrapAction(_("No"), "images/cancel.png"))
                dlg.closeaction = self.closeaction
                return dlg.get_post(request, *args, **kwargs)
            elif self.msg != "":
                dlg = XferContainerDialogBox()
                dlg.request = self.request
                dlg.caption = self.caption
                dlg.set_dialog(self.msg, self.typemsg)
                dlg.add_action(WrapAction(_("Ok"), "images/ok.png"))
                dlg.closeaction = self.closeaction
                return dlg.get_post(request, *args, **kwargs)
            elif self.except_msg != "":
                dlg = XferContainerDialogBox()
                dlg.request = self.request
                dlg.is_view_right = self.is_view_right
                dlg.caption = self.caption
                dlg.set_dialog(self.except_msg, XFER_DBOX_WARNING)
                if self.except_classact is not None:
                    except_action = self.except_classact()
                    if self.check_action_permission(except_action.get_action()):
                        dlg.add_action(except_action.get_action(_("Retry"), ""))
                dlg.closeaction = self.closeaction
                return dlg.get_post(request, *args, **kwargs)
            elif self.traitment_data is not None:
                return self._get_from_custom(request, *args, **kwargs)
            else:
                if "CONFIRME" in self.params.keys():
                    del self.params["CONFIRME"]
                self._finalize()
                return self.get_response()
        finally:
            getLogger("lucterios.core.request").debug(
                "<< get %s [%s]", request.path, request.user)

    def _finalize(self):
        if self.redirect_act is not None:
            if self.format == 'JSON':
                self.responsejson['action'] = self.redirect_act[0].get_action_json(modal=self.redirect_act[1], close=self.redirect_act[2], params=self.redirect_act[3])
            else:
                self.responsexml.append(self.redirect_act[0].get_action_xml(modal=self.redirect_act[1], close=self.redirect_act[2], params=self.redirect_act[3]))
        XferContainerAbstract._finalize(self)


XFER_DBOX_INFORMATION = 1
XFER_DBOX_CONFIRMATION = 2
XFER_DBOX_WARNING = 3
XFER_DBOX_ERROR = 4


class XferContainerDialogBox(XferContainerAbstract):

    observer_name = "core.dialogbox"

    msgtype = XFER_DBOX_INFORMATION
    msgtext = ""
    actions = []

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.msgtype = XFER_DBOX_INFORMATION
        self.msgtext = ""
        self.actions = []

    def set_dialog(self, msgtext, msgtype):
        self.msgtype = msgtype
        self.msgtext = msgtext

    def add_action(self, action, options=None, modal=FORMTYPE_MODAL, close=CLOSE_YES, params=None):
        if self.check_action_permission(action):
            if isinstance(options, dict):
                warnings.warn("[XferContainerDialogBox.add_action] Deprecated in Lucterios 2.2", DeprecationWarning)
                modal = options.get('modal', FORMTYPE_MODAL)
                close = options.get('close', CLOSE_YES)
                params = options.get('params', None)
            self.actions.append((action, modal, close, SELECT_NONE, params))

    def _finalize(self):
        self.responsejson['data'] = {'text': six.text_type(self.msgtext), 'type': self.msgtype}
        self.responsejson['actions'] = get_actions_json(self.actions)
        XferContainerAbstract._finalize(self)


class XferContainerCustom(XferContainerAbstract):

    observer_name = "core.custom"

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.actions = []
        self.components = {}
        self.tab = 0

    def add_component(self, component):
        component.tab = self.tab
        comp_id = component.get_id()
        self.components[comp_id] = component

    def get_components(self, cmp_name):
        comp_res = None
        for comp in self.components.values():
            if comp.name == cmp_name:
                comp_res = comp
        return comp_res

    def move_components(self, cmp_name, col_offset, row_offset):
        new_components = {}
        for comp in self.components.values():
            if comp.name == cmp_name:
                comp.col += col_offset
                comp.row += row_offset
            comp_id = comp.get_id()
            new_components[comp_id] = comp
        self.components = new_components

    def move(self, tab, col_offset, row_offset):
        new_components = {}
        for comp in self.components.values():
            if comp.tab == tab:
                comp.col += col_offset
                comp.row += row_offset
            comp_id = comp.get_id()
            new_components[comp_id] = comp
        self.components = new_components

    def get_max_row(self):
        row = -1
        for comp in self.components.values():
            if comp.tab == self.tab:
                row = max((row, comp.row))
        return row

    def remove_component(self, cmp_name):
        comp_id = None
        for (key, comp) in self.components.items():
            if comp.name == cmp_name:
                comp_id = key
        if comp_id is not None:
            del self.components[comp_id]

    def change_select_to_label(self, cmp_name):
        old_obj = self.get_components(cmp_name)
        if isinstance(old_obj, XferCompSelect):
            value = old_obj.value
            if isinstance(old_obj.select_list, list):
                for key, sel_val in old_obj.select_list:
                    if six.text_type(value) == six.text_type(key):
                        value = sel_val
                        break
                self.remove_component(cmp_name)
                self.tab = old_obj.tab
                new_lbl = XferCompLabelForm(cmp_name)
                new_lbl.set_value(value)
                new_lbl.col = old_obj.col
                new_lbl.row = old_obj.row
                new_lbl.vmin = old_obj.vmin
                new_lbl.hmin = old_obj.hmin
                new_lbl.colspan = old_obj.colspan
                new_lbl.rowspan = old_obj.rowspan
                new_lbl.description = old_obj.description
                self.add_component(new_lbl)

    def change_to_readonly(self, cmp_name):
        old_obj = self.get_components(cmp_name)
        new_lbl = XferCompLabelForm.convert_to_label(old_obj)
        self.remove_component(cmp_name)
        self.tab = old_obj.tab
        self.add_component(new_lbl)

    def find_tab(self, tab_name):
        num = -1
        tab_name = six.text_type(tab_name)
        for comp in self.components.values():
            if isinstance(comp, XferCompTab):
                if comp.value == tab_name:
                    num = comp.tab
        return num

    def max_tab(self):
        index = 0
        for comp in self.components.values():
            if isinstance(comp, XferCompTab):
                index = max(index, comp.tab)
        return index

    def new_tab(self, tab_name, num=-1):
        old_num = self.find_tab(tab_name)
        if old_num == -1:
            if num == -1:
                self.tab = self.max_tab() + 1
            else:
                for comp in self.components.values():
                    if comp.tab >= num:
                        comp.tab = comp.tab + 1
                self.tab = num
            new_tab = XferCompTab("__tab_%d" % self.tab)
            new_tab.set_value(six.text_type(tab_name))
            new_tab.set_location(-1, -1)
            self.add_component(new_tab)
        else:
            self.tab = old_num

    def del_tab(self, tab_name):
        tab_names = tab_name.split('@')
        comp_id = None
        for (key, comp) in self.components.items():
            if isinstance(comp, XferCompTab):
                if (comp.value == tab_name) or ((len(tab_names) > 1) and (comp.value == tab_names[1])):
                    comp_id = key
        if comp_id is not None:
            del self.components[comp_id]

    def get_reading_comp(self, field_name):
        sub_value = self.item
        for fieldname in field_name.split('.'):
            if sub_value is not None:
                try:
                    sub_value = getattr(sub_value, fieldname)
                except ObjectDoesNotExist:
                    getLogger("lucterios.core").exception("fieldname '%s' not found", fieldname)
                    sub_value = None
        value = adapt_value(sub_value)
        dep_field = self.item.get_field_by_name(field_name)
        if isinstance(dep_field, EmailField):
            comp = XferCompLinkLabel(field_name)
            comp.set_link('mailto:' + value)
        else:
            comp = XferCompLabelForm(field_name)
        comp.set_value(value)
        comp.set_format(get_format_from_field(dep_field))
        return comp

    def get_writing_comp(self, field_name):
        def get_value_from_field(default):
            try:
                val = getattr(self.item, field_name)
            except ObjectDoesNotExist:
                getLogger("lucterios.core").exception("fieldname '%s' not found", field_name)
                val = None
            if val is None:
                if is_needed:
                    if dep_field.default != NOT_PROVIDED:
                        val = dep_field.default
                    else:
                        val = default
            return val
        from django.db.models.fields import IntegerField, DecimalField, BooleanField, TextField, DateField, TimeField, DateTimeField, CharField
        from django.db.models.fields.related import ForeignKey
        dep_field = self.item.get_field_by_name(field_name)
        is_needed = dep_field.unique or not (dep_field.blank or dep_field.null)
        if isinstance(dep_field, IntegerField):
            if (dep_field.choices is not None) and (len(dep_field.choices) > 0):
                comp = XferCompSelect(field_name)
                comp.set_select(list(dep_field.choices))
                min_value = 0
            else:
                min_value, max_value = get_range_value(dep_field)
                comp = XferCompFloat(field_name, min_value, max_value, 0)
            comp.set_value(get_value_from_field(min_value))
        elif isinstance(dep_field, DecimalField):
            min_value, max_value = get_range_value(dep_field)
            comp = XferCompFloat(
                field_name, min_value, max_value, dep_field.decimal_places)
            comp.set_value(get_value_from_field(min_value))
        elif isinstance(dep_field, BooleanField):
            comp = XferCompCheck(field_name)
            comp.set_value(get_value_from_field(False))
        elif isinstance(dep_field, TextField):
            comp = XferCompMemo(field_name)
            comp.set_value(get_value_from_field(""))
        elif isinstance(dep_field, DateField):
            comp = XferCompDate(field_name)
            comp.set_value(get_value_from_field(datetime.date.today()))
        elif isinstance(dep_field, TimeField):
            comp = XferCompTime(field_name)
            comp.set_value(get_value_from_field(datetime.time()))
        elif isinstance(dep_field, DateTimeField):
            comp = XferCompDateTime(field_name)
            comp.set_value(get_value_from_field(datetime.datetime.now()))
        elif isinstance(dep_field, ForeignKey):
            comp = XferCompSelect(field_name)
            try:
                value = self.item
                for fieldname in field_name.split('.'):
                    value = getattr(value, fieldname)
            except ObjectDoesNotExist:
                value = None
            if value is None:
                comp.set_value(0)
            else:
                comp.set_value(value.id)
            if hasattr(self.item, fieldname + '_query'):
                sub_select = getattr(self.item, fieldname + '_query')
            else:
                sub_select = dep_field.remote_field.model.objects.all()
            comp.set_needed(not dep_field.null)
            comp.set_select_query(sub_select)
        elif (dep_field is not None) and dep_field.is_relation and dep_field.many_to_many:
            comp = XferCompCheckList(field_name)
            comp.simple = 2
            if self.item.id is not None:
                values = []
                for item in getattr(self.item, field_name).all():
                    values.append(item.id)
                comp.set_value(values)
            if hasattr(self.item, field_name + '_query'):
                sub_select = getattr(self.item, field_name + '_query')
            else:
                sub_select = get_dico_from_setquery(get_corrected_setquery(dep_field.remote_field.model.objects.all()))
            comp.set_select(sub_select)
        else:
            comp = XferCompEdit(field_name)
            comp.set_value(get_value_from_field(""))
            if isinstance(dep_field, CharField):
                comp.size = dep_field.max_length
        comp.set_needed(is_needed)
        return comp

    def get_maxsize_of_lines(self, field_names):
        maxsize_of_lines = 1
        for line_field_name in field_names:
            if isinstance(line_field_name, tuple):
                nb_current_line = 0
                for sub_field_name in line_field_name:
                    nb_current_line += 1
                    if isinstance(sub_field_name, six.text_type):
                        dep_field = self.item.get_field_by_name(sub_field_name)
                        if (dep_field is not None) and dep_field.is_relation and dep_field.many_to_many:
                            nb_current_line += 2
                maxsize_of_lines = max((maxsize_of_lines, nb_current_line))
            else:
                dep_field = self.item.get_field_by_name(line_field_name)
                if (dep_field is not None) and dep_field.is_relation and dep_field.many_to_many:
                    maxsize_of_lines = max((maxsize_of_lines, 3))
        return maxsize_of_lines

    def get_current_offset(self, maxsize_of_lines, line_field_size, offset):
        colspan = 1
        if offset == (line_field_size - 1):
            colspan = maxsize_of_lines - offset
        return colspan

    def filltab_from_model(self, col, row, readonly, field_names):
        maxsize_of_lines = self.get_maxsize_of_lines(field_names)
        for line_field_name in field_names:
            if not isinstance(line_field_name, tuple):
                line_field_name = line_field_name,
            offset = 0
            height = 1
            comp_col_addon = 0
            for field_name in line_field_name:
                if field_name is None:
                    continue
                colspan = self.get_current_offset(maxsize_of_lines, len(line_field_name), offset)
                if field_name[-4:] == '_set':  # field is one-to-many relation
                    child = getattr(self.item, field_name).all()
                    if hasattr(self.item, field_name[:-4] + '_query'):
                        child = child.filter(getattr(self.item, field_name[:-4] + '_query'))
                    comp = XferCompGrid(field_name[:-4])
                    comp.set_model(child, None, self)
                    comp.add_action_notified(self, model=child.model)
                    comp.set_location(col + comp_col_addon + offset, row, colspan, 1)
                    comp.description = six.text_type(child.model._meta.verbose_name)
                    self.add_component(comp)
                    offset += 1 + comp_col_addon
                else:
                    if isinstance(field_name, tuple):
                        verbose_name, field_name = field_name
                    else:
                        verbose_name = None
                    dep_field = self.item.get_field_by_name(field_name)
                    # field real in model
                    if (dep_field is None) or not dep_field.auto_created or dep_field.concrete:
                        # field not many-to-many
                        if readonly:
                            comp = self.get_reading_comp(field_name)
                        else:
                            comp = self.get_writing_comp(field_name)
                        comp.set_location(col + comp_col_addon + offset, row, colspan, 1)
                        if verbose_name is None:
                            comp.description = six.text_type(dep_field.verbose_name)
                        else:
                            comp.description = six.text_type(verbose_name)
                        self.add_component(comp)
                        offset += 1 + comp_col_addon
            row += height

    def fill_from_model(self, col, row, readonly, desc_fields=None):
        current_desc_fields = desc_fields
        if desc_fields is None:
            if readonly:
                current_desc_fields = self.item.get_show_fields()
            else:
                current_desc_fields = self.item.get_edit_fields()
        if isinstance(current_desc_fields, list):
            current_desc_fields = {'': current_desc_fields}
        tab_keys = list(current_desc_fields.keys())
        if '' in tab_keys:
            self.filltab_from_model(
                col, row, readonly, current_desc_fields[''])
            tab_keys.remove('')
        tab_keys.sort()
        for tab_key in tab_keys:
            self.new_tab(tab_key[tab_key.find('@') + 1:])
            self.filltab_from_model(
                0, 0, readonly, current_desc_fields[tab_key])
        if desc_fields is None:
            if readonly:
                self.item.editor.show(self)
            else:
                self.item.editor.edit(self)

    def add_action(self, action, pos_act=-1, modal=FORMTYPE_MODAL, close=CLOSE_YES, params=None):
        if self.check_action_permission(action):
            if pos_act != -1:
                self.actions.insert(pos_act, (action, modal, close, SELECT_NONE, params))
            else:
                self.actions.append((action, modal, close, SELECT_NONE, params))

    def get_sort_components(self):
        final_components = {}
        sortedkey_components = []
        for comp in self.components.values():
            comp_id = comp.get_id()
            sortedkey_components.append(comp_id)
            final_components[comp_id] = comp
        sortedkey_components.sort()
        return sortedkey_components, final_components

    def _finalize(self):
        sortedkey_components, final_components = self.get_sort_components()
        self.responsejson['data'] = {}
        self.responsejson['comp'] = []
        for key in sortedkey_components:
            comp = final_components[key]
            self.responsejson['comp'].append(comp.get_json())
            self.responsejson['data'][comp.name] = comp.get_json_value()
        self.responsejson['actions'] = get_actions_json(self.actions)
        XferContainerAbstract._finalize(self)
