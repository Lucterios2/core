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


def get_text_size(para_text, font_size=9, line_height=10, text_align='left', is_cell=False):
    return 1, 1


def build_from_xml(xml_content, watermark):
    xsl_file = join(dirname(__file__), "ConvertxlpToCSV.xsl")
    if not isfile(xsl_file):
        raise LucteriosException(GRAVE, "Error:no csv xsl file!")
    with open(xsl_file, 'rb') as xsl_file:
        csv_transform = etree.XSLT(etree.XML(xsl_file.read()))
    xml_rep_content = etree.XML(xml_content)
    for xml_br in xml_rep_content.xpath("//br"):
        xml_br.text = ','
    return str(csv_transform(xml_rep_content)).encode('utf-8')
