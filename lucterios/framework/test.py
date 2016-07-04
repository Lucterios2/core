# -*- coding: utf-8 -*-
'''
Unit test tools for Lucterios

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
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from lxml import etree

from django.test import TestCase, Client, RequestFactory
from django.utils import six, timezone

from lucterios.framework.middleware import LucteriosErrorMiddleware
from lucterios.CORE.models import LucteriosUser
from lucterios.CORE.parameters import notfree_mode_connect, Params


def add_user(username):
    user = LucteriosUser.objects.create_user(
        username=username, password=username, last_login=timezone.now())
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

    def create_request(self, path, data):
        request = self.post(path, data)
        request.META['HTTP_ACCEPT_LANGUAGE'] = self.language
        request.user = self.user
        return request

    def call(self, path, data):
        request = None
        try:
            request = self.create_request(path, data)
            return self.xfer.get(request)
        except Exception as expt:
            if request is None:
                request = self.post(path, {})
            err = LucteriosErrorMiddleware()
            return err.process_exception(request, expt)


class LucteriosTest(TestCase):

    language = 'fr'

    def __init__(self, methodName):
        TestCase.__init__(self, methodName)
        self.xfer_class = None

    def setUp(self):
        self.factory = XmlRequestFactory(self.xfer_class, self.language)
        self.client = XmlClient(self.language)
        self.response_xml = None
        Params.clear()
        notfree_mode_connect()

    def parse_xml(self, xml, root_tag='REPONSE', first_child=True):
        contentxml = etree.fromstring(xml)
        if first_child:
            root = contentxml.getchildren()[0]
        else:
            root = contentxml
        self.assertEqual(root.tag, root_tag, "NOT %s" % root_tag)
        self.response_xml = root

    def call(self, path, data, is_client=True):
        if is_client:
            response = self.client.call(path, data)
        else:
            response = self.factory.call(path, data)
        self.assertEqual(
            response.status_code, 200, "HTTP error:" + str(response.status_code))
        self.parse_xml(response.content)

    def get_first_xpath(self, xpath):
        if xpath == '':
            return self.response_xml
        else:
            xml_values = self.response_xml.xpath(xpath)
            self.assertEqual(len(xml_values), 1, "%s not unique" % xpath)
            return xml_values[0]

    def print_xml(self, xpath):
        xml_value = self.get_first_xpath(xpath)
        six.print_(etree.tostring(
            xml_value, xml_declaration=True, pretty_print=True, encoding='utf-8').decode("utf-8"))

    def assert_count_equal(self, xpath, size):
        xml_values = self.response_xml.xpath(xpath)
        self.assertEqual(len(xml_values), size, "size of %s different: %d=>%d" % (
            xpath, len(xml_values), size))

    def assert_xml_equal(self, xpath, value, txtrange=None):
        xml_value = self.get_first_xpath(xpath)
        txt_value = xml_value.text
        if isinstance(txtrange, tuple):
            txt_value = txt_value[txtrange[0]:txtrange[1]]
        if isinstance(txtrange, bool):
            txt_value = txt_value[0:len(value)]
        self.assertEqual(txt_value, value, "%s: %s => %s" %
                         (xpath, txt_value, value))

    def assert_attrib_equal(self, xpath, name, value):
        xml_value = self.get_first_xpath(xpath)
        attr_value = xml_value.get(name)
        self.assertEqual(attr_value, value, "%s/@%s: %s => %s" %
                         (xpath, name, attr_value, value))

    def assert_observer(self, obsname, extension, action):
        try:
            self.assert_attrib_equal('', 'observer', obsname)
            self.assert_attrib_equal('', 'source_extension', extension)
            self.assert_attrib_equal('', 'source_action', action)
        except AssertionError:
            if self.get_first_xpath('').get('observer') == 'core.exception':
                six.print_(
                    "Error:" + six.text_type(self.get_first_xpath('EXCEPTION/MESSAGE').text))
                six.print_("Call-stack:" + six.text_type(
                    self.get_first_xpath('EXCEPTION/DEBUG_INFO').text).replace("{[br/]}", "\n"))
            if self.get_first_xpath('').get('observer') == 'core.dialogbox':
                six.print_(
                    "Message:" + six.text_type(self.get_first_xpath('TEXT').text))
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
        if act_desc[1] is None:
            self.assert_attrib_equal(xpath, "icon", None)
        elif act_desc[1].startswith('images/'):
            self.assert_attrib_equal(
                xpath, "icon", '/static/lucterios.CORE/' + act_desc[1])
        else:
            self.assert_attrib_equal(xpath, "icon", '/static/' + act_desc[1])
        if len(act_desc) > 2:
            self.assert_attrib_equal(xpath, "extension", act_desc[2])
            self.assert_attrib_equal(xpath, "action", act_desc[3])
            self.assert_attrib_equal(
                xpath, "close", six.text_type(act_desc[4]))
            self.assert_attrib_equal(
                xpath, "modal", six.text_type(act_desc[5]))
            self.assert_attrib_equal(
                xpath, "unique", six.text_type(act_desc[6]))
            if len(act_desc) > 7:
                for key, value in act_desc[7].items():
                    self.assert_xml_equal(
                        "%s/PARAM[@name='%s']" % (xpath, key), value)
        else:
            self.assert_attrib_equal(xpath, "extension", None)
            self.assert_attrib_equal(xpath, "action", None)
            self.assert_attrib_equal(xpath, "close", six.text_type(1))
            self.assert_attrib_equal(xpath, "modal", six.text_type(1))
            self.assert_attrib_equal(xpath, "unique", six.text_type(1))
