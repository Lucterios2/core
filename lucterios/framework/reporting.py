# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from os.path import isfile, join, dirname
from posix import unlink, system
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
from lucterios.framework.filetools import BASE64_PREFIX, save_from_base64
from reportlab.platypus.tables import TableStyle

def get_size(xmltext, name):
    return float(xmltext.get(name)) * mm

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

def create_para(xmltext):
    para_text = extract_text(xmltext)
    font_name = xmltext.get('font_family')
    align = xmltext.get('text_align')
    if (align == 'left') or (align == 'start'):
        alignment = TA_LEFT
    elif align == 'center':
        alignment = TA_CENTER
    else:
        alignment = TA_RIGHT
    font_size = int(xmltext.get('font_size'))
    style = ParagraphStyle(name='text', fontName=font_name, fontSize=font_size, \
                           alignment=alignment, leading=int(xmltext.get('line_height')))
    six.print_("%s:%s" % (xmltext.tag, para_text))
    text = Paragraph(para_text, style=style)
    return text, style

def extract_columns_for_table(xmlcolumns):
    cellcolumns = []
    width_columns = []
    for xmlcolumn in xmlcolumns:
        width_columns.append(get_size(xmlcolumn, 'width'))
        cells = xmlcolumn.xpath('cell')
        text, _ = create_para(cells[0])
        cellcolumns.append(text)
    return cellcolumns, width_columns

TABLE_STYLE = TableStyle([
    ('GRID', (0, 0), (-1, -1), 0.3 * mm, (0, 0, 0)),
    ('BOX', (0, 0), (-1, -1), 0.3 * mm, (0, 0, 0))
])

class LucteriosPDF(object):
    # pylint: disable=too-many-instance-attributes

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
        filenamepath = join(dirname(__file__), 'fonts', 'FreeSans.ttf')
        pdfmetrics.registerFont(TTFont('sans-serif', filenamepath))

    def _init(self):
        self.pages = self.xml.xpath('page')
        self.width = get_size(self.xml, 'page_width')
        self.height = get_size(self.xml, 'page_height')
        self.l_margin = get_size(self.xml, 'margin_left')
        self.t_margin = get_size(self.xml, 'margin_top')
        self.r_margin = get_size(self.xml, 'margin_right')
        self.b_margin = get_size(self.xml, 'margin_bottom')
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

    def parse_table(self, xmltable, current_x, current_y, current_w, current_h):
        data = []
        cellcolumns, width_columns = extract_columns_for_table(xmltable.xpath('columns'))
        data.append(cellcolumns)
        for row in xmltable.xpath('rows'):
            row_line = []
            for cell in row.xpath('cell'):
                text, style = create_para(cell)
                row_line.append(text)
            data.append(row_line)
        table = Table(data, style=TABLE_STYLE, colWidths=width_columns)
        current_w, current_h = table.wrapOn(self.pdf, current_w, current_h)
        current_y += style.leading
        table.drawOn(self.pdf, current_x, self.height - current_y)
        self.position_y = current_y + current_h

    def parse_image(self, xmlimage, current_x, current_y, current_w, current_h):
        img_content = xmlimage.text.strip()
        is_base64 = img_content[:len(BASE64_PREFIX)] == BASE64_PREFIX
        if is_base64:
            img_file = save_from_base64(img_content)
        else:
            img_file = img_content
        img = Image(img_file)
        img.drawHeight = current_h
        img.drawWidth = current_w
        current_w, current_h = img.wrapOn(self.pdf, current_w, current_h)
        img.drawOn(self.pdf, current_x, self.height - current_y - current_h)
        self.position_y = current_y + current_h
        if is_base64 and isfile(img_file):
            unlink(img_file)

    def parse_text(self, xmltext, current_x, current_y, current_w, current_h):
        text, style = create_para(xmltext)
        _, new_current_h = text.wrapOn(self.pdf, current_w, current_h)
        if new_current_h == 0:
            new_current_h = style.leading
        current_y += style.leading * 0.15
        new_current_h += style.leading * 0.25
        text.drawOn(self.pdf, current_x, self.height - current_y)
        self.position_y = current_y + max(new_current_h, current_h)

    def _parse_comp(self, comp, y_offset):
        last_y_offset = self.y_offset
        self.y_offset = y_offset
        self.position_y = y_offset
        for child in comp:
            current_x = self.l_margin + get_size(child, 'left')
            current_y = self.get_top_component(child)
            current_w = get_size(child, 'width')
            current_h = get_size(child, 'height')
            mtd = 'parse_' + child.tag.lower()
            if hasattr(self, mtd):
                fct = getattr(self, mtd)
                six.print_("print: %s (x=%f,position_y*%f,w=%f,h=%f) " % (child.tag, current_x / mm, current_y / mm, current_w / mm, current_h / mm))
                fct(child, current_x, current_y, current_w, current_h)
            else:
                six.print_("Unsupported method: " + mtd)
        self.y_offset = last_y_offset

    def draw_header(self):
        header = self.current_page.xpath('header')
        self._parse_comp(header[0], self.t_margin)

    def draw_footer(self):
        bottom = self.current_page.xpath('bottom')
        self._parse_comp(bottom[0], -1 * self.b_margin)

    def execute(self, xml_content):
        self.xml = etree.fromstring(xml_content)
        self._init()
        for page in self.pages:
            self.current_page = page
            bodies = self.current_page.xpath('body')
            for body in bodies:
                self.draw_header()
                self._parse_comp(body, self.header_h + self.t_margin)
                self.draw_footer()
                self.pdf.showPage()

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
