# -*- coding: utf-8 -*-
'''
Created on feb. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.test import TestCase, Client, RequestFactory
from django.utils import six
from lxml import etree
from lucterios.framework.middleware import LucteriosErrorMiddleware
from lucterios.CORE.models import LucteriosUser

def add_user(username):
    user = LucteriosUser.objects.create_user(username=username, password=username)
    user.first_name = username
    user.last_name = username.upper()
    user.is_staff = False
    user.is_active = True
    user.save()
    return user

def add_empty_user():
    user = add_user('empty')
    user.last_name = 'NOFULL'
    user.save()
    return user

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
        self.user = LucteriosUser()
        self.user.is_superuser = True
        self.user.is_staff = True
        if xfer_class is not None:
            self.xfer = xfer_class()
        else:
            self.xfer = None

    def call(self, path, data):
        try:
            request = self.post(path, data)
            request.META['HTTP_ACCEPT_LANGUAGE'] = self.language
            request.user = self.user
            return self.xfer.get(request)
        except Exception as expt:  # pylint: disable=broad-except
            err = LucteriosErrorMiddleware()
            return err.process_exception(request, expt)

class LucteriosTest(TestCase):
    # pylint: disable=too-many-public-methods

    language = 'fr'

    def __init__(self, methodName):
        TestCase.__init__(self, methodName)
        self.xfer_class = None

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

    def print_xml(self, xpath):
        xml_value = self._get_first_xpath(xpath)
        six.print_(etree.tostring(xml_value, xml_declaration=True, pretty_print=True, encoding='utf-8'))

    def assert_count_equal(self, xpath, size):
        xml_values = self.response_xml.xpath(xpath)
        self.assertEqual(len(xml_values), size, "size of %s different: %d=>%d" % (xpath, len(xml_values), size))

    def assert_xml_equal(self, xpath, value, txtrange=None):
        xml_value = self._get_first_xpath(xpath)
        txt_value = xml_value.text
        if isinstance(txtrange, tuple):
            txt_value = txt_value[txtrange[0]:txtrange[1]]
        if isinstance(txtrange, bool):
            txt_value = txt_value[0:len(value)]
        self.assertEqual(txt_value, value, "%s: %s => %s" % (xpath, txt_value, value))

    def assert_attrib_equal(self, xpath, name, value):
        xml_value = self._get_first_xpath(xpath)
        attr_value = xml_value.get(name)
        self.assertEqual(attr_value, value, "%s/@%s: %s => %s" % (xpath, name, attr_value, value))

    def assert_observer(self, obsname, extension, action):
        try:
            self.assert_attrib_equal('', 'observer', obsname)
            self.assert_attrib_equal('', 'source_extension', extension)
            self.assert_attrib_equal('', 'source_action', action)
        except AssertionError:
            if self._get_first_xpath('').get('observer') == 'CORE.Exception':
                six.print_("Error:" + six.text_type(self._get_first_xpath('EXCEPTION/MESSAGE').text))
                six.print_("Call-stack:" + six.text_type(self._get_first_xpath('EXCEPTION/DEBUG_INFO').text).replace("{[br/]}", "\n"))
            if self._get_first_xpath('').get('observer') == 'Core.DialogBox':
                six.print_("Message:" + six.text_type(self._get_first_xpath('TEXT').text))
            raise

    def assert_comp_equal(self, xpath, text, coord):
        self.assert_xml_equal(xpath, text)
        self.assert_coordcomp_equal(xpath, coord)

    def assert_coordcomp_equal(self, xpath, coord):
        self.assert_attrib_equal(xpath, "x", six.text_type(coord[0]))
        self.assert_attrib_equal(xpath, "y", six.text_type(coord[1]))
        self.assert_attrib_equal(xpath, "colspan", six.text_type(coord[2]))
        self.assert_attrib_equal(xpath, "rowspan", six.text_type(coord[3]))
        if len(coord) > 4:
            self.assert_attrib_equal(xpath, "tab", six.text_type(coord[4]))

    def assert_action_equal(self, xpath, act_desc):
        self.assert_xml_equal(xpath, act_desc[0])
        self.assert_attrib_equal(xpath, "icon", act_desc[1])
        if len(act_desc) > 2:
            self.assert_attrib_equal(xpath, "extension", act_desc[2])
            self.assert_attrib_equal(xpath, "action", act_desc[3])
            self.assert_attrib_equal(xpath, "close", six.text_type(act_desc[4]))
            self.assert_attrib_equal(xpath, "modal", six.text_type(act_desc[5]))
            self.assert_attrib_equal(xpath, "unique", six.text_type(act_desc[6]))
            if len(act_desc) > 7:
                for key, value in act_desc[7].items():
                    self.assert_xml_equal("%s/PARAM[@name='%s']" % (xpath, key), value)
        else:
            self.assert_attrib_equal(xpath, "extension", None)
            self.assert_attrib_equal(xpath, "action", None)
            self.assert_attrib_equal(xpath, "close", six.text_type(1))
            self.assert_attrib_equal(xpath, "modal", six.text_type(1))
            self.assert_attrib_equal(xpath, "unique", six.text_type(1))
