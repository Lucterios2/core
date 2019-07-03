# -*- coding: utf-8 -*-
'''
Unit test of example view of dummy

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

from lucterios.framework.test import LucteriosTest
from lucterios.dummy.views import ExampleList, ExampleAddModify, ExampleShow, \
    ExamplePrint, ExampleListing, ExampleSearch, ExampleLabel, OtherList, \
    OtherAddModify, OtherShow, ExampleReporting
from lucterios.dummy.models import Example
from base64 import b64decode
from django.utils import six
from lucterios.framework.printgenerators import ActionGenerator


class ExampleTest(LucteriosTest):

    def setUp(self):

        LucteriosTest.setUp(self)
        Example.objects.create(name='abc', value=12, price=1224.06,
                               date='1997-10-07', time='21:43', valid=True, comment="blablabla")
        Example.objects.create(name='zzzz', value=7, price=714.03,
                               date='2008-03-21', time='15:21', valid=False, comment="")
        Example.objects.create(name='uvw', value=9, price=918.05,
                               date='2014-05-11', time='04:57', valid=True, comment="")
        Example.objects.create(name='blabla', value=17, price=1734.08,
                               date='2001-07-17', time='23:14', valid=False, comment="")
        Example.objects.create(name='boom', value=4, price=408.02,
                               date='1984-08-02', time='11:36', valid=True, comment="")

    def testlist(self):
        self.factory.xfer = ExampleList()
        self.calljson('/lucterios.dummy/exampleList', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')

        self.assert_grid_equal('example', {'name': 'name', 'value': 'value', 'price': 'price'}, 5)
        self.assert_json_equal('', '#example/headers/@0/@0', 'name')
        self.assert_json_equal('', '#example/headers/@0/@1', 'name')
        self.assert_json_equal('', '#example/headers/@0/@2', None)
        self.assert_json_equal('', '#example/headers/@0/@4', "%s")
        self.assert_json_equal('', '#example/headers/@1/@0', 'value')
        self.assert_json_equal('', '#example/headers/@1/@1', 'value')
        self.assert_json_equal('', '#example/headers/@1/@2', "N0")
        self.assert_json_equal('', '#example/headers/@1/@4', "%s")
        self.assert_json_equal('', '#example/headers/@2/@0', 'price')
        self.assert_json_equal('', '#example/headers/@2/@1', 'price')
        self.assert_json_equal('', '#example/headers/@2/@2', "C2EUR")
        self.assert_json_equal('', '#example/headers/@2/@4', "{[font color='green']}%s{[/font]};{[font color='red']}%s{[/font]}")

        self.assert_json_equal('', "example/@0/name", 'abc')
        self.assert_json_equal('', "example/@1/name", 'zzzz')
        self.assert_json_equal('', "example/@2/name", 'uvw')
        self.assert_json_equal('', "example/@3/name", 'blabla')
        self.assert_json_equal('', "example/@4/name", 'boom')

    def testlist_order1(self):
        self.factory.xfer = ExampleList()
        self.calljson('/lucterios.dummy/exampleList', {'GRID_ORDER%example': 'valid,-value'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')
        self.assert_count_equal("example", 5)
        self.assert_json_equal('', "example/@0/name", 'blabla')
        self.assert_json_equal('', "example/@1/name", 'zzzz')
        self.assert_json_equal('', "example/@2/name", 'abc')
        self.assert_json_equal('', "example/@3/name", 'uvw')
        self.assert_json_equal('', "example/@4/name", 'boom')

    def testlist_order2(self):
        self.factory.xfer = ExampleList()
        self.calljson('/lucterios.dummy/exampleList',
                      {'GRID_ORDER%example': 'name'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')
        self.assert_count_equal("example", 5)
        self.assert_json_equal('', "example/@0/name", 'abc')
        self.assert_json_equal('', "example/@1/name", 'blabla')
        self.assert_json_equal('', "example/@2/name", 'boom')
        self.assert_json_equal('', "example/@3/name", 'uvw')
        self.assert_json_equal('', "example/@4/name", 'zzzz')

    def testadd(self):
        self.factory.xfer = ExampleAddModify()
        self.calljson('/lucterios.dummy/exampleAddModify', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleAddModify')
        self.assert_count_equal('', 8)
        self.assert_json_equal('EDIT', "name", "")
        self.assert_json_equal('FLOAT', "value", 0)
        self.assert_json_equal('FLOAT', "price", 100.0)
        self.assert_json_equal('DATE', "date", None)
        self.assert_json_equal('TIME', "time", "00:00:00")
        self.assert_json_equal('CHECK', "valid", 0)
        self.assert_json_equal('MEMO', "comment", "")

    def testshow(self):
        self.factory.xfer = ExampleShow()
        self.calljson('/lucterios.dummy/exampleShow', {'example': '2'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleShow')
        self.assert_count_equal('', 9)
        self.assert_json_equal('LABELFORM', "name", "zzzz")
        self.assert_attrib_equal("name", "formatnum", None)
        self.assert_attrib_equal("name", "formatstr", "%s")
        self.assert_json_equal('LABELFORM', "value", 7)
        self.assert_attrib_equal("value", "formatnum", "N0")
        self.assert_attrib_equal("value", "formatstr", "%s")
        self.assert_json_equal('LABELFORM', "price", 714.03)
        self.assert_attrib_equal("price", "formatnum", "C2EUR")
        self.assert_attrib_equal("price", "formatstr", "{[font color='green']}%s{[/font]};{[font color='red']}%s{[/font]}")
        self.assert_json_equal('LABELFORM', "date", "2008-03-21")
        self.assert_attrib_equal("date", "formatnum", "D")
        self.assert_attrib_equal("date", "formatstr", "%s")
        self.assert_json_equal('LABELFORM', "time", "15:21:00")
        self.assert_attrib_equal("time", "formatnum", "T")
        self.assert_attrib_equal("time", "formatstr", "%s")
        self.assert_json_equal('LABELFORM', "valid", False)
        self.assert_attrib_equal("valid", "formatnum", "B")
        self.assert_attrib_equal("valid", "formatstr", "%s")
        self.assert_json_equal('LABELFORM', "comment", "")
        self.assert_attrib_equal("comment", "formatnum", None)
        self.assert_attrib_equal("comment", "formatstr", "%s")
        self.assert_json_equal('LABELFORM', "virtual", 49.9821)
        self.assert_attrib_equal("virtual", "formatnum", "N4")
        self.assert_attrib_equal("virtual", "formatstr", "%s")
        self.assertEqual(len(self.response_json['context']), 1)

        self.factory.xfer = ExampleShow()
        self.calljson('/lucterios.dummy/exampleShow', {'example': '2', 'name': 'truc', 'value': '37', 'valid': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleShow')
        self.assert_count_equal('', 9)
        self.assert_json_equal('LABELFORM', "name", "zzzz")
        self.assert_json_equal('LABELFORM', "value", 7)
        self.assert_json_equal('LABELFORM', "price", 714.03)
        self.assert_json_equal('LABELFORM', "date", "2008-03-21")
        self.assert_json_equal('LABELFORM', "time", "15:21:00")
        self.assert_json_equal('LABELFORM', "valid", False)
        self.assert_json_equal('LABELFORM', "comment", "")
        self.assert_json_equal('LABELFORM', "virtual", 49.9821)
        self.assertEqual(len(self.response_json['context']), 1)

    def testsearch(self):
        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'value||3||10'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal("example", 3)
        self.assert_json_equal('', "example/@0/name", 'zzzz')
        self.assert_json_equal('', "example/@1/name", 'uvw')
        self.assert_json_equal('', "example/@2/name", 'boom')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'price||4||700.0'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal("example", 4)
        self.assert_json_equal('', "example/@0/name", 'abc')
        self.assert_json_equal('', "example/@1/name", 'zzzz')
        self.assert_json_equal('', "example/@2/name", 'uvw')
        self.assert_json_equal('', "example/@3/name", 'blabla')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'date||3||2010-12-31//date||4||2000-01-01'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal("example", 2)
        self.assert_json_equal('', "example/@0/name", 'zzzz')
        self.assert_json_equal('', "example/@1/name", 'blabla')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'time||4||06:00:00//time||3||18:00:00'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal("example", 2)
        self.assert_json_equal('', "example/@0/name", 'zzzz')
        self.assert_json_equal('', "example/@1/name", 'boom')

    def testprint(self):
        self.factory.xfer = ExamplePrint()
        self.calljson('/lucterios.dummy/examplePrint', {'example': '2'}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'examplePrint')
        self.save_pdf()

    def testlabel(self):
        self.factory.xfer = ExampleLabel()
        self.calljson('/lucterios.dummy/exampleLabel', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleLabel')
        self.assert_count_equal('', 4)
        self.assert_comp_equal(('SELECT', 'PRINT_MODE'), "3", (0, 0, 2, 1))
        self.assertEqual(len(self.json_comp['PRINT_MODE']['case']), 1)
        self.assert_comp_equal(('SELECT', 'LABEL'), "1", (0, 1, 2, 1))
        self.assertEqual(len(self.json_comp['LABEL']['case']), 6)
        self.assert_comp_equal(('FLOAT', 'FIRSTLABEL'), "1", (0, 2, 2, 1))
        self.assert_comp_equal(('SELECT', 'MODEL'), "2", (0, 3, 2, 1))
        self.assertEqual(len(self.json_comp['MODEL']['case']), 1)

        self.factory.xfer = ExampleLabel()
        self.calljson('/lucterios.dummy/exampleLabel', {'PRINT_MODE': '3', 'LABEL': 1, 'FIRSTLABEL': 3, 'MODEL': 2}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleLabel')
        self.save_pdf()

    def testlisting(self):
        for item_idx in range(0, 25):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx + 78.15,
                                   date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleListing()
        self.calljson('/lucterios.dummy/exampleListing', {'PRINT_MODE': '4', 'MODEL': 1, 'TITLE': 'special example', 'INFO': 'comment', 'WITHNUM': True}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleListing')
        csv_value = b64decode(six.text_type(self.response_json['print']["content"])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 38, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"special example"')
        self.assertEqual(content_csv[3].strip(), '"comment"')
        self.assertEqual(content_csv[4].strip(), '"#";"Name";"value + price";"date + time";')

    def testlisting_pdf(self):
        for item_idx in range(0, 150):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx + 78.15,
                                   date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleListing()
        self.calljson('/lucterios.dummy/exampleListing', {'PRINT_MODE': '3', 'MODEL': 1}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleListing')
        self.save_pdf()

    def testreporting(self):
        for item_idx in range(0, 25):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx + 78.15,
                                   date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleReporting()
        self.calljson('/lucterios.dummy/exampleReporting', {'PRINT_MODE': '4', 'MODEL': 3}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleReporting')
        csv_value = b64decode(six.text_type(self.response_json['print']["content"])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 10 * 30 + 1, str(content_csv))
        self.assertEqual(content_csv[3].strip(), '"A abc"')

    def testreporting_pdf(self):
        for item_idx in range(0, 150):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx + 78.15,
                                   date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleReporting()
        self.calljson('/lucterios.dummy/exampleReporting', {'PRINT_MODE': '3', 'MODEL': 3}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleReporting')
        self.save_pdf()

    def test_other_list(self):
        self.factory.xfer = OtherList()
        self.calljson('/lucterios.dummy/otherList', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherList')
        self.assert_count_equal('', 3)
        self.assert_grid_equal('other', {'bool': 'bool', 'integer': 'integer', 'real': 'real', 'text': 'text'}, 0)

    def test_other_addshow(self):
        self.factory.xfer = OtherAddModify()
        self.calljson('/lucterios.dummy/otherAddModify', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherAddModify')
        self.assert_count_equal('', 5)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal(self.json_actions[0], ('Ok', 'images/ok.png', 'lucterios.dummy', 'otherAddModify', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal(self.json_actions[1], ('Annuler', 'images/cancel.png'))
        self.assert_json_equal('IMAGE', "img", '/static/lucterios.dummy/images/10.png')
        self.assert_json_equal('CHECK', "bool", False)
        self.assert_json_equal('FLOAT', "integer", 0)
        self.assert_json_equal('FLOAT', "real", -5000.0)
        self.assert_json_equal('EDIT', "text", '')

        self.factory.xfer = OtherAddModify()
        self.calljson('/lucterios.dummy/otherAddModify', {'SAVE': 'YES', 'text': 'abc', 'bool': '1', 'real': '-159.37', 'integer': '13'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.dummy', 'otherAddModify')

        self.factory.xfer = OtherShow()
        self.calljson('/lucterios.dummy/otherShow', {'other': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherShow')
        self.assert_count_equal('', 5)
        self.assertEqual(len(self.json_actions), 3)
        self.assert_action_equal(self.json_actions[0], ('Modifier', 'images/edit.png', 'lucterios.dummy', 'otherAddModify', 1, 1, 1))
        self.assert_action_equal(self.json_actions[1], ('Imprimer', 'images/print.png', 'lucterios.dummy', 'otherPrint', 0, 1, 1))
        self.assert_action_equal(self.json_actions[2], ('Fermer', 'images/close.png'))
        self.assert_json_equal('IMAGE', "img", '/static/lucterios.dummy/images/10.png')
        self.assert_json_equal('LABELFORM', "bool", True)
        self.assert_json_equal('LABELFORM', "integer", 13)
        self.assert_json_equal('LABELFORM', "real", -159.37)
        self.assert_json_equal('LABELFORM', "text", 'abc')

        self.factory.xfer = OtherAddModify()
        self.calljson('/lucterios.dummy/otherAddModify', {'SAVE': 'YES', 'other': '1', 'bool': '0'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.dummy', 'otherAddModify')

        self.factory.xfer = OtherShow()
        self.calljson('/lucterios.dummy/otherShow', {'other': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherShow')
        self.assert_count_equal('', 5)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal(self.json_actions[0], ('Modifier', 'images/edit.png', 'lucterios.dummy', 'otherAddModify', 1, 1, 1))
        self.assert_action_equal(self.json_actions[1], ('Fermer', 'images/close.png'))
        self.assert_json_equal('LABELFORM', "bool", False)

    def test_printaction(self):
        generator = ActionGenerator(ExampleShow(), False)
        xml = generator.generate(self.factory.create_request('/lucterios.dummy/examplePrint', {'example': '2'}))
        self.parse_xml(xml, 'model', False)
        self.print_xml('')
        self.assert_attrib_equal("page/header", "extent", "12.0")
        self.assert_count_equal('page/header/*', 1)
        self.assert_attrib_equal("page/bottom", "extent", "0.0")
        self.assert_count_equal('page/bottom/*', 0)
        self.assert_count_equal('page/body/*', 17)
        self.assert_xml_equal('page/body/image[1]', 'images/9.pn', (-12, -1))
        self.assert_attrib_equal("page/body/image[1]", "height", "23.0")
        self.assert_attrib_equal("page/body/image[1]", "width", "23.0")
        self.assert_attrib_equal("page/body/image[1]", "top", "0.0")
        self.assert_attrib_equal("page/body/image[1]", "left", "0.0")
        self.assert_xml_equal("page/body/text[1]/b", 'name')
        self.assert_attrib_equal("page/body/text[1]", "top", "0.0")
        self.assert_attrib_equal("page/body/text[1]", "left", "56.0")
        self.assert_attrib_equal("page/body/text[1]", "width", "35.0")
        self.assert_attrib_equal("page/body/text[1]", "height", "5.0")
        self.assert_xml_equal("page/body/text[2]", 'zzzz')
        self.assert_attrib_equal("page/body/text[2]", "top", "0.0")
        self.assert_attrib_equal("page/body/text[2]", "left", "91.0")
        self.assert_attrib_equal("page/body/text[2]", "width", "99.0")
        self.assert_attrib_equal("page/body/text[2]", "height", "5.0")

        self.assert_xml_equal("page/body/text[3]/b", 'value')
        self.assert_attrib_equal("page/body/text[3]", "top", "5.0")
        self.assert_attrib_equal("page/body/text[3]", "left", "56.0")
        self.assert_attrib_equal("page/body/text[3]", "width", "35.0")
        self.assert_attrib_equal("page/body/text[3]", "height", "5.0")
        self.assert_xml_equal("page/body/text[4]", '7')
        self.assert_attrib_equal("page/body/text[4]", "top", "5.0")
        self.assert_attrib_equal("page/body/text[4]", "left", "91.0")
        self.assert_attrib_equal("page/body/text[4]", "width", "44.0")
        self.assert_attrib_equal("page/body/text[4]", "height", "5.0")

        self.assert_xml_equal("page/body/text[5]/b", 'price')
        self.assert_xml_equal("page/body/text[6]", '714.03')
        self.assert_xml_equal("page/body/text[7]/b", 'date')
        self.assert_xml_equal("page/body/text[8]", '2008-03-21')
        self.assert_xml_equal("page/body/text[9]/b", 'time')
        self.assert_xml_equal("page/body/text[10]", '15:21:00')
        self.assert_xml_equal("page/body/text[11]/b", 'reduction')
        self.assert_xml_equal("page/body/text[12]", '49.9821')
        self.assert_xml_equal("page/body/text[13]/b", 'valid')
        self.assert_xml_equal("page/body/text[14]", 'False')
        self.assert_xml_equal("page/body/text[15]/b", 'comment')
        self.assert_xml_equal("page/body/text[16]", None)
