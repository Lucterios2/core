# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XFER_DBOX_WARNING

class ContainerAcknowledgeTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        self.value = False

    def test_simple(self):
        self.call('/customer/details', {'id':12, 'value':'abc'}, False)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_count_equal('CONTEXT/PARAM', 2)
        self.assert_xml_equal('CONTEXT/PARAM[@name="id"]', '12')
        self.assert_xml_equal('CONTEXT/PARAM[@name="value"]', 'abc')
        self.assert_count_equal('CLOSE_ACTION', 0)

    def test_close(self):
        def fillresponse_close():
            self.factory.xfer.set_close_action(XferContainerAcknowledge().get_changed("close", "", "customer", "list"))
        self.factory.xfer.fillresponse = fillresponse_close
        self.call('/customer/details', {}, False)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTION', 0)
        self.assert_count_equal('CLOSE_ACTION', 1)
        self.assert_count_equal('CLOSE_ACTION/ACTION', 1)
        self.assert_xml_equal('CLOSE_ACTION/ACTION', "close")
        self.assert_attrib_equal('CLOSE_ACTION/ACTION', 'extension', "customer")
        self.assert_attrib_equal('CLOSE_ACTION/ACTION', 'action', "list")

    def test_redirect(self):
        def fillresponse_redirect():
            self.factory.xfer.redirect_action(XferContainerAcknowledge().get_changed("redirect", "", "customer", "list"))
        self.factory.xfer.fillresponse = fillresponse_redirect
        self.call('/customer/details', {}, False)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTION', 1)
        self.assert_xml_equal('ACTION', "redirect")
        self.assert_attrib_equal('ACTION', 'extension', "customer")
        self.assert_attrib_equal('ACTION', 'action', "list")

    def test_confirme(self):
        self.value = False
        def fillresponse_confirme():
            if self.factory.xfer.confirme("Do you want?"):
                self.value = True
        self.factory.xfer.fillresponse = fillresponse_confirme
        self.call('/customer/details', {}, False)
        self.assertEqual(self.value, False)
        self.assert_attrib_equal('', 'observer', 'Core.DialogBox')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_attrib_equal('CONTEXT/PARAM', 'name', 'CONFIRME')
        self.assert_xml_equal('CONTEXT/PARAM', 'YES')
        self.assert_attrib_equal('TEXT', 'type', '2')
        self.assert_xml_equal('TEXT', 'Do you want?')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_xml_equal('ACTIONS/ACTION[1]', 'Oui')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'icon', 'images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'extension', 'customer')
        self.assert_attrib_equal('ACTIONS/ACTION[1]', 'action', 'details')
        self.assert_xml_equal('ACTIONS/ACTION[2]', 'Non')
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'icon', 'images/cancel.png')
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION[2]', 'action', None)

        self.call('/customer/details', {'CONFIRME':'YES'}, False)
        self.assertEqual(self.value, True)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

    def test_message(self):
        def fillresponse_message():
            self.factory.xfer.message("Finished!", XFER_DBOX_WARNING)
        self.factory.xfer.fillresponse = fillresponse_message
        self.call('/customer/details', {}, False)
        self.assert_attrib_equal('', 'observer', 'Core.DialogBox')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_attrib_equal('TEXT', 'type', '3')
        self.assert_xml_equal('TEXT', 'Finished!')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_xml_equal('ACTIONS/ACTION', 'Ok')
        self.assert_attrib_equal('ACTIONS/ACTION', 'icon', 'images/ok.png')
        self.assert_attrib_equal('ACTIONS/ACTION', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION', 'action', None)

    def test_traitment(self):
        self.value = False
        def fillresponse_traitment():
            if self.factory.xfer.traitment("customer/images/foo.png", "Traitment{[newline]}Wait...", "Done"):
                self.value = True
        self.factory.xfer.fillresponse = fillresponse_traitment
        self.call('/customer/details', {}, False)
        self.assertEqual(self.value, False)
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_attrib_equal('CONTEXT/PARAM', 'name', 'RELOAD')
        self.assert_xml_equal('CONTEXT/PARAM', 'YES')
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', '{[newline]}{[center]}Traitment{[newline]}Wait...{[/center]}')
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img_title"]', 'customer/images/foo.png')
        self.assert_xml_equal('COMPONENTS/BUTTON[@name="Next"]/ACTIONS/ACTION', 'Traitment...')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="Next"]/ACTIONS/ACTION', 'extension', 'customer')
        self.assert_attrib_equal('COMPONENTS/BUTTON[@name="Next"]/ACTIONS/ACTION', 'action', 'details')
        self.assert_xml_equal('COMPONENTS/BUTTON[@name="Next"]/JavaScript', 'parent.refresh()')
        self.assert_count_equal('ACTIONS', 1)
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_xml_equal('ACTIONS/ACTION', 'Cancel')
        self.assert_attrib_equal('ACTIONS/ACTION', 'icon', 'images/cancel.png')
        self.assert_attrib_equal('ACTIONS/ACTION', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION', 'action', None)

        self.call('/customer/details', {'RELOAD':'YES'}, False)
        self.assertEqual(self.value, True)
        self.assert_attrib_equal('', 'observer', 'Core.Custom')
        self.assert_attrib_equal('', 'source_extension', 'customer')
        self.assert_attrib_equal('', 'source_action', 'details')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_attrib_equal('CONTEXT/PARAM', 'name', 'RELOAD')
        self.assert_xml_equal('CONTEXT/PARAM', 'YES')
        self.assert_count_equal('COMPONENTS/*', 2)
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img_title"]', 'customer/images/foo.png')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', '{[newline]}{[center]}Done{[/center]}')
        self.assert_xml_equal('ACTIONS/ACTION', 'Fermer')
        self.assert_attrib_equal('ACTIONS/ACTION', 'icon', 'images/close.png')
        self.assert_attrib_equal('ACTIONS/ACTION', 'extension', None)
        self.assert_attrib_equal('ACTIONS/ACTION', 'action', None)
