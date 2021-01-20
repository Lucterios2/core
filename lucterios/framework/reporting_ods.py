# -*- coding: utf-8 -*-
'''
CSV generator from print xml

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2020 sd-libre.fr
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

import sys
from _io import BytesIO
from logging import getLogger
from uuid import uuid4
from json import loads
from xml.sax import ContentHandler, parseString

from odf.opendocument import OpenDocumentSpreadsheet
from odf.table import Table, TableRow, TableCell, TableColumn
from odf.style import Style, TableColumnProperties, TableRowProperties, ParagraphProperties, TextProperties, TableCellProperties
from odf.number import Number, DateStyle, NumberStyle, DayOfWeek, CurrencySymbol, CurrencyStyle, Month, Year, Day
from odf.draw import Frame, Image
from odf.text import P, Span

from lucterios.framework.reporting_base import LucteriosBase
from lucterios.framework.tools import change_with_format, add_currency, toHtml
from lucterios.framework.filetools import is_image_base64


class ParserParam(ContentHandler):

    class TextInfo(object):

        def __init__(self, owner):
            self.owner = owner
            self.bold = False
            self.italic = False
            self.underline = False
            self.color = None

        def clone(self):
            new_obj = ParserParam.TextInfo(self.owner)
            new_obj.bold = self.bold
            new_obj.italic = self.italic
            new_obj.underline = self.underline
            new_obj.color = self.color
            return new_obj

        def setParam(self, param, attrs):
            if param == 'b':
                self.bold = True
            if param == 'i':
                self.italic = True
            if param == 'u':
                self.underline = True
            if param == 'fond':
                self.color = attrs.getValue('color')

        def cloneWithParam(self, param, attrs):
            new_obj = self.clone()
            new_obj.setParam(param, attrs)
            return new_obj

        def getStyle(self):
            new_style, new_property = self.owner.create_text_property()
            if self.bold:
                new_property.setAttribute("fontweight", "bold")
            if self.italic:
                new_property.setAttribute("fontstyle", "italic")
            if self.underline:
                new_property.setAttribute("textunderlinestyle", "solid")
                new_property.setAttribute("textunderlinewidth", "auto")
                new_property.setAttribute("textunderlinecolor", "font-colot")
            return new_style

    def __init__(self, owner):
        self.owner = owner
        self.para_align = 'left'

    def startDocument(self):
        self.paragraph_list = []
        self.text_info_list = [self.TextInfo(self.owner)]
        self.current_paragraph = P()
        self.last_tag = None

    def add_paragraph(self):
        if len(self.current_paragraph.childNodes) > 0:
            self.paragraph_list.append(self.current_paragraph)
            self.current_paragraph = P()

    def startElement(self, name, attrs):
        if name == 'center':
            self.para_align = 'center'
            self.add_paragraph()
        elif (name == 'p') and ('align' in attrs.getNames()):
            align = attrs.getValue('align')
            if align == 'right':
                self.para_align = 'right'
                self.add_paragraph()
        elif name in ('b', 'u', 'i', 'font'):
            self.text_info_list.append(self.text_info_list[-1].cloneWithParam(name, attrs))

    def characters(self, content):
        content = content.strip()
        if content != '':
            Span(parent=self.current_paragraph, text=content, stylename=self.text_info_list[-1].getStyle())

    def endElement(self, name):
        if name in ('b', 'u', 'i', 'font'):
            del self.text_info_list[-1]
        elif name in ('br', 'center'):
            self.paragraph_list.append(self.current_paragraph)
            self.current_paragraph = P()
        self.last_tag = name

    def endDocument(self):
        if (len(self.current_paragraph.childNodes) > 0) or (self.last_tag == 'br'):
            self.paragraph_list.append(self.current_paragraph)

    def run(self, xmltext):
        from lxml import etree
        formatstr = xmltext.get('formatstr')
        if not isinstance(formatstr, str) or (formatstr.count('%s') != 1):
            formatstr = "%s"
        try:
            xml_content_string = toHtml(formatstr) % etree.tostring(xmltext, xml_declaration=False, encoding='utf-8').decode("utf-8")
        except Exception:
            print('formatstr', formatstr)
            raise
        parseString("<span>%s</span>" % xml_content_string, self)
        return self.paragraph_list


class LucteriosODS(LucteriosBase):

    WIDTH_COL = 5
    HEIGHT_ROW = 5

    def __init__(self, watermark):
        LucteriosBase.__init__(self, watermark)
        self.opendoc = OpenDocumentSpreadsheet()
        self.first_sheet = Table(parent=self.opendoc.spreadsheet, name='Pages')
        self.initial_fonts()

    def _init(self):
        LucteriosBase._init(self)
        TableColumn(parent=self.first_sheet, numbercolumnsrepeated=int((self.width + self.r_margin + self.l_margin) / self.WIDTH_COL), stylename=self.style_width_col)
        self.init_height = self.height

    def initial_fonts(self):
        self.style_text_num = 0
        self.style_celltext_num = 0
        self.style_photo_num = 0
        self.style_width_col = Style(parent=self.opendoc.automaticstyles, name='col-lct', family='table-column')
        TableColumnProperties(parent=self.style_width_col, columnwidth='%.0fmm' % self.WIDTH_COL)
        self.style_heigh_row = Style(parent=self.opendoc.automaticstyles, name='row-lct', family='table-row')
        TableRowProperties(parent=self.style_heigh_row, rowheight='%.0fmm' % self.HEIGHT_ROW)
        date_style = DateStyle(parent=self.opendoc.automaticstyles, name='LongDate', automaticorder="true", formatsource="language")
        date_style.appendChild(DayOfWeek(style='long'))
        date_style.appendChild(Day(style='long'))
        date_style.appendChild(Month(style='long'))
        date_style.appendChild(Year(style='long'))
        self.decStyleList = []

    def getDecStyle(self, formatnum):
        if formatnum not in self.decStyleList:
            prec = int(formatnum[1])
            if formatnum[0] == 'C':
                currency_style = CurrencyStyle(parent=self.opendoc.automaticstyles, name=formatnum)
                currency_style.appendChild(Number(decimalplaces=prec, minintegerdigits='1'))
                currency_style.appendChild(CurrencySymbol(text=add_currency('', formatnum)))
            else:
                number_style = NumberStyle(parent=self.opendoc.automaticstyles, name=formatnum)
                number_style.appendChild(Number(decimalplaces=prec, minintegerdigits='1'))
            self.decStyleList.append(formatnum)
        return formatnum

    def coord_cell(self, current_x, current_y, current_w, current_h):
        cell_posx = int(0.5 + current_x / self.WIDTH_COL)
        cell_posy = int(current_y / self.HEIGHT_ROW - 0.1) + 1
        cell_spanx = int(current_w / self.WIDTH_COL) + 1
        cell_spany = int(current_h / self.HEIGHT_ROW - 0.1) + 1
        return cell_posx, cell_posy, cell_spanx, cell_spany

    def get_cell(self, cell_posx, cell_posy, cell_spanx=1, cell_spany=1):
        while len(self.first_sheet.childNodes) <= cell_posy:
            new_tr = TableRow(stylename=self.style_heigh_row)
            self.first_sheet.addElement(new_tr)
        current_row = self.first_sheet.childNodes[cell_posy]
        while len(current_row.childNodes) <= cell_posx:
            current_row.addElement(TableCell())
        while (len(current_row.childNodes) > cell_posx) and (len(current_row.childNodes[cell_posx].childNodes) > 0):
            cell_posx += 1
        if len(current_row.childNodes) == cell_posx:
            current_row.addElement(TableCell())
        current_cell = current_row.childNodes[cell_posx]
        current_cell.setAttribute('numbercolumnsspanned', str(cell_spanx))
        current_cell.setAttribute('numberrowsspanned', str(cell_spany))
        for coloffset in range(cell_spanx):
            for rowoffset in range(cell_spany):
                if (coloffset, rowoffset) != (0, 0):
                    P(parent=self.get_cell(cell_posx + coloffset, cell_posy + rowoffset), text='.')
        return current_cell

    def create_text_property(self):
        self.style_text_num += 1
        new_style = Style(parent=self.opendoc.automaticstyles, name="T%d" % self.style_text_num, family='text')
        return new_style, TextProperties(parent=new_style)

    def create_style_celltext(self, xmltext, border, bgdcolor):
        self.style_celltext_num += 1
        font_name = xmltext.get('font_family')
        if font_name is None:
            font_name = 'sans-serif'
        align = xmltext.get('text_align')
        if (align == 'left') or (align == 'start'):
            alignment = 'start'
        elif align == 'center':
            alignment = 'center'
        else:
            alignment = 'end'
        if xmltext.get('font_size') is None:
            font_size = 10.0
        else:
            font_size = float(xmltext.get('font_size'))
        new_style = Style(parent=self.opendoc.automaticstyles, name="ce%d" % self.style_celltext_num, family='table-cell')
        cellprop = TableCellProperties(parent=new_style, textalignsource="fix", repeatcontent="false", wrapoption="wrap", verticalalign="middle")
        if border:
            cellprop.setAttribute('border', "0.06pt solid #000000")
        if bgdcolor:
            cellprop.setAttribute('backgroundcolor', bgdcolor)
        ParagraphProperties(parent=new_style, textalign=alignment)
        TextProperties(parent=new_style, usewindowfontcolor="true", textoutline="false", textlinethroughstyle="none", textlinethroughtype="none",
                       fontname=font_name, fontsize="%dpt" % int(font_size))
        getLogger('lucterios.printing.ods').debug("STYLE : font_name=%s, alignment=%s, font_size=%.1f, border=%s, bgdcolor=%s", font_name, alignment, font_size, border, bgdcolor)
        return new_style

    def create_style_photo(self):
        self.style_photo_num += 1
        return Style(parent=self.opendoc.automaticstyles, name="photo%d" % self.style_photo_num, family="graphic")

    def get_datastyle(self, current_cell):
        stylename = current_cell.getAttribute('stylename')
        for sub_style in reversed(self.opendoc.automaticstyles.childNodes):
            if sub_style.getAttribute('name') == stylename:
                return sub_style

    def format_cell(self, current_cell, formatnum, jsonvalue):
        currentvalue = loads(jsonvalue)
        if isinstance(currentvalue, list) or isinstance(currentvalue, dict):
            return True
        result = True
        if formatnum[0] in ('N', 'C'):
            try:
                prec = int(formatnum[1])
                if currentvalue is not None:
                    if formatnum[0] == 'C':
                        current_cell.setAttribute('valuetype', 'currency')
                        current_cell.setAttribute('currency', formatnum[2:])
                    else:
                        current_cell.setAttribute('valuetype', 'float')
                    current_cell.setAttribute('value', round(float(currentvalue), prec))
                else:
                    current_cell.setAttribute('valuetype', 'string')
                    result = False
                self.get_datastyle(current_cell).setAttribute('datastylename', self.getDecStyle(formatnum))
            except ValueError:
                pass
        elif formatnum[0] == 'D':
            if currentvalue is not None:
                current_cell.setAttribute('valuetype', 'date')
                current_cell.setAttribute('datevalue', str(currentvalue))
            else:
                current_cell.setAttribute('valuetype', 'string')
                result = False
            self.get_datastyle(current_cell).setAttribute('datastylename', "LongDate")
        return result

    def create_cell(self, xmltext, cell_posx, cell_posy, cell_spanx, cell_spany, border=False, bgdcolor=None):
        change_with_format(xmltext)
        parser = ParserParam(self)
        paras = parser.run(xmltext)
        if (len(paras) > 0) or border:
            if parser.para_align != 'left':
                xmltext.set('text_align', parser.para_align)
            current_cell = self.get_cell(cell_posx, cell_posy, cell_spanx, cell_spany)
            current_cell.setAttribute('stylename', self.create_style_celltext(xmltext, border, bgdcolor))
            formatnum = xmltext.get('formatnum')
            if (formatnum is not None) and (formatnum[1] in ('C', 'N', 'D')):
                if not self.format_cell(current_cell, loads(formatnum), xmltext.get('jsonvalue')):
                    current_paragraph = P()
                    Span(parent=current_paragraph, text='---', stylename=parser.text_info_list[0].getStyle())
                    paras = [current_paragraph]
            elif (formatnum is not None) and (formatnum[0] == '{'):
                formatnum = loads(formatnum)
                currentvalue = str(loads(xmltext.get('jsonvalue')))
                current_paragraph = P()
                if currentvalue in formatnum.keys():
                    Span(parent=current_paragraph, text=formatnum[currentvalue], stylename=parser.text_info_list[0].getStyle())
                paras = [current_paragraph]
            for para in paras:
                current_cell.appendChild(para)
            getLogger('lucterios.printing.ods').debug("CELL : cell_posx=%.1f, cell_posy=%.1f, cell_spanx=%.1f, cell_spany=%.1f : %s",
                                                      cell_posx, cell_posy, cell_spanx, cell_spany, "|".join([str(para) for para in paras]))

    def parse_table(self, xmltable, current_x, current_y, current_w, current_h):
        cell_posx, cell_posy, _cell_spanx, _cell_spany = self.coord_cell(current_x, current_y, current_w, current_h)
        colomns_spans = []
        height_size = 1
        sum_col_spans = 0
        for xmlcolumn in xmltable.xpath('columns'):
            colomn_span = int(float(xmlcolumn.get('width')) / self.WIDTH_COL) + 1
            self.create_cell(xmlcolumn.xpath('cell')[0], cell_posx + sum_col_spans, cell_posy, colomn_span, height_size, True, "#808080")
            sum_col_spans += colomn_span
            colomns_spans.append(colomn_span)
        current_posy = cell_posy + height_size
        for row in xmltable.xpath('rows'):
            cell_idx = 0
            for cell in row.xpath('cell'):
                colomn_span = colomns_spans[cell_idx]
                if (cell.text is not None) and is_image_base64(cell.text):
                    img_w, img_h = self.get_image_size(cell)
                    row_span = int((img_h * self.WIDTH_COL * (colomn_span - 1) / (img_w * self.HEIGHT_ROW)) - 0.1)
                    height_size = max(height_size, row_span)
                cell_idx += 1
        last_color_ref = None
        is_gray = False
        for row in xmltable.xpath('rows'):
            cell_idx = 0
            sum_col_spans = 0
            color_ref = row.get('color_ref')
            if color_ref is None:
                is_gray = not is_gray
            else:
                if last_color_ref is None:
                    is_gray = True
                elif last_color_ref != color_ref:
                    is_gray = is_gray
                last_color_ref = color_ref
            for cell in row.xpath('cell'):
                colomn_span = colomns_spans[cell_idx]
                if (cell.text is not None) and is_image_base64(cell.text):
                    self.create_image(cell, cell_posx + sum_col_spans, current_posy, colomn_span, height_size, self.WIDTH_COL * (colomn_span - 1), self.HEIGHT_ROW * height_size)
                else:
                    self.create_cell(cell, cell_posx + sum_col_spans, current_posy, colomn_span, height_size, True, "#cccccc" if is_gray else None)
                sum_col_spans += colomn_span
                cell_idx += 1
            current_posy += height_size
        self.position_y = current_posy * self.HEIGHT_ROW
        getLogger('lucterios.printing.ods').debug("TABLE current_x=%.1f, current_y=%.1f, current_w=%.1f, current_h=%.1f => position_y=%.1f",
                                                  current_x, current_y, current_w, current_h, self.position_y)

    def parse_text(self, xmltext, current_x, current_y, current_w, current_h):
        getLogger('lucterios.printing.ods').debug("TEXT current_x=%.1f, current_y=%.1f, current_w=%.1f, current_h=%.1f",
                                                  current_x, current_y, current_w, current_h)
        cell_posx, cell_posy, cell_spanx, cell_spany = self.coord_cell(current_x, current_y, current_w, current_h)
        current_cell = self.create_cell(xmltext, cell_posx, cell_posy, cell_spanx, cell_spany)
        self.position_y = (cell_posy + cell_spany) * self.HEIGHT_ROW
        return current_cell

    def get_image_size(self, xmlimage):
        img_file = self.open_image(xmlimage)
        try:
            import PIL.Image
            with PIL.Image.open(img_file) as img:
                return img.size
        finally:
            if img_file is not None:
                img_file.close()

    def create_image(self, xmlimage, cell_posx, cell_posy, cell_spanx, cell_spany, current_w, current_h):
        img_w, img_h = self.get_image_size(xmlimage)
        img_file = self.open_image(xmlimage)
        try:
            new_current_w = current_h * img_w / img_h
            if new_current_w > current_w:
                current_h = current_w * img_h / img_w
            else:
                current_w = new_current_w
            mediatype = None
            href = self.opendoc.addPicture("Pictures/%s" % (uuid4().hex.upper()), mediatype, img_file.read())
            current_cell = self.get_cell(cell_posx, cell_posy, cell_spanx, cell_spany)
            photoframe = Frame(stylename=self.create_style_photo(), width="%fmm" % current_w, height="%fmm" % current_h)
            photoframe.addElement(Image(href=href))
            current_cell.addElement(photoframe)
        finally:
            if img_file is not None:
                img_file.close()

    def parse_image(self, xmlimage, current_x, current_y, current_w, current_h):
        if (xmlimage.text is not None) and (xmlimage.text.strip() != ''):
            cell_posx, cell_posy, cell_spanx, cell_spany = self.coord_cell(current_x, current_y, current_w, current_h)
            self.create_image(xmlimage, cell_posx, cell_posy, cell_spanx, cell_spany, current_w, current_h)

    def add_page(self):
        if not self.is_changing_page:
            self.is_changing_page = True
            self.draw_header()
        self.y_offset = self._height + self.header_h + self.t_margin
        self._height += self.init_height

    def draw_watermark(self):
        pass

    def execute(self, xml_content):
        LucteriosBase.execute(self, xml_content)
        self.draw_footer()

    def output(self):
        old_stdout = sys.stdout
        try:
            outfile = BytesIO()
            sys.stdout = outfile
            self.opendoc.save('-')
            return outfile.getvalue()
        finally:
            sys.stdout = old_stdout


def get_text_size(para_text, font_size=9, line_height=10, text_align='left', is_cell=False):
    px_by_mm = 72.0 / 2.54 * 0.1
    lines = para_text.split('\n')
    max_line = ""
    for line in lines:
        if len(line) > len(max_line):
            max_line = line
    width_in_px = len(max_line) * font_size
    if is_cell:
        height_in_px = font_size * max(1, len(lines) * 2 / 3)
    else:
        height_in_px = font_size * len(lines)
    height_in_px += abs(line_height - font_size) * 2
    return width_in_px / px_by_mm, height_in_px / px_by_mm


def build_from_xml(xml_content, watermark):
    lpdf = LucteriosODS(watermark)
    lpdf.execute(xml_content)
    return lpdf.output()
