# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from django.test import TestCase
from django.test import Client
from lxml import etree

class XmlClient(Client):
    
    def check(self, condition, msg):
        if not condition:
            raise Exception(msg)
    
    def call(self, path, data={}):
        response = self.post(path, data)
        self.check(response.status_code == 200, "HTTP error:"+str(response.status_code))
        contentxml = etree.fromstring(response.content)
        self.check(contentxml.getchildren()[0].tag == 'REPONSE', "NOT REPONSE")
        return contentxml.getchildren()[0]

class AuthentificationTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.client = XmlClient()
        user = User.objects.create_user(username='admin', password='admin')
        user.first_name = 'administrator'
        user.last_name = 'ADMIN'
        user.is_staff=True
        user.is_active=True
        user.save()

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

        res_xml = self.client.call('/CORE/authentification', {'login':'','pass':''})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.text, 'BADAUTH')
        
        res_xml = self.client.call('/CORE/authentification', {'login':'aaa','pass':'bbb'})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.text, 'BADAUTH')

    def test_connect(self):
        res_xml = self.client.call('/CORE/authentification', {'login':'admin','pass':'admin'})
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
        #self.assertEqual(connect_xml.xpath('INFO_SERVER')[0].text, '')
        self.assertEqual(connect_xml.xpath('LOGIN')[0].text, 'admin')
        self.assertEqual(connect_xml.xpath('REALNAME')[0].text, 'administrator ADMIN')

        res_xml = self.client.call('/CORE/exitConnection', {})
        self.assertEqual(res_xml.get('observer'), 'Core.Acknowledge')
        self.assertEqual(res_xml.get('source_extension'), 'CORE')
        self.assertEqual(res_xml.get('source_action'), 'exitConnection')

    def test_menu_connected(self):
        res_xml = self.client.call('/CORE/authentification', {'login':'admin','pass':'admin'})
        self.assertEqual(res_xml.text, 'OK')
        
        res_xml = self.client.call('/CORE/menu', {})
        self.assertEqual(res_xml.get('observer'), 'CORE.Menu')
        self.assertEqual(res_xml.get('source_extension'), 'CORE')
        self.assertEqual(res_xml.get('source_action'), 'menu')
        menus_xml = res_xml.xpath('MENUS')[0]
        #print etree.tostring(menus_xml, xml_declaration=True, pretty_print=True, encoding='utf-8')
        self.assertEqual(menus_xml.xpath("MENU[@id='core.general']")[0].text, 'General')
        self.assertEqual(menus_xml.xpath("MENU[@id='core.general']/MENU[@id='CORE/changerpassword']")[0].text, '_Mot de passe')
        self.assertEqual(menus_xml.xpath("MENU[@id='core.admin']")[0].text, 'Administration')

        res_xml = self.client.call('/CORE/exitConnection', {})
        self.assertEqual(res_xml.get('observer'), 'Core.Acknowledge')

        res_xml = self.client.call('/CORE/menu', {})
        self.assertEqual(res_xml.get('observer'), 'CORE.Auth')
        self.assertEqual(res_xml.text, 'NEEDAUTH')
