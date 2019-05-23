# -*- coding: utf-8 -*-
'''
PDF generator from print xml

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
from os.path import isfile, join, dirname
from os import unlink, system
from reportlab.pdfgen import canvas
from lxml import etree
from logging import getLogger

from django.utils import six

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, Paragraph, Table
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.tables import TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth

from lucterios.framework.filetools import BASE64_PREFIX, open_from_base64
from copy import deepcopy


def get_size(xmltext, name):
    try:
        return float(xmltext.get(name)) * mm
    except TypeError:
        return 0


class ConvertHTML_XMLReportlab(object):

    @classmethod
    def _new_para(cls):
        xmlrl_item = etree.Element('para')
        xmlrl_item.attrib['autoLeading'] = 'max'
        return xmlrl_item

    def __init__(self, xmlrl_result):
        self.xmlrl_result = xmlrl_result
        self._options = {'ul': 0, 'ol': 0}
        self.current_style = {}
        self.num_index = 1
        self._html_item = None

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        if options is None:
            self._options = {'ul': 0, 'ol': 0}
        else:
            self._options = options

    @property
    def html_item(self):
        return self._html_item

    @html_item.setter
    def html_item(self, value):
        self._html_item = value
        self.current_style = {}
        style_text = self._html_item.attrib.get('style')
        if style_text is not None:
            for style_item in style_text.split(';'):
                style_val = style_item.split(':')
                if len(style_val) == 2:
                    self.current_style[style_val[0]] = style_val[1]
        getLogger('lucterios.printing').debug("]]] ConvertHTML_XMLReportlab.html_item(tag=%s / style= %s)", self._html_item.tag, self.current_style)

    def fill_attrib(self, xml_source, xml_target):
        for key, val in xml_source.attrib.items():
            if (key not in ('style')):
                xml_target.attrib[key] = val

    def fill_text_if_not_null(self, item_source, item_target):
        if item_source.text is not None:
            if item_target.text is None:
                item_target.text = ""
            item_target.text += item_source.text
        if item_source.tail is not None:
            if item_target.tail is None:
                item_target.tail = ""
            item_target.tail += item_source.tail

    def _parse_span(self):
        xmlrl_item = None
        if 'font-size' in self.current_style:
            xmlrl_item = self._new_para()
            xmlrl_item.attrib['size'] = self.current_style['font-size'].replace('px', '')
        elif 'color' in self.current_style:
            xmlrl_item = etree.Element('font')
            xmlrl_item.attrib['color'] = self.current_style['color']
        return xmlrl_item

    def _parse_p(self):
        xmlrl_item = self._new_para()
        if self.html_item.attrib.get('align') is not None:
            xmlrl_item.attrib['align'] = self.html_item.attrib['align']
        return xmlrl_item

    def _parse_blockquote(self):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['lindent'] = '20'
        if self.html_item.tag in self.options.keys():
            self.options[self.html_item.tag] += 1
        return xmlrl_item

    def _parse_ul(self):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['lindent'] = '20'
        if self.html_item.tag in self.options.keys():
            self.options[self.html_item.tag] += 1
        return xmlrl_item

    def _parse_ol(self):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['lindent'] = '20'
        if self.html_item.tag in self.options.keys():
            self.options[self.html_item.tag] += 1
        return xmlrl_item

    def _parse_li(self):
        if self.options['ul'] > 0:
            bullet_element = etree.Element('b')
            bullet_element.text = '\u2022 '
            self.xmlrl_result.append(bullet_element)
        elif self.options['ol'] > 0:
            bullet_element = etree.Element('b')
            bullet_element.text = '%d - ' % self.num_index
            self.xmlrl_result.append(bullet_element)
            self.num_index += 1
        return etree.Element('span')

    def _parse_center(self):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['align'] = "center"
        return xmlrl_item

    def _parse_hr(self):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['borderColor'] = 'rgb(0,0,0)'
        xmlrl_item.attrib['borderWidth'] = '1pt'
        xmlrl_item.attrib['size'] = '5pt'
        xmlrl_item.append(etree.Element('br'))
        self.xmlrl_result.append(xmlrl_item)
        return None

    def _parse_font(self):
        if self.html_item.attrib.get('Font-weight') == "bold":
            xmlrl_item = etree.Element('b')
        elif self.html_item.attrib.get('Font-style') == "italic":
            xmlrl_item = etree.Element('i')
        elif self.html_item.attrib.get('text-decoration') == "underline":
            xmlrl_item = etree.Element('u')
        else:
            xmlrl_item = etree.Element('font')
            if 'size' in self.html_item.attrib:
                xmlrl_item.attrib['size'] = self.html_item.attrib['size']
        return xmlrl_item

    def _reoganize_para(self, xmlrl_item):
        def add_xmlrl(new_xmlrl):
            self.xmlrl_result.append(new_xmlrl)
        if len(xmlrl_item) == 0:
            add_xmlrl(xmlrl_item)
        else:
            extra_xmlrl = self._new_para()
            self.fill_attrib(xmlrl_item, extra_xmlrl)
            self.fill_text_if_not_null(xmlrl_item, extra_xmlrl)
            for sub_xmlrl in xmlrl_item:
                if sub_xmlrl.tag == 'para':
                    if len(extra_xmlrl) > 0:
                        add_xmlrl(extra_xmlrl)
                    sub_lindent = int(sub_xmlrl.attrib['lindent']) if 'lindent' in sub_xmlrl.attrib else 0
                    item_lindent = int(xmlrl_item.attrib['lindent']) if 'lindent' in xmlrl_item.attrib else 0
                    self.fill_attrib(xmlrl_item, sub_xmlrl)
                    if (sub_lindent + item_lindent) > 0:
                        sub_xmlrl.attrib['lindent'] = six.text_type(sub_lindent + item_lindent)
                    self.fill_text_if_not_null(xmlrl_item, sub_xmlrl)
                    add_xmlrl(sub_xmlrl)
                    extra_xmlrl = self._new_para()
                    self.fill_attrib(xmlrl_item, extra_xmlrl)
                else:
                    extra_xmlrl.append(sub_xmlrl)
            if len(extra_xmlrl) > 0:
                add_xmlrl(extra_xmlrl)

    def _switch_para(self, xmlrl_item):
        for sub_xmlrl in xmlrl_item:
            new_xmlrl = etree.Element(sub_xmlrl.tag)
            self.fill_attrib(sub_xmlrl, new_xmlrl)
            new_parent_xmlrl = etree.Element(xmlrl_item.tag)
            self.fill_attrib(xmlrl_item, new_parent_xmlrl)
            new_xmlrl.append(new_parent_xmlrl)
            new_parent_xmlrl.extend(sub_xmlrl)
            self.fill_text_if_not_null(sub_xmlrl, new_parent_xmlrl)
            self.xmlrl_result.append(new_xmlrl)

    def _all_in_para(self):
        if len(self.xmlrl_result) > 0:
            xmlrl_finalize = etree.Element(self.xmlrl_result.tag)
            self.fill_attrib(self.xmlrl_result, xmlrl_finalize)
            self.fill_text_if_not_null(self.xmlrl_result, xmlrl_finalize)
            new_para_item = None
            for xmlrl_item in self.xmlrl_result:
                if xmlrl_item.tag == 'para':
                    if new_para_item is not None:
                        xmlrl_finalize.append(deepcopy(new_para_item))
                    new_para_item = None
                    xmlrl_finalize.append(deepcopy(xmlrl_item))
                else:
                    if new_para_item is None:
                        new_para_item = etree.Element('para')
                    new_para_item.append(deepcopy(xmlrl_item))
            if new_para_item is not None:
                xmlrl_finalize.append(deepcopy(new_para_item))
            self.xmlrl_result = xmlrl_finalize

    def run(self, html_items, options=None):
        self.options = options
        self.fill_text_if_not_null(html_items, self.xmlrl_result)
        for self.html_item in html_items:
            xmlrl_item = None
            if hasattr(self, "_parse_%s" % self.html_item.tag):
                funct = getattr(self, "_parse_%s" % self.html_item.tag)
                xmlrl_item = funct()
            else:
                xmlrl_item = etree.Element(self.html_item.tag)
                self.fill_attrib(self.html_item, xmlrl_item)
            if xmlrl_item is not None:
                new_parser = self.__class__(xmlrl_item)
                new_parser.run(self.html_item, self.options)
                if xmlrl_item.tag == 'para':
                    self._reoganize_para(xmlrl_item)
                    if self.html_item.tag in self.options.keys():
                        self.options[self.html_item.tag] -= 1
                elif xmlrl_item.tag == 'span':
                    self.xmlrl_result.extend(xmlrl_item)
                    self.fill_text_if_not_null(xmlrl_item, self.xmlrl_result)
                elif (len(xmlrl_item) > 0) and (xmlrl_item[0].tag == 'para'):
                    self._switch_para(xmlrl_item)
                else:
                    self.xmlrl_result.append(xmlrl_item)
                if self.html_item.tag == 'li':
                    self.xmlrl_result.append(etree.Element('br'))
        self._all_in_para()

    @classmethod
    def convert(cls, html_items):
        getLogger('lucterios.printing').debug("\n[[[ ConvertHTML_XMLReportlab html = %s", etree.tostring(html_items, pretty_print=True).decode())
        xmlrl_items = etree.Element('MULTI')
        parser = cls(xmlrl_items)
        parser.run(html_items)
        reportlab_xml_list = []
        last_text = ""
        if (xmlrl_items.text is not None) and (xmlrl_items.text.strip() != ''):
            last_text = xmlrl_items.text
        for xmlrl_item in xmlrl_items:
            xml_text = etree.tostring(xmlrl_item).decode().strip()
            if xml_text.startswith('<para'):
                if last_text != "":
                    reportlab_xml_list.append(last_text)
                last_text = ""
                reportlab_xml_list.append(xml_text)
            else:
                last_text += xml_text
        if last_text != "":
            reportlab_xml_list.append(last_text)
        if len(reportlab_xml_list) == 0:
            reportlab_xml_list = ['']
        getLogger('lucterios.printing').debug("[[[ ConvertHTML_XMLReportlab = %s", reportlab_xml_list)
        return reportlab_xml_list


TABLE_STYLE = TableStyle([
    ('GRID', (0, 0), (-1, -1), 0.3 * mm, (0, 0, 0)),
    ('BOX', (0, 0), (-1, -1), 0.3 * mm, (0, 0, 0))
])

g_initial_fonts = False


def initial_fonts():
    global g_initial_fonts
    if not g_initial_fonts:
        font_dir_path = join(dirname(__file__), 'fonts')
        pdfmetrics.registerFont(
            TTFont('sans-serif', join(font_dir_path, 'FreeSans.ttf')))
        pdfmetrics.registerFont(
            TTFont('sans-serif-bold', join(font_dir_path, 'FreeSansBold.ttf')))
        pdfmetrics.registerFont(
            TTFont('sans-serif-italic', join(font_dir_path, 'FreeSansOblique.ttf')))
        pdfmetrics.registerFont(
            TTFont('sans-serif-bolditalic', join(font_dir_path, 'FreeSansBoldOblique.ttf')))
        pdfmetrics.registerFontFamily("sans-serif", normal="sans-serif", bold="sans-serif-bold",
                                      italic="sans-serif-italic", boldItalic="sans-serif-bolditalic")
        g_initial_fonts = True


def get_text_size(para_text, font_size=9, line_height=10, text_align='left', is_cell=False):
    initial_fonts()
    lines = para_text.split('\n')
    max_line = ""
    for line in lines:
        if len(line) > len(max_line):
            max_line = line
    width = stringWidth(max_line, "sans-serif", font_size)
    if is_cell:
        height = font_size * max(1, len(lines) * 2 / 3)
    else:
        height = font_size * len(lines)
    height += abs(line_height - font_size) * 2
    return width / mm, height / mm


class LucteriosPDF(object):

    def __init__(self):
        self.pdf = canvas.Canvas("lucterios.pdf")
        self.styles = getSampleStyleSheet()
        self.xml = None
        self.pages = None
        self._width = 0
        self._height = 0
        self._l_margin = 0
        self._t_margin = 0
        self._r_margin = 0
        self._b_margin = 0
        self._header_h = 0
        self._bottom_h = 0
        self._y_offset = 0
        self._position_y = 0
        self.current_page = None
        self.is_changing_page = False
        initial_fonts()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def l_margin(self):
        return self._l_margin

    @property
    def t_margin(self):
        return self._t_margin

    @property
    def r_margin(self):
        return self._r_margin

    @property
    def b_margin(self):
        return self._b_margin

    @property
    def header_h(self):
        return self._header_h

    @property
    def bottom_h(self):
        return self._bottom_h

    @property
    def y_offset(self):
        return self._y_offset

    @property
    def position_y(self):
        return self._position_y

    @y_offset.setter
    def y_offset(self, value):
        self._y_offset = value
        getLogger('lucterios.printing').debug("y_offset=%.2f", self._y_offset)

    @position_y.setter
    def position_y(self, value):
        self._position_y = value
        getLogger('lucterios.printing').debug("position_y=%.2f" % self._position_y)

    def _init(self):
        self.pages = self.xml.xpath('page')
        self._width = get_size(self.xml, 'page_width')
        self._height = get_size(self.xml, 'page_height')
        self._l_margin = get_size(self.xml, 'margin_left')
        self._t_margin = get_size(self.xml, 'margin_top')
        self._r_margin = get_size(self.xml, 'margin_right')
        self._b_margin = get_size(self.xml, 'margin_bottom')
        if len(self.pages) > 0:
            header = self.pages[0].xpath('header')
            bottom = self.pages[0].xpath('bottom')
            self._header_h = get_size(header[0], 'extent')
            self._bottom_h = get_size(bottom[0], 'extent')
        getLogger('lucterios.printing').debug("Init (H=%.2f/W=%.2f) margin[l=%.2f,t=%.2f,r=%.2f,b=%.2f] - header_h=%.2f/bottom_h=%.2f",
                                              self.height, self.width,
                                              self.l_margin, self.t_margin, self.r_margin, self.b_margin,
                                              self._header_h, self._bottom_h)
        self.pdf.setPageSize((self.width, self.height))

    def get_top_component(self, xmlitem):
        spacing = get_size(xmlitem, 'spacing')
        if abs(spacing) > 0.001:
            if abs(self.position_y - self.y_offset) > 0.001:
                current_y = max(self.y_offset, self.position_y + spacing)
            else:
                current_y = self.y_offset
        else:
            current_y = self.y_offset + get_size(xmlitem, 'top')
        return current_y

    def create_para(self, xmltext, current_w, current_h, offset_font_size=0):
        para_text_list = ConvertHTML_XMLReportlab.convert(xmltext)
        font_name = xmltext.get('font_family')
        if font_name is None:
            font_name = 'sans-serif'
        align = xmltext.get('text_align')
        if (align == 'left') or (align == 'start'):
            alignment = TA_LEFT
        elif align == 'center':
            alignment = TA_CENTER
        else:
            alignment = TA_RIGHT
        if xmltext.get('font_size') is None:
            font_size = 10.0 - offset_font_size
        else:
            font_size = float(xmltext.get('font_size')) - offset_font_size
        if xmltext.get('line_height') is None:
            line_height = 11
        else:
            line_height = int(xmltext.get('line_height'))
        style = ParagraphStyle(name='text', fontName=font_name, fontSize=font_size,
                               alignment=alignment, leading=line_height)
        # six.print_("%s:%s" % (xmltext.tag, para_text))
        texts = []
        for para_text in para_text_list:
            text = Paragraph(para_text, style=style)
            _, new_current_h = text.wrapOn(self.pdf, current_w, current_h)
            texts.append((text, new_current_h))
        return texts, style

    def extract_columns_for_table(self, xmlcolumns):
        max_current_h = 0
        cellcolumns = []
        width_columns = []
        for xmlcolumn in xmlcolumns:
            current_w = get_size(xmlcolumn, 'width')
            width_columns.append(current_w)
            cells = xmlcolumn.xpath('cell')
            paras, _ = self.create_para(cells[0], current_w, 0, 0.85)
            max_current_h = max(max_current_h, paras[0][1])
            cellcolumns.append(paras[0][0])
        return cellcolumns, width_columns, max_current_h

    def parse_table(self, xmltable, current_x, current_y, current_w, current_h):

        def get_table_heigth(current_data, current_width_columns):
            table = Table(
                current_data, style=TABLE_STYLE, colWidths=current_width_columns)
            _, table_h = table.wrapOn(self.pdf, current_w, current_h)
            return table_h

        def draw_table(width_columns, data):
            table = Table(data, style=TABLE_STYLE, colWidths=width_columns)
            _, new_current_h = table.wrapOn(self.pdf, current_w, current_h)
            table.drawOn(
                self.pdf, current_x, self.height - current_y - new_current_h)
            self.position_y = current_y + max(new_current_h, current_h)
            return
        cellcolumns, width_columns, _ = self.extract_columns_for_table(xmltable.xpath('columns'))
        data = []
        data.append(cellcolumns)
        for row in xmltable.xpath('rows'):
            row_line = []
            col_idx = 0
            for cell in row.xpath('cell'):
                if (cell.text is not None) and (cell.text[:len(BASE64_PREFIX)] == BASE64_PREFIX):
                    img = self.parse_image(cell, -1000, -1000, None, None)
                    row_line.append(img)
                else:
                    paras, _ = self.create_para(cell, width_columns[col_idx], 0)
                    row_line.append(paras[0][0])
                col_idx += 1
            table_height = get_table_heigth(data + [row_line], width_columns)
            # six.print_("table y:%f height:%f h-b:%F" % (current_y / mm, table_height / mm, (self.height - self.bottom_h - self.b_margin) / mm))
            if (current_y + table_height) > (self.height - self.bottom_h - self.b_margin):
                draw_table(width_columns, data)
                self.add_page()
                current_y = self.header_h + self.t_margin
                data = []
                data.append(cellcolumns)
            data.append(row_line)
        getLogger('lucterios.printing').debug("-- parse_table (x=%.2f/y=%.2f/h=%.2f/w=%.2f) --", current_x, current_y, current_h, current_w)
        draw_table(width_columns, data)

    def parse_image(self, xmlimage, current_x, current_y, current_w, current_h):
        if xmlimage.text is not None:
            from PIL import ImageFile
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            img_content = xmlimage.text.strip()
            is_base64 = img_content[:len(BASE64_PREFIX)] == BASE64_PREFIX
            if is_base64:
                img_file = open_from_base64(img_content)
            else:
                img_file = open(img_content, "rb")
            try:
                img = Image(img_file)
                if current_h is not None:
                    img.drawHeight = current_h
                    img.drawWidth = current_w
                else:
                    current_h = img.drawHeight
                    current_w = img.drawWidth
                _, new_current_h = img.wrapOn(self.pdf, current_w, current_h)
                getLogger('lucterios.printing').debug("-- parse_image (x=%.2f/y=%.2f/h=%.2f/w=%.2f) --", current_x, current_y, current_h, current_w)
                img.drawOn(self.pdf, current_x, self.height - current_y - current_h)
                self.position_y = current_y + max(new_current_h, current_h)
                return img
            finally:
                if img_file is not None:
                    img_file.close()
        else:
            return None

    def parse_text(self, xmltext, current_x, current_y, current_w, current_h):
        SPACE_BETWEEN_PARA = 6
        paras, style = self.create_para(xmltext, current_w, current_h)
        sum_current_h = 0
        for _, new_current_h in paras:
            sum_current_h += new_current_h + SPACE_BETWEEN_PARA
        getLogger('lucterios.printing').debug("-- parse_text (x=%.2f/y=%.2f/h=%.2f/w=%.2f) - sum_current_h=%.2f --", current_x, current_y, current_h, current_w, sum_current_h)
        y_offset = 0
        for text, new_current_h in paras:
            if new_current_h == 0:
                new_current_h = style.leading
            new_current_h += style.leading * 0.40
            text.drawOn(self.pdf, current_x, self.height - current_y - y_offset - new_current_h)
            y_offset += new_current_h
        self.position_y = current_y + max(sum_current_h, current_h)

    def _parse_comp(self, comp, y_offset):
        last_y_offset = self.y_offset
        self.y_offset = y_offset
        self.position_y = y_offset
        for child in comp:
            if self.position_y > (self.height - self.b_margin - self.bottom_h):
                self.add_page()
            current_x = self.l_margin + get_size(child, 'left')
            current_y = self.get_top_component(child)
            current_w = get_size(child, 'width')
            current_h = get_size(child, 'height')
            mtd = 'parse_' + child.tag.lower()
            if hasattr(self, mtd):
                fct = getattr(self, mtd)
                # six.print_("print: %s (x=%f,y=%f,w=%f,h=%f) " % (child.tag, current_x / mm, current_y / mm, current_w / mm, current_h / mm))
                fct(child, current_x, current_y, current_w, current_h)
            else:
                six.print_("Unsupported method: " + mtd)
        self.y_offset = last_y_offset

    def add_page(self):
        if not self.is_changing_page:
            self.is_changing_page = True
            try:
                if not self.pdf.pageHasData():
                    self.pdf.showPage()
                getLogger('lucterios.printing').debug("== add_page ==")
                self.draw_header()
                self.draw_footer()
                # six.print_("before page %f - %f => %f" % (self.position_y, self.y_offset, self.header_h + self.t_margin))
                getLogger('lucterios.printing').debug("\t>> body <<")
                self.y_offset = self.header_h + self.t_margin
                self.position_y = self.y_offset
            finally:
                self.is_changing_page = False

    def draw_header(self):
        getLogger('lucterios.printing').debug("\t>> header <<")
        header = self.current_page.xpath('header')
        self._parse_comp(header[0], self.t_margin)

    def draw_footer(self):
        getLogger('lucterios.printing').debug("\t>> footer <<")
        bottom = self.current_page.xpath('bottom')
        self._parse_comp(bottom[0], self.height - self.b_margin - self.bottom_h)

    def execute(self, xml_content):
        self.xml = etree.fromstring(xml_content)
        self._init()
        for page in self.pages:
            self.current_page = page
            bodies = self.current_page.xpath('body')
            for body in bodies:
                self.add_page()
                self._parse_comp(body, self.header_h + self.t_margin)

    def output(self):
        return self.pdf.getpdfdata()


def transforme_xml2pdf(xml_content):
    lpdf = LucteriosPDF()
    lpdf.execute(xml_content)
    return lpdf.output()


def transform_file_xml2pdf(xml_filename, pdf_filename):
    with open(xml_filename, 'rb') as flb:
        pdf_content = transforme_xml2pdf(flb.read())
    if isfile(pdf_filename):
        unlink(pdf_filename)
    if pdf_content != six.text_type(''):
        with open(pdf_filename, 'wb') as flb:
            flb.write(pdf_content)
    return isfile(pdf_filename)


def main():
    import sys
    file_name = sys.argv[1]
    if transform_file_xml2pdf(file_name, file_name + '.pdf'):
        system("acroread %s.pdf" % file_name)


if __name__ == '__main__':
    main()
