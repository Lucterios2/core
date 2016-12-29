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
from collections import namedtuple
from logging import getLogger
import warnings

from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.utils.http import urlquote_plus
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from lucterios.framework.tools import get_actions_xml, WrapAction, ActionsManage, SELECT_MULTI,\
    CLOSE_YES
from lucterios.framework.tools import FORMTYPE_MODAL, SELECT_SINGLE, SELECT_NONE
from lucterios.framework.models import get_value_converted, get_value_if_choices
from django.db.models.fields import FieldDoesNotExist
from lucterios.framework.xferbasic import NULL_VALUE
from lucterios.framework.filetools import md5sum


class XferComponent(object):

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
        compxml.attrib['needed'] = six.text_type(
            1) if self.needed else six.text_type(0)

    def get_reponse_xml(self):
        compxml = etree.Element(self._component_ident)
        self._get_attribut(compxml)
        if self._get_content() is None:
            compxml.text = NULL_VALUE
        else:
            compxml.text = six.text_type(self._get_content())
        return compxml


class XferCompTab(XferComponent):

    def __init__(self):
        XferComponent.__init__(self, '')
        self._component_ident = "TAB"

    def set_value(self, value):
        self.value = value.strip()


class XferCompCaptcha(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "CAPTCHA"


class XferCompPassword(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "PASSWD"
        self.security = 1

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        compxml.attrib['security'] = six.text_type(self.security)


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
        self._centered = False
        self._italic = False
        self._bold = False
        self._underline = False
        self._blank_line_before = False
        self._color = 'black'

    def set_value_as_title(self, value):
        self._blank_line_before = True
        self._centered = True
        self._underline = True
        self._bold = True
        self.set_value(six.text_type(value))

    def set_value_as_name(self, value):
        self._bold = True
        self.set_value(six.text_type(value))

    def set_value_as_info(self, value):
        self._bold = True
        self._underline = True
        self.set_value(six.text_type(value))

    def set_value_as_infocenter(self, value):
        self._centered = True
        self._underline = True
        self._bold = True
        self.set_value(six.text_type(value))

    def set_value_as_header(self, value):
        self._centered = True
        self._italic = True
        self.set_value(six.text_type(value))

    def set_value_center(self, value):
        self._centered = True
        self.set_value(six.text_type(value))

    def set_value_as_headername(self, value):
        self._centered = True
        self._bold = True
        self.set_value(six.text_type(value))

    def set_centered(self):
        self._centered = True

    def set_bold(self):
        self._bold = True

    def set_underlined(self):
        self._underline = True

    def set_italic(self):
        self._italic = True

    def set_color(self, color):
        self._color = color

    def add_blank_line_before(self):
        self._blank_line_before = True

    def get_reponse_xml(self):
        if self._color != 'black':
            self.set_value('{[font color="%s"]}%s{[/font]}' %
                           (self._color, self.value))
        if self._bold:
            self.set_value('{[b]}%s{[/b]}' % self.value)
        if self._italic:
            self.set_value('{[i]}%s{[/i]}' % self.value)
        if self._underline:
            self.set_value('{[u]}%s{[/u]}' % self.value)
        if self._centered:
            self.set_value('{[center]}%s{[/center]}' % self.value)
        if self._blank_line_before:
            self.set_value('{[br/]}%s' % self.value)
        return XferComponent.get_reponse_xml(self)


class XferCompLinkLabel(XferCompLabelForm):

    def __init__(self, name):
        XferCompLabelForm.__init__(self, name)
        self._component_ident = "LINK"
        self.link = ''

    def set_link(self, link):
        self.link = link.strip()

    def get_reponse_xml(self):
        compxml = XferCompLabelForm.get_reponse_xml(self)
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

    def set_action(self, request, action, options=None, modal=FORMTYPE_MODAL, close=CLOSE_YES, params=None):
        assert (action is None) or isinstance(action, WrapAction)
        if isinstance(action, WrapAction) and action.check_permission(request):
            if (options is not None) and isinstance(options, dict):
                warnings.warn("[%s.set_action] Deprecated in Lucterios 2.2" % self.__class__.__name__, DeprecationWarning)
                modal = options.get('modal', FORMTYPE_MODAL)
                close = options.get('close', CLOSE_YES)
                params = options.get('params', None)
            self.action = (action, modal, close, params)

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        if self.is_mini:
            compxml.attrib['isMini'] = '1'

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        if self.action is not None:
            xml_acts = etree.SubElement(compxml, "ACTIONS")
            new_xml = self.action[0].get_action_xml(modal=self.action[1], close=self.action[2], unique=SELECT_NONE, params=self.action[3])
            if new_xml is not None:
                new_xml.attrib['id'] = self.name
                new_xml.attrib['name'] = self.name
                xml_acts.append(new_xml)
        if self.java_script != "":
            etree.SubElement(compxml, "JavaScript").text = six.text_type(
                urlquote_plus(self.java_script))
        return compxml


class XferCompEdit(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "EDIT"
        self.mask = ""
        self.size = -1

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        compxml.attrib['size'] = six.text_type(self.size)

    def _get_content(self):
        if self.value is None:
            return ""
        else:
            return self.value

    def get_reponse_xml(self):
        compxml = XferCompButton.get_reponse_xml(self)
        if self.mask != '':
            etree.SubElement(
                compxml, "REG_EXPR").text = six.text_type(self.mask)
        return compxml


class XferCompFloat(XferCompButton):

    def __init__(self, name, minval=0.0, maxval=10000.0, precval=2):
        XferCompButton.__init__(self, name)
        self._component_ident = "FLOAT"
        self.min = float(minval)
        self.max = float(maxval)
        self.prec = int(precval)
        self.value = self.min
        self.needed = True

    def set_value(self, value):
        if value is None:
            self.value = None
        else:
            self.value = float(value)

    def _get_content(self):
        if self.value is None:
            return NULL_VALUE
        else:
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

    def _get_content(self):
        if self.value is None:
            return ""
        else:
            return self.value

    def get_reponse_xml(self):
        compxml = XferCompButton.get_reponse_xml(self)
        for sub_menu in self.sub_menu:
            xml_menu = etree.SubElement(compxml, "SUBMENU")
            etree.SubElement(
                xml_menu, "NAME").text = six.text_type(sub_menu[0])
            etree.SubElement(
                xml_menu, "VALUE").text = six.text_type(sub_menu[1])
        return compxml


class XferCompXML(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "XML"
        self.schema = ""
        self.sub_menu = []
        self.hmin = 200
        self.vmin = 50

    def add_sub_menu(self, name, value):
        self.sub_menu.append((name, value))

    def get_reponse_xml(self):
        compxml = XferCompButton.get_reponse_xml(self)
        etree.SubElement(compxml, "SCHEMA").text = self.schema
        for sub_menu in self.sub_menu:
            xml_menu = etree.SubElement(compxml, "SUBMENU")
            etree.SubElement(
                xml_menu, "NAME").text = six.text_type(sub_menu[0])
            etree.SubElement(
                xml_menu, "VALUE").text = six.text_type(sub_menu[1])
        return compxml


class XferCompDate(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "DATE"

    def set_value(self, value):
        if value is None:
            self.value = None
        else:
            self.value = value


class XferCompTime(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "TIME"

    def set_value(self, value):
        if value is None:
            self.value = None
        else:
            self.value = value


class XferCompDateTime(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "DATETIME"

    def set_value(self, value):
        if value is None:
            self.value = None
        else:
            self.value = value


class XferCompCheck(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "CHECK"

    def set_value(self, value):
        if value is None:
            self.value = None
        else:
            value = six.text_type(value)
            if (value == 'False') or (value == '0') or (value == '') or (value == 'n'):
                self.value = 0
            else:
                self.value = 1


class XferCompSelect(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "SELECT"
        self.select_list = []
        self.value = None

    def set_select(self, select_list):
        self.select_list = select_list

    def set_needed(self, needed):
        self.needed = needed
        if self.needed and (len(self.select_list) > 0) and (self.select_list[0][1] is None):
            del self.select_list[0]

    def set_select_query(self, query):
        self.select_list = []
        if not self.needed:
            self.select_list.append((0, None))
        for item in query:
            try:
                self.select_list.append((item.id, item.get_text_value()))
            except AttributeError:
                self.select_list.append((item.id, six.text_type(item)))

    def set_value(self, value):
        self.value = value

    def get_value_text(self):
        if isinstance(self.select_list, dict):
            return self.select_list[self.value]
        else:
            value_found = False
            for select_item in self.select_list:
                if six.text_type(select_item[0]) == six.text_type(self.value):
                    return select_item[1]
            if not value_found:
                return self.select_list[0][1]

    def get_reponse_xml(self):
        if isinstance(self.select_list, dict):
            list_of_select = list(
                self.select_list.items())
        else:
            list_of_select = list(self.select_list)
        if len(list_of_select) > 0:
            value_found = False
            for select_item in list_of_select:
                if six.text_type(select_item[0]) == six.text_type(self.value):
                    value_found = True
            if not value_found:
                self.value = list_of_select[0][0]
        compxml = XferCompButton.get_reponse_xml(self)
        for (key, val) in list_of_select:
            xml_case = etree.SubElement(compxml, "CASE")
            xml_case.attrib['id'] = six.text_type(key)
            if val is None:
                xml_case.text = "---"
            else:
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
        if isinstance(value, six.text_type):
            value = value.split(";")
        else:
            value = list(value)
        self.value = []
        for item in value:
            self.value.append(six.text_type(item))

    def set_select(self, select_list):
        self.select_list = select_list

    def set_select_query(self, query):
        self.select_list = []
        for item in query:
            self.select_list.append((item.id, six.text_type(item)))

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
            if six.text_type(key) in self.value:
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
            etree.SubElement(
                compxml, "FILTER").text = six.text_type(filte_item)
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

    def set_download(self, filename):
        sign_value = md5sum(filename)
        self.set_filename(
            "CORE/download?filename=%s&sign=%s" % (filename, sign_value))

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
if hasattr(settings, 'MAX_GRID_RECORD'):
    MAX_GRID_RECORD = settings.MAX_GRID_RECORD

GRID_PAGE = 'GRID_PAGE%'
GRID_ORDER = 'GRID_ORDER%'

DEFAULT_ACTION_LIST = [('show', _("Edit"), "images/show.png", SELECT_SINGLE), ('edit', _("Modify"), "images/edit.png",
                                                                               SELECT_SINGLE), ('delete', _("Delete"), "images/delete.png", SELECT_MULTI), ('add', _("Add"), "images/add.png", SELECT_NONE)]

XferCompHeader = namedtuple('XferCompHeader', 'name descript type orderable')


class XferCompGrid(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "GRID"
        self.max_grid_record = MAX_GRID_RECORD
        self.headers = []
        self.record_ids = []
        self.records = {}
        self.actions = []
        self.page_max = 0
        self.page_num = 0
        self.nb_lines = 0
        self.order_list = None

    def add_header(self, name, descript, htype="", horderable=0):
        self.headers.append(XferCompHeader(name, descript, htype, horderable))

    def delete_header(self, name):
        head_idx = 0
        for header in self.headers:
            if header.name == name:
                break
            head_idx += 1
        if head_idx < len(self.headers):
            del self.headers[head_idx]

    def change_type_header(self, name, htype):
        head_idx = 0
        for header in self.headers:
            if header.name == name:
                break
            head_idx += 1
        if head_idx < len(self.headers):
            self.headers[head_idx] = XferCompHeader(self.headers[head_idx].name, self.headers[
                                                    head_idx].descript, htype, self.headers[head_idx].orderable)

    def add_action(self, request, action, options=None, pos_act=-1, modal=FORMTYPE_MODAL, close=CLOSE_YES, unique=SELECT_NONE, params=None):
        if isinstance(action, WrapAction) and action.check_permission(request):
            if isinstance(options, dict):
                warnings.warn("[XferCompGrid.add_action] Deprecated in Lucterios 2.2", DeprecationWarning)
                modal = options.get('modal', FORMTYPE_MODAL)
                close = options.get('close', CLOSE_YES)
                unique = options.get('unique', SELECT_NONE)
                params = options.get('params', None)
            if pos_act != -1:
                self.actions.insert(pos_act, (action, modal, close, unique, params))
            else:
                self.actions.append((action, modal, close, unique, params))

    def define_page(self, xfer_custom=None):
        if (xfer_custom is not None) and not xfer_custom.getparam('PRINTING', False):
            order_txt = xfer_custom.getparam(GRID_ORDER + self.name, '')
            if order_txt == '':
                self.order_list = None
            else:
                self.order_list = order_txt.split(',')
            self.page_max = int(self.nb_lines / self.max_grid_record) + 1
            self.page_num = xfer_custom.getparam(GRID_PAGE + self.name, 0)
            if self.page_max < self.page_num:
                self.page_num = 0
            record_min = self.page_num * self.max_grid_record
            record_max = (self.page_num + 1) * self.max_grid_record
        else:
            record_min = 0
            record_max = self.nb_lines
            self.order_list = None
            self.page_max = 1
            self.page_num = 0
        return (record_min, record_max)

    def _new_record(self, compid):
        if compid not in self.records.keys():
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
        if self.order_list is not None:
            compxml.attrib['order'] = ",".join(self.order_list)

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        for header in self.headers:
            xml_header = etree.SubElement(compxml, "HEADER")
            xml_header.attrib['name'] = six.text_type(header.name)
            if header.type != "":
                xml_header.attrib['type'] = six.text_type(header.type)
            xml_header.attrib['orderable'] = six.text_type(header.orderable)
            xml_header.text = six.text_type(header.descript)
        for key in self.record_ids:
            record = self.records[key]
            xml_record = etree.SubElement(compxml, "RECORD")
            xml_record.attrib['id'] = six.text_type(key)
            for header in self.headers:
                xml_value = etree.SubElement(xml_record, "VALUE")
                xml_value.attrib['name'] = six.text_type(header.name)
                xml_value.text = six.text_type(
                    get_value_converted(record[header.name]))
        if len(self.actions) != 0:
            compxml.append(get_actions_xml(self.actions))
        return compxml

    def _add_header_from_model(self, query_set, fieldnames, has_xfer):
        from django.db.models.fields import IntegerField, FloatField, BooleanField
        for fieldname in fieldnames:
            horderable = 0
            if isinstance(fieldname, tuple):
                verbose_name, fieldname = fieldname
                hfield = 'str'
            elif fieldname[-4:] == '_set':  # field is one-to-many relation
                dep_field = query_set.model.get_field_by_name(
                    fieldname[:-4])
                hfield = 'str'
                verbose_name = dep_field.related_model._meta.verbose_name
            else:
                dep_field = query_set.model.get_field_by_name(
                    fieldname)
                if isinstance(dep_field, IntegerField):
                    hfield = 'int'
                elif isinstance(dep_field, FloatField):
                    hfield = 'float'
                elif isinstance(dep_field, BooleanField):
                    hfield = 'bool'
                else:
                    hfield = 'str'
                verbose_name = dep_field.verbose_name
                if has_xfer:
                    horderable = 1
            self.add_header(fieldname, verbose_name, hfield, horderable)

    def set_model(self, query_set, fieldnames, xfer_custom=None):
        if fieldnames is None:
            fieldnames = query_set.model.get_default_fields()
        self._add_header_from_model(
            query_set, fieldnames, xfer_custom is not None)
        self.nb_lines = len(query_set)
        primary_key_fieldname = query_set.model._meta.pk.attname
        record_min, record_max = self.define_page(xfer_custom)
        if self.order_list is not None:
            query_set = query_set.order_by(*self.order_list)
        for value in query_set[record_min:record_max]:
            child = value.get_final_child()
            child.set_context(xfer_custom)
            pk_id = getattr(child, primary_key_fieldname)
            for fieldname in fieldnames:
                if isinstance(fieldname, tuple):
                    _, fieldname = fieldname
                if fieldname[-4:] == '_set':  # field is one-to-many relation
                    resvalue = []
                    sub_items = getattr(child, fieldname).all()
                    for sub_items_value in sub_items:
                        resvalue.append(six.text_type(sub_items_value))
                    resvalue = "{[br/]}".join(resvalue)
                else:
                    resvalue = child
                    for field_name in fieldname.split('.'):
                        if resvalue is not None:
                            try:
                                resvalue = getattr(resvalue, field_name)
                            except ObjectDoesNotExist:
                                getLogger("lucterios.core").exception("fieldname '%s' not found", field_name)
                                resvalue = None
                    try:
                        field_desc = query_set.model.get_field_by_name(
                            fieldname)
                        resvalue = get_value_if_choices(resvalue, field_desc)
                    except FieldDoesNotExist:
                        pass
                self.set_value(pk_id, fieldname, resvalue)

    def add_actions(self, xfer_custom, model=None, action_list=None):
        if model is None:
            model = xfer_custom.model
        if action_list is None:
            action_list = DEFAULT_ACTION_LIST
        for act_type, title, icon, unique in action_list:
            self.add_action(xfer_custom.request, ActionsManage.get_act_changed(
                model.__name__, act_type, title, icon), modal=FORMTYPE_MODAL, unique=unique)

    def add_action_notified(self, xfer_custom, model=None):
        from lucterios.framework.xferadvance import action_list_sorted
        if model is None:
            model = xfer_custom.model.get_long_name()
        elif hasattr(model, "get_long_name"):
            model = model.get_long_name()
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_GRID, xfer_custom, model, key=action_list_sorted, gridname=self.name):
            self.add_action(xfer_custom.request, act, **opt)

    def delete_action(self, url_text):
        modify_idx = 0
        for action in self.actions:
            if action[0].url_text == url_text:
                break
            modify_idx += 1
        if modify_idx < len(self.actions):
            del self.actions[modify_idx]
