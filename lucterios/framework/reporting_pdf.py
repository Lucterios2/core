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
from os.path import join, dirname
from reportlab.pdfgen import canvas
from lxml import etree
from logging import getLogger
from re import sub
from copy import deepcopy

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Image, Paragraph, Table
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus.tables import TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth

from lucterios.framework.filetools import is_image_base64
from lucterios.framework.tools import change_with_format
from lucterios.framework.reporting_base import LucteriosBase

WATERMARK_NB = 2


class ConvertHTML_XMLReportlab(object):

    @classmethod
    def _new_para(cls):
        xmlrl_item = etree.Element('para')
        xmlrl_item.attrib['autoLeading'] = 'max'
        return xmlrl_item

    def __init__(self, xmlrl_result, no_para):
        self.xmlrl_result = xmlrl_result
        self._options = {'ul': 0, 'ol': 0}
        self.current_style = {}
        self.num_index = 1
        self._html_item = None
        self.no_para = no_para

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
                    self.current_style[style_val[0].strip()] = style_val[1].strip()
        getLogger('lucterios.printing.pdf').debug("]]] ConvertHTML_XMLReportlab.html_item(tag=%s / style= %s)", self._html_item.tag, self.current_style)

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

    def _parse_span(self, text):
        xmlrl_item = None
        if 'font-size' in self.current_style:
            xmlrl_item = self._new_para()
            xmlrl_item.attrib['size'] = self.current_style['font-size'].replace('px', '')
        elif 'color' in self.current_style:
            xmlrl_item = etree.Element('font')
            xmlrl_item.attrib['color'] = self.current_style['color']
        return xmlrl_item

    def _parse_p(self, text):
        if (text is None) and (len(self.html_item) == 0):
            return None
        if self.no_para:
            xmlrl_item = etree.Element("div")
            xmlrl_item.text = " "
            self.xmlrl_result.append(xmlrl_item)
            return etree.Element("div")
        xmlrl_item = self._new_para()
        if self.html_item.attrib.get('align') is not None:
            xmlrl_item.attrib['align'] = self.html_item.attrib['align']
        return xmlrl_item

    def _parse_blockquote(self, text):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['lindent'] = '20'
        if self.html_item.tag in self.options.keys():
            self.options[self.html_item.tag] += 1
        return xmlrl_item

    def _parse_ul(self, text):
        if self.html_item.tag in self.options.keys():
            self.options[self.html_item.tag] += 1
        return etree.Element('div')

    def _parse_ol(self, text):
        if self.html_item.tag in self.options.keys():
            self.options[self.html_item.tag] += 1
        return etree.Element('div')

    def _parse_li(self, text):
        prefix = "\u00a0" * 4
        if self.options['ul'] > 0:
            bullet_element = etree.Element('b')
            bullet_element.text = prefix + '\u2022 '
        elif self.options['ol'] > 0:
            bullet_element = etree.Element('b')
            bullet_element.text = prefix + '%d - ' % self.num_index
            self.num_index += 1
        else:
            bullet_element = None
        if bullet_element is not None:
            self.xmlrl_result.append(bullet_element)
        return etree.Element('div')

    def _parse_center(self, text):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['align'] = "center"
        return xmlrl_item

    def _parse_hr(self, text):
        xmlrl_item = self._new_para()
        xmlrl_item.attrib['borderColor'] = 'rgb(0,0,0)'
        xmlrl_item.attrib['borderWidth'] = '1pt'
        xmlrl_item.attrib['size'] = '5pt'
        xmlrl_item.append(etree.Element('br'))
        self.xmlrl_result.append(xmlrl_item)
        return None

    def _parse_font(self, text):
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
                        sub_xmlrl.attrib['lindent'] = str(sub_lindent + item_lindent)
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

    def create_xml_node(self):
        xmlrl_item = None
        if hasattr(self, "_parse_%s" % self.html_item.tag):
            funct = getattr(self, "_parse_%s" % self.html_item.tag)
            xmlrl_item = funct(self.html_item.text)
        else:
            xmlrl_item = etree.Element(self.html_item.tag)
            self.fill_attrib(self.html_item, xmlrl_item)
        return xmlrl_item

    def manage_chip(self):
        if self.html_item.tag == 'li':
            self.xmlrl_result.append(etree.Element('br'))
        if self.html_item.tag in ('ul', 'ol'):
            self.options[self.html_item.tag] -= 1

    def run(self, html_items, options=None):
        self.options = options
        self.fill_text_if_not_null(html_items, self.xmlrl_result)
        for self.html_item in html_items:
            if isinstance(self.html_item.tag, str):
                xmlrl_item = self.create_xml_node()
                if xmlrl_item is not None:
                    new_parser = self.__class__(xmlrl_item, self.no_para)
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
                    self.manage_chip()
        self._all_in_para()

    @classmethod
    def convert(cls, html_items, no_para):
        getLogger('lucterios.printing.pdf').debug("\n[[[ ConvertHTML_XMLReportlab html = %s", etree.tostring(html_items, pretty_print=True).decode())
        xmlrl_items = etree.Element('MULTI')
        parser = cls(xmlrl_items, no_para)
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
                pos_end = xml_text.find('</para>')
                if (pos_end != -1) and ((pos_end + 7) < len(xml_text)):
                    reportlab_xml_list.append(xml_text[:pos_end + 7])
                    reportlab_xml_list.append(xml_text[pos_end + 7:])
                else:
                    reportlab_xml_list.append(xml_text)
            else:
                last_text += xml_text
        if last_text != "":
            reportlab_xml_list.append(last_text)
        if len(reportlab_xml_list) == 0:
            reportlab_xml_list = ['']
        getLogger('lucterios.printing.pdf').debug("[[[ ConvertHTML_XMLReportlab = %s", reportlab_xml_list)
        return reportlab_xml_list


def get_table_style(rows_grey=None):
    cmds = [
        ('GRID', (0, 0), (-1, -1), 0.3 * mm, (0, 0, 0)),
        ('BOX', (0, 0), (-1, -1), 0.3 * mm, (0, 0, 0))
    ]
    cmds.append(('BACKGROUND', (0, 0), (-1, 0), HexColor(0x808080)))
    cmds.append(('VALIGN', (0, 0), (-1, 0), 'TOP')),
    if isinstance(rows_grey, list):
        for row_idx in rows_grey:
            cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx), HexColor(0xE8E8E8)))
    return TableStyle(cmds)


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


class TableManage(object):

    def __init__(self, parent, xmlcolumns, current_w, current_h):
        self.parent = parent
        self.max_current_h = 0
        self.cellcolumns = []
        self.width_columns = []
        self.current_w = current_w
        self.current_h = current_h
        for xmlcolumn in xmlcolumns:
            current_w = LucteriosPDF.get_size(xmlcolumn, 'width')
            self.width_columns.append(current_w)
            cells = xmlcolumn.xpath('cell')
            paras, _ = parent.create_para(cells[0], current_w, 0, 0.85)
            self.max_current_h = max(self.max_current_h, paras[0][1])
            self.cellcolumns.append(paras[0][0])
        self.last_color_ref = None
        self.color_ref = None
        self._is_gray = False
        self.clean()

    def is_gray(self):
        if self.color_ref is None:
            self._is_gray = not self._is_gray
        else:
            if self.last_color_ref is None:
                self._is_gray = True
            elif self.last_color_ref != self.color_ref:
                self._is_gray = not self._is_gray
            self.last_color_ref = self.color_ref
        return self._is_gray

    def analyse_row(self, row):
        self.row_line = []
        col_idx = 0
        for cell in row.xpath('cell'):
            if (cell.text is not None) and is_image_base64(cell.text):
                img = self.parent.parse_image(cell, -1000, -1000, None, None)
                self.row_line.append(img)
            else:
                paras, _ = self.parent.create_para(cell, self.width_columns[col_idx], 0)
                self.row_line.append(paras[0][0])
            col_idx += 1
        self.color_ref = row.get('color_ref')

    def clean(self):
        self.row_colors = []
        self.data = [self.cellcolumns]

    def check_heigth(self):
        table = Table(self.data + [self.row_line], style=get_table_style(), colWidths=self.width_columns)
        _, table_h = table.wrapOn(self.parent.pdf, self.current_w, self.current_h)
        return table_h

    def draw_table(self, pos_x, pos_y):
        # getLogger('lucterios.printing.pdf').debug("-- parse_table (x=%.2f/y=%.2f/h=%.2f/w=%.2f) --", pos_x, pos_y, self.current_h, self.current_w)
        table = Table(self.data, style=get_table_style(self.row_colors), colWidths=self.width_columns)
        _, new_current_h = table.wrapOn(self.parent.pdf, self.current_w, self.current_h)
        table.drawOn(self.parent.pdf, pos_x, pos_y - new_current_h)
        return max(new_current_h, self.current_h)

    def append_line(self):
        self.data.append(self.row_line)
        if self.is_gray():
            self.row_colors.append(len(self.data) - 1)


class LucteriosPDF(LucteriosBase):

    def __init__(self, watermark):
        LucteriosBase.__init__(self, watermark)
        self.pdf = canvas.Canvas("lucterios.pdf")
        self.styles = getSampleStyleSheet()
        initial_fonts()

    @classmethod
    def get_size(cls, xmltext, name):
        try:
            return float(xmltext.get(name)) * mm
        except TypeError:
            return 0

    def _init(self):
        LucteriosBase._init(self)
        self.pdf.setPageSize((self.width, self.height))

    def create_para(self, xmltext, current_w, current_h, offset_font_size=0, no_para=False):
        change_with_format(xmltext)
        para_text_list = ConvertHTML_XMLReportlab.convert(xmltext, no_para)
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
        # print("%s:%s" % (xmltext.tag, para_text))
        texts = []
        for para_text in para_text_list:
            try:
                text = Paragraph(para_text, style=style)
            except Exception:
                para_text = para_text.replace('<br/>', '\n').replace('<br>', '\n')
                para_text = sub(r'<.*?>', '', para_text).replace('\n', '<br/>')
                text = Paragraph(para_text, style=style)
            _, new_current_h = text.wrapOn(self.pdf, current_w, current_h)
            texts.append((text, new_current_h))
        return texts, style

    def parse_table(self, xmltable, current_x, current_y, current_w, current_h):
        table_manage = TableManage(self, xmltable.xpath('columns'), current_w, current_h)
        for row in xmltable.xpath('rows'):
            table_manage.analyse_row(row)
            table_height = table_manage.check_heigth()
            if (current_y + table_height) > (self.height - self.bottom_h - self.b_margin):
                self.position_y = current_y + table_manage.draw_table(current_x, self.height - current_y)
                self.add_page()
                current_y = self.header_h + self.t_margin
                table_manage.clean()
            table_manage.append_line()
        self.position_y = current_y + table_manage.draw_table(current_x, self.height - current_y)

    def parse_image(self, xmlimage, current_x, current_y, current_w, current_h):
        if (xmlimage.text is not None) and (xmlimage.text.strip() != ''):
            img_file = self.open_image(xmlimage)
            try:
                img = Image(img_file)
                if current_h is not None:
                    img.drawHeight = current_h
                    img.drawWidth = current_w
                else:
                    current_h = img.drawHeight
                    current_w = img.drawWidth
                _, new_current_h = img.wrapOn(self.pdf, current_w, current_h)
                getLogger('lucterios.printing.pdf').debug("-- parse_image (x=%.2f/y=%.2f/h=%.2f/w=%.2f) --", current_x, current_y, current_h, current_w)
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
        paras, style = self.create_para(xmltext, current_w, current_h, no_para=True)
        sum_current_h = 0
        for _, new_current_h in paras:
            sum_current_h += new_current_h + SPACE_BETWEEN_PARA
        getLogger('lucterios.printing.pdf').debug("-- parse_text (x=%.2f/y=%.2f/h=%.2f/w=%.2f) - sum_current_h=%.2f --", current_x, current_y, current_h, current_w, sum_current_h)
        y_offset = 0
        for text, new_current_h in paras:
            if new_current_h == 0:
                new_current_h = style.leading
            new_current_h += style.leading * 0.40
            text.drawOn(self.pdf, current_x, self.height - current_y - y_offset - new_current_h)
            y_offset += new_current_h
        self.position_y = current_y + max(sum_current_h, current_h)

    def add_page(self):
        if not self.is_changing_page:
            self.is_changing_page = True
            try:
                if not self.pdf.pageHasData():
                    self.pdf.showPage()
                getLogger('lucterios.printing.pdf').debug("== add_page ==")
                self.draw_header()
                self.draw_footer()
                # print("before page %f - %f => %f" % (self.position_y, self.y_offset, self.header_h + self.t_margin))
                getLogger('lucterios.printing.pdf').debug("\t>> body <<")
                self.y_offset = self.header_h + self.t_margin
                self.position_y = self.y_offset
            finally:
                self.is_changing_page = False

    def draw_watermark(self):
        for watermark_iter in range(WATERMARK_NB):
            self.pdf.saveState()
            self.pdf.setFont('sans-serif-bold', 50)
            self.pdf.setFillColorRGB(0.8, 0.8, 0.8)
            self.pdf.translate(self.width / 2, self.height * (watermark_iter + 1) / (WATERMARK_NB + 1))
            self.pdf.rotate(30)
            self.pdf.drawCentredString(0, 0, self.watermark)
            self.pdf.restoreState()

    def output(self):
        return self.pdf.getpdfdata()


def get_letter_ratio(width_ratio):
    return min(1.2, max(0.8, width_ratio))


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


def build_from_xml(xml_content, watermark):
    lpdf = LucteriosPDF(watermark)
    lpdf.execute(xml_content)
    return lpdf.output()
