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
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest
from lucterios.dummy.views import ExampleList, ExampleAddModify, ExampleShow, \
    ExamplePrint, ExampleListing, ExampleSearch, ExampleLabel
from lucterios.dummy.models import Example
from base64 import b64decode
from django.utils import six

class ExampleTest(LucteriosTest):

    def setUp(self):
        # pylint: disable=no-member
        LucteriosTest.setUp(self)
        Example.objects.create(name='abc', value=12, price=1224.06, date='1997-10-07', time='21:43', valid=True, comment="blablabla")
        Example.objects.create(name='zzzz', value=7, price=714.03, date='2008-03-21', time='15:21', valid=False, comment="")
        Example.objects.create(name='uvw', value=9, price=918.05, date='2014-05-11', time='04:57', valid=True, comment="")
        Example.objects.create(name='blabla', value=17, price=1734.08, date='2001-07-17', time='23:14', valid=False, comment="")
        Example.objects.create(name='boom', value=4, price=408.02, date='1984-08-02', time='11:36', valid=True, comment="")

    def testlist(self):
        self.factory.xfer = ExampleList()
        self.call('/lucterios.dummy/exampleList', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleList')

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

    def testadd(self):
        self.factory.xfer = ExampleAddModify()
        self.call('/lucterios.dummy/exampleAddModify', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleAddModify')

    def testshow(self):
        self.factory.xfer = ExampleShow()
        self.call('/lucterios.dummy/exampleShow', {'example':'2'}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleShow')

    def testsearch(self):
        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleSearch')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA':'value||3||10'}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=3]/VALUE[@name="name"]', 'uvw')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=5]/VALUE[@name="name"]', 'boom')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA':'price||4||700.0'}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=1]/VALUE[@name="name"]', 'abc')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=3]/VALUE[@name="name"]', 'uvw')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=4]/VALUE[@name="name"]', 'blabla')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA':'date||3||2010-12-31//date||4||2000-01-01'}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=4]/VALUE[@name="name"]', 'blabla')

        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {'CRITERIA':'time||4||06:00:00//time||3||18:00:00'}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleSearch')
        self.assert_count_equal('COMPONENTS/GRID[@name="example"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=2]/VALUE[@name="name"]', 'zzzz')
        self.assert_xml_equal('COMPONENTS/GRID[@name="example"]/RECORD[@id=5]/VALUE[@name="name"]', 'boom')

    def test_fieldsprint(self):
        print_text = ""
        for print_fields in Example.get_print_fields():
            print_text += "#%s " % print_fields[1]
        self.assertEqual("#name #value #price #date #time #valid #comment ", print_text)
        example_obj = Example.objects.get(name='abc') # pylint: disable=no-member
        self.assertEqual("abc 12 1224.06 7 octobre 1997 21:43:00 Oui blablabla ", example_obj.evaluate(print_text))

    def testprint(self):
        self.factory.xfer = ExamplePrint()
        self.call('/lucterios.dummy/examplePrint', {'example':'2'}, False)
        self.assert_observer('Core.Print', 'lucterios.dummy', 'examplePrint')
        pdf_value = b64decode(six.text_type(self._get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testlabel(self):
        self.factory.xfer = ExampleLabel()
        self.call('/lucterios.dummy/exampleLabel', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleLabel')
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
        self.call('/lucterios.dummy/exampleLabel', {'PRINT_MODE':'3', 'LABEL':1, 'FIRSTLABEL':3, 'MODEL':2}, False)
        self.assert_observer('Core.Print', 'lucterios.dummy', 'exampleLabel')
        pdf_value = b64decode(six.text_type(self._get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))

    def testlisting(self):
        for item_idx in range(0, 25):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx + 78.15, date='1997-10-07', time='21:43', valid=True, comment="") # pylint: disable=no-member
        self.factory.xfer = ExampleListing()
        self.call('/lucterios.dummy/exampleListing', {'PRINT_MODE':'4', 'MODEL':1}, False)
        self.assert_observer('Core.Print', 'lucterios.dummy', 'exampleListing')
        csv_value = b64decode(six.text_type(self._get_first_xpath('PRINT').text)).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 36, str(content_csv))
        self.assertEqual(content_csv[1].strip(), '"Example"')
        self.assertEqual(content_csv[3].strip(), '"Name";"value + price";"date + time";')

    def testlisting_pdf(self):
        for item_idx in range(0, 150):
            Example.objects.create(name='uvw_%d' % item_idx, value=12 + item_idx, price=34.18 * item_idx + 78.15, date='1997-10-07', time='21:43', valid=True, comment="") # pylint: disable=no-member
        self.factory.xfer = ExampleListing()
        self.call('/lucterios.dummy/exampleListing', {'PRINT_MODE':'3', 'MODEL':1}, False)
        self.assert_observer('Core.Print', 'lucterios.dummy', 'exampleListing')
        pdf_value = b64decode(six.text_type(self._get_first_xpath('PRINT').text))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))
