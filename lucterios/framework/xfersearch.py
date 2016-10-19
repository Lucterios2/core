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

from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django.db.models.fields.related import ManyToManyField
from django.db.models import Q

from lucterios.framework.tools import CLOSE_NO, FORMTYPE_REFRESH
from lucterios.framework.tools import WrapAction, ActionsManage
from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm, XferCompGrid, \
    XferCompSelect, XferCompButton, XferCompFloat, XferCompEdit, XferCompCheck, \
    XferCompDate, XferCompTime, XferCompCheckList
from lucterios.framework.xferadvance import action_list_sorted
from lucterios.framework.xfergraphic import XferContainerCustom, get_range_value

TYPE_FLOAT = 'float'
TYPE_STR = 'str'
TYPE_BOOL = 'bool'
TYPE_DATE = 'date'
TYPE_TIME = 'time'
TYPE_DATETIME = 'datetime'
TYPE_LIST = 'list'
TYPE_LISTMULT = 'listmult'

OP_NULL = ('0', '')
OP_EQUAL = ('1', _('equals'), '__iexact')
OP_DIFFERENT = ('2', _("different"), '__iexact')
OP_LESS = ('3', _("inferior"), '__lt')
OP_MORE = ('4', _("superior"), '__gt')
OP_CONTAINS = ('5', _("contains"), '__icontains')
OP_STARTBY = ('6', _("starts with"), '__istartswith')
OP_ENDBY = ('7', _("ends with"), '__iendswith')
OP_OR = ('8', _("or"), '__in')
OP_AND = ('9', _("and"), '__id')
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


def get_script_for_operator():
    script = "var new_operator='';\n"
    for current_type, op_list in LIST_OP_BY_TYPE.items():
        script += "if (type=='%(type)s') {\n" % {'type': current_type}
        for op_id, op_title, __op_q in op_list:
            script += "    new_operator+='<CASE id=\"%(op_id)s\">%(op_title)s</CASE>';\n" % {
                'op_id': op_id, 'op_title': op_title}
        script += "}\n"
    script += "parent.get('searchOperator').setValue('<SELECT>'+new_operator+'</SELECT>');\n"
    return script


def get_criteria_list(criteria):
    criteria_list = []
    for criteria_item in criteria.split('//'):
        criteriaval = criteria_item.split('||')
        criteria_list.append(criteriaval)
    return criteria_list


def get_search_query_from_criteria(criteria, model):
    criteria_list = get_criteria_list(criteria)
    fields_desc = FieldDescList()
    fields_desc.initial(model)
    return fields_desc.get_query_from_criterialist(criteria_list)


def get_search_query(criteria, model):
    filter_result, _ = get_search_query_from_criteria(criteria, model)
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
                    (six.text_type(select_obj.id), six.text_type(select_obj)))
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
                    # field not many-to-many
                    if not (dep_field.is_relation and dep_field.many_to_many):
                        self.dbfield = dep_field
                    else:
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
                    (six.text_type(choice_id), six.text_type(choice_val)))
        else:
            self.field_type = TYPE_FLOAT
            min_value, max_value = get_range_value(dbfield)
            self.field_list = [
                (six.text_type(min_value), six.text_type(max_value), '0')]

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
                self.field_list = [(six.text_type(min_value), six.text_type(max_value), six.text_type(self.dbfield.decimal_places))]
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
        # list => 'xxx||yyyy;xxx||yyyy;xxx||yyyy'
        res = []
        for item in self.field_list:
            res.append("||".join(item))
        return ";".join(res)

    def add_from_script(self):
        script_ref = "findFields['%s']='%s';\n" % (self.fieldname, self.field_type)
        if (self.field_type == TYPE_LIST) or (self.field_type == TYPE_LISTMULT) or (self.field_type == TYPE_FLOAT):
            script_ref += "findLists['%s']='%s';\n" % (self.fieldname, self.get_list().replace("'", "\\'"))
        return script_ref

    def get_value(self, value, operation):
        if self.field_type == TYPE_STR:
            new_val_txt = '"%s"' % value
        elif self.field_type == TYPE_BOOL:
            if value == 'o':
                new_val_txt = "oui"
            else:
                new_val_txt = "non"
        elif self.field_type == TYPE_DATE:
            new_val_txt = value
        elif self.field_type == TYPE_DATETIME:
            new_val_txt = value
        elif (self.field_type == TYPE_LIST) or (self.field_type == TYPE_LISTMULT):
            new_val_txt = ''
            ids = value.split(';')
            for new_item in self.field_list:
                if new_item[0] in ids:
                    if new_val_txt != '':
                        new_val_txt += ' %s ' % OP_LIST[operation][1]
                    new_val_txt += '"%s"' % new_item[1]
        else:
            new_val_txt = value
        return new_val_txt

    def get_query(self, value, operation):
        def get_int_list(value):
            val_ids = []
            for val_str in value.split(';'):
                val_ids.append(int(val_str))
            return val_ids
        query_res = self.initial_q
        field_with_op = self.dbfieldname + OP_LIST[operation][2]
        if self.field_type == TYPE_BOOL:
            if value == 'o':
                query_res = query_res & Q(**{self.dbfieldname: True})
            else:
                query_res = query_res & Q(**{self.dbfieldname: False})
        elif self.field_type == TYPE_LIST:
            query_res = query_res & Q(**{field_with_op: get_int_list(value)})
        elif self.field_type == TYPE_LISTMULT:
            val_ids = get_int_list(value)
            if operation == int(OP_OR[0]):
                query_res = query_res & Q(**{field_with_op: val_ids})
            else:
                query_res = self.initial_q

                for value_item in val_ids:
                    query_res = query_res & Q(**{field_with_op: value_item})
        else:
            if operation == int(OP_DIFFERENT[0]):
                query_res = self.initial_q & ~Q(**{field_with_op: value})
            else:
                query_res = self.initial_q & Q(**{field_with_op: value})
        return query_res

    def get_new_criteria(self, params):
        operation = params['searchOperator']
        new_type = self.field_type
        if new_type != '':
            new_val = ''
            if new_type == TYPE_FLOAT:
                new_val = params['searchValueFloat']
            if new_type == TYPE_STR:
                new_val = params['searchValueStr']
            if new_type == TYPE_BOOL:
                new_val = params['searchValueBool']
            if new_type == TYPE_DATE:
                new_val = params['searchValueDate']
            if new_type == TYPE_TIME:
                new_val = params['searchValueTime']
            if new_type == TYPE_DATETIME:
                new_val = params['searchValueDate'] + \
                    ' ' + params['searchValueTime']
            if (new_type == TYPE_LIST) or (new_type == TYPE_LISTMULT):
                new_val = params['searchValueList']
            if (new_val != '') or ((new_type == TYPE_STR) and (operation == OP_EQUAL[0])) or ((new_type == TYPE_STR) and (operation == OP_DIFFERENT[0])):
                return [self.fieldname, operation, new_val]
        return None


class FieldDescList(object):

    def __init__(self):
        self.field_desc_list = []

    def initial(self, model):
        self.field_desc_list = []
        for field_name in model.get_search_fields():
            new_field = FieldDescItem(field_name)
            if new_field.init(model):
                self.field_desc_list.append(new_field)

    def get_select_and_script(self):
        selector = []
        script_ref = "findFields=new Array();\n"
        script_ref += "findLists=new Array();\n"
        for field_desc_item in self.field_desc_list:
            selector.append(
                (field_desc_item.fieldname, field_desc_item.description))
            script_ref += field_desc_item.add_from_script()
        return selector, script_ref

    def get(self, fieldname):
        for field_desc_item in self.field_desc_list:
            if field_desc_item.fieldname == fieldname:
                return field_desc_item
        return None

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
                new_val_txt = field_desc_item.get_value(new_val, new_op)
                filter_result = filter_result & field_desc_item.get_query(
                    new_val, new_op)
                if (field_desc_item.field_type == TYPE_LIST) or (field_desc_item.field_type == TYPE_LISTMULT):
                    sep_criteria = OP_EQUAL[1]
                else:
                    sep_criteria = OP_LIST[new_op][1]
                criteria_desc[six.text_type(crit_index)] = "{[b]}%s{[/b]} %s {[i]}%s{[/i]}" % (
                    field_desc_item.description, sep_criteria, new_val_txt)
                crit_index += 1
        return filter_result, criteria_desc


class XferSearchEditor(XferContainerCustom):

    def __init__(self):
        XferContainerCustom.__init__(self)
        self.action_grid = None
        self.fieldnames = None
        self.fields_desc = FieldDescList()
        self.criteria_list = []
        self.filter = None
        self.action_list = [('listing', _("Listing"), "images/print.png"),
                            ('label', _("Label"), "images/print.png")]

    def read_criteria_from_params(self):
        criteria = self.getparam('CRITERIA')
        if criteria is not None:
            self.criteria_list = get_criteria_list(criteria)
        act_param = self.getparam('ACT')
        if act_param == 'ADD':
            new_name = self.getparam('searchSelector')
            new_criteria = self.fields_desc.get(
                new_name).get_new_criteria(self.params)
            if new_criteria is not None:
                self.criteria_list.append(new_criteria)
        elif act_param is not None:
            del self.criteria_list[int(self.params['ACT'])]
        temp_list = []
        for criteria_item in self.criteria_list:
            if len(criteria_item) >= 3:
                temp_list.append('||'.join(criteria_item))
        self.params['CRITERIA'] = '//'.join(temp_list)
        if 'ACT' in self.params.keys():
            del self.params['ACT']
        key_list = list(self.params.keys())
        for ctx_key in key_list:
            if ctx_key[0:6] == 'search':
                del self.params[ctx_key]

    def get_text_search(self):
        filter_result, criteria_desc = self.fields_desc.get_query_from_criterialist(
            self.criteria_list)
        if len(filter_result.children) > 0:
            self.filter = filter_result
        else:
            self.filter = None
        return criteria_desc

    def fillresponse_add_title(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0)
        self.add_component(lbl)

    def fillresponse_search_select(self):
        selector, script_ref = self.fields_desc.get_select_and_script()
        script_ref += """
var name=current.getValue();
var type=findFields[name];
parent.get('searchValueFloat').setVisible(type=='float');
parent.get('searchValueStr').setVisible(type=='str');
parent.get('searchValueBool').setVisible(type=='bool');
parent.get('searchValueDate').setVisible(type=='date' || type=='datetime');
parent.get('searchValueTime').setVisible(type=='time' || type=='datetime');
parent.get('searchValueList').setVisible(type=='list' || type=='listmult');
"""
        script_ref += get_script_for_operator()
        script_ref += """
if (type=='float') {
    var prec=findLists[name].split('||');
    parent.get('searchValueFloat').setValue('<FLOAT min=\"'+prec[0]+'\" max=\"'+prec[1]+'\" prec=\"'+prec[2]+'\"></FLOAT>');
}
if (type=='str') {
    parent.get('searchValueStr').setValue('<STR></STR>');
}
if (type=='bool') {
    parent.get('searchValueBool').setValue('<BOOL>n</BOOL>');
}
if (type=='date' || type=='datetime') {
    parent.get('searchValueDate').setValue('<DATE>1900/01/01</DATE>');
}
if (type=='time' || type=='datetime') {
    parent.get('searchValueTime').setValue('<DATE>00:00:00</DATE>');
}
if ((type=='list') || (type=='listmult')) {
    var list=findLists[name].split(';');
    var list_txt='';
    for(i=0;i<list.length;i++) {
        var val=list[i].split('||');
        if (val.length>1) {
            list_txt+='<CASE id=\"'+val[0]+'\">'+val[1]+'</CASE>';
        }
    }
    parent.get('searchValueList').setValue('<SELECT>'+list_txt+'</SELECT>');
}
"""
        label = XferCompLabelForm('labelsearchSelector')
        label.set_value("{[bold]Nouveau critere{[/bold]")
        label.set_location(0, 10, 1, 7)
        self.add_component(label)
        comp = XferCompSelect("searchSelector")
        comp.set_select(selector)
        comp.set_value("")
        comp.set_location(1, 10, 1, 7)
        comp.set_size(20, 200)
        comp.java_script = script_ref
        self.add_component(comp)
        comp = XferCompSelect("searchOperator")
        comp.set_select({})
        comp.set_value("")
        comp.set_size(20, 200)
        comp.set_location(2, 10, 1, 7)
        self.add_component(comp)

    def fillresponse_search_values(self):
        comp = XferCompButton("searchButtonAdd")
        comp.set_is_mini(True)
        comp.set_location(4, 10, 1, 7)
        comp.set_action(self.request, self.get_action("", "images/add.png"), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'ACT': 'ADD'})
        self.add_component(comp)

        comp = XferCompDate("searchValueDate")
        comp.set_needed(True)
        comp.set_location(3, 11)
        comp.set_size(20, 200)
        self.add_component(comp)
        comp = XferCompFloat("searchValueFloat")
        comp.set_needed(True)
        comp.set_location(3, 12)
        comp.set_size(20, 200)
        self.add_component(comp)
        comp = XferCompEdit("searchValueStr")
        comp.set_location(3, 13)
        comp.set_size(20, 200)
        self.add_component(comp)
        comp = XferCompCheckList("searchValueList")
        comp.set_location(3, 14)
        comp.set_size(80, 200)
        self.add_component(comp)
        comp = XferCompCheck("searchValueBool")
        comp.set_location(3, 15)
        comp.set_size(20, 200)
        self.add_component(comp)
        comp = XferCompTime("searchValueTime")
        comp.set_needed(True)
        comp.set_location(3, 16)
        comp.set_size(20, 200)
        self.add_component(comp)

        label = XferCompLabelForm('labelsearchSep')
        label.set_value("")
        label.set_size(1, 200)
        label.set_location(3, 17)
        self.add_component(label)

    def fillresponse_show_criteria(self):
        criteria_text_list = self.get_text_search()
        label = XferCompLabelForm('labelsearchDescTitle')
        if len(criteria_text_list) > 0:
            label.set_value_as_info("Your criteria of search")
            label.set_location(0, 17, 2, 4)
        else:
            label.set_value_as_infocenter("No criteria of search")
            label.set_location(0, 17, 4)
        self.add_component(label)

        row = 17
        for criteria_id, criteria_text in criteria_text_list.items():
            label = XferCompLabelForm('labelSearchText_' + criteria_id)
            label.set_value(criteria_text)
            label.set_location(2, row, 2)
            self.add_component(label)
            comp = XferCompButton("searchButtonDel_" + criteria_id)
            comp.set_is_mini(True)
            comp.set_location(4, row)
            comp.set_action(self.request, self.get_action("", "images/delete.png"),
                            modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'ACT': criteria_id})
            self.add_component(comp)
            row += 1

    def fillresponse(self):
        self.fields_desc.initial(self.item)
        self.read_criteria_from_params()
        self.fillresponse_add_title()
        self.fillresponse_search_select()
        self.fillresponse_search_values()
        self.fillresponse_show_criteria()
        row = self.get_max_row()
        if isinstance(self.filter, Q) and (len(self.filter.children) > 0):
            self.items = self.model.objects.filter(
                self.filter)
        else:
            self.items = self.model.objects.all()
        grid = XferCompGrid(self.field_id)
        grid.set_model(self.items, self.fieldnames, self)
        grid.add_actions(self, action_list=self.action_grid)
        grid.add_action_notified(self)
        grid.set_location(0, row + 4, 4)
        grid.set_size(200, 500)
        self.add_component(grid)
        lbl = XferCompLabelForm("nb")
        lbl.set_location(0, row + 5, 4)
        lbl.set_value(_("Total number of %(name)s: %(count)d") % {
                      'name': self.model._meta.verbose_name_plural, 'count': grid.nb_lines})
        self.add_component(lbl)
        for act_type, title, icon in self.action_list:
            self.add_action(ActionsManage.get_act_changed(
                self.model.__name__, act_type, title, icon), {'close': CLOSE_NO})
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_LIST, self, key=action_list_sorted):
            self.add_action(act, **opt)
        self.add_action(WrapAction(_('Close'), 'images/close.png'))
