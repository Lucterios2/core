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
from logging import getLogger
from datetime import datetime, time, date
import warnings

from django.utils import six
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from lucterios.framework.tools import WrapAction, ActionsManage, SELECT_MULTI, CLOSE_YES, get_actions_json, adapt_value,\
    format_to_string
from lucterios.framework.tools import FORMTYPE_MODAL, SELECT_SINGLE, SELECT_NONE
from lucterios.framework.models import get_format_from_field, extract_format
from lucterios.framework.xferbasic import NULL_VALUE
from lucterios.framework.filetools import md5sum, BASE64_PREFIX


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

    def get_json_value(self):
        return self._get_content()

    def get_json(self):
        compjson = {}
        compjson['name'] = self.name
        compjson['component'] = self._component_ident
        compjson['description'] = self.description
        if isinstance(self.tab, six.integer_types):
            compjson['tab'] = self.tab
        if isinstance(self.col, six.integer_types):
            compjson['x'] = self.col
        if isinstance(self.row, six.integer_types):
            compjson['y'] = self.row
        if isinstance(self.colspan, six.integer_types):
            compjson['colspan'] = self.colspan
        if isinstance(self.rowspan, six.integer_types):
            compjson['rowspan'] = self.rowspan
        if isinstance(self.vmin, six.integer_types):
            compjson['VMin'] = self.vmin
        if isinstance(self.hmin, six.integer_types):
            compjson['HMin'] = self.hmin
        compjson['needed'] = self.needed
        return compjson


class XferCompTab(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
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

    def get_json(self):
        compjson = XferComponent.get_json(self)
        compjson['security'] = self.security
        return compjson


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

    def get_json(self):
        compjson = XferComponent.get_json(self)
        compjson['type'] = self.type
        return compjson


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
        self._formatnum = None
        self._formatstr = None

    def set_format(self, format_string):
        self._formatnum, formatstr = extract_format(format_string)
        if formatstr is not None:
            self._formatstr = formatstr

    def set_value(self, value):
        if value is None:
            self.value = None
        elif isinstance(value, datetime) or isinstance(value, time) or isinstance(value, date):
            self.value = value.isoformat()
        elif isinstance(value, list) or isinstance(value, tuple):
            self.value = list(value)
        elif isinstance(value, object):
            self.value = six.text_type(value)
        else:
            self.value = value

    def set_value_as_title(self, value):
        self._blank_line_before = True
        self._centered = True
        self._underline = True
        self._bold = True
        self.set_value(value)

    def set_value_as_name(self, value):
        self._bold = True
        self.set_value(value)

    def set_value_as_info(self, value):
        self._bold = True
        self._underline = True
        self.set_value(value)

    def set_value_as_infocenter(self, value):
        self._centered = True
        self._underline = True
        self._bold = True
        self.set_value(value)

    def set_value_as_header(self, value):
        self._centered = True
        self._italic = True
        self.set_value(value)

    def set_value_center(self, value):
        self._centered = True
        self.set_value(value)

    def set_value_as_headername(self, value):
        self._centered = True
        self._bold = True
        self.set_value(value)

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

    def _format_label(self):
        if self._formatstr is None:
            self._formatstr = "%s"
        if self._color != 'black':
            self._formatstr = '{[font color="%s"]}%s{[/font]}' % (self._color, self._formatstr)
        if self._bold:
            self._formatstr = '{[b]}%s{[/b]}' % self._formatstr
        if self._italic:
            self._formatstr = '{[i]}%s{[/i]}' % self._formatstr
        if self._underline:
            self._formatstr = '{[u]}%s{[/u]}' % self._formatstr
        if self._centered:
            self._formatstr = '{[center]}%s{[/center]}' % self._formatstr
        if self._blank_line_before:
            self._formatstr = '{[br/]}%s' % self._formatstr

    def get_json(self):
        self._format_label()
        compjson = XferComponent.get_json(self)
        compjson['formatstr'] = self._formatstr
        compjson['formatnum'] = self._formatnum
        return compjson

    @classmethod
    def convert_to_label(cls, old_obj):
        import re
        format_string = None
        value = old_obj.value
        if value is None:
            value = None
        elif isinstance(old_obj, XferCompSelect):
            format_string = {}
            if isinstance(old_obj.select_list, dict):
                old_obj.select_list = list(old_obj.select_list.items())
            if isinstance(old_obj.select_list, list):
                for key, sel_val in old_obj.select_list:
                    format_string[key] = six.text_type(sel_val)
        elif isinstance(old_obj, XferCompCheck):
            format_string = 'B'
            if value:
                value = True
            else:
                value = False
        elif isinstance(old_obj, XferCompDate):
            format_string = 'D'
            if not isinstance(value, date):
                value = date(*[int(subvalue) for subvalue in re.split(r'[^\d]', six.text_type(value))[:3]])
        elif isinstance(old_obj, XferCompDateTime):
            format_string = 'H'
            if not isinstance(value, datetime):
                value = datetime(*[int(subvalue) for subvalue in re.split(r'[^\d]', six.text_type(value))])
        elif isinstance(old_obj, XferCompTime):
            format_string = 'T'
            if not isinstance(value, time):
                value = time(*[int(subvalue) for subvalue in re.split(r'[^\d]', six.text_type(value))[:2]])
        elif isinstance(old_obj, XferCompFloat):
            format_string = 'N%d' % old_obj.prec
        new_lbl = cls(old_obj.name)
        new_lbl.set_value(value)
        new_lbl.set_format(format_string)
        new_lbl.col = old_obj.col
        new_lbl.row = old_obj.row
        new_lbl.vmin = old_obj.vmin
        new_lbl.hmin = old_obj.hmin
        new_lbl.colspan = old_obj.colspan
        new_lbl.rowspan = old_obj.rowspan
        new_lbl.description = old_obj.description
        return new_lbl

    def get_print_value(self):
        return format_to_string(self.value, self._formatnum, self._formatstr)


class XferCompLinkLabel(XferCompLabelForm):

    def __init__(self, name):
        XferCompLabelForm.__init__(self, name)
        self._component_ident = "LINK"
        self.link = ''

    def set_link(self, link):
        self.link = link.strip()

    def get_json(self):
        compjson = XferComponent.get_json(self)
        compjson['link'] = self.link
        return compjson


class XferCompButton(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "BUTTON"
        self.action = None
        self.java_script = ""
        self.is_mini = False
        self.is_default = False

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

    def get_json(self):
        compjson = XferComponent.get_json(self)
        compjson['is_mini'] = self.is_mini
        compjson['is_default'] = self.is_default
        compjson['javascript'] = self.java_script
        if self.action is not None:
            compjson['action'] = self.action[0].get_action_json(modal=self.action[1], close=self.action[2], unique=SELECT_NONE, params=self.action[3])
            compjson['action']['id'] = self.name
            compjson['action']['name'] = self.name
        else:
            compjson['action'] = None
        return compjson


class XferCompEdit(XferCompButton):

    def __init__(self, name):
        XferCompButton.__init__(self, name)
        self._component_ident = "EDIT"
        self.mask = ""
        self.size = -1

    def _get_content(self):
        if self.value is None:
            return ""
        else:
            return self.value

    def get_json(self):
        compjson = XferCompButton.get_json(self)
        compjson['size'] = self.size
        compjson['reg_expr'] = self.mask
        return compjson


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

    def get_json_value(self):
        if self.value is None:
            return NULL_VALUE
        elif self.prec == 0:
            return int(self.value)
        else:
            return float(self.value)

    def get_json(self):
        compjson = XferCompButton.get_json(self)
        compjson['min'] = self.min
        compjson['max'] = self.max
        compjson['prec'] = self.prec
        return compjson


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

    def _get_content(self):
        if self.value is None:
            return ""
        else:
            return self.value

    def get_json(self):
        compjson = XferCompButton.get_json(self)
        compjson['submenu'] = list(self.sub_menu)
        compjson['with_hypertext'] = self.with_hypertext
        return compjson


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

    def get_json(self):
        compjson = XferCompButton.get_json(self)
        compjson['submenu'] = list(self.sub_menu)
        if isinstance(self.schema, six.binary_type):
            self.schema = self.schema.decode()
        compjson['schema'] = self.schema
        return compjson


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
        self._check_case()

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
        self._check_case()

    def set_value(self, value):
        self.value = value
        self._check_case()

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

    def _check_case(self):
        if isinstance(self.select_list, dict):
            list_of_select = list(self.select_list.items())
        else:
            list_of_select = list(self.select_list)
        if len(list_of_select) > 0:
            value_found = False
            for select_item in list_of_select:
                if six.text_type(select_item[0]) == six.text_type(self.value):
                    value_found = True
            if not value_found:
                self.value = list_of_select[0][0]
        return list_of_select

    def get_json(self):
        compjson = XferCompButton.get_json(self)
        compjson['case'] = self._check_case()
        return compjson


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

    def get_json_value(self):
        return self.value

    def get_json(self):
        compjson = XferCompButton.get_json(self)
        if isinstance(self.select_list, dict):
            compjson['case'] = list(self.select_list.items())
        else:
            compjson['case'] = list(self.select_list)
        if (self.simple and (self.simple != 2)) or (self.simple == 1):
            compjson['simple'] = '1'
        elif self.simple == 2:
            compjson['simple'] = '2'
        else:
            compjson['simple'] = '0'
        return compjson


class XferCompUpLoad(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "UPLOAD"
        self.filter = []
        self.compress = False
        self.http_file = False
        self.maxsize = 1024 * 1024  # 1Mo

    def add_filter(self, newfiltre):
        self.filter.append(newfiltre)

    def get_json(self):
        compjson = XferComponent.get_json(self)
        compjson['filter'] = list(self.filter)
        compjson['compress'] = self.compress
        compjson['http_file'] = self.http_file
        compjson['maxsize'] = self.maxsize
        return compjson


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

    def get_json(self):
        compjson = XferCompButton.get_json(self)
        compjson['filename'] = self.filename
        compjson['compress'] = self.compress
        compjson['http_file'] = self.http_file
        compjson['maxsize'] = self.maxsize
        return compjson


SIZE_BY_PAGE = 25
if hasattr(settings, 'SIZE_BY_PAGE'):
    SIZE_BY_PAGE = settings.SIZE_BY_PAGE

GRID_PAGE = 'GRID_PAGE%'
GRID_SIZE = 'GRID_SIZE%'
GRID_ORDER = 'GRID_ORDER%'

DEFAULT_ACTION_LIST = [('show', _("Edit"), "images/show.png", SELECT_SINGLE), ('edit', _("Modify"), "images/edit.png",
                                                                               SELECT_SINGLE), ('delete', _("Delete"), "images/delete.png", SELECT_MULTI), ('add', _("Add"), "images/add.png", SELECT_NONE)]


class XferCompHeader(object):

    def __init__(self, name, descript, htype, orderable, formatstr="%s"):
        self.name = name
        self.descript = descript
        self.htype = htype
        self.orderable = orderable
        self.formatstr = formatstr

    def get_json(self):
        return [self.name, self.descript, self.htype, self.orderable, self.formatstr]


class XferCompGrid(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "GRID"
        self.size_by_page = SIZE_BY_PAGE
        self.nb_lines = 0
        self.headers = []
        self.record_ids = []
        self.records = {}
        self.actions = []
        self.page_max = 0
        self.page_num = 0
        self.order_list = None
        self.no_pager = False

    def add_header(self, name, descript, htype="", horderable=0, formatstr="%s"):
        self.headers.append(XferCompHeader(name, descript, htype, horderable, formatstr))

    def get_header(self, name):
        head_idx = 0
        for header in self.headers:
            if header.name == name:
                return self.headers[head_idx]
            head_idx += 1
        return None

    def delete_header(self, name):
        head_idx = 0
        for header in self.headers:
            if header.name == name:
                break
            head_idx += 1
        if head_idx < len(self.headers):
            del self.headers[head_idx]

    def change_type_header(self, name, htype, formatstr=None):
        head = self.get_header(name)
        if head is not None:
            head.htype = htype
            if formatstr is not None:
                head.formatstr = formatstr

    def add_action(self, request, action, pos_act=-1, modal=FORMTYPE_MODAL, close=CLOSE_YES, unique=SELECT_NONE, params=None):
        if isinstance(action, WrapAction) and action.check_permission(request):
            if pos_act != -1:
                self.actions.insert(pos_act, (action, modal, close, unique, params))
            else:
                self.actions.append((action, modal, close, unique, params))

    def define_page(self, xfer_custom=None):
        self.order_list = None
        if xfer_custom is not None:
            order_txt = xfer_custom.getparam(GRID_ORDER + self.name, '')
            if order_txt != '':
                self.order_list = order_txt.split(',')
        if (xfer_custom is not None) and not xfer_custom.getparam('PRINTING', False):
            self.size_by_page = xfer_custom.getparam(GRID_SIZE + self.name, self.size_by_page)
            self.page_num = xfer_custom.getparam(GRID_PAGE + self.name, 0)
            self.page_max = int(self.nb_lines / self.size_by_page) + 1
            if self.page_max < self.page_num:
                self.page_num = 0
            record_min = self.page_num * self.size_by_page
            record_max = (self.page_num + 1) * self.size_by_page
        else:
            record_min = 0
            record_max = self.nb_lines
            self.size_by_page = self.nb_lines
            self.page_max = 1
            self.page_num = 0
            self.no_pager = True
        return (record_min, record_max)

    def _new_record(self, compid):
        if compid not in self.records.keys():
            new_record = {}
            for header in self.headers:
                if header.htype == 'int':
                    new_record[header.name] = 0
                elif header.htype == 'float':
                    new_record[header.name] = 0.0
                elif header.htype == 'bool':
                    new_record[header.name] = False
                else:
                    new_record[header.name] = ""
            self.records[compid] = new_record
            self.record_ids.append(compid)
            self.records[compid]['__color_ref__'] = None

    def set_value(self, compid, name, value):
        self._new_record(compid)
        self.records[compid][name] = value

    def get_json(self):
        compjson = XferComponent.get_json(self)
        compjson['page_max'] = self.page_max
        compjson['page_num'] = self.page_num
        compjson['order'] = self.order_list
        compjson['headers'] = [head.get_json() for head in self.headers]
        compjson['actions'] = get_actions_json(self.actions)
        compjson['size_by_page'] = self.size_by_page
        compjson['nb_lines'] = self.nb_lines
        compjson['no_pager'] = self.no_pager
        return compjson

    def get_json_value(self):
        compjson = []
        for key in self.record_ids:
            record = self.records[key]
            json_record = {}
            json_record['id'] = key
            for header in self.headers:
                json_record[header.name] = adapt_value(record[header.name])
            for rec_name in record.keys():
                if isinstance(rec_name, six.text_type) and rec_name.startswith('__') and (rec_name not in self.headers):
                    json_record[rec_name] = record[rec_name]
            compjson.append(json_record)
        return compjson

    def _add_header_from_model(self, query_set, fieldnames, has_xfer):
        for fieldname in fieldnames:
            format_str = "%s"
            horderable = 0
            if isinstance(fieldname, tuple):
                verbose_name, fieldname = fieldname
                hfield = None
                if ('.' not in fieldname) and len(query_set) > 0:
                    try:
                        first_record = query_set[0]
                        first_value = getattr(first_record, fieldname)
                        if isinstance(first_value, six.text_type) and first_value.startswith(BASE64_PREFIX):
                            hfield = 'icon'
                    except Exception:
                        pass
            elif fieldname[-4:] == '_set':  # field is one-to-many relation
                dep_field = query_set.model.get_field_by_name(fieldname[:-4])
                hfield = None
                verbose_name = dep_field.related_model._meta.verbose_name
            else:
                dep_field = query_set.model.get_field_by_name(fieldname)
                hfield = get_format_from_field(dep_field)
                if isinstance(hfield, six.text_type) and (';' in hfield):
                    hfield = hfield.split(';')
                    format_str = ";".join(hfield[1:])
                    hfield = hfield[0]
                verbose_name = dep_field.verbose_name
                if has_xfer:
                    horderable = 1
            self.add_header(fieldname, verbose_name, hfield, horderable, format_str)

    def set_model(self, query_set, fieldnames, xfer_custom=None):
        if fieldnames is None:
            fieldnames = query_set.model.get_default_fields()
        self._add_header_from_model(query_set, fieldnames, xfer_custom is not None)
        self.nb_lines = len(query_set)
        primary_key_fieldname = query_set.model._meta.pk.attname
        record_min, record_max = self.define_page(xfer_custom)
        if self.order_list is not None:
            query_set = query_set.order_by(*self.order_list)
        for value in query_set[record_min:record_max]:
            child = value.get_final_child()
            child.set_context(xfer_custom)
            pk_id = getattr(child, primary_key_fieldname)
            self.set_value(pk_id, '__color_ref__', child.get_color_ref())
            for fieldname in fieldnames:
                if isinstance(fieldname, tuple):
                    _, fieldname = fieldname
                if fieldname[-4:] == '_set':  # field is one-to-many relation
                    resvalue = []
                    sub_items = getattr(child, fieldname).all()
                    for sub_items_value in sub_items:
                        resvalue.append(six.text_type(sub_items_value))
                else:
                    resvalue = child
                    for field_name in fieldname.split('.'):
                        if resvalue is not None:
                            try:
                                resvalue = getattr(resvalue, field_name)
                            except (ObjectDoesNotExist, AttributeError):
                                getLogger("lucterios.core").exception("fieldname '%s' not found", field_name)
                                resvalue = None
                self.set_value(pk_id, fieldname, resvalue)

    def add_action_notified(self, xfer_custom, model=None):
        from lucterios.framework.xferadvance import action_list_sorted
        if model is None:
            model = xfer_custom.model.get_long_name()
        elif hasattr(model, "get_long_name"):
            model = model.get_long_name()
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_GRID, xfer_custom, model, key=action_list_sorted, gridname=self.name):
            self.add_action(xfer_custom.request, act, **opt)

    def delete_action(self, url_text, lastitem=False):
        action_idx = 0
        modify_idx = None
        for action in self.actions:
            if action[0].url_text == url_text:
                if (modify_idx is None) or lastitem:
                    modify_idx = action_idx
            action_idx += 1
        if modify_idx is not None:
            del self.actions[modify_idx]
