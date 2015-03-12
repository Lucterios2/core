# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest
from django.utils import six

class DummyTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def test_bidule1(self):
        self.call('/dummy/bidule', {})
        self.assert_attrib_equal('', 'observer', 'CORE.Exception')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'bidule')
        self.assert_xml_equal('EXCEPTION/MESSAGE', 'Error of bidule')
        self.assert_xml_equal('EXCEPTION/CODE', '2')
        self.assert_xml_equal('EXCEPTION/DEBUG_INFO', 'lucterios/dummy/views.py in line 29 in fillresponse : raise LucteriosException(GRAVE, "Error of bidule")', (-111, -7))
        self.assert_xml_equal('EXCEPTION/TYPE', 'LucteriosException')

    def test_bidule2(self):
        self.call('/dummy/bidule', {'error':'big'})
        self.assert_attrib_equal('', 'observer', 'CORE.Exception')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'bidule')
        self.assert_xml_equal('EXCEPTION/MESSAGE', 'Other error:big')
        self.assert_xml_equal('EXCEPTION/CODE', '0')
        self.assert_xml_equal('EXCEPTION/DEBUG_INFO', 'lucterios/dummy/views.py in line 31 in fillresponse : raise AttributeError("Other error:" + error)', (-105, -7))
        self.assert_xml_equal('EXCEPTION/TYPE', 'AttributeError')

    def test_truc(self):
        self.call('/dummy/truc', {})
        self.assert_attrib_equal('', 'observer', 'Core.DialogBox')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'truc')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_attrib_equal('TEXT', 'type', '1')
        self.assert_xml_equal('TEXT', 'Hello world (None,4)!')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_xml_equal('ACTIONS/ACTION[1]', 'Ok')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'icon', 'images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'action', None)

    def test_multi(self):
        self.call('/dummy/multi', {})
        self.assert_attrib_equal('', 'observer', 'Core.DialogBox')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'multi')
        self.assert_attrib_equal('TEXT', 'type', '2')
        self.assert_xml_equal('TEXT', 'Do you want?')

        self.call('/dummy/multi', {'CONFIRME':'YES'})
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'multi')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', '{[br/]}{[center]}Waiting...{[/center]}')

        self.call('/dummy/multi', {'CONFIRME':'YES', 'RELOAD':'YES'})
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'multi')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', '{[br/]}{[center]}Done!{[/center]}')

    def test_testcomposants(self):
        # pylint: disable=too-many-statements
        self.call('/dummy/testComposants', {})
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'testComposants')
        self.assert_count_equal('COMPONENTS/*', 22)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl2"]', 'editor=aaa')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl3"]', 'Real=3.1399999')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl4"]', 'Memo=xyz')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl5"]', 'Date=2007-04-23')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl6"]', 'Hour=12:34:00')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl7"]', 'Date Hour=2008-07-12 23:47:31')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl8"]', 'Coche=False')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl9"]', 'Select=1')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl10"]', 'Integer=5')
        if six.PY2:
            self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl11"]', "CheckList=[u'1', u'2']")
        else:
            self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl11"]', "CheckList=['1', '2']")
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="Lbl12"]', 'Bouton')

        self.assert_xml_equal('COMPONENTS/EDIT[@name="edt1"]', 'aaa')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="flt1"]', '3.14')
        self.assert_attrib_equal('COMPONENTS/FLOAT[@name="flt1"]', 'min', '0.0')
        self.assert_attrib_equal('COMPONENTS/FLOAT[@name="flt1"]', 'max', '10000.0')
        self.assert_attrib_equal('COMPONENTS/FLOAT[@name="flt1"]', 'prec', '2')
        self.assert_xml_equal('COMPONENTS/MEMO[@name="mm1"]', 'xyz')
        self.assert_attrib_equal('COMPONENTS/MEMO[@name="mm1"]', 'FirstLine', '-1')
        self.assert_attrib_equal('COMPONENTS/MEMO[@name="mm1"]', 'VMin', '50')
        self.assert_attrib_equal('COMPONENTS/MEMO[@name="mm1"]', 'HMin', '200')
        self.assert_xml_equal('COMPONENTS/DATE[@name="dt1"]', '2007-04-23')
        self.assert_xml_equal('COMPONENTS/TIME[@name="tm1"]', '12:34:00')
        self.assert_xml_equal('COMPONENTS/DATETIME[@name="stm1"]', '2008-07-12 23:47:31')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="ck1"]', '0')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="slct1"]', '1')
        self.assert_count_equal('COMPONENTS/SELECT[@name="slct1"]/CASE', 3)
        self.assert_xml_equal('COMPONENTS/SELECT[@name="slct1"]/CASE[@id="1"]', 'abc')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="slct1"]/CASE[@id="2"]', 'def')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="slct1"]/CASE[@id="3"]', 'ghij')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="flt2"]', '5')
        self.assert_attrib_equal('COMPONENTS/FLOAT[@name="flt2"]', 'min', '0.0')
        self.assert_attrib_equal('COMPONENTS/FLOAT[@name="flt2"]', 'max', '100.0')
        self.assert_attrib_equal('COMPONENTS/FLOAT[@name="flt2"]', 'prec', '0')
        self.assert_count_equal('COMPONENTS/CHECKLIST[@name="cl1"]', 1)
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]', 'simple', '0')

        self.assert_count_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE', 4)
        self.assert_xml_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="1"]', 'abc')
        self.assert_xml_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="2"]', 'def')
        self.assert_xml_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="3"]', 'ghij')
        self.assert_xml_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="4"]', 'klmn')
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="1"]', 'checked', '1')
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="2"]', 'checked', '1')
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="3"]', 'checked', '0')
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="4"]', 'checked', '0')

        for (tag, name) in [('EDIT', 'edt1'), ('FLOAT', 'flt1'), ('MEMO', 'mm1'), ('DATE', 'dt1'), \
                             ('TIME', 'tm1'), ('DATETIME', 'stm1'), ('CHECK', 'ck1'), ('SELECT', 'slct1'), \
                             ('FLOAT', 'flt2'), ('CHECKLIST', 'cl1')]:
            self.assert_count_equal('COMPONENTS/%s[@name="%s"]/ACTIONS/ACTION' % (tag, name), 1)
            self.assert_xml_equal('COMPONENTS/%s[@name="%s"]/ACTIONS/ACTION' % (tag, name), 'Modify')
            self.assert_attrib_equal('COMPONENTS/%s[@name="%s"]/ACTIONS/ACTION' % (tag, name), 'extension', 'dummy')
            self.assert_attrib_equal('COMPONENTS/%s[@name="%s"]/ACTIONS/ACTION' % (tag, name), 'action', 'testComposants')
            self.assert_attrib_equal('COMPONENTS/%s[@name="%s"]/ACTIONS/ACTION' % (tag, name), 'close', '0')
            self.assert_attrib_equal('COMPONENTS/%s[@name="%s"]/ACTIONS/ACTION' % (tag, name), 'modal', '2')
            self.assert_attrib_equal('COMPONENTS/%s[@name="%s"]/ACTIONS/ACTION' % (tag, name), 'unique', '1')

    def test_testcomposants_again(self):
        # pylint: disable=too-many-statements
        self.call('/dummy/testComposants', {'edt1':'bbb', 'flt1':'7.896666', 'mm1':'qwerty', 'dt1':'2015-02-22', 'tm1':'21:05:00', \
                     'ck1':'o', 'slct1':'2', 'flt2':'27', 'cl1':'2;4', 'stm1':'2015-03-30 10:00:00'})
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'testComposants')
        self.assert_count_equal('COMPONENTS/*', 22)

        self.assert_xml_equal('COMPONENTS/EDIT[@name="edt1"]', 'bbb')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="flt1"]', '7.90')
        self.assert_xml_equal('COMPONENTS/MEMO[@name="mm1"]', 'qwerty')
        self.assert_xml_equal('COMPONENTS/DATE[@name="dt1"]', '2015-02-22')
        self.assert_xml_equal('COMPONENTS/TIME[@name="tm1"]', '21:05:00')
        self.assert_xml_equal('COMPONENTS/DATETIME[@name="stm1"]', '2015-03-30 10:00:00')
        self.assert_xml_equal('COMPONENTS/CHECK[@name="ck1"]', '1')
        self.assert_xml_equal('COMPONENTS/SELECT[@name="slct1"]', '2')
        self.assert_xml_equal('COMPONENTS/FLOAT[@name="flt2"]', '27')
        self.assert_count_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE', 4)
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="1"]', 'checked', '0')
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="2"]', 'checked', '1')
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="3"]', 'checked', '0')
        self.assert_attrib_equal('COMPONENTS/CHECKLIST[@name="cl1"]/CASE[@id="4"]', 'checked', '1')

    def test_simplegrid(self):
        self.call('/dummy/simpleGrid', {})
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'simpleGrid')

        self.assert_count_equal('COMPONENTS/*', 1)
        self.assert_count_equal('COMPONENTS/GRID[@name="grid"]/*', 6)
        self.assert_count_equal('COMPONENTS/GRID[@name="grid"]/HEADER', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col1"]', 'Integer')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col2"]', 'Float')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col3"]', 'Boolean')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col4"]', 'String')
        self.assert_attrib_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col1"]', 'type', 'int')
        self.assert_attrib_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col2"]', 'type', 'float')
        self.assert_attrib_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col3"]', 'type', 'bool')
        self.assert_attrib_equal('COMPONENTS/GRID[@name="grid"]/HEADER[@name="col4"]', 'type', 'str')

        self.assert_count_equal('COMPONENTS/GRID[@name="grid"]/RECORD', 2)
        self.assert_count_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="1"]/VALUE', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="1"]/VALUE[@name="col1"]', '25')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="1"]/VALUE[@name="col2"]', '7.54')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="1"]/VALUE[@name="col3"]', '1')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="1"]/VALUE[@name="col4"]', 'foo')
        self.assert_count_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="5"]/VALUE', 4)
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="5"]/VALUE[@name="col1"]', '0')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="5"]/VALUE[@name="col2"]', '789.644')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="5"]/VALUE[@name="col3"]', '0')
        self.assert_xml_equal('COMPONENTS/GRID[@name="grid"]/RECORD[@id="5"]/VALUE[@name="col4"]', 'string')
