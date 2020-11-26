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
from os.path import join, dirname, isfile
from lxml import etree

from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework.tools import change_with_format


def get_text_size(para_text, font_size=9, line_height=10, text_align='left', is_cell=False):
    return 1, 1


class LucteriosXLTExtension(object):

    def _node_to_string(self, first_node):
        text_value = ""
        if first_node.text is not None:
            text_value += first_node.text.strip() + ' '
        for item in first_node:
            text_value += self._node_to_string(item) + ' '
        if first_node.tail is not None:
            text_value += first_node.tail.strip() + ' '
        return text_value.strip()

    def formater(self, context_xml, input_xml):
        if len(input_xml) > 0:
            change_with_format(input_xml[0])
            text_value = self._node_to_string(input_xml[0])
            for _loop in range(3):
                text_value = text_value.replace(' ,', ',')
                text_value = text_value.replace(', ', ',')
            return text_value
        else:
            return ''


def build_from_xml(xml_content, watermark):
    xsl_file = join(dirname(__file__), "ConvertxlpToCSV.xsl")
    if not isfile(xsl_file):
        raise LucteriosException(GRAVE, "Error:no csv xsl file!")
    with open(xsl_file, 'rb') as xsl_file:
        extensions = etree.Extension(LucteriosXLTExtension(), ('formater',), ns='lucterios')
        csv_transform = etree.XSLT(etree.XML(xsl_file.read()), extensions=extensions)
    xml_rep_content = etree.XML(xml_content)
    for xml_br in xml_rep_content.xpath("//br"):
        xml_br.text = ','
    return str(csv_transform(xml_rep_content)).encode('utf-8')
