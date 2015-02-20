# -*- coding: utf-8 -*-
'''
Created on feb. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, Client, RequestFactory
from lxml import etree

def check(condition, msg):
    if not condition:
        raise AssertionError(msg)

def add_admin_user():
    from django.contrib.auth.models import User
    user = User.objects.create_user(username='admin', password='admin')
    user.first_name = 'administrator'
    user.last_name = 'ADMIN'
    user.is_staff = True
    user.is_active = True
    user.save()

def add_empty_user():
    from django.contrib.auth.models import User
    user = User.objects.create_user(username='empty', password='empty')
    user.first_name = 'empty'
    user.last_name = 'NOFULL'
    user.is_staff = False
    user.is_active = True
    user.save()

class XmlClient(Client):

    def __init__(self, language='fr'):
        Client.__init__(self)
        self.language = language

    def call(self, path, data):
        return self.post(path, data, HTTP_ACCEPT_LANGUAGE=self.language)

class XmlRequestFactory(RequestFactory):

    def __init__(self, xfer_class, language='fr'):
        RequestFactory.__init__(self)
        self.language = language
        if xfer_class is not None:
            self.xfer = xfer_class()
        else:
            self.xfer = None

    def call(self, path, data):
        if self.xfer is not None:
            request = self.post(path, data)
            request.META['HTTP_ACCEPT_LANGUAGE'] = self.language
            request.user = AnonymousUser()
            return self.xfer.get(request)
        else:
            return None

class LucteriosTest(TestCase):
    # pylint: disable=too-many-public-methods

    xfer_class = None
    language = 'fr'

    def setUp(self):
        self.factory = XmlRequestFactory(self.xfer_class, self.language)
        self.client = XmlClient(self.language)
        self.response_xml = None

    def call(self, path, data, is_client=True):
        if is_client:
            response = self.client.call(path, data)
        else:
            response = self.factory.call(path, data)
        self.assertEqual(response.status_code, 200, "HTTP error:" + str(response.status_code))
        contentxml = etree.fromstring(response.content)
        self.assertEqual(contentxml.getchildren()[0].tag, 'REPONSE', "NOT REPONSE")
        self.response_xml = contentxml.getchildren()[0]


    def _get_first_xpath(self, xpath):
        if xpath == '':
            return self.response_xml
        else:
            xml_values = self.response_xml.xpath(xpath)
            self.assertEqual(len(xml_values), 1, "%s not unique" % xpath)
            return xml_values[0]

    def assert_count_equal(self, xpath, size):
        xml_values = self.response_xml.xpath(xpath)
        self.assertEqual(len(xml_values), size, "size of %s different" % xpath)

    def assert_xml_equal(self, xpath, value, txtrange=None):
        xml_value = self._get_first_xpath(xpath)
        txt_value = xml_value.text
        if isinstance(txtrange, tuple):
            txt_value = txt_value[txtrange[0]:txtrange[1]]
        self.assertEqual(txt_value, value, "%s: %s => %s" % (xpath, txt_value, value))

    def assert_attrib_equal(self, xpath, name, value):
        xml_value = self._get_first_xpath(xpath)
        self.assertEqual(xml_value.get(name), value, xpath)
