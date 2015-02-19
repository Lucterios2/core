# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from django.test import TestCase

from lucterios.framework.test import XmlClient, XmlRequestFactory, add_admin_user, add_empty_user
from lucterios.framework.xferbasic import XferContainerAcknowledge, XFER_DBOX_WARNING

class AuthentificationTest(TestCase):
    # pylint: disable=too-many-public-methods
    def setUp(self):
        self.client = XmlClient()
        add_admin_user()
        add_empty_user()

    def test_menu_noconnect(self):
        res_xml = self.client.call('/CORE/menu', {})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.get('source_extension'), 'CORE')
        self.assertEqual(res_xml.get('source_action'), 'menu')
        self.assertEqual(res_xml.text, 'NEEDAUTH')

    def test_badconnect(self):
        res_xml = self.client.call('/CORE/authentification', {})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.get('source_extension'), 'CORE')
        self.assertEqual(res_xml.get('source_action'), 'authentification')
        self.assertEqual(res_xml.text, 'NEEDAUTH')

        res_xml = self.client.call('/CORE/authentification', {'login':'', 'pass':''})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.text, 'BADAUTH')

        res_xml = self.client.call('/CORE/authentification', {'login':'aaa', 'pass':'bbb'})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.text, 'BADAUTH')

    def test_connect(self):
        res_xml = self.client.call('/CORE/authentification', {'login':'admin', 'pass':'admin'})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.text, 'OK')
        connect_xml = res_xml.xpath('CONNECTION')[0]
        self.assertEqual(connect_xml.xpath('TITLE')[0].text, 'Lucterios standard')
        self.assertEqual(connect_xml.xpath('SUBTITLE')[0].text, 'other subtitle')
        self.assertEqual(connect_xml.xpath('VERSION')[0].text, '1.999')
        self.assertEqual(connect_xml.xpath('SERVERVERSION')[0].text, '1.9')
        self.assertEqual(connect_xml.xpath('COPYRIGHT')[0].text[:4], '(c) ')
        self.assertEqual(connect_xml.xpath('LOGONAME')[0].text[:20], 'data:image/*;base64,')
        self.assertEqual(connect_xml.xpath('SUPPORT_EMAIL')[0].text[:8], 'support@')
        # self.assertEqual(connect_xml.xpath('INFO_SERVER')[0].text, '')
        self.assertEqual(connect_xml.xpath('LOGIN')[0].text, 'admin')
        self.assertEqual(connect_xml.xpath('REALNAME')[0].text, 'administrator ADMIN')

        res_xml = self.client.call('/CORE/exitConnection', {})
        self.assertEqual(res_xml.get('observer'), 'Core.Acknowledge')
        self.assertEqual(res_xml.get('source_extension'), 'CORE')
        self.assertEqual(res_xml.get('source_action'), 'exitConnection')

    def test_menu_connected(self):
        res_xml = self.client.call('/CORE/authentification', {'login':'admin', 'pass':'admin'})
        self.assertEqual(res_xml.text, 'OK')

        res_xml = self.client.call('/CORE/menu', {})
        self.assertEqual(res_xml.get('observer'), 'CORE.Menu')
        self.assertEqual(res_xml.get('source_extension'), 'CORE')
        self.assertEqual(res_xml.get('source_action'), 'menu')
        menus_xml = res_xml.xpath('MENUS')[0]
        # import logging
        # logging.getLogger(__name__).debug(etree.tostring(menus_xml, xml_declaration=True, pretty_print=True, encoding='utf-8'))
        self.assertEqual(menus_xml.xpath("MENU[@id='core.general']")[0].text, u'Général')
        self.assertEqual(menus_xml.xpath("MENU[@id='core.general']/MENU[@id='CORE/changerpassword']")[0].text, 'Mot de _passe')
        self.assertEqual(menus_xml.xpath("MENU[@id='core.admin']")[0].text, 'Administration')

        res_xml = self.client.call('/CORE/exitConnection', {})
        self.assertEqual(res_xml.get('observer'), 'Core.Acknowledge')

        res_xml = self.client.call('/CORE/menu', {})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.text, 'NEEDAUTH')


class ContainerAcknowledgeTest(TestCase):
    # pylint: disable=too-many-public-methods
    
    ack = None

    def setUp(self):
        self.ack = XferContainerAcknowledge()
        self.factory = XmlRequestFactory(self.ack)
        self.value = False

    def test_simple(self):
        res_xml = self.factory.call('/customer/details', {'id':12, 'value':'abc'})
        self.assertEqual(res_xml.get('observer'), 'Core.Acknowledge')
        self.assertEqual(res_xml.get('source_extension'), 'customer')
        self.assertEqual(res_xml.get('source_action'), 'details')
        self.assertEqual(len(res_xml.xpath('CONTEXT')), 1)
        self.assertEqual(len(res_xml.xpath('CONTEXT/PARAM')), 2)
        self.assertEqual(res_xml.xpath('CONTEXT/PARAM')[0].get('name'), 'id')
        self.assertEqual(res_xml.xpath('CONTEXT/PARAM')[0].text, '12')
        self.assertEqual(res_xml.xpath('CONTEXT/PARAM')[1].get('name'), 'value')
        self.assertEqual(res_xml.xpath('CONTEXT/PARAM')[1].text, 'abc')
        self.assertEqual(len(res_xml.xpath('CLOSE_ACTION')), 0)

    def test_redirect(self):
        def fillresponse_redirect():
            self.ack.redirect_action(XferContainerAcknowledge().get_changed("redirect", "", "customer", "list"))
        self.ack.fillresponse = fillresponse_redirect
        res_xml = self.factory.call('/customer/details', {})
        self.assertEqual(res_xml.get('observer'), 'Core.Acknowledge')
        self.assertEqual(res_xml.get('source_extension'), 'customer')
        self.assertEqual(res_xml.get('source_action'), 'details')
        self.assertEqual(len(res_xml.xpath('CONTEXT')), 0)
        self.assertEqual(len(res_xml.xpath('CLOSE_ACTION')), 1)
        self.assertEqual(len(res_xml.xpath('CLOSE_ACTION/ACTION')), 1)
        self.assertEqual(res_xml.xpath('CLOSE_ACTION/ACTION')[0].text, "redirect")
        self.assertEqual(res_xml.xpath('CLOSE_ACTION/ACTION')[0].get('extension'), "customer")
        self.assertEqual(res_xml.xpath('CLOSE_ACTION/ACTION')[0].get('action'), "list")

    def test_confirme(self):
        self.value = False
        def fillresponse_confirme():
            if self.ack.confirme("Do you want?"):
                self.value = True
        self.ack.fillresponse = fillresponse_confirme
        res_xml = self.factory.call('/customer/details', {})
        self.assertEqual(self.value, False)
        self.assertEqual(res_xml.get('observer'), 'Core.DialogBox')
        self.assertEqual(res_xml.get('source_extension'), 'customer')
        self.assertEqual(res_xml.get('source_action'), 'details')
        self.assertEqual(len(res_xml.xpath('CONTEXT')), 1)
        self.assertEqual(res_xml.xpath('CONTEXT/PARAM')[0].get('name'), 'CONFIRME')
        self.assertEqual(res_xml.xpath('CONTEXT/PARAM')[0].text, 'YES')
        self.assertEqual(res_xml.xpath('TEXT')[0].get('type'), '2')
        self.assertEqual(res_xml.xpath('TEXT')[0].text, 'Do you want?')
        self.assertEqual(len(res_xml.xpath('ACTIONS')), 1)
        self.assertEqual(len(res_xml.xpath('ACTIONS/ACTION')), 2)
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].text, 'Yes')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].get('icon'), 'images/ok.png')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].get('extension'), 'customer')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].get('action'), 'details')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[1].text, 'No')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[1].get('icon'), 'images/cancel.png')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[1].get('extension'), None)
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[1].get('action'), None)

        res_xml = self.factory.call('/customer/details', {'CONFIRME':'YES'})
        self.assertEqual(self.value, True)
        self.assertEqual(res_xml.get('observer'), 'Core.Acknowledge')

    def test_message(self):
        self.value = False
        def fillresponse_message():
            self.ack.message("Finished!", XFER_DBOX_WARNING)
        self.ack.fillresponse = fillresponse_message
        res_xml = self.factory.call('/customer/details', {})
        self.assertEqual(res_xml.get('observer'), 'Core.DialogBox')
        self.assertEqual(res_xml.get('source_extension'), 'customer')
        self.assertEqual(res_xml.get('source_action'), 'details')
        self.assertEqual(len(res_xml.xpath('CONTEXT')), 0)
        self.assertEqual(res_xml.xpath('TEXT')[0].get('type'), '3')
        self.assertEqual(res_xml.xpath('TEXT')[0].text, 'Finished!')
        self.assertEqual(len(res_xml.xpath('ACTIONS')), 1)
        self.assertEqual(len(res_xml.xpath('ACTIONS/ACTION')), 1)
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].text, 'Ok')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].get('icon'), 'images/ok.png')
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].get('extension'), None)
        self.assertEqual(res_xml.xpath('ACTIONS/ACTION')[0].get('action'), None)
