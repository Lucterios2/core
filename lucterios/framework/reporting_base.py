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
from lxml import etree
from logging import getLogger
from lucterios.framework.filetools import is_image_base64, open_from_base64


class LucteriosBase(object):

    def __init__(self, watermark):
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
        self.watermark = watermark.strip()

    @classmethod
    def get_size(cls, xmltext, name):
        try:
            return float(xmltext.get(name))
        except TypeError:
            return 0

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
        self._width = self.get_size(self.xml, 'page_width')
        self._height = self.get_size(self.xml, 'page_height')
        self._l_margin = self.get_size(self.xml, 'margin_left')
        self._t_margin = self.get_size(self.xml, 'margin_top')
        self._r_margin = self.get_size(self.xml, 'margin_right')
        self._b_margin = self.get_size(self.xml, 'margin_bottom')
        if len(self.pages) > 0:
            header = self.pages[0].xpath('header')
            bottom = self.pages[0].xpath('bottom')
            self._header_h = self.get_size(header[0], 'extent')
            self._bottom_h = self.get_size(bottom[0], 'extent')
        getLogger('lucterios.printing').debug("Init (H=%.2f/W=%.2f) margin[l=%.2f,t=%.2f,r=%.2f,b=%.2f] - header_h=%.2f/bottom_h=%.2f",
                                              self.height, self.width,
                                              self.l_margin, self.t_margin, self.r_margin, self.b_margin,
                                              self._header_h, self._bottom_h)

    def get_top_component(self, xmlitem):
        spacing = self.get_size(xmlitem, 'spacing')
        if abs(spacing) > 0.001:
            if abs(self.position_y - self.y_offset) > 0.001:
                current_y = max(self.y_offset, self.position_y + spacing)
            else:
                current_y = self.y_offset
        else:
            current_y = self.y_offset + self.get_size(xmlitem, 'top')
        return current_y

    def parse_table(self, xmltable, current_x, current_y, current_w, current_h):
        raise Exception('No implemented !')

    def open_image(self, xmlimage):
        from PIL import ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        img_content = xmlimage.text.strip()
        if is_image_base64(img_content):
            img_file = open_from_base64(img_content)
        else:
            img_file = open(img_content, "rb")
        return img_file

    def parse_image(self, xmlimage, current_x, current_y, current_w, current_h):
        raise Exception('No implemented !')

    def parse_text(self, xmltext, current_x, current_y, current_w, current_h):
        raise Exception('No implemented !')

    def _parse_comp(self, comp, y_offset):
        last_y_offset = self.y_offset
        self.y_offset = y_offset
        self.position_y = y_offset
        for child in comp:
            if self.position_y > (self.height - self.b_margin - self.bottom_h):
                self.add_page()
            current_x = self.l_margin + self.get_size(child, 'left')
            current_y = self.get_top_component(child)
            current_w = self.get_size(child, 'width')
            current_h = self.get_size(child, 'height')
            mtd = 'parse_' + child.tag.lower()
            if hasattr(self, mtd):
                fct = getattr(self, mtd)
                # print("print: %s (x=%f,y=%f,w=%f,h=%f) " % (child.tag, current_x / mm, current_y / mm, current_w / mm, current_h / mm))
                fct(child, current_x, current_y, current_w, current_h)
            else:
                print("Unsupported method: " + mtd)
        self.y_offset = last_y_offset

    def add_page(self):
        raise Exception('No implemented !')

    def draw_watermark(self):
        raise Exception('No implemented !')

    def draw_header(self):
        getLogger('lucterios.printing').debug("\t>> header <<")
        if self.watermark != '':
            self.draw_watermark()
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
        raise Exception('No implemented !')
