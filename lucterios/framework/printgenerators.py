# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lxml import etree

from lucterios.framework.xfercomponents import XferCompTab, XferCompLABEL, \
    XferCompLinkLabel, XferCompLabelForm, XferCompImage, XferCompGrid
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.filetools import BASE64_PREFIX, get_image_absolutepath, \
    get_image_size
from lucterios.framework.xferadvance import get_items_from_filter
from lucterios.framework.tools import get_value_converted
from django.utils import six

def remove_format(xml_text):
    xml_text = xml_text.replace('<b>', '')
    xml_text = xml_text.replace('<i>', '')
    xml_text = xml_text.replace('<u>', '')
    xml_text = xml_text.replace('</b>', '')
    xml_text = xml_text.replace('</i>', '')
    xml_text = xml_text.replace('</u>', '')
    xml_text = xml_text.replace('{[newline]}', '')
    xml_text = xml_text.replace('{[bold]}', '')
    xml_text = xml_text.replace('{[/bold]}', '')
    xml_text = xml_text.replace('{[italic]}', '')
    xml_text = xml_text.replace('{[/italic]}', '')
    xml_text = xml_text.replace('{[underline]}', '')
    xml_text = xml_text.replace('{[/underline]}', '')
    return xml_text

def convert_to_html(tagname, text, font_family="sans-serif", font_size=9, line_height=10, text_align='left'):
    text = six.text_type(text).replace('{[newline]}', '<br/>')
    text = text.replace('{[', '<')
    text = text.replace(']}', '>')
    xml_text = etree.XML("<%(tagname)s>%(text)s</%(tagname)s>" % {'tagname':tagname, 'text':text})
    xml_text.attrib['font_family'] = font_family
    xml_text.attrib['font_size'] = "%d" % font_size
    xml_text.attrib['line_height'] = "%d" % line_height

    xml_text.attrib['text_align'] = text_align
    xml_text.attrib['spacing'] = "0.0"
    return xml_text

def get_text_size(text):
    size_x = 0
    size_y = 0
    text = six.text_type(text).replace('{[newline]}', "\n").replace('{[br/]}', "\n")
    for line in text.split('\n'):
        size_x = max(size_x, len(remove_format(line)))
        size_y = size_y + 1
    return (size_x, size_y)

def evaluate_cell(item, column):
    value = column[2]
    for field in column[3]:
        field_val = get_value_converted(getattr(item, field[1:]), True)
        value = value.replace(field, six.text_type(field_val))
    return value

class PrintItem(object):
    # pylint: disable=too-many-instance-attributes

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
            self.left = self.left + self.owner.col_width[col_idx]
        for col_idx in range(self.col, self.col + self.colspan):
            self.width = self.width + self.owner.col_width[col_idx]

class PrintImage(PrintItem):

    DPI = 0.34

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
        self.height = int(self.img_size[1] * self.DPI)

    def get_xml(self):
        xml_img = etree.Element('image')
        xml_img.text = self.value
        if (self.img_size[0] * self.DPI) < self.width:
            self.width = int(self.img_size[0] * self.DPI)
            self.height = int(self.img_size[1] * self.DPI)
        else:
            self.height = int(self.width * self.img_size[1] / self.img_size[0])
        self.fill_attrib(xml_img)
        return xml_img

class PrintTable(PrintItem):

    def __init__(self, comp, owner):
        PrintItem.__init__(self, comp, owner)
        self.columns = []
        self.rows = []
        self.size_rows = [0]

    def compute_table_size(self):
        for header in self.comp.headers:
            size_cx, size_cy = get_text_size(header.descript)
            column = [header.descript, size_cx]
            self.size_rows[0] = max(self.size_rows[0], size_cy)
            row_idx = 0
            for record in self.comp.records:
                while len(self.rows) <= row_idx:
                    self.rows.append([])

                while len(self.size_rows) <= (row_idx + 1):
                    self.size_rows.append(0)

                value = record[header.name]
                if header.type == 'icon':
                    value = BASE64_PREFIX + value
                    img_size = get_image_size(value)
                    size_x = int(img_size[0] * PrintImage.DPI)
                    size_y = int(img_size[1] * PrintImage.DPI)
                else:
                    size_x, size_y = get_text_size(value)
                self.rows[row_idx].append(value)
                self.size_rows[row_idx + 1] = max(self.size_rows[row_idx + 1], size_y)
                column[1] = max(column[1], size_x)
                row_idx += 1

            self.columns.append(column)

    def get_table_sizes(self):
        size_x = 0
        for column in self.columns:
            size_x = size_x + column[1]
        size_y = 0
        for size_row in self.size_rows:
            size_y = size_y + size_row
        return size_y, size_x

    def write_columns(self, xml_table, size_x):
        for column in self.columns:
            size_col = int(self.width * column[1] / size_x)
            new_col = etree.SubElement(xml_table, "columns")
            new_col.attrib['width'] = "%d.0" % size_col
            xml_text = convert_to_html('cell', column[0], "sans-serif", 9, 10, "center")
            xml_text.attrib['font_family'] = "sans-serif"
            xml_text.attrib['font_size'] = "9"
            xml_text.attrib['line_height'] = "10"
            xml_text.attrib['text_align'] = "center"
            new_col.append(xml_text)
        return

    def write_rows(self, xml_table):
        for row in self.rows:
            new_row = etree.SubElement(xml_table, "rows")
            for value in row:
                xml_text = convert_to_html('cell', value, "sans-serif", 9, 10, "start")
                if value[:len(BASE64_PREFIX)] == BASE64_PREFIX:
                    xml_text.attrib['image'] = "1"
                new_row.append(xml_text)

    def get_xml(self):
        xml_table = etree.Element('table')
        self.fill_attrib(xml_table)

        self.columns = []
        self.rows = []
        self.size_rows = [0]

        self.compute_table_size()
        if len(self.rows) == 0:

            row = []
            for _ in self.columns:
                row.append('')
            self.rows.append(row)
            self.size_rows.append(get_text_size('')[1])

        size_y, size_x = self.get_table_sizes()
        self.height = 6 * size_y
        self.write_columns(xml_table, size_x)
        self.write_rows(xml_table)
        return xml_table

class PrintTab(PrintItem):

    SEP_HEIGHT = 5

    def __init__(self, comp, owner):
        PrintItem.__init__(self, comp, owner)
        self.size_x, size_y = get_text_size(self.comp.value)
        self.height = 4.8 * size_y + self.SEP_HEIGHT * 2

    def calcul_position(self):
        self.left = 10
        self.owner.top = self.owner.top + self.SEP_HEIGHT
        self.top = self.owner.top
        self.width = self.owner.page_width - 2 * self.owner.horizontal_marge - self.left

    def get_xml(self):
        xml_text = convert_to_html('text', self.comp.value)
        self.top += self.SEP_HEIGHT
        self.fill_attrib(xml_text)
        return xml_text

class PrintLabel(PrintItem):

    def __init__(self, comp, owner):
        PrintItem.__init__(self, comp, owner)
        self.size_x, size_y = get_text_size(get_value_converted(self.comp.value, True))
        self.height = 4.8 * size_y

    def get_xml(self):
        xml_text = convert_to_html('text', get_value_converted(self.comp.value, True))
        self.fill_attrib(xml_text)
        return xml_text

class ReportGenerator(object):
    # pylint: disable=too-many-instance-attributes

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

    def add_page(self):
        self.content_width = self.page_width - 2 * self.horizontal_marge
        page = etree.SubElement(self.modelxml, "page")
        self.header = etree.SubElement(page, "header")
        self.bottom = etree.SubElement(page, "bottom")
        self.body = etree.SubElement(page, "body")

    def get_text_from_title(self):
        xml_text = convert_to_html('text', "<b><u>%s</u></b>" % self.title, text_align='center')
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
        self.header.attrib['extent'] = "%d.0" % self.header_height
        self.bottom.attrib['extent'] = "%d.0" % self.bottom_height

    def fill_content(self, _):
        pass

    def generate(self, request):
        self.modelxml = etree.Element('model')
        self.add_page()
        self.fill_content(request)
        self.fill_attrib()
        return etree.tostring(self.modelxml, xml_declaration=True, pretty_print=True, encoding='utf-8')

class ActionGenerator(ReportGenerator):

    def __init__(self, action):
        ReportGenerator.__init__(self)
        self.action = action
        self.header_height = 12
        self.last_top = 0
        self.top = 0
        self.print_items = []
        self.col_width = []

    def add_page(self):
        ReportGenerator.add_page(self)
        self.header.append(self.get_text_from_title())
        self.top = 0

    def change_page(self, check_top_value=True):
        if not check_top_value or (self.top > (self.page_height - 2 * self.vertical_marge)):
            self.add_page()

    def get_height_of_rowspan(self, print_item):
        value = 0
        last_y = -1
        current_height = 0
        for item in self.print_items:
            if (item.tab == print_item.tab) and (item.rowspan == 1) and (item.row >= print_item.row) and (item.row < (print_item.row + print_item.rowspan)):
                if last_y == item.row:
                    current_height = max(current_height, item.height)
                else:
                    value += current_height
                    current_height = item.height
                    last_y = item.row
        value += current_height
        if value < print_item.height:
            value = print_item.height - value
        return value

    def compute_components(self):
        col_size = []
        max_col = 0
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
            elif isinstance(comp, XferCompLABEL) or isinstance(comp, XferCompLinkLabel) or isinstance(comp, XferCompLabelForm):
                new_item = PrintLabel(comp, self)
            if new_item is not None:
                new_size_x = new_item.size_x / new_item.colspan
                for item_idx in range(0, new_item.col + new_item.colspan):
                    while len(col_size) <= item_idx:
                        col_size.append(0)
                    if item_idx >= new_item.col:
                        col_size[item_idx] = max(col_size[item_idx], new_size_x)
                max_col = max(max_col, new_item.col + new_item.colspan)
                self.print_items.append(new_item)
        return max_col, col_size

    def define_col_size(self, col_size, max_col):
        total_size = 0
        for col_idx in range(0, max_col):
            total_size = total_size + col_size[col_idx]
        for col_idx in range(0, max_col):
            if total_size == 0:
                self.col_width.append(0)
            else:
                self.col_width.append(int(self.content_width * col_size[col_idx] / total_size))

    def fill_content(self, request):
        self.action._initialize(request)  # pylint: disable=protected-access
        self.action.fillresponse(**self.action._get_params())  # pylint: disable=protected-access
        self.action._finalize()  # pylint: disable=protected-access
        self.print_items = []
        self.col_width = []
        max_col, col_size = self.compute_components()
        if max_col == 0:
            raise LucteriosException(IMPORTANT, "No colonm to print!")
        self.define_col_size(col_size, max_col)
        self.top = 0
        last_y = -1
        current_height = 0
        self.last_top = 0
        for item in self.print_items:
            if last_y == item.row:
                if item.rowspan == 1:
                    current_height = max(current_height, item.height)
                else:
                    current_height = max(current_height, self.get_height_of_rowspan(item))
            else:
                self.top = self.top + current_height
                self.change_page()
                if item.rowspan == 1:
                    current_height = item.height
                else:
                    current_height = self.get_height_of_rowspan(item)
                last_y = item.row
            item.calcul_position()
            self.body.append(item.get_xml())
            self.last_top = item.top + item.height

class ListingGenerator(ReportGenerator):

    def __init__(self, model):
        import re
        ReportGenerator.__init__(self)
        self.header_height = 12
        self.columns = []
        self.model = model
        self.filter = None
        self.finder = re.compile("#[a-z_0-9]+")

    def add_page(self):
        ReportGenerator.add_page(self)
        self.header.append(self.get_text_from_title())

    def fill_content(self, _):
        xml_table = etree.Element('table')
        self.body.append(xml_table)
        xml_table.attrib['height'] = "%d.0" % (self.page_height - 2 * self.vertical_marge)
        xml_table.attrib['width'] = "%d.0" % self.content_width
        xml_table.attrib['top'] = "0.0"
        xml_table.attrib['left'] = "0.0"
        xml_table.attrib['spacing'] = "0.0"
        size_x = 0
        new_columns = []
        for column in self.columns:
            size_x += column[0]
            fields = self.finder.findall(column[2])
            new_columns.append((column[0], column[1], column[2], fields))
        self.columns = new_columns

        for column in self.columns:
            size_col = int(self.content_width * column[0] / size_x)
            new_col = etree.SubElement(xml_table, "columns")
            new_col.attrib['width'] = "%d.0" % size_col
            xml_text = convert_to_html('cell', column[1], "sans-serif", 9, 10, "center")
            xml_text.attrib['font_family'] = "sans-serif"
            xml_text.attrib['font_size'] = "9"
            xml_text.attrib['line_height'] = "10"
            xml_text.attrib['text_align'] = "center"
            new_col.append(xml_text)
        items = get_items_from_filter(self.model, self.filter)
        for item in items:
            new_row = etree.SubElement(xml_table, "rows")
            for column in self.columns:
                xml_text = convert_to_html('cell', evaluate_cell(item, column), "sans-serif", 9, 10, "start")
                new_row.append(xml_text)
