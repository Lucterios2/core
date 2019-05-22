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
from lucterios.framework.filetools import BASE64_PREFIX, open_from_base64
from reportlab.platypus.tables import TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from logging import getLogger


def get_size(xmltext, name):
    try:
        return float(xmltext.get(name)) * mm
    except TypeError:
        return 0


def extract_text(xmltext, basic_para):
    def add_with_check_null(old_element, new_element):
        if new_element.text is not None:
            if old_element.text is None:
                old_element.text = ""
            old_element.text += new_element.text
        if new_element.tail is not None:
            if old_element.tail is None:
                old_element.tail = ""
            old_element.tail += new_element.tail

    def convert_style(style_text):
        res_style = {}
        if style_text is not None:
            for style_item in style_text.split(';'):
                style_val = style_item.split(':')
                if len(style_val) == 2:
                    res_style[style_val[0]] = style_val[1]
        return res_style

    def new_para():
        new_element = etree.Element('para')
        new_element.attrib['autoLeading'] = 'max'
        return new_element

    def add_sub_text(xmltext, sub_text, options=None):
        num_index = 1
        if options is None:
            options = {'blockquote': 0, 'ul': 0, 'ol': 0}
        inside_para = False
        for item in xmltext:
            style_text = item.attrib.get('style')
            style = convert_style(style_text)
            getLogger('lucterios.printing').debug("]]] extract_text.add_sub_text(tag=%s style=%s - >%s)", item.tag, style_text, style)
            new_element = None
            if (item.tag == 'span'):
                if 'font-size' in style:
                    new_element = new_para()
                    new_element.attrib['size'] = style['font-size'].replace('px', '')
                    inside_para = True
                elif 'color' in style:
                    new_element = etree.Element('font')
                    new_element.attrib['color'] = style['color']
            elif item.tag == 'p':
                new_element = new_para()
            elif (item.tag in ('blockquote', 'ul', 'ol')):
                if options[item.tag] > 0:
                    new_element = etree.Element('span')
                else:
                    new_element = new_para()
                inside_para = True
                if item.tag in options.keys():
                    options[item.tag] += 1
            elif item.tag == 'li':
                if options['ul'] > 0:
                    bullet_element = etree.Element('b')
                    bullet_element.text = '\u2022 '
                    sub_text.append(bullet_element)
                elif options['ol'] > 0:
                    bullet_element = etree.Element('b')
                    bullet_element.text = '%d - ' % num_index
                    sub_text.append(bullet_element)
                    num_index += 1
                new_element = etree.Element('li')
            elif item.tag == 'hr':
                new_element = new_para()
                new_element.attrib['borderColor'] = 'rgb(0,0,0)'
                new_element.attrib['borderWidth'] = '1pt'
                sub_text.append(new_element)
                new_element = None
            elif (item.tag == 'br') and inside_para:
                pass
            elif (item.tag == 'font') and (item.attrib.get('Font-weight') == "bold"):
                new_element = etree.Element('b')
            elif (item.tag == 'font') and (item.attrib.get('Font-style') == "italic"):
                new_element = etree.Element('i')
            elif (item.tag == 'font') and (item.attrib.get('text-decoration') == "underline"):
                new_element = etree.Element('u')
            else:
                new_element = etree.Element(item.tag)
                for key, val in item.attrib.items():
                    if (key not in ('style')):
                        new_element.attrib[key] = val
            if new_element is not None:
                add_sub_text(item, new_element, options)
                if (item.tag in options.keys()) and (options[item.tag] > 0) and (new_element.tag == 'para'):
                    new_element.attrib['lindent'] = six.text_type(20 * options[item.tag])
                    options[item.tag] -= 1
                if new_element.tag in ('span', 'center'):
                    sub_text.extend(new_element)
                    add_with_check_null(sub_text, new_element)
                else:
                    sub_text.append(new_element)
        add_with_check_null(sub_text, xmltext)

    blocks_xml = etree.Element('MULTI')
    add_sub_text(xmltext, blocks_xml)
    para_text_list_xml = []
    new_para_item = None
    getLogger('lucterios.printing').debug("\n[[[ extract_text = %s", etree.tostring(blocks_xml, pretty_print=True).decode())
    for item_xml in blocks_xml:
        if item_xml.tag == 'para':
            if new_para_item is not None:
                para_text_list_xml.append(etree.tostring(new_para_item).decode())
            new_para_item = None
            para_text_list_xml.append(etree.tostring(item_xml).decode())
        else:
            if new_para_item is None:
                if basic_para:
                    new_para_item = etree.Element('para')
                else:
                    new_para_item = new_para()
            new_para_item.append(item_xml)
    if new_para_item is not None:
        para_text_list_xml.append(etree.tostring(new_para_item).decode())
    if len(para_text_list_xml) == 0:
        para_text_list_xml = [blocks_xml.text if blocks_xml.text is not None else '']
    getLogger('lucterios.printing').debug("[[[ extract_text = %s", para_text_list_xml)
    return para_text_list_xml


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

    def create_para(self, xmltext, current_w, current_h, offset_font_size=0, basic_para=True):
        para_text_list = extract_text(xmltext, basic_para)
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
        SPACE_BETWEEN_PARA = 5
        paras, style = self.create_para(xmltext, current_w, current_h, basic_para=False)
        getLogger('lucterios.printing').debug("-- parse_text (x=%.2f/y=%.2f/h=%.2f/w=%.2f) --", current_x, current_y, current_h, current_w)
        sum_current_h = 0
        for _, new_current_h in paras:
            sum_current_h += new_current_h + SPACE_BETWEEN_PARA
        y_begin = self.height - current_y - sum_current_h
        for text, new_current_h in paras:
            if new_current_h == 0:
                new_current_h = style.leading
            new_current_h += style.leading * 0.40
            text.drawOn(self.pdf, current_x, y_begin)
            y_begin -= new_current_h + SPACE_BETWEEN_PARA
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
