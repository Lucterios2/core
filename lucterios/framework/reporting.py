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
from django.utils import six
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, Paragraph, Table
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
from lucterios.framework.filetools import BASE64_PREFIX, open_from_base64
from reportlab.platypus.tables import TableStyle
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth


def get_size(xmltext, name):
    try:
        return float(xmltext.get(name)) * mm
    except TypeError:
        return 0


def extract_text(xmltext):
    def add_sub_text(xmltext, sub_text):
        for item in xmltext:
            if (item.tag == 'font') and (item.attrib.get('Font-weight') == "bold"):
                new_element = etree.Element('b')
            elif (item.tag == 'font') and (item.attrib.get('Font-style') == "italic"):
                new_element = etree.Element('i')
            elif (item.tag == 'font') and (item.attrib.get('text-decoration') == "underline"):
                new_element = etree.Element('u')
            else:
                new_element = etree.Element(item.tag)
                for key, val in item.attrib.items():
                    new_element.attrib[key] = val
            new_element.text = item.text
            new_element.tail = item.tail
            add_sub_text(item, new_element)
            sub_text.append(new_element)
        sub_text.text = xmltext.text
    res_text = etree.Element('TEXT')
    add_sub_text(xmltext, res_text)
    pattern = re.compile(r'\s+')
    para_text = six.text_type(etree.tostring(res_text))
    para_text = para_text[para_text.find('>') + 1:]
    para_text = para_text.replace('</TEXT>', '')
    para_text = para_text.replace("\\n", " ")
    para_text = para_text.replace("'", "")
    para_text = re.sub(pattern, ' ', para_text)
    para_text = para_text.strip()
    return para_text

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
        self.width = 0
        self.height = 0
        self.l_margin = 0
        self.t_margin = 0
        self.r_margin = 0
        self.b_margin = 0
        self.header_h = 0
        self.bottom_h = 0
        self.y_offset = 0
        self.position_y = 0
        self.current_page = None
        initial_fonts()

    def _init(self):
        self.pages = self.xml.xpath('page')
        self.width = get_size(self.xml, 'page_width')
        self.height = get_size(self.xml, 'page_height')
        self.l_margin = get_size(self.xml, 'margin_left')
        self.t_margin = get_size(self.xml, 'margin_top')
        self.r_margin = get_size(self.xml, 'margin_right')
        self.b_margin = get_size(self.xml, 'margin_bottom')
        if len(self.pages) > 0:
            header = self.pages[0].xpath('header')
            bottom = self.pages[0].xpath('bottom')
            self.header_h = get_size(header[0], 'extent')
            self.bottom_h = get_size(bottom[0], 'extent')
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
        para_text = extract_text(xmltext)
        font_name = xmltext.get('font_family')
        if font_name is None:
            font_name = 'sans-serif'
        align = xmltext.get('text_align')
        if para_text.startswith('<center>'):
            align = 'center'
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
        text = Paragraph(para_text, style=style)
        _, new_current_h = text.wrapOn(self.pdf, current_w, current_h)
        return text, style, new_current_h

    def extract_columns_for_table(self, xmlcolumns):
        max_current_h = 0
        cellcolumns = []
        width_columns = []
        for xmlcolumn in xmlcolumns:
            current_w = get_size(xmlcolumn, 'width')
            width_columns.append(current_w)
            cells = xmlcolumn.xpath('cell')
            text, _, new_current_h = self.create_para(
                cells[0], current_w, 0, 0.85)
            max_current_h = max(max_current_h, new_current_h)
            cellcolumns.append(text)
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
        cellcolumns, width_columns, _ = self.extract_columns_for_table(
            xmltable.xpath('columns'))
        data = []
        data.append(cellcolumns)
        for row in xmltable.xpath('rows'):
            row_line = []
            col_idx = 0
            for cell in row.xpath('cell'):
                text, _, _ = self.create_para(cell, width_columns[col_idx], 0)
                row_line.append(text)
                col_idx += 1
            table_height = get_table_heigth(data + [row_line], width_columns)
            # six.print_("table y:%f height:%f h-b:%F" % (self.position_y / mm, table_height / mm, (self.height - self.bottom_h - self.b_margin) / mm))
            if (self.position_y + table_height) > (self.height - self.bottom_h - self.b_margin):
                draw_table(width_columns, data)
                self.add_page()
                current_y = self.header_h + self.t_margin
                data = []
                data.append(cellcolumns)
            data.append(row_line)
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
                img.drawHeight = current_h
                img.drawWidth = current_w
                _, new_current_h = img.wrapOn(
                    self.pdf, current_w, current_h)
                img.drawOn(
                    self.pdf, current_x, self.height - current_y - current_h)
                self.position_y = current_y + max(new_current_h, current_h)
            finally:
                if img_file is not None:
                    img_file.close()

    def parse_text(self, xmltext, current_x, current_y, current_w, current_h):
        text, style, new_current_h = self.create_para(
            xmltext, current_w, current_h)
        if new_current_h == 0:
            new_current_h = style.leading
        new_current_h += style.leading * 0.40
        text.drawOn(
            self.pdf, current_x, self.height - current_y - new_current_h)
        self.position_y = current_y + max(new_current_h, current_h)

    def _parse_comp(self, comp, y_offset):
        last_y_offset = self.y_offset
        self.y_offset = y_offset
        self.position_y = y_offset
        for child in comp:
            if self.position_y > (self.height + self.bottom_h):
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
        if not self.pdf.pageHasData():
            self.pdf.showPage()
        self.draw_header()
        self.draw_footer()
        # six.print_("before page %f - %f => %f" % (self.position_y, self.y_offset, self.header_h + self.t_margin))
        self.y_offset = self.header_h + self.t_margin
        self.position_y = self.y_offset

    def draw_header(self):
        header = self.current_page.xpath('header')
        self._parse_comp(header[0], self.t_margin)

    def draw_footer(self):
        bottom = self.current_page.xpath('bottom')
        self._parse_comp(
            bottom[0], self.height - self.b_margin - self.bottom_h)

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
