# -*- coding: utf-8 -*-
'''
Components for customer viewer for Lucterios

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
from lxml import etree

from django.utils import six
from django.utils.translation import ugettext as _
from django.utils.http import urlquote_plus

from lucterios.framework.tools import get_action_xml, get_actions_xml, check_permission, StubAction, ActionsManage, SELECT_MULTI
from lucterios.framework.tools import CLOSE_NO, FORMTYPE_MODAL, SELECT_SINGLE, SELECT_NONE
from lucterios.framework.xferbasic import XferContainerAbstract
import datetime
from lucterios.framework.models import get_value_converted, get_value_if_choices
from django.db.models.fields import FieldDoesNotExist

class XferComponent(object):
    # pylint: disable=too-many-instance-attributes

    def __init__(self, name):
        self.name = name
        self._component_ident = ""
        self.value = ""
        self.tab = 0
        self.col = 0
        self.row = 0
        self.vmin = ""
        self.hmin = ""
        self.colspan = 1
        self.rowspan = 1
        self.description = ""
        self.needed = False

    def set_location(self, col, row, colspan=1, rowspan=1):
        self.col = col
        self.row = row
        self.colspan = colspan
        self.rowspan = rowspan

    def set_size(self, vmin, hmin):
        self.vmin = vmin
        self.hmin = hmin

    def set_value(self, value):
        self.value = value

    def set_needed(self, needed):
        self.needed = needed

    def _get_content(self):
        return self.value

    def get_id(self):
        return "tab=%04d_y=%04d_x=%04d" % (int(self.tab), int(self.row) + 1, int(self.col) + 1)

    def _get_attribut(self, compxml):
        compxml.attrib['name'] = self.name
        compxml.attrib['description'] = self.description
        if isinstance(self.tab, six.integer_types):
            compxml.attrib['tab'] = six.text_type(self.tab)
        if isinstance(self.col, six.integer_types):
            compxml.attrib['x'] = six.text_type(self.col)
        if isinstance(self.row, six.integer_types):
            compxml.attrib['y'] = six.text_type(self.row)
        if isinstance(self.colspan, six.integer_types):
            compxml.attrib['colspan'] = six.text_type(self.colspan)
        if isinstance(self.rowspan, six.integer_types):
            compxml.attrib['rowspan'] = six.text_type(self.rowspan)
        if isinstance(self.vmin, six.integer_types):
            compxml.attrib['VMin'] = six.text_type(self.vmin)
        if isinstance(self.hmin, six.integer_types):
            compxml.attrib['HMin'] = six.text_type(self.hmin)
        compxml.attrib['needed'] = six.text_type(1) if self.needed else six.text_type(0)

    def get_reponse_xml(self):
        compxml = etree.Element(self._component_ident)
        self._get_attribut(compxml)
        compxml.text = six.text_type(self._get_content())
        return compxml

class XferCompTab(XferComponent):

    def __init__(self):
        XferComponent.__init__(self, '')
        self._component_ident = "TAB"

    def set_value(self, value):
        self.value = value.strip()

class XferCompLABEL(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "LABEL"

    def set_value(self, value):
        self.value = value.strip()

class XferCompPassword(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "PASSWD"

class XferCompImage(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "IMAGE"
        self.type = ""

    def set_value(self, value):
        if isinstance(value, six.binary_type):
            self.value = value.decode("utf-8")
        else:
            self.value = six.text_type(value)

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        if self.type != '':
            compxml.attrib['type'] = six.text_type(self.type)

class XferCompLabelForm(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "LABELFORM"

    def set_value_as_title(self, value):
        self.set_value(six.text_type('{[br/]}{[center]}{[u]}{[b]}%s{[/b]}{[/u]}{[/center]}') % value)

    def set_value_as_name(self, value):
        self.set_value(six.text_type('{[b]}%s{[/b]}') % value)

    def set_value_as_info(self, value):
        self.set_value("{[b]{[u]%s{[/u]{[/b]" % value)

    def set_value_as_infocenter(self, value):
        self.set_value("{[center]}{[b]}{[u]}%s{[/u]{[/b]{[/center]}" % value)

    def set_value_as_header(self, value):
        self.set_value(six.text_type('{[center]}{[i]}%s{[/i]}{[/center]}') % value)

class XferCompLinkLabel(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "LINK"
        self.link = ''

    def set_link(self, link):
        self.link = link.strip()

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        etree.SubElement(compxml, "LINK").text = six.text_type(self.link)
        return compxml

class XferCompButton(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "BUTTON"
        self.action = None
        self.java_script = ""
        self.is_mini = False

    def set_is_mini(self, is_mini):
        if is_mini:
            self.is_mini = True
        else:
            self.is_mini = False

    def set_action(self, request, action, option):
        if (isinstance(action, XferContainerAbstract) or isinstance(action, StubAction)) and check_permission(action, request):
            self.action = (action, option)

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        if self.is_mini:
            compxml.attrib['isMini'] = '1'

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        if self.action is not None:
            xml_acts = etree.SubElement(compxml, "ACTIONS")
            new_xml = get_action_xml(self.action[0], self.action[1])
            if new_xml != None:
                xml_acts.append(new_xml)
        if self.java_script != "":
            etree.SubElement(compxml, "JavaScript").text = six.text_type(urlquote_plus(self.java_script))
        return compxml

class XferCompEdit(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "EDIT"

class XferCompFloat(XferCompButton):

    def __init__(self, name, minval=0.0, maxval=10000.0, precval=2):
        XferCompButton.__init__(self, name)
        self._component_ident = "FLOAT"
        self.min = float(minval)
        self.max = float(maxval)
        self.prec = int(precval)
        self.value = self.min

    def set_value(self, value):
        if value is None:
            self.value = self.min
        else:
            self.value = float(value)

    def _get_content(self):
        value_format = "%%.%df" % self.prec
        return value_format % self.value

    def _get_attribut(self, compxml):
        XferCompButton._get_attribut(self, compxml)
        compxml.attrib['min'] = six.text_type(self.min)
        compxml.attrib['max'] = six.text_type(self.max)
        compxml.attrib['prec'] = six.text_type(self.prec)

class XferCompMemo(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "MEMO"
        self.sub_menu = []
        self.hmin = 200
        self.vmin = 50
        self.with_hypertext = False

    def add_sub_menu(self, name, value):
        self.sub_menu.append((name, value))

    def _get_attribut(self, compxml):
        XferCompButton._get_attribut(self, compxml)
        if self.with_hypertext:
            compxml.attrib['with_hypertext'] = "1"
        else:
            compxml.attrib['with_hypertext'] = "0"

    def get_reponse_xml(self):
        compxml = XferCompButton.get_reponse_xml(self)
        for sub_menu in self.sub_menu:
            xml_menu = etree.SubElement(compxml, "SUBMENU")
            etree.SubElement(xml_menu, "NAME").text = six.text_type(sub_menu[0])
            etree.SubElement(xml_menu, "VALUE").text = six.text_type(sub_menu[1])
        return compxml

class XferCompDate(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "DATE"

    def set_value(self, value):
        if value is None:
            self.value = datetime.date.today()
        else:
            self.value = value

class XferCompTime(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "TIME"

    def set_value(self, value):
        if value is None:
            self.value = datetime.time()
        else:
            self.value = value

class XferCompDateTime(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "DATETIME"

    def set_value(self, value):
        if value is None:
            self.value = datetime.datetime.now()
        else:
            self.value = value

class XferCompCheck(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "CHECK"

    def set_value(self, value):
        value = six.text_type(value)
        if (value == 'False') or (value == '0') or (value == '') or (value == 'n'):
            self.value = 0
        else:
            self.value = 1

class XferCompSelect(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "SELECT"
        self.select_list = {}
        self.value = None

    def set_select(self, select_list):
        self.select_list = select_list

    def set_value(self, value):
        self.value = value

    def get_reponse_xml(self):
        if isinstance(self.select_list, dict):
            list_of_select = list(self.select_list.items())
        else:
            list_of_select = list(self.select_list)
        if self.value is None and (len(list_of_select) > 0) and (len(list_of_select[0]) > 0):
            self.value = list_of_select[0][0]
        compxml = XferCompButton.get_reponse_xml(self)
        for (key, val) in list_of_select:
            xml_case = etree.SubElement(compxml, "CASE")
            xml_case.attrib['id'] = six.text_type(key)
            xml_case.text = six.text_type(val)
        return compxml

class XferCompCheckList(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "CHECKLIST"
        self.select_list = {}
        self.value = []
        self.simple = False

    def set_value(self, value):
        self.value = list(value)

    def set_select(self, select_list):
        self.select_list = select_list

    def _get_content(self):
        return ''

    def _get_attribut(self, compxml):
        XferCompButton._get_attribut(self, compxml)
        if self.simple:
            compxml.attrib['simple'] = '1'
        else:
            compxml.attrib['simple'] = '0'

    def get_reponse_xml(self):
        compxml = XferCompButton.get_reponse_xml(self)
        if isinstance(self.select_list, dict):
            list_of_select = list(self.select_list.items())
        else:
            list_of_select = list(self.select_list)

        for (key, val) in list_of_select:
            xml_case = etree.SubElement(compxml, "CASE")
            xml_case.attrib['id'] = six.text_type(key)
            if key in self.value:
                xml_case.attrib['checked'] = '1'
            else:
                xml_case.attrib['checked'] = '0'
            xml_case.text = six.text_type(val)
        return compxml

class XferCompUpLoad(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "UPLOAD"
        self.fitre = []
        self.compress = False
        self.http_file = False
        self.maxsize = 1024 * 1024  # 1Mo

    def add_filter(self, newfiltre):
        self.fitre.append(newfiltre)

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        if self.compress:
            compxml.attrib['Compress'] = '1'
        if self.http_file:
            compxml.attrib['HttpFile'] = '1'
        compxml.attrib['maxsize'] = six.text_type(self.maxsize)

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        for filte_item in self.fitre:
            etree.SubElement(compxml, "FILTER").text = six.text_type(filte_item)
        return compxml

class XferCompDownLoad(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "DOWNLOAD"
        self.filename = ""
        self.compress = False
        self.http_file = False
        self.maxsize = 1048576

    def set_filename(self, filename):
        self.filename = six.text_type(filename).strip()

    def _get_attribut(self, compxml):
        XferCompButton._get_attribut(self, compxml)
        if self.compress:
            compxml.attrib['Compress'] = '1'
        if self.http_file:
            compxml.attrib['HttpFile'] = '1'
        compxml.attrib['maxsize'] = six.text_type(self.maxsize)

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        etree.SubElement(compxml, "FILENAME").text = self.filename
        return compxml

MAX_GRID_RECORD = 25
GRID_PAGE = 'GRID_PAGE%'

from collections import namedtuple
XferCompHeader = namedtuple('XferCompHeader', 'name descript type')

class XferCompGrid(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "GRID"
        self.headers = []
        self.record_ids = []
        self.records = {}
        self.actions = []
        self.page_max = 0
        self.page_num = 0
        self.nb_lines = 0

    def add_header(self, name, descript, htype=""):
        self.headers.append(XferCompHeader(name, descript, htype))

    def add_action(self, request, action, option, pos_act=-1):
        if 'close' not in option.keys():
            option['close'] = CLOSE_NO
        if (isinstance(action, XferContainerAbstract) or isinstance(action, StubAction)) and check_permission(action, request):
            if pos_act != -1:
                self.actions.insert(pos_act, (action, option))
            else:
                self.actions.append((action, option))

    def define_page(self, xfer_custom=None):
        if xfer_custom is not None:
            self.page_max = int(self.nb_lines / MAX_GRID_RECORD)
            self.page_num = xfer_custom.getparam(GRID_PAGE + self.name)
            if self.page_num is None:
                self.page_num = 0
            else:
                self.page_num = int(self.page_num)
                if self.page_max < self.page_num:
                    self.page_num = 0
            record_min = self.page_num * MAX_GRID_RECORD
            record_max = (self.page_num + 1) * MAX_GRID_RECORD
        else:
            record_min = 0
            record_max = self.nb_lines
            self.page_max = 1
            self.page_num = 0
        return (record_min, record_max)

    def _new_record(self, compid):
        if not compid in self.records.keys():
            new_record = {}
            for header in self.headers:
                if header.type == 'int':
                    new_record[header.name] = 0
                elif header.type == 'float':
                    new_record[header.name] = 0.0
                elif header.type == 'bool':
                    new_record[header.name] = False
                else:
                    new_record[header.name] = ""
            self.records[compid] = new_record
            self.record_ids.append(compid)

    def set_value(self, compid, name, value):
        self._new_record(compid)
        self.records[compid][name] = value

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        if isinstance(self.page_max, six.integer_types) and (self.page_max > 1):
            compxml.attrib['PageMax'] = six.text_type(self.page_max)
            compxml.attrib['PageNum'] = six.text_type(self.page_num)

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        for header in self.headers:
            xml_header = etree.SubElement(compxml, "HEADER")
            xml_header.attrib['name'] = six.text_type(header.name)
            if header.type != "":
                xml_header.attrib['type'] = six.text_type(header.type)
            xml_header.text = six.text_type(header.descript)
        for key in self.record_ids:
            record = self.records[key]
            xml_record = etree.SubElement(compxml, "RECORD")
            xml_record.attrib['id'] = six.text_type(key)
            for header in self.headers:
                xml_value = etree.SubElement(xml_record, "VALUE")
                xml_value.attrib['name'] = six.text_type(header.name)
                xml_value.text = six.text_type(get_value_converted(record[header.name]))
        if len(self.actions) != 0:
            compxml.append(get_actions_xml(self.actions))
        return compxml

    def _add_header_from_model(self, query_set, fieldnames):
        from django.db.models.fields import IntegerField, FloatField, BooleanField
        for fieldname in fieldnames:
            if isinstance(fieldname, tuple):
                verbose_name, fieldname = fieldname
                hfield = 'str'
            else:
                dep_field = query_set.model._meta.get_field_by_name(fieldname)  # pylint: disable=protected-access
                if isinstance(dep_field[0], IntegerField):
                    hfield = 'int'
                elif isinstance(dep_field[0], FloatField):
                    hfield = 'float'
                elif isinstance(dep_field[0], BooleanField):
                    hfield = 'bool'
                else:
                    hfield = 'str'
                verbose_name = dep_field[0].verbose_name
            self.add_header(fieldname, verbose_name, hfield)

    def set_model(self, query_set, fieldnames, xfer_custom=None):
        if fieldnames == None:
            if hasattr(query_set.model, 'default_fields'):
                fieldnames = list(getattr(query_set.model, 'default_fields'))
            else:
                fieldnames = []
        self._add_header_from_model(query_set, fieldnames)
        self.nb_lines = len(query_set)
        primary_key_fieldname = query_set.model._meta.pk.attname  # pylint: disable=protected-access
        record_min, record_max = self.define_page(xfer_custom)
        for value in query_set[record_min:record_max]:
            pk_id = getattr(value, primary_key_fieldname)
            for fieldname in fieldnames:
                if isinstance(fieldname, tuple):
                    _, fieldname = fieldname
                resvalue = getattr(value, fieldname)
                try:
                    field_desc = query_set.model._meta.get_field_by_name(fieldname)  # pylint: disable=protected-access
                    resvalue = get_value_if_choices(resvalue, field_desc)
                except FieldDoesNotExist:
                    pass
                self.set_value(pk_id, fieldname, resvalue)

    def add_actions(self, xfer_custom, model=None, action_list=None):
        if model is None:
            model = xfer_custom.model
        if action_list is None:
            action_list = [('show', _("Edit"), "images/edit.png", SELECT_SINGLE), ('edit', _("Modify"), "images/edit.png", SELECT_SINGLE), \
                         ('del', _("Delete"), "images/delete.png", SELECT_MULTI), ('add', _("Add"), "images/add.png", SELECT_NONE)]
        for act_type, title, icon, unique in action_list:
            self.add_action(xfer_custom.request, ActionsManage.get_act_changed(model.__name__, act_type, title, icon), {'modal':FORMTYPE_MODAL, 'unique':unique})
