# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest

class DummyTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def test_bidule(self):
        self.call('/dummy/bidule', {})
        self.assert_attrib_equal('', 'observer', 'CORE.Exception')

    def test_truc(self):
        self.call('/dummy/truc', {})
        self.assert_attrib_equal('', 'observer', 'Core.DialogBox')
        self.assert_attrib_equal('', 'source_extension', 'dummy')
        self.assert_attrib_equal('', 'source_action', 'truc')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_attrib_equal('TEXT', 'type', '1')
        self.assert_xml_equal('TEXT', 'Hello world!')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_xml_equal('ACTIONS/ACTION[1]', 'Ok')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'icon', 'images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'action', None)
