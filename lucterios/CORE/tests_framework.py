# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XFER_DBOX_WARNING
from django.utils.http import urlquote_plus

class ContainerAcknowledgeTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        self.xfer_class = XferContainerAcknowledge
        LucteriosTest.setUp(self)
        self.value = False

    def test_simple(self):
        self.call('/customer/details', {'id':12, 'value':'abc'}, False)
        self.assert_observer('Core.Acknowledge', 'customer', 'details')
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
        self.assert_observer('Core.Acknowledge', 'customer', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTION', 0)
        self.assert_count_equal('CLOSE_ACTION/ACTION', 1)
        self.assert_action_equal('CLOSE_ACTION/ACTION', ("close", None, "customer", "list", 1, 1, 1))

    def test_redirect(self):
        def fillresponse_redirect():
            self.factory.xfer.redirect_action(XferContainerAcknowledge().get_changed("redirect", "", "customer", "list"))
        self.factory.xfer.fillresponse = fillresponse_redirect
        self.call('/customer/details', {}, False)
        self.assert_observer('Core.Acknowledge', 'customer', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('ACTION', 1)
        self.assert_action_equal('ACTION', ("redirect", None, "customer", "list", 1, 1, 1))

    def test_confirme(self):
        self.value = False
        def fillresponse_confirme():
            if self.factory.xfer.confirme("Do you want?"):
                self.value = True
        self.factory.xfer.fillresponse = fillresponse_confirme
        self.call('/customer/details', {}, False)
        self.assertEqual(self.value, False)
        self.assert_observer('Core.DialogBox', 'customer', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_attrib_equal('TEXT', 'type', '2')
        self.assert_xml_equal('TEXT', 'Do you want?')
        self.assert_count_equal('ACTIONS/ACTION', 2)
        self.assert_action_equal('ACTIONS/ACTION[1]', ('Oui', 'images/ok.png', 'customer', 'details', 1, 1, 1, {'CONFIRME':"YES"}))
        self.assert_action_equal('ACTIONS/ACTION[2]', ('Non', 'images/cancel.png'))

        self.call('/customer/details', {'CONFIRME':'YES'}, False)
        self.assertEqual(self.value, True)
        self.assert_attrib_equal('', 'observer', 'Core.Acknowledge')

    def test_message(self):
        def fillresponse_message():
            self.factory.xfer.message("Finished!", XFER_DBOX_WARNING)
        self.factory.xfer.fillresponse = fillresponse_message
        self.call('/customer/details', {}, False)
        self.assert_observer('Core.DialogBox', 'customer', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_attrib_equal('TEXT', 'type', '3')
        self.assert_xml_equal('TEXT', 'Finished!')
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal('ACTIONS/ACTION', ('Ok', 'images/ok.png'))

    def test_traitment(self):
        self.value = False
        def fillresponse_traitment():
            if self.factory.xfer.traitment("customer/images/foo.png", "Traitment{[br/]}Wait...", "Done"):
                self.value = True
        self.factory.xfer.fillresponse = fillresponse_traitment
        self.call('/customer/details', {}, False)
        self.assertEqual(self.value, False)
        self.assert_observer('Core.Custom', 'customer', 'details')
        self.assert_count_equal('CONTEXT', 0)
        self.assert_count_equal('COMPONENTS/*', 3)
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', '{[br/]}{[center]}Traitment{[br/]}Wait...{[/center]}')
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img_title"]', 'customer/images/foo.png')
        self.assert_action_equal('COMPONENTS/BUTTON[@name="Next"]/ACTIONS/ACTION', ('Traitement...', None, 'customer', 'details', 1, 1, 1, {'RELOAD':"YES"}))
        self.assert_xml_equal('COMPONENTS/BUTTON[@name="Next"]/JavaScript', urlquote_plus('parent.refresh()'))
        self.assert_count_equal('ACTIONS/ACTION', 1)
        self.assert_action_equal('ACTIONS/ACTION', ('Annuler', 'images/cancel.png'))

        self.call('/customer/details', {'RELOAD':'YES'}, False)
        self.assertEqual(self.value, True)
        self.assert_observer('Core.Custom', 'customer', 'details')
        self.assert_count_equal('CONTEXT', 1)
        self.assert_attrib_equal('CONTEXT/PARAM', 'name', 'RELOAD')
        self.assert_xml_equal('CONTEXT/PARAM', 'YES')
        self.assert_count_equal('COMPONENTS/*', 2)
        self.assert_xml_equal('COMPONENTS/IMAGE[@name="img_title"]', 'customer/images/foo.png')
        self.assert_xml_equal('COMPONENTS/LABELFORM[@name="info"]', '{[br/]}{[center]}Done{[/center]}')
        self.assert_action_equal('ACTIONS/ACTION', ('Fermer', 'images/close.png'))
