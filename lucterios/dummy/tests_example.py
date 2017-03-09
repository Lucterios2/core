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
        self.call('/lucterios.dummy/exampleList', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')

        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/HEADER', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/HEADER[@name="name"]', "name")
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/HEADER[@name="value"]', "value")
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/HEADER[@name="price"]', "price")
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=1]/VALUE[@name="name"]', 'abc')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=3]/VALUE[@name="name"]', 'uvw')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=4]/VALUE[@name="name"]', 'blabla')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=5]/VALUE[@name="name"]', 'boom')

    def testlist_order1(self):
        self.factory.xfer = ExampleList()
        self.call('/lucterios.dummy/exampleList', {'GRID_ORDER%example': 'valid,-value'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[1]/VALUE[@name="name"]', 'blabla')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[3]/VALUE[@name="name"]', 'abc')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[4]/VALUE[@name="name"]', 'uvw')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[5]/VALUE[@name="name"]', 'boom')

    def testlist_order2(self):
        self.factory.xfer = ExampleList()
        self.call('/lucterios.dummy/exampleList', {'GRID_ORDER%example': 'name'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 5)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[1]/VALUE[@name="name"]', 'abc')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[2]/VALUE[@name="name"]', 'blabla')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[3]/VALUE[@name="name"]', 'boom')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[4]/VALUE[@name="name"]', 'uvw')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[5]/VALUE[@name="name"]', 'zzzz')

    def testadd(self):
        self.factory.xfer = ExampleAddModify()
        self.call('/lucterios.dummy/exampleAddModify', {}, False)
        self.assert_observer(
            'core.custom', 'lucterios.dummy', 'exampleAddModify')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/EDIT[@name="name"]', None)
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="value"]', "0")
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="price"]', "100.00")
        self.assert_xml_equal('COMPONENTS/DATE[@name="date"]', "NULL")
        self.assert_xml_equal('COMPONENTS/TIME[@name="time"]', "00:00:00")
        self.assert_xml_equal('COMPONENTS/CHECK[@name="valid"]', "0")
        self.assert_xml_equal('COMPONENTS/MEMO[@name="comment"]', None)

    def testshow(self):
        self.factory.xfer = ExampleShow()
        self.call('/lucterios.dummy/exampleShow', {'example': '2'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleShow')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="name"]', "zzzz")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="value"]', "7")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="price"]', "714.03")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="date"]', "21 mars 2008")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="time"]', "15:21")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="valid"]', "Non")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="comment"]', None)

        self.factory.xfer = ExampleShow()
        self.call('/lucterios.dummy/exampleShow', {'example': '2', 'name': 'truc', 'value': '37', 'valid': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleShow')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="name"]', "zzzz")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="value"]', "7")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="price"]', "714.03")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="date"]', "21 mars 2008")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="time"]', "15:21")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="valid"]', "Non")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="comment"]', None)
        self.assert_count_equal('CONTEXT/PARAM', 1)

    def testsearch(self):
        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA': 'value||3||10'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=3]/VALUE[@name="name"]', 'uvw')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=5]/VALUE[@name="name"]', 'boom')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA': 'price||4||700.0'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=1]/VALUE[@name="name"]', 'abc')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=3]/VALUE[@name="name"]', 'uvw')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=4]/VALUE[@name="name"]', 'blabla')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA': 'date||3||2010-12-31//date||4||2000-01-01'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=4]/VALUE[@name="name"]', 'blabla')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA': 'time||4||06:00:00//time||3||18:00:00'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=5]/VALUE[@name="name"]', 'boom')

    def test_fieldsprint(self):
        print_text = ""
        for get_all_print_fields in Example.get_all_print_fields():
            print_text += "#%s " % get_all_print_fields[1]
        self.assertEqual(
            "#name #value #price #date #time #valid #comment ", print_text)
        example_obj = Example.objects.get(
            name='abc')
        self.assertEqual(
            "abc 12 1224.06 7 octobre 1997 21:43 Oui blablabla ", example_obj.evaluate(print_text))

    def testprint(self):
        self.factory.xfer = ExamplePrint()
        self.call('/lucterios.dummy/examplePrint', {'example': '2'}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'examplePrint')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testlabel(self):
        self.factory.xfer = ExampleLabel()
        self.call('/lucterios.dummy/exampleLabel', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleLabel')
        self.assert_count_equal('COMPONENTS/*', 8)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblPrintMode"]', "{[b]}Type de rapport{[/b]}", (0, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]', "3", (1, 0, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="PRINT_MODE"]/CASE', 1)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblLABEL"]', "{[b]}étiquette{[/b]}", (0, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="LABEL"]', "1", (1, 1, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="LABEL"]/CASE', 6)
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblFIRSTLABEL"]', "{[b]}N° première étiquette{[/b]}", (0, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="FIRSTLABEL"]', "1", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="lblMODEL"]', "{[b]}modèle{[/b]}", (0, 3, 1, 1))
        self.assert_comp_equal('COMPONENTS/SELECT[@name="MODEL"]', "2", (1, 3, 1, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="MODEL"]/CASE', 1)

        self.factory.xfer = ExampleLabel()
        self.call('/lucterios.dummy/exampleLabel', {'PRINT_MODE': '3', 'LABEL': 1, 'FIRSTLABEL': 3, 'MODEL': 2}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleLabel')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testlisting(self):
        for item_idx in range(0, 25):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleListing()
        self.call('/lucterios.dummy/exampleListing', {'PRINT_MODE': '4', 'MODEL': 1}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleListing')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 37, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Example"')
        self.assertEqual(content_csv[3].strip(), '"Name";"value + price";"date + time";')

    def testlisting_pdf(self):
        for item_idx in range(0, 150):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleListing()
        self.call('/lucterios.dummy/exampleListing', {'PRINT_MODE': '3', 'MODEL': 1}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleListing')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testreporting(self):
        for item_idx in range(0, 25):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleReporting()
        self.call('/lucterios.dummy/exampleReporting', {'PRINT_MODE': '4', 'MODEL': 3}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleReporting')
        csv_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 10 * 30 + 1, str(content_csv))
        self.assertEqual(content_csv[3].strip(), '"A abc"')

    def testreporting_pdf(self):
        for item_idx in range(0, 150):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleReporting()
        self.call('/lucterios.dummy/exampleReporting', {'PRINT_MODE': '3', 'MODEL': 3}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleReporting')
        pdf_value = b64decode(six.text_type(self.get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def test_other_list(self):
        self.factory.xfer = OtherList()
        self.call('/lucterios.dummy/otherList', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherList')
        self.assert_count_equal('COMPONENTS/*', 4)
        self.assert_count_equal('COMPONENTS/GRID[@name="other"]/HEADER', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="other"]/HEADER[@name="text"]', "text")
        self.assert_xml_equal('COMPONENTS/GRID[@name="other"]/HEADER[@name="bool"]', "bool")
        self.assert_xml_equal('COMPONENTS/GRID[@name="other"]/HEADER[@name="integer"]', "integer")
        self.assert_xml_equal('COMPONENTS/GRID[@name="other"]/HEADER[@name="real"]', "real")
        self.assert_count_equal('COMPONENTS/GRID[@name="other"]/RECORD', 0)

    def test_other_addshow(self):
        self.factory.xfer = OtherAddModify()
        self.call('/lucterios.dummy/otherAddModify', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherAddModify')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Ok', 'images/ok.png', 'lucterios.dummy', 'otherAddModify', 1, 1, 1, {'SAVE': 'YES'}))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Annuler', 'images/cancel.png'))

        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.dummy/images/10.png', (0, 0, 1, 6))
        self.assert_comp_equal('COMPONENTS/CHECK[@name="bool"]', "0", (1, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="integer"]', "0", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="real"]', "-5000.00", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/EDIT[@name="text"]', None, (1, 3, 1, 1))

        self.factory.xfer = OtherAddModify()
        self.call('/lucterios.dummy/otherAddModify', {'SAVE': 'YES', 'text': 'abc', 'bool': '1', 'real': '-159.37', 'integer': '13'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.dummy', 'otherAddModify')

        self.factory.xfer = OtherShow()
        self.call('/lucterios.dummy/otherShow', {'other': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherShow')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('ACTIONS/ACTION', 3)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Modifier', 'images/edit.png', 'lucterios.dummy', 'otherAddModify', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Imprimer', 'images/print.png', 'lucterios.dummy', 'otherPrint', 0, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[3]', ('Fermer', 'images/close.png'))

        self.assert_comp_equal('COMPONENTS/IMAGE[@name="img"]', '/static/lucterios.dummy/images/10.png', (0, 0, 1, 6))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="bool"]', "Oui", (1, 0, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="integer"]', "13", (1, 1, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="real"]', "-159.37", (1, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="text"]', "abc", (1, 3, 1, 1))
        self.factory.xfer = OtherAddModify()
        self.call('/lucterios.dummy/otherAddModify', {'SAVE': 'YES', 'other': '1', 'bool': '0'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.dummy', 'otherAddModify')

        self.factory.xfer = OtherShow()
        self.call('/lucterios.dummy/otherShow', {'other': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherShow')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Modifier', 'images/edit.png', 'lucterios.dummy', 'otherAddModify', 1, 1, 1))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Fermer', 'images/close.png'))
        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="bool"]', "Non", (1, 0, 1, 1))

    def test_printaction(self):
        generator = ActionGenerator(ExampleShow(), False)
        xml = generator.generate(self.factory.create_request('/lucterios.dummy/examplePrint', {'example': '2'}))
        self.parse_xml(xml, 'model', False)
        self.print_xml('')
        self.assert_attrib_equal("page/header", "extent", "12.0")
        self.assert_count_equal('page/header/*', 1)
        self.assert_attrib_equal("page/bottom", "extent", "0.0")
        self.assert_count_equal('page/bottom/*', 0)
        self.assert_count_equal('page/body/*', 15)
        self.assert_xml_equal('page/body/image[1]', 'images/9.pn', (-12, -1))
        self.assert_attrib_equal("page/body/image[1]", "height", "23.0")
        self.assert_attrib_equal("page/body/image[1]", "width", "23.0")
        self.assert_attrib_equal("page/body/image[1]", "top", "0.0")
        self.assert_attrib_equal("page/body/image[1]", "left", "0.0")
        self.assert_xml_equal("page/body/text[1]/b", 'name')
        self.assert_attrib_equal("page/body/text[1]", "top", "0.0")
        self.assert_attrib_equal("page/body/text[1]", "left", "56.0")
        self.assert_attrib_equal("page/body/text[1]", "width", "34.0")
        self.assert_attrib_equal("page/body/text[1]", "height", "5.0")
        self.assert_xml_equal("page/body/text[2]", 'zzzz')
        self.assert_attrib_equal("page/body/text[2]", "top", "0.0")
        self.assert_attrib_equal("page/body/text[2]", "left", "90.0")
        self.assert_attrib_equal("page/body/text[2]", "width", "100.0")
        self.assert_attrib_equal("page/body/text[2]", "height", "5.0")

        self.assert_xml_equal("page/body/text[3]/b", 'value')
        self.assert_attrib_equal("page/body/text[3]", "top", "5.0")
        self.assert_attrib_equal("page/body/text[3]", "left", "56.0")
        self.assert_attrib_equal("page/body/text[3]", "width", "34.0")
        self.assert_attrib_equal("page/body/text[3]", "height", "5.0")
        self.assert_xml_equal("page/body/text[4]", '7')
        self.assert_attrib_equal("page/body/text[4]", "top", "5.0")
        self.assert_attrib_equal("page/body/text[4]", "left", "90.0")
        self.assert_attrib_equal("page/body/text[4]", "width", "51.0")
        self.assert_attrib_equal("page/body/text[4]", "height", "5.0")


class ExampleTestJson(LucteriosTest):

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

    def assert_count(self, value):
        self.assertEqual(len(self.response_json['data']), value)

    def assert_value(self, name, value):
        self.assertEqual(self.response_json['data'][name], value)

    def testlist(self):
        self.factory.xfer = ExampleList()
        self.calljson('/lucterios.dummy/exampleList', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')

        self.assertEqual(self.response_json['comp'][2]['component'], 'GRID')
        self.assertEqual(self.response_json['comp'][2]['name'], 'example')
        self.assertEqual(len(self.response_json['comp'][2]['headers']), 3)
        self.assertEqual(self.response_json['comp'][2]['headers'][0][1], "name")
        self.assertEqual(self.response_json['comp'][2]['headers'][1][1], "value")
        self.assertEqual(self.response_json['comp'][2]['headers'][2][1], "price")

        self.assertEqual(len(self.response_json['data']["example"]), 5)
        self.assertEqual(self.response_json['data']["example"][0]['name'], 'abc')
        self.assertEqual(self.response_json['data']["example"][1]['name'], 'zzzz')
        self.assertEqual(self.response_json['data']["example"][2]['name'], 'uvw')
        self.assertEqual(self.response_json['data']["example"][3]['name'], 'blabla')
        self.assertEqual(self.response_json['data']["example"][4]['name'], 'boom')

    def testlist_order1(self):
        self.factory.xfer = ExampleList()
        self.calljson('/lucterios.dummy/exampleList',
                      {'GRID_ORDER%example': 'valid,-value'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')
        self.assertEqual(len(self.response_json['data']["example"]), 5)
        self.assertEqual(self.response_json['data']["example"][0]['name'], 'blabla')
        self.assertEqual(self.response_json['data']["example"][1]['name'], 'zzzz')
        self.assertEqual(self.response_json['data']["example"][2]['name'], 'abc')
        self.assertEqual(self.response_json['data']["example"][3]['name'], 'uvw')
        self.assertEqual(self.response_json['data']["example"][4]['name'], 'boom')

    def testlist_order2(self):
        self.factory.xfer = ExampleList()
        self.calljson('/lucterios.dummy/exampleList',
                      {'GRID_ORDER%example': 'name'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleList')
        self.assertEqual(len(self.response_json['data']["example"]), 5)
        self.assertEqual(self.response_json['data']["example"][0]['name'], 'abc')
        self.assertEqual(self.response_json['data']["example"][1]['name'], 'blabla')
        self.assertEqual(self.response_json['data']["example"][2]['name'], 'boom')
        self.assertEqual(self.response_json['data']["example"][3]['name'], 'uvw')
        self.assertEqual(self.response_json['data']["example"][4]['name'], 'zzzz')

    def testadd(self):
        self.factory.xfer = ExampleAddModify()
        self.calljson('/lucterios.dummy/exampleAddModify', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleAddModify')
        self.assert_count(8)
        self.assert_value("name", "")
        self.assert_value("value", 0)
        self.assert_value("price", 100.0)
        self.assert_value("date", None)
        self.assert_value("time", "00:00:00")
        self.assert_value("valid", 0)
        self.assert_value("comment", "")

    def testshow(self):
        self.factory.xfer = ExampleShow()
        self.calljson('/lucterios.dummy/exampleShow', {'example': '2'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleShow')
        self.assert_count(8)
        self.assert_value("name", "zzzz")
        self.assert_value("value", "7")
        self.assert_value("price", "714.03")
        self.assert_value("date", "21 mars 2008")
        self.assert_value("time", "15:21")
        self.assert_value("valid", "Non")
        self.assert_value("comment", "")
        self.assertEqual(len(self.response_json['context']), 1)

        self.factory.xfer = ExampleShow()
        self.calljson('/lucterios.dummy/exampleShow', {'example': '2', 'name': 'truc', 'value': '37', 'valid': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleShow')
        self.assert_count(8)
        self.assert_value("name", "zzzz")
        self.assert_value("value", "7")
        self.assert_value("price", "714.03")
        self.assert_value("date", "21 mars 2008")
        self.assert_value("time", "15:21")
        self.assert_value("valid", "Non")
        self.assert_value("comment", "")
        self.assertEqual(len(self.response_json['context']), 1)

    def testsearch(self):
        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'value||3||10'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assertEqual(len(self.response_json['data']["example"]), 3)
        self.assertEqual(self.response_json['data']["example"][0]['name'], 'zzzz')
        self.assertEqual(self.response_json['data']["example"][1]['name'], 'uvw')
        self.assertEqual(self.response_json['data']["example"][2]['name'], 'boom')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'price||4||700.0'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assertEqual(len(self.response_json['data']["example"]), 4)
        self.assertEqual(self.response_json['data']["example"][0]['name'], 'abc')
        self.assertEqual(self.response_json['data']["example"][1]['name'], 'zzzz')
        self.assertEqual(self.response_json['data']["example"][2]['name'], 'uvw')
        self.assertEqual(self.response_json['data']["example"][3]['name'], 'blabla')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'date||3||2010-12-31//date||4||2000-01-01'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assertEqual(len(self.response_json['data']["example"]), 2)
        self.assertEqual(self.response_json['data']["example"][0]['name'], 'zzzz')
        self.assertEqual(self.response_json['data']["example"][1]['name'], 'blabla')

        self.factory.xfer = ExampleSearch()
        self.calljson('/lucterios.dummy/exampleSearch', {'CRITERIA': 'time||4||06:00:00//time||3||18:00:00'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleSearch')
        self.assertEqual(len(self.response_json['data']["example"]), 2)
        self.assertEqual(self.response_json['data']["example"][0]['name'], 'zzzz')
        self.assertEqual(self.response_json['data']["example"][1]['name'], 'boom')

    def testprint(self):
        self.factory.xfer = ExamplePrint()
        self.calljson('/lucterios.dummy/examplePrint', {'example': '2'}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'examplePrint')
        pdf_value = b64decode(six.text_type(self.response_json['print']["content"]))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testlabel(self):
        self.factory.xfer = ExampleLabel()
        self.calljson('/lucterios.dummy/exampleLabel', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'exampleLabel')
        self.assert_count(8)

        self.factory.xfer = ExampleLabel()
        self.calljson('/lucterios.dummy/exampleLabel', {'PRINT_MODE': '3', 'LABEL': 1, 'FIRSTLABEL': 3, 'MODEL': 2}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleLabel')
        pdf_value = b64decode(six.text_type(self.response_json['print']["content"]))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testlisting(self):
        for item_idx in range(0, 25):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleListing()
        self.calljson('/lucterios.dummy/exampleListing', {'PRINT_MODE': '4', 'MODEL': 1}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleListing')
        csv_value = b64decode(six.text_type(self.response_json['print']["content"])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 37, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Example"')
        self.assertEqual(content_csv[3].strip(), '"Name";"value + price";"date + time";')

    def testlisting_pdf(self):
        for item_idx in range(0, 150):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleListing()
        self.calljson('/lucterios.dummy/exampleListing', {'PRINT_MODE': '3', 'MODEL': 1}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleListing')
        pdf_value = b64decode(six.text_type(self.response_json['print']["content"]))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testreporting(self):
        for item_idx in range(0, 25):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleReporting()
        self.calljson('/lucterios.dummy/exampleReporting', {'PRINT_MODE': '4', 'MODEL': 3}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleReporting')
        csv_value = b64decode(six.text_type(self.response_json['print']["content"])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 10 * 30 + 1, str(content_csv))
        self.assertEqual(content_csv[3].strip(), '"A abc"')

    def testreporting_pdf(self):
        for item_idx in range(0, 150):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx +
                                   78.15, date='1997-10-07', time='21:43', valid=True, comment="")
        self.factory.xfer = ExampleReporting()
        self.calljson('/lucterios.dummy/exampleReporting', {'PRINT_MODE': '3', 'MODEL': 3}, False)
        self.assert_observer('core.print', 'lucterios.dummy', 'exampleReporting')
        pdf_value = b64decode(six.text_type(self.response_json['print']["content"]))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def test_other_list(self):
        self.factory.xfer = OtherList()
        self.calljson('/lucterios.dummy/otherList', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherList')
        self.assert_count(4)
        self.assertEqual(self.response_json['comp'][2]['component'], 'GRID')
        self.assertEqual(self.response_json['comp'][2]['name'], 'other')
        self.assertEqual(len(self.response_json['comp'][2]['headers']), 4)
        self.assertEqual(self.response_json['comp'][2]['headers'][0][1], "bool")
        self.assertEqual(self.response_json['comp'][2]['headers'][1][1], "integer")
        self.assertEqual(self.response_json['comp'][2]['headers'][2][1], "real")
        self.assertEqual(self.response_json['comp'][2]['headers'][3][1], "text")
        self.assertEqual(len(self.response_json['data']["other"]), 0)

    def test_other_addshow(self):
        self.factory.xfer = OtherAddModify()
        self.calljson('/lucterios.dummy/otherAddModify', {}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherAddModify')
        self.assert_count(5)
        self.assertEqual(len(self.response_json['actions']), 2)
        self.assertEqual(self.response_json['actions'][0]['id'], 'lucterios.dummy/otherAddModify')
        self.assertEqual(self.response_json['actions'][0]['text'], 'Ok')
        self.assertEqual(self.response_json['actions'][0]['params'], {'SAVE': 'YES'})
        self.assertEqual(self.response_json['actions'][1]['id'], '')
        self.assertEqual(self.response_json['actions'][1]['text'], 'Annuler')
        self.assert_value("img", '/static/lucterios.dummy/images/10.png')
        self.assert_value("bool", False)
        self.assert_value("integer", 0)
        self.assert_value("real", -5000.0)
        self.assert_value("text", '')

        self.factory.xfer = OtherAddModify()
        self.calljson('/lucterios.dummy/otherAddModify', {'SAVE': 'YES', 'text': 'abc', 'bool': '1', 'real': '-159.37', 'integer': '13'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.dummy', 'otherAddModify')

        self.factory.xfer = OtherShow()
        self.calljson('/lucterios.dummy/otherShow', {'other': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherShow')
        self.assert_count(5)
        self.assertEqual(len(self.response_json['actions']), 3)
        self.assertEqual(self.response_json['actions'][0]['id'], 'lucterios.dummy/otherAddModify')
        self.assertEqual(self.response_json['actions'][0]['text'], 'Modifier')
        self.assertEqual(self.response_json['actions'][0]['params'], None)
        self.assertEqual(self.response_json['actions'][1]['id'], 'lucterios.dummy/otherPrint')
        self.assertEqual(self.response_json['actions'][1]['text'], 'Imprimer')
        self.assertEqual(self.response_json['actions'][1]['params'], None)
        self.assertEqual(self.response_json['actions'][2]['id'], '')
        self.assertEqual(self.response_json['actions'][2]['text'], 'Fermer')
        self.assert_value("img", '/static/lucterios.dummy/images/10.png')
        self.assert_value("bool", "Oui")
        self.assert_value("integer", "13")
        self.assert_value("real", "-159.37")
        self.assert_value("text", 'abc')

        self.factory.xfer = OtherAddModify()
        self.calljson('/lucterios.dummy/otherAddModify', {'SAVE': 'YES', 'other': '1', 'bool': '0'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.dummy', 'otherAddModify')

        self.factory.xfer = OtherShow()
        self.calljson('/lucterios.dummy/otherShow', {'other': '1'}, False)
        self.assert_observer('core.custom', 'lucterios.dummy', 'otherShow')
        self.assert_count(5)
        self.assertEqual(len(self.response_json['actions']), 2)
        self.assertEqual(self.response_json['actions'][0]['id'], 'lucterios.dummy/otherAddModify')
        self.assertEqual(self.response_json['actions'][0]['text'], 'Modifier')
        self.assertEqual(self.response_json['actions'][0]['params'], None)
        self.assertEqual(self.response_json['actions'][1]['id'], '')
        self.assertEqual(self.response_json['actions'][1]['text'], 'Fermer')
        self.assert_value("bool", "Non")
