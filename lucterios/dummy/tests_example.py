# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest
from lucterios.dummy.views import ExampleList, ExampleAddModify, ExampleShow, \
    ExamplePrint, ExampleListing, ExampleSearch
from lucterios.dummy.models import Example

class ExampleTest(LucteriosTest):

    def setUp(self):
        # pylint: disable=no-member
        LucteriosTest.setUp(self)
        Example.objects.create(name='abc', value=12, price=1224.06, date='1997-10-07', time='21:43', valid=True, comment="")
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

    def testprint(self):
        self.factory.xfer = ExamplePrint()
        self.call('/lucterios.dummy/examplePrint', {'example':'2', 'PRINT_MODE':'3'}, False)
        self.assert_observer('Core.Print', 'lucterios.dummy', 'examplePrint')

    def testlisting(self):
        self.factory.xfer = ExampleListing()
        self.call('/lucterios.dummy/exampleListing', {'PRINT_MODE':'4'}, False)
        self.assert_observer('Core.Print', 'lucterios.dummy', 'exampleListing')

    def testsearch(self):
        self.factory.xfer = ExampleSearch()
        self.call('/lucterios.dummy/exampleSearch', {}, False)
        self.assert_observer('Core.Custom', 'lucterios.dummy', 'exampleSearch')
