# -*- coding: utf-8 -*-
'''
Searching abstract viewer class and tools associated for Lucterios

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
import json
from datetime import datetime, time

from django.utils.translation import gettext_lazy as _
from django.db.models.fields.related import ManyToManyField
from django.db.models import Q

from lucterios.framework.tools import WrapAction, ActionsManage, format_value
from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm, XferCompGrid, XferCompSearch
from lucterios.framework.xferadvance import action_list_sorted, TITLE_CLOSE
from lucterios.framework.xfergraphic import XferContainerCustom, get_range_value

TYPE_FLOAT = 'float'
TYPE_STR = 'str'
TYPE_BOOL = 'bool'
TYPE_DATE = 'date'
TYPE_TIME = 'time'
TYPE_DATETIME = 'datetime'
TYPE_LIST = 'list'
TYPE_LISTMULT = 'listmult'

OP_NULL = (0, '')
OP_EQUAL = (1, _('equals'), '__iexact')
OP_DIFFERENT = (2, _("different"), '__iexact')
OP_LESS = (3, _("inferior"), '__lte')
OP_MORE = (4, _("superior"), '__gte')
OP_CONTAINS = (5, _("contains"), '__icontains')
OP_STARTBY = (6, _("starts with"), '__istartswith')
OP_ENDBY = (7, _("ends with"), '__iendswith')
OP_OR = (8, _("or"), '__in')
OP_AND = (9, _("and"), '__id')
OP_LIST = [OP_NULL, OP_EQUAL, OP_DIFFERENT, OP_LESS, OP_MORE,
           OP_CONTAINS, OP_STARTBY, OP_ENDBY, OP_OR, OP_AND]

LIST_OP_BY_TYPE = {
    TYPE_FLOAT: (OP_EQUAL, OP_DIFFERENT, OP_LESS, OP_MORE,),
    TYPE_STR: (OP_CONTAINS, OP_EQUAL, OP_DIFFERENT, OP_STARTBY, OP_ENDBY),
    TYPE_BOOL: (OP_EQUAL,),
    TYPE_DATE: (OP_EQUAL, OP_DIFFERENT, OP_LESS, OP_MORE,),
    TYPE_TIME: (OP_EQUAL, OP_DIFFERENT, OP_LESS, OP_MORE,),
    TYPE_DATETIME: (OP_EQUAL, OP_DIFFERENT, OP_LESS, OP_MORE,),
    TYPE_LIST: (OP_OR,),
    TYPE_LISTMULT: (OP_OR, OP_AND,),
}

CURRENT_DATE = "CURRENT"


def get_criteria_list(criteria):
    try:
        criteria_list = json.loads(criteria)
    except json.decoder.JSONDecodeError:
        criteria_list = []
        for criteria_item in criteria.split('//'):
            criteriaval = criteria_item.split('||')
            if len(criteriaval) == 3:
                criteriaval[1] = int(criteriaval[1])
                if ';' in criteriaval[2]:
                    criteriaval[2] = criteriaval[2].split(';')
                criteria_list.append(criteriaval)
    return criteria_list


def get_search_query_from_criteria(criteria, model):
    criteria_list = get_criteria_list(criteria)
    fields_desc = FieldDescList()
    fields_desc.initial(model, onlyfields=[item[0] for item in criteria_list])
    return fields_desc.get_query_from_criterialist(criteria_list)


def get_info_list(criteria, model):
    _filter, result_desc = get_search_query_from_criteria(criteria, model)
    info_list = list(result_desc.values())
    if len(info_list) > 0:
        info_list.insert(0, "{[b]}{[u]}%s{[/u]}{[/b]}" % _("Your criteria of search"))
    else:
        info_list.insert(0, "{[b]}{[u]}%s{[/u]}{[/b]}" % _("No criteria of search"))
    return info_list


def get_search_query(criteria, model):
    filter_result, _desc = get_search_query_from_criteria(criteria, model)
    return [filter_result]


class FieldDescItem(object):

    def __init__(self, fieldname):
        self.fieldname = fieldname
        self.description = ''
        self.field_type = TYPE_FLOAT
        self.field_list = []
        self.dbfieldname = ''
        self.dbfield = None
        self.initial_q = Q()
        if isinstance(self.fieldname, tuple) and (len(self.fieldname) == 4):
            self.dbfield = self.fieldname[1]
            self.dbfieldname = self.fieldname[2]
            self.initial_q = self.fieldname[3]
            self.fieldname = self.fieldname[0]
            self.sub_fieldnames = self.fieldname.split('.')[-1:]
        else:
            self.sub_fieldnames = self.fieldname.split('.')

    def _init_for_list(self, sub_model, multi):
        if len(self.sub_fieldnames) == 1:
            if multi:
                self.field_type = TYPE_LISTMULT
            else:
                self.field_type = TYPE_LIST
            self.field_list = []
            for select_obj in sub_model.objects.all():
                self.field_list.append(
                    (str(select_obj.id), str(select_obj)))
        else:
            sub_fied_desc = FieldDescItem(".".join(self.sub_fieldnames[1:]))
            if not sub_fied_desc.init(sub_model):
                return False
            self.description = "%s > %s" % (
                self.description, sub_fied_desc.description)
            self.dbfieldname = "%s__%s" % (
                self.dbfieldname, sub_fied_desc.dbfieldname)
            self.field_type = sub_fied_desc.field_type
            self.field_list = sub_fied_desc.field_list
        return True

    def init_field_from_name(self, model):
        if self.dbfield is None:
            if self.sub_fieldnames[0][-4:] == '_set':
                self.dbfieldname = self.sub_fieldnames[0][:-4]
                self.dbfield = getattr(model, self.sub_fieldnames[0])
                if not hasattr(self.dbfield, 'model'):
                    self.dbfield = getattr(model(), self.sub_fieldnames[0])
                self.description = self.dbfield.model._meta.verbose_name
            else:
                dep_field = model._meta.get_field(
                    self.sub_fieldnames[0])
                self.dbfieldname = self.sub_fieldnames[0]
                # field real in model
                if not dep_field.auto_created or dep_field.concrete:
                    self.dbfield = dep_field
                    self.description = self.dbfield.verbose_name
        else:
            self.description = self.dbfield.verbose_name

    def manage_integer_or_choices(self, dbfield):
        if (dbfield.choices is not None) and (len(dbfield.choices) > 0):
            self.field_type = TYPE_LIST
            self.field_list = []
            for choice_id, choice_val in dbfield.choices:
                self.field_list.append(
                    (str(choice_id), str(choice_val)))
        else:
            self.field_type = TYPE_FLOAT
            min_value, max_value = get_range_value(dbfield)
            self.field_list = [
                (str(min_value), str(max_value), '0')]

    def init(self, model):

        self.init_field_from_name(model)
        if self.dbfield is not None:
            from django.db.models.fields import IntegerField, DecimalField, BooleanField, TextField, DateField, TimeField, DateTimeField
            from django.db.models.fields.related import ForeignKey
            if isinstance(self.dbfield, IntegerField):
                self.manage_integer_or_choices(self.dbfield)
            elif isinstance(self.dbfield, DecimalField):
                self.field_type = TYPE_FLOAT
                min_value, max_value = get_range_value(self.dbfield)
                self.field_list = [(str(min_value), str(max_value), str(self.dbfield.decimal_places))]
            elif isinstance(self.dbfield, BooleanField):
                self.field_type = TYPE_BOOL
            elif isinstance(self.dbfield, TextField):
                self.field_type = TYPE_STR
            elif isinstance(self.dbfield, DateField):
                self.field_type = TYPE_DATE
            elif isinstance(self.dbfield, TimeField):
                self.field_type = TYPE_TIME
            elif isinstance(self.dbfield, DateTimeField):
                self.field_type = TYPE_DATETIME
            elif isinstance(self.dbfield, ForeignKey):
                return self._init_for_list(self.dbfield.remote_field.model, False)
            elif isinstance(self.dbfield, ManyToManyField):
                return self._init_for_list(self.dbfield.remote_field.model, True)
            elif 'RelatedManager' in self.dbfield.__class__.__name__:
                return self._init_for_list(self.dbfield.model, False)
            else:
                self.field_type = TYPE_STR
            return True
        else:
            return False

    def get_list(self):
        # list => '[["xxx",yyyy],["xxx","yyyy"],[xxx,yyyy]]'
        return json.dumps(self.field_list)

    def get_selector(self):
        return {
            'name': self.fieldname,
            'description': self.description,
            'type': self.field_type,
            'extra': self.field_list
        }

    def date_check(self, value, valtype):
        if isinstance(value, str):
            if value == CURRENT_DATE:
                return str(_('now'))
            else:
                try:
                    formatNum = 'D'
                    if valtype == TYPE_TIME:
                        formatNum = 'T'
                    elif valtype == TYPE_DATETIME:
                        formatNum = 'H'
                    return format_value(value, formatNum)
                except Exception:
                    return value
        else:
            return [self.date_check(val, valtype) for val in value]

    def get_value(self, value, operation):
        sep_for_list = ' %s ' % OP_LIST[8 if (operation != OP_DIFFERENT[0]) else 9][1]
        if self.field_type == TYPE_STR:
            new_val_txt = '"%s"' % value if isinstance(value, str) else sep_for_list.join(['"%s"' % subvalue for subvalue in value])
        elif self.field_type == TYPE_BOOL:
            if (value == 'o') or (value is True):
                new_val_txt = _("Yes")
            else:
                new_val_txt = _("No")
        elif self.field_type in [TYPE_DATE, TYPE_TIME, TYPE_DATETIME]:
            new_val_txt = sep_for_list.join(self.date_check(value.split(';'), self.field_type))
        elif (self.field_type == TYPE_LIST) or (self.field_type == TYPE_LISTMULT):
            new_val_txt = ''
            ids = value.split(';') if isinstance(value, str) else list(value)
            for new_item in self.field_list:
                if new_item[0] in ids:
                    if new_val_txt != '':
                        new_val_txt += ' %s ' % OP_LIST[operation][1]
                    new_val_txt += '"%s"' % new_item[1]
        else:
            new_val_txt = value if isinstance(value, str) else sep_for_list.join(value)
        return new_val_txt

    def get_criteria_description(self, new_op, new_val):
        if self.fieldname == 'id':
            return _("%d items") % len(new_val.split(';') if isinstance(new_val, str) else list(new_val))
        new_val_txt = self.get_value(new_val, new_op)
        if (self.field_type == TYPE_LIST) or (self.field_type == TYPE_LISTMULT):
            sep_criteria = OP_EQUAL[1]
        else:
            sep_criteria = OP_LIST[new_op][1]
        desc_text = "{[b]}%s{[/b]} %s {[i]}%s{[/i]}" % (self.description, sep_criteria, new_val_txt)
        return desc_text

    def get_query(self, value, operation):
        def get_int_list(value):
            if isinstance(value, str):
                val_ids = []
                for val_str in value.split(';'):
                    val_ids.append(int(val_str))
                return val_ids
            else:
                return [int(val_str) for val_str in list(value)]
        query_res = self.initial_q
        field_with_op = self.dbfieldname + OP_LIST[operation][2]
        if self.field_type == TYPE_BOOL:
            if len(self.initial_q) == 0:
                if (value == 'o') or (value is True):
                    query_res = query_res & Q(**{self.dbfieldname: True})
                else:
                    query_res = query_res & Q(**{self.dbfieldname: False})
            else:
                if (value == 'o') or (value is True):
                    query_res = query_res & Q(**{self.dbfieldname: 'True'})
                else:
                    query_res = query_res & ~Q(**{self.dbfieldname: 'True'})
        elif self.field_type == TYPE_LIST:
            query_res = query_res & Q(**{field_with_op: get_int_list(value)})
        elif self.field_type == TYPE_LISTMULT:
            val_ids = get_int_list(value)
            if operation == OP_OR[0]:
                query_res = query_res & Q(**{field_with_op: val_ids})
            else:
                query_res = self.initial_q

                for value_item in val_ids:
                    query_res = query_res & Q(**{field_with_op: value_item})
        elif (self.field_type == TYPE_FLOAT) and operation == OP_EQUAL[0]:
            field_with_op1 = self.dbfieldname + OP_LESS[2]
            field_with_op2 = self.dbfieldname + OP_MORE[2]
            if isinstance(value, str):
                value = float(value)
                new_query = Q(**{field_with_op1: value + 1e-4}) & Q(**{field_with_op2: value - 1e-4})
            else:
                new_query = Q()
                for sub_value in value:
                    sub_value = float(sub_value)
                    new_query |= Q(**{field_with_op1: sub_value + 1e-4}) & Q(**{field_with_op2: sub_value - 1e-4})
            query_res = self.initial_q & (new_query)
        else:
            if (self.field_type == TYPE_DATE) and (value == CURRENT_DATE):
                value = datetime.now().date().isoformat()
            if (self.field_type == TYPE_DATETIME) and (value == CURRENT_DATE):
                value = datetime.now().isoformat()
            if (self.field_type == TYPE_TIME) and (value == CURRENT_DATE):
                current_date = datetime.now()
                value = time(current_date.hour, current_date.minute).isoformat()
            if isinstance(value, str):
                if operation == OP_DIFFERENT[0]:
                    new_query = ~Q(**{field_with_op: value})
                else:
                    new_query = Q(**{field_with_op: value})
            else:
                new_query = Q()
                for sub_value in value:
                    if operation == OP_DIFFERENT[0]:
                        new_query &= ~Q(**{field_with_op: sub_value})
                    else:
                        new_query |= Q(**{field_with_op: sub_value})
            query_res = self.initial_q & (new_query)
        return query_res


class FieldDescList(object):

    def __init__(self):
        self.field_desc_list = []
        self.field_id_desc = []

    def initial(self, model, onlyfields=None):
        self.field_desc_list = []
        for field_name in model.get_search_fields():
            if (onlyfields is not None) and (field_name not in onlyfields) and (field_name[0] not in onlyfields):
                continue
            new_field = FieldDescItem(field_name)
            if new_field.init(model):
                self.field_desc_list.append(new_field)
        self.field_id_desc = FieldDescItem('id')
        self.field_id_desc.init(model)
        self.field_id_desc.field_type = TYPE_LISTMULT

    def get_selectors(self):
        return [field_desc_item.get_selector() for field_desc_item in self.field_desc_list]

    def get(self, fieldname):
        if fieldname == '':
            return None
        if fieldname == self.field_id_desc.fieldname:
            return self.field_id_desc
        for field_desc_item in self.field_desc_list:
            if field_desc_item.fieldname == fieldname:
                return field_desc_item
        return None

    def get_query(self, criteria_list):
        filter_result = Q()
        for criteria_item in criteria_list:
            field_desc_item = self.get(criteria_item[0])
            if field_desc_item is not None:
                filter_result = filter_result & field_desc_item.get_query(criteria_item[2], int(criteria_item[1]))
        if len(filter_result) == 0:
            filter_result = None
        return filter_result

    def get_query_from_criterialist(self, criteria_list):
        filter_result = Q()
        criteria_desc = {}
        crit_index = 0
        for criteria_item in criteria_list:
            new_name = criteria_item[0]
            if new_name != '':
                new_op = int(criteria_item[1])
                new_val = criteria_item[2]
                field_desc_item = self.get(new_name)
                if field_desc_item is not None:
                    filter_result = filter_result & field_desc_item.get_query(new_val, new_op)
                    desc_text = field_desc_item.get_criteria_description(new_op, new_val)
                    criteria_desc[str(crit_index)] = desc_text
                    crit_index += 1
        return filter_result, criteria_desc


class XferSearchEditor(XferContainerCustom):
    readonly = True
    methods_allowed = ('GET', )

    def __init__(self):
        XferContainerCustom.__init__(self)
        self.filter = None
        self.fieldnames = None
        self.fields_desc = FieldDescList()
        self.criteria_list = []
        self.size_by_page = None

    def fillresponse_add_title(self):
        criteria = self.getparam('CRITERIA')
        self.criteria_list = get_criteria_list(criteria) if criteria is not None else []
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0, 5)
        self.add_component(lbl)

    def fillresponse_search(self):
        comp = XferCompSearch('CRITERIA')
        comp.set_selectors(self.fields_desc.get_selectors())
        comp.set_value(self.criteria_list)
        comp.set_location(0, 10, 6)
        comp.description = _("New criteria")
        self.add_component(comp)
        self.filter = self.fields_desc.get_query(self.criteria_list)

    def filter_items(self):
        if isinstance(self.filter, Q) and (len(self.filter.children) > 0):
            self.items = self.model.objects.filter(self.filter).distinct()
        else:
            self.items = self.model.objects.all()

    def fillresponse(self):
        self.fields_desc.initial(self.item)
        self.fillresponse_add_title()
        self.fillresponse_search()
        self.filter_items()
        grid = XferCompGrid(self.field_id)
        if self.size_by_page is not None:
            grid.size_by_page = self.size_by_page
        grid.set_model(self.items, self.fieldnames, self)
        grid.add_action_notified(self)
        grid.set_location(0, self.get_max_row() + 4, 6)
        grid.set_height(350)
        self.add_component(grid)
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_LIST, self, key=action_list_sorted):
            self.add_action(act, **opt)
        self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))
