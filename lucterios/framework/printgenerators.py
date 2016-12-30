# -*- coding: utf-8 -*-
"""
Tools to generate print xml for action, listing or label

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
"""

from __future__ import unicode_literals
from lxml import etree
from copy import deepcopy
from os.path import join, dirname, isfile
import logging
import datetime
import re

from django.utils import six
from django.db.models import Q

from lucterios.framework.xfercomponents import XferCompTab, \
    XferCompLinkLabel, XferCompLabelForm, XferCompImage, XferCompGrid, \
    XferCompDate, XferCompDateTime, XferCompSelect, XferCompTime, XferCompCheck
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.tools import toHtml
from lucterios.framework.filetools import BASE64_PREFIX, get_image_absolutepath, \
    get_image_size
from lucterios.framework.models import get_value_converted
from lucterios.framework.reporting import transforme_xml2pdf, get_text_size
from lucterios.framework.xferbasic import XferContainerAbstract

DPI = 0.3528125


def remove_format(xml_text):
    xml_text = xml_text.replace('&#160;', ' ')
    xml_text = xml_text.replace('<b>', '')
    xml_text = xml_text.replace('<i>', '')
    xml_text = xml_text.replace('<u>', '')
    xml_text = xml_text.replace('</b>', '')
    xml_text = xml_text.replace('</i>', '')
    xml_text = xml_text.replace('</u>', '')
    xml_text = xml_text.replace('{[b]}', '')
    xml_text = xml_text.replace('{[i]}', '')
    xml_text = xml_text.replace('{[u]}', '')
    xml_text = xml_text.replace('{[/b]}', '')
    xml_text = xml_text.replace('{[/i]}', '')
    xml_text = xml_text.replace('{[/u]}', '')
    xml_text = xml_text.replace('{[br/]}', '')
    xml_text = xml_text.replace('{[newline]}', '')
    xml_text = xml_text.replace('{[bold]}', '')
    xml_text = xml_text.replace('{[/bold]}', '')
    xml_text = xml_text.replace('{[italic]}', '')
    xml_text = xml_text.replace('{[/italic]}', '')
    xml_text = xml_text.replace('{[underline]}', '')
    xml_text = xml_text.replace('{[/underline]}', '')
    return xml_text


def calcul_text_size(text, font_size=9, line_height=10, text_align='left', is_cell=False):
    text = six.text_type(text)
    text = text.replace('<br/>', '\n')
    text = text.replace('{[br/]}', '\n')
    text = text.replace('{[newline]}', '\n')
    if text == '\n':
        text = 'A'
    width, height = get_text_size(
        remove_format(text), font_size, line_height, text_align, is_cell)
    width = max(10.0, width * 1.2)
    height = height * 1.2
    return width, height


def convert_to_html(tagname, text, font_family="sans-serif", font_size=9, line_height=10, text_align='left'):
    try:
        xml_text = etree.XML(
            "<%(tagname)s>%(text)s</%(tagname)s>" % {'tagname': tagname, 'text': toHtml(text)})
        xml_text.attrib['font_family'] = font_family
        xml_text.attrib['font_size'] = "%d" % font_size
        xml_text.attrib['line_height'] = "%d" % line_height

        xml_text.attrib['text_align'] = text_align
        xml_text.attrib['spacing'] = "0.0"
    except etree.XMLSyntaxError:
        raise Exception(
            'convert_to_html error:tagname=%s text=%s' % (tagname, text))
    return xml_text


def convert_text_xml(xml_text):
    if 'font_family' in xml_text.attrib:
        font_family = xml_text.attrib['font_family']
    else:
        font_family = "sans-serif"
    if 'font_size' in xml_text.attrib:
        font_size = int(xml_text.attrib['font_size'])
    else:
        font_size = 9
    if 'line_height' in xml_text.attrib:
        line_height = int(xml_text.attrib['line_height'])
    else:
        line_height = 10
    if 'text_align' in xml_text.attrib:
        text_align = xml_text.attrib['text_align']
    else:
        text_align = 'center'
    return convert_to_html(xml_text.tag, xml_text.text, font_family, font_size, line_height, text_align)


class PrintItem(object):

    def __init__(self, comp, owner):
        self.comp = comp
        self.owner = owner
        self.tab = comp.tab
        self.col = comp.col
        self.row = comp.row
        self.colspan = comp.colspan
        self.rowspan = comp.rowspan
        self.size_x = 0
        self.height = 0
        self.width = 0
        self.left = 0
        self.top = 0

    def fill_attrib(self, xml_comp):
        xml_comp.attrib['height'] = "%d.0" % self.height
        xml_comp.attrib['width'] = "%d.0" % self.width
        xml_comp.attrib['top'] = "%d.0" % self.top
        xml_comp.attrib['left'] = "%d.0" % self.left
        xml_comp.attrib['spacing'] = "0.0"

    def calcul_position(self):
        self.left = 0
        self.width = 0
        self.top = self.owner.top
        for col_idx in range(0, self.col):
            self.left = self.left + self.owner.col_width[self.tab][col_idx]
        for col_idx in range(self.col, self.col + self.colspan):
            self.width = self.width + self.owner.col_width[self.tab][col_idx]


class PrintImage(PrintItem):

    def __init__(self, comp, owner):
        PrintItem.__init__(self, comp, owner)
        if self.comp.type != '':
            if self.comp.value[:len(BASE64_PREFIX)] == BASE64_PREFIX:
                self.value = self.comp.value
            else:
                self.value = BASE64_PREFIX + self.comp.value
        else:
            self.value = get_image_absolutepath(self.comp.value)
        self.img_size = get_image_size(self.value)
        self.size_x = int(round(self.img_size[0] * DPI * 1.1))
        self.height = int(round(self.img_size[1] * DPI * 1.1))

    def get_xml(self):
        xml_img = etree.Element('image')
        xml_img.text = self.value
        if (abs(self.width) < 0.0001) or ((self.img_size[0] * DPI) < self.width):
            self.width = int(round(self.img_size[0] * DPI))
            self.height = int(round(self.img_size[1] * DPI))
        else:
            self.height = int(
                round(self.width * self.img_size[1] / self.img_size[0]))
        self.fill_attrib(xml_img)
        return xml_img


class PrintTable(PrintItem):

    RATIO = 1.4

    def __init__(self, comp, owner):
        PrintItem.__init__(self, comp, owner)
        self.columns = []
        self.rows = []
        self.size_rows = [0]
        self.compute_table_size()
        self.size_y, self.size_x = self.get_table_sizes()
        self.height = self.size_y * self.RATIO
        self.letter_ratio = 1.0
        self.width_ratio = 1.0

    def compute_table_size(self):
        for header in self.comp.headers:
            size_cx, size_cy = calcul_text_size(
                header.descript, 9, 10, "center", True)
            column = [header.descript, size_cx * self.RATIO]
            self.size_rows[0] = max(self.size_rows[0], size_cy)
            row_idx = 0
            for record in self.comp.records.values():
                while len(self.rows) <= row_idx:
                    self.rows.append([])
                while len(self.size_rows) <= (row_idx + 1):
                    self.size_rows.append(0)
                value = get_value_converted(record[header.name], True)
                if header.type == 'icon':
                    value = BASE64_PREFIX + value
                    img_size = get_image_size(value)
                    size_x = int(round(img_size[0] * DPI))
                    size_y = int(round(img_size[1] * DPI))
                else:
                    size_x, size_y = calcul_text_size(
                        value, 9, 10, "start", True)
                self.rows[row_idx].append(six.text_type(value))
                self.size_rows[
                    row_idx + 1] = max(self.size_rows[row_idx + 1], size_y)
                column[1] = max(column[1], size_x * self.RATIO)
                row_idx += 1
            self.columns.append(column)

    def get_table_sizes(self):
        size_x = 0
        for column in self.columns:
            size_x = size_x + column[1]
        size_y = 0
        for size_row in self.size_rows:
            size_y += size_row
        if len(self.size_rows) == 1:
            _cx, size_cy = calcul_text_size("A", 9, 10, "center", True)
            size_y += size_cy
        return size_y, size_x

    def size_ratio(self, init_size):
        return min(init_size, int(init_size * self.letter_ratio))

    def write_columns(self, xml_table):
        for column in self.columns:
            size_col = int(round(self.width_ratio * column[1]))
            new_col = etree.SubElement(xml_table, "columns")
            new_col.attrib['width'] = "%d.0" % size_col
            xml_text = convert_to_html(
                'cell', "{[i]}%s{[/i]}" % column[0], "sans-serif", self.size_ratio(9), self.size_ratio(10), "center")
            new_col.append(xml_text)

    def write_rows(self, xml_table):
        for row in self.rows:
            new_row = etree.SubElement(xml_table, "rows")
            for value in row:
                xml_text = convert_to_html(
                    'cell', value, "sans-serif", self.size_ratio(9), self.size_ratio(10), "start")
                if value[:len(BASE64_PREFIX)] == BASE64_PREFIX:
                    xml_text.attrib['image'] = "1"
                new_row.append(xml_text)

    def get_xml(self):
        if len(self.rows) == 0:
            row = []
            for _ in self.columns:
                row.append('')
            self.rows.append(row)
            self.size_rows.append(calcul_text_size('')[1])
        xml_table = etree.Element('table')
        self.width_ratio = self.width / self.size_x
        self.letter_ratio = min(1.33, max(0.66, self.width_ratio))
        self.write_columns(xml_table)
        self.write_rows(xml_table)
        self.fill_attrib(xml_table)
        return xml_table

    def calcul_position(self):
        PrintItem.calcul_position(self)
        self.top = self.owner.top + 3
        self.left -= 1
        self.width -= 2


class PrintTab(PrintItem):

    SEP_HEIGHT = 5

    def __init__(self, comp, owner):
        PrintItem.__init__(self, comp, owner)
        self.size_x, size_y = calcul_text_size(self.comp.value)
        self.height = size_y + self.SEP_HEIGHT * 2

    def calcul_position(self):
        self.left = 10
        self.owner.top += self.SEP_HEIGHT / 2
        self.top = self.owner.top
        self.width = self.owner.page_width - 2 * \
            self.owner.horizontal_marge - self.left

    def get_xml(self):
        xml_text = convert_to_html('text', "{[u]}%s{[/u]}" % self.comp.value)
        self.top += self.SEP_HEIGHT
        self.fill_attrib(xml_text)
        return xml_text


class PrintLabel(PrintItem):

    def __init__(self, comp, owner):
        PrintItem.__init__(self, comp, owner)
        try:
            if isinstance(self.comp, XferCompDate):
                if isinstance(self.comp.value, datetime.date):
                    self.value = self.comp.value
                else:
                    self.value = datetime.date(
                        *[int(subvalue) for subvalue in re.split(r'[^\d]', six.text_type(self.comp.value))[:3]])
            elif isinstance(self.comp, XferCompDateTime):
                if isinstance(self.comp.value, datetime.datetime):
                    self.value = self.comp.value
                else:
                    self.value = datetime.datetime(
                        *[int(subvalue) for subvalue in re.split(r'[^\d]', six.text_type(self.comp.value))])
            elif isinstance(self.comp, XferCompTime):
                if isinstance(self.comp.value, datetime.time):
                    self.value = self.comp.value
                else:
                    self.value = datetime.time(
                        *[int(subvalue) for subvalue in re.split(r'[^\d]', six.text_type(self.comp.value))[:2]])
            elif isinstance(self.comp, XferCompSelect):
                self.value = self.comp.get_value_text()
            elif isinstance(self.comp, XferCompCheck):
                self.value = get_value_converted(bool(self.comp.value), True)
            else:
                self.value = self.comp.value
        except Exception as err:
            logging.getLogger("lucterios.core.print").exception(
                six.text_type(err))
            self.value = six.text_type(self.comp.value)
        self.value = get_value_converted(self.value, True)
        self.size_x, self.height = calcul_text_size(self.value)
        self.height = self.height * 1.1

    def get_xml(self):
        xml_text = convert_to_html('text', self.value)
        self.fill_attrib(xml_text)
        return xml_text


class ReportGenerator(object):

    def __init__(self):
        self.title = ''
        self.modelxml = etree.Element('model')
        self.page_width = 210
        self.page_height = 297
        self.horizontal_marge = 10
        self.vertical_marge = 10
        self.header_height = 0
        self.bottom_height = 0
        self.header = None
        self.bottom = None
        self.body = None
        self.content_width = 0
        self.mode = 0
        self.xfer = XferContainerAbstract()

    def fill_attrib_headerfooter(self):
        if self.header is not None:
            self.header.attrib['extent'] = "%d.0" % self.header_height
        if self.bottom is not None:
            self.bottom.attrib['extent'] = "%d.0" % self.bottom_height

    def get_num_page(self):
        return len(self.modelxml.xpath("page"))

    def add_page(self):
        self.content_width = self.page_width - 2 * self.horizontal_marge
        page = etree.SubElement(self.modelxml, "page")
        self.header = etree.SubElement(page, "header")
        self.bottom = etree.SubElement(page, "bottom")
        self.body = etree.SubElement(page, "body")
        self.fill_attrib_headerfooter()

    def get_text_from_title(self):
        xml_text = convert_to_html(
            'text', "{[b]}{[u]}%s{[/u]}{[/b]}" % self.title, text_align='center')
        xml_text.attrib['height'] = "%d.0" % 12
        xml_text.attrib['width'] = "%d.0" % self.content_width
        xml_text.attrib['top'] = "0.0"
        xml_text.attrib['left'] = "0.0"
        return xml_text

    def fill_attrib(self):
        self.modelxml.attrib['page_width'] = "%d.0" % self.page_width
        self.modelxml.attrib['page_height'] = "%d.0" % self.page_height
        self.modelxml.attrib['margin_right'] = "%d.0" % self.horizontal_marge
        self.modelxml.attrib['margin_left'] = "%d.0" % self.horizontal_marge
        self.modelxml.attrib['margin_bottom'] = "%d.0" % self.vertical_marge
        self.modelxml.attrib['margin_top'] = "%d.0" % self.vertical_marge
        self.fill_attrib_headerfooter()

    def fill_content(self, request):
        if request is not None:
            self.xfer._initialize(request)

    def generate(self, request):
        self.modelxml = etree.Element('model')
        self.add_page()
        self.fill_content(request)
        self.fill_attrib()
        xml_generated = etree.tostring(
            self.modelxml, xml_declaration=True, pretty_print=True, encoding='utf-8')
        logging.getLogger("lucterios.core.print").debug(
            xml_generated.decode("utf-8"))
        return xml_generated

    def generate_report(self, request, is_csv):
        report_content = self.generate(request)
        if is_csv:
            xsl_file = join(dirname(__file__), "ConvertxlpToCSV.xsl")
            if not isfile(xsl_file):
                raise LucteriosException(GRAVE, "Error:no csv xsl file!")
            with open(xsl_file, 'rb') as xsl_file:
                csv_transform = etree.XSLT(etree.XML(xsl_file.read()))
            xml_rep_content = etree.XML(report_content)
            for xml_br in xml_rep_content.xpath("//br"):
                xml_br.text = ' '
            content = six.text_type(
                csv_transform(xml_rep_content)).encode('utf-8')
        else:
            content = transforme_xml2pdf(report_content)
        if len(content) > 0:
            return content
        else:
            return ""


class ActionGenerator(ReportGenerator):

    def __init__(self, action, tab_change_page):
        ReportGenerator.__init__(self)
        self.action = action
        self.header_height = 12
        self.last_top = 0
        self.top = 0
        self.print_items = []
        self.col_width = {}
        self.tab_change_page = tab_change_page

    def add_page(self):
        ReportGenerator.add_page(self)
        self.header.append(self.get_text_from_title())
        self.top = 0

    def change_page(self, check_top_value=True):
        if not check_top_value or (self.top > (self.page_height - 2 * self.vertical_marge)):
            self.add_page()

    def compute_components(self):
        col_size = {}
        max_col = {}
        sortedkey_components, final_components = self.action.get_sort_components()
        for key in sortedkey_components:
            comp = final_components[key]
            new_item = None
            if isinstance(comp, XferCompImage):
                new_item = PrintImage(comp, self)
            elif isinstance(comp, XferCompGrid):
                new_item = PrintTable(comp, self)
            elif isinstance(comp, XferCompTab):
                new_item = PrintTab(comp, self)
            elif isinstance(comp, XferCompLinkLabel) or isinstance(comp, XferCompLabelForm) or \
                    isinstance(comp, XferCompDate) or isinstance(comp, XferCompDateTime) \
                    or isinstance(comp, XferCompTime) or isinstance(comp, XferCompSelect) or isinstance(comp, XferCompCheck):
                new_item = PrintLabel(comp, self)
            if new_item is not None:
                if new_item.tab not in col_size.keys():
                    col_size[new_item.tab] = []
                if new_item.tab not in max_col.keys():
                    max_col[new_item.tab] = 0
                new_size_x = new_item.size_x / new_item.colspan
                for item_idx in range(0, new_item.col + new_item.colspan):
                    while len(col_size[new_item.tab]) <= item_idx:
                        col_size[new_item.tab].append(0)
                    if item_idx >= new_item.col:
                        col_size[new_item.tab][item_idx] = max(
                            col_size[new_item.tab][item_idx], new_size_x)
                max_col[new_item.tab] = max(
                    max_col[new_item.tab], new_item.col + new_item.colspan)
                self.print_items.append(new_item)
        return max_col, col_size

    def define_col_size(self, tab_id, col_size, max_col):
        total_size = 0
        self.col_width[tab_id] = []
        for col_idx in range(0, max_col):
            total_size = total_size + col_size[col_idx]
        for col_idx in range(0, max_col):
            if total_size == 0:
                new_col_size = 0
            else:
                new_col_size = int(round(self.content_width * col_size[col_idx] / total_size))
            self.col_width[tab_id].append(new_col_size)

    def fill_content(self, request):
        self.action._initialize(request)
        self.action.params['PRINTING'] = True
        self.action.fillresponse(**self.action._get_params())
        self.action._finalize()
        self.print_items = []
        self.col_width = {}
        max_col, col_size = self.compute_components()
        if len(max_col) == 0:
            raise LucteriosException(IMPORTANT, "No colunm to print!")
        for tab_id in max_col.keys():
            self.define_col_size(tab_id, col_size[tab_id], max_col[tab_id])
        self.top = 0
        last_y = -1
        num_tab = 0
        current_height = 0
        self.last_top = 0
        for item in self.print_items:
            new_page = False
            if self.tab_change_page and isinstance(item, PrintTab):
                num_tab += 1
                if (num_tab > 1):
                    self.add_page()
                    current_height = 0
                    new_page = True
            if not new_page and (last_y != item.row):
                self.top = self.top + current_height
                for last_item in self.print_items:
                    if last_item == item:
                        break
                    if ((item.row == -1) and not self.tab_change_page) or ((last_item.tab == item.tab) and ((last_item.row + last_item.rowspan) <= (item.row + item.rowspan))):
                        self.top = max(
                            self.top, last_item.top + last_item.height)
                self.change_page()
                current_height = 0
            item.calcul_position()
            self.body.append(item.get_xml())
            if item.rowspan == 1:
                current_height = max(current_height, item.height)
            last_y = item.row
            self.last_top = item.top + item.height


class ReportModelGenerator(ReportGenerator):

    def __init__(self, model):
        ReportGenerator.__init__(self)
        self.model = model
        self.filter = None
        self.filter_callback = None

    def get_items_filtered(self):
        if isinstance(self.filter, Q) and (len(self.filter.children) > 0):
            item_list = self.model.objects.filter(
                self.filter)
        else:
            item_list = self.model.objects.all()
        if self.filter_callback is None:
            return item_list
        else:
            return self.filter_callback(item_list)

    @staticmethod
    def copy_attribs(source_node, target_node):
        for att_name in source_node.keys():
            target_node.attrib[att_name] = source_node.get(att_name)

    @staticmethod
    def add_convert_model(node, partname, report_xml, current_item, xfer):
        current_item.set_context(xfer)
        for item in report_xml.xpath(partname)[0]:
            if item.tag == 'text':
                new_item = convert_to_html(
                    'text', current_item.evaluate(item.text))
                ReportModelGenerator.copy_attribs(item, new_item)
            elif item.tag == 'table':
                new_item = etree.Element('table')
                ReportModelGenerator.copy_attribs(item, new_item)
                for column in item.xpath('columns'):
                    new_column = etree.SubElement(new_item, 'columns')
                    new_column.attrib['width'] = column.get('width')
                    new_cell = convert_to_html(
                        'cell', current_item.evaluate(column.text))
                    ReportModelGenerator.copy_attribs(column, new_cell)
                    new_column.append(new_cell)
                for row in item.xpath('rows'):
                    sub_values = [current_item]
                    data = row.get('data')
                    if hasattr(current_item, six.text_type(data)):
                        new_value = getattr(current_item, data)
                        if data[-4:] == '_set':
                            sub_values = new_value.all()
                            if hasattr(current_item, data[:-4] + '_query'):
                                sub_values = sub_values.filter(
                                    getattr(current_item, data[:-4] + '_query'))
                        elif hasattr(new_value, "evaluate"):
                            sub_values = [new_value]
                    for sub_value in sub_values:
                        sub_value.set_context(xfer)
                        new_row = etree.SubElement(new_item, 'rows')
                        for cell in row.xpath('cell'):
                            new_cell = convert_to_html(
                                'cell', sub_value.evaluate(cell.text))
                            ReportModelGenerator.copy_attribs(cell, new_cell)
                            new_row.append(new_cell)
            elif item.tag == 'image':
                new_item = deepcopy(item)
                new_item.text = current_item.evaluate(item.text)
            else:
                new_item = deepcopy(item)
            node.append(new_item)


class ListingGenerator(ReportModelGenerator):

    def __init__(self, model):
        ReportModelGenerator.__init__(self, model)
        self.header_height = 12
        self.columns = []

    def add_page(self):
        ReportGenerator.add_page(self)
        self.header.append(self.get_text_from_title())

    def fill_content(self, request):
        ReportModelGenerator.fill_content(self, request)
        xml_table = etree.Element('table')
        self.body.append(xml_table)
        xml_table.attrib['height'] = "%d.0" % (
            self.page_height - 2 * self.vertical_marge)
        xml_table.attrib['width'] = "%d.0" % self.content_width
        xml_table.attrib['top'] = "0.0"
        xml_table.attrib['left'] = "0.0"
        xml_table.attrib['spacing'] = "0.0"
        size_x = 0
        for column in self.columns:
            size_x += int(round(column[0]))
        for column in self.columns:
            size_col = int(
                round(self.content_width * int(round(column[0])) / size_x))
            new_col = etree.SubElement(xml_table, "columns")
            new_col.attrib['width'] = "%d.0" % size_col
            xml_text = convert_to_html(
                'cell', column[1], "sans-serif", 9, 10, "center")
            xml_text.attrib['font_family'] = "sans-serif"
            xml_text.attrib['font_size'] = "9"
            xml_text.attrib['line_height'] = "10"
            xml_text.attrib['text_align'] = "center"
            new_col.append(xml_text)
        for item in self.get_items_filtered():
            item.set_context(self.xfer)
            new_row = etree.SubElement(xml_table, "rows")
            for column in self.columns:
                xml_text = convert_to_html(
                    'cell', item.evaluate(column[2]), "sans-serif", 9, 10, "start")
                new_row.append(xml_text)


class LabelGenerator(ReportModelGenerator):

    def __init__(self, model, first_label):
        ReportModelGenerator.__init__(self, model)
        self.first_label = first_label
        self.label_text = ""
        self.label_size = {'page_width': 210, 'page_height': 297, 'cell_width': 105, 'cell_height': 70, 'columns': 2,
                           'rows': 4, 'left_marge': 0, 'top_marge': 8, 'horizontal_space': 105, 'vertical_space': 70}

    def fill_content(self, request):
        ReportModelGenerator.fill_content(self, request)
        self.horizontal_marge = self.label_size['left_marge']
        self.vertical_marge = self.label_size['top_marge']
        self.page_width = self.label_size['page_width']
        self.page_height = self.label_size['page_height']
        label_values = []
        for _ in range(1, self.first_label):
            label_values.append("")
        for item in self.get_items_filtered():
            item.set_context(self.xfer)
            label_values.append(item.evaluate(self.label_text))
        index = 0
        for labelval in label_values:
            if index == (self.label_size['columns'] * self.label_size['rows']):
                index = 0
                self.add_page()
            col_num = index % self.label_size['columns']
            row_num = int(index / self.label_size['columns'])
            left = col_num * self.label_size['horizontal_space']
            top = row_num * self.label_size['vertical_space']
            if self.mode == 0:
                xml_text = convert_to_html(
                    'text', labelval, "sans-serif", 9, 10, "center")
                xml_text.attrib['height'] = "%d.0" % self.label_size[
                    'cell_height']
                xml_text.attrib['width'] = "%d.0" % self.label_size[
                    'cell_width']
                xml_text.attrib['top'] = "%d.0" % top
                xml_text.attrib['left'] = "%d.0" % left
                xml_text.attrib['spacing'] = "0.0"
                self.body.append(xml_text)
            else:
                docroot = etree.XML(labelval)
                for xml_text in docroot.find('body').iter():
                    if xml_text.tag == 'body':
                        continue
                    if xml_text.tag == 'text':
                        new_xml_text = convert_text_xml(xml_text)
                    else:
                        new_xml_text = xml_text
                    if 'top' in xml_text.attrib:
                        top_offset = float(top) + float(xml_text.attrib['top'])
                    else:
                        top_offset = float(top)
                    if 'left' in xml_text.attrib:
                        left_offset = float(
                            left) + float(xml_text.attrib['left'])
                    else:
                        left_offset = float(left)
                    if 'width' in xml_text.attrib:
                        width = float(xml_text.attrib['width'])
                    else:
                        width = self.label_size['cell_width']
                    if 'height' in xml_text.attrib:
                        height = float(xml_text.attrib['height'])
                    else:
                        height = self.label_size['cell_height']
                    new_xml_text.attrib['top'] = "%.1f" % top_offset
                    new_xml_text.attrib['left'] = "%.1f" % left_offset
                    new_xml_text.attrib['width'] = "%.1f" % width
                    new_xml_text.attrib['height'] = "%.1f" % height
                    new_xml_text.attrib['spacing'] = "0.0"
                    self.body.append(new_xml_text)
            index += 1


class ReportingGenerator(ReportGenerator):

    def __init__(self):
        ReportGenerator.__init__(self)
        self.report_xml = None
        self.current_item = None
        self.items_callback = None
        self.items = []

    @property
    def model_text(self):
        if self.report_xml is None:
            return ""
        else:
            return etree.tostring(self.report_xml, xml_declaration=True, pretty_print=True, encoding='utf-8')

    @model_text.setter
    def model_text(self, value):
        self.report_xml = etree.fromstring(value)
        self.header_height = 0.0
        self.bottom_height = 0.0
        self.horizontal_marge = float(self.report_xml.get('hmargin'))
        self.vertical_marge = float(self.report_xml.get('vmargin'))
        self.page_width = float(self.report_xml.get('page_width'))
        self.page_height = float(self.report_xml.get('page_height'))
        if len(self.report_xml.xpath('header')) > 0:
            self.header_height = float(
                self.report_xml.xpath('header')[0].get('extent'))
        if len(self.report_xml.xpath('bottom')) > 0:
            self.bottom_height = float(
                self.report_xml.xpath('bottom')[0].get('extent'))

    def add_convert_model(self, node, partname):
        ReportModelGenerator.add_convert_model(
            node, partname, self.report_xml, self.current_item, self.xfer)

    def add_page(self):
        if self.current_item is not None:
            ReportGenerator.add_page(self)
            if len(self.report_xml.xpath('header')) > 0:
                self.add_convert_model(self.header, 'header')
            if len(self.report_xml.xpath('bottom')) > 0:
                self.add_convert_model(self.bottom, 'bottom')

    def get_items(self):
        if self.items_callback is None:
            return self.items
        else:
            return self.items_callback()

    def fill_content(self, request):
        ReportGenerator.fill_content(self, request)
        for self.current_item in self.get_items():
            self.add_page()
            self.add_convert_model(self.body, 'body')
