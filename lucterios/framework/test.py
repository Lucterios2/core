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
from os.path import join, isfile, isdir
from os import makedirs, unlink
from base64 import b64decode
from lxml import etree
from contextlib import closing
from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET

from django.test import TestCase, Client, RequestFactory
from django.test.testcases import TransactionTestCase
from django.utils import six, timezone

from lucterios.framework.middleware import LucteriosErrorMiddleware
from lucterios.framework.xfergraphic import XferContainerAcknowledge
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
            err = LucteriosErrorMiddleware(None)
            return err.process_exception(request, expt)


class LucteriosTestAbstract(object):

    language = 'fr'

    PDF_DIRECTORY = 'pdf'

    def __init__(self):
        self.xfer_class = XferContainerAcknowledge

    def clean_resp(self):
        self.response_xml = None
        self.response_json = None
        self.json_meta = {}
        self.json_data = {}
        self.json_comp = {}
        self.json_context = {}
        self.json_actions = []

    def setUp(self):
        self.factory = XmlRequestFactory(self.xfer_class, self.language)
        self.client = XmlClient(self.language)
        self.response = None
        self.clean_resp()
        Params.clear()
        notfree_mode_connect()
        if not isdir(self.PDF_DIRECTORY):
            makedirs(self.PDF_DIRECTORY)
        for ident in range(10):
            filename = self._get_pdf_filename(ident if ident > 0 else None)
            if isfile(filename):
                unlink(filename)

    def _get_pdf_filename(self, ident):
        filename = join(self.PDF_DIRECTORY, "%s-%s-%s%s.pdf" % (self.__class__.__module__, self.__class__.__name__,
                                                                self._testMethodName,
                                                                "-%03d" % ident if ident is not None else ""))
        return filename

    def save_pdf(self, base64_content=None, ident=None):
        filename = self._get_pdf_filename(ident)
        if isfile(filename):
            unlink(filename)
        if base64_content is None:
            pdf_value = b64decode(six.text_type(self.response_json['print']["content"]))
        else:
            pdf_value = b64decode(six.text_type(base64_content))
        self.assertEqual(pdf_value[:4], "%PDF".encode('ascii', 'ignore'))
        with open(filename, "wb") as pdf_writer:
            pdf_writer.write(pdf_value)

    def parse_xml(self, xml, root_tag='REPONSE', first_child=True):
        contentxml = etree.fromstring(xml)
        if first_child:
            root = contentxml.getchildren()[0]
        else:
            root = contentxml
        self.assertEqual(root.tag, root_tag, "NOT %s" % root_tag)
        self.response_xml = root

    def call_ex(self, path, data, is_client, status_expected=200):
        if is_client:
            self.response = self.client.call(path, data)
        else:
            self.assertEqual('/' + self.factory.xfer.url_text, path)
            self.response = self.factory.call(path, data)
        self.clean_resp()
        self.assertEqual(self.response.status_code, status_expected, "HTTP error:" + str(self.response.status_code))

    def calljson(self, path, data, is_client=True):
        import json
        data['FORMAT'] = 'JSON'
        self.call_ex(path, data, is_client)
        self.response_json = json.loads(self.response.content.decode())
        if 'meta' in self.response_json.keys():
            self.json_meta = self.response_json['meta']
        if 'actions' in self.response_json.keys():
            self.json_actions = self.response_json['actions']
        if 'data' in self.response_json.keys():
            self.json_data = self.response_json['data']
        if 'exception' in self.response_json.keys():
            self.json_data = self.response_json['exception']
        if 'context' in self.response_json.keys():
            self.json_context = self.response_json['context']
        if 'comp' in self.response_json.keys():
            for item_comp in self.response_json['comp']:
                self.json_comp[item_comp['name']] = item_comp

    def get_first_xpath(self, xpath):
        if xpath == '':
            return self.response_xml
        else:
            xml_values = self.response_xml.xpath(xpath)
            self.assertEqual(len(xml_values), 1, "%s not unique" % xpath)
            return xml_values[0]

    def get_json_path(self, path):
        values = self.json_data
        if (len(path) > 0) and (path[0] == '#'):
            path = path[1:]
            values = self.json_comp
        for path_item in path.split('/'):
            if path_item != '':
                if path_item[0] == '@':
                    index = int(path_item[1:])
                    values = values[index]
                else:
                    values = values[path_item]
        return values

    def print_xml(self, xpath):
        self.assertTrue(self.response_xml is not None)
        xml_value = self.get_first_xpath(xpath)
        six.print_(etree.tostring(xml_value, xml_declaration=True, pretty_print=True, encoding='utf-8').decode("utf-8"))

    def print_json(self, path=None):
        from django.core.serializers.json import DjangoJSONEncoder
        import json
        if path is None:
            path = self.response_json
        elif isinstance(path, six.text_type):
            path = self.get_json_path(path)
        six.print_(json.dumps(path, cls=DjangoJSONEncoder, indent=3))

    def assert_count_equal(self, path, size):
        if self.response_json is None:
            self.assertTrue(self.response_xml is not None)
            values = self.response_xml.xpath(path)
        else:
            values = self.get_json_path(path)
        self.assertEqual(len(values), size, "size of %s different: %d=>%d" % (path, len(values), size))

    def assert_json_equal(self, comp_type, comp_name, value, txtrange=None):
        def is_number(text):
            try:
                float(text)
                return True
            except ValueError:
                return False
        self.assertTrue(self.response_json is not None)
        if comp_type != '':
            self.assertEqual(self.json_comp[comp_name]['component'], comp_type)
        txt_value = self.get_json_path(comp_name)
        if isinstance(txtrange, tuple):
            txt_value = txt_value[txtrange[0]:txtrange[1]]
            value = six.text_type(value)[0:len(txt_value)]
        if isinstance(txtrange, bool):
            txt_value = txt_value[0:len(value)]
        if (isinstance(txt_value, float) and is_number(value)) or (isinstance(value, float) and is_number(txt_value)):
            self.assertAlmostEqual(float(txt_value), float(value), msg="%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value), delta=1e-2)
        elif isinstance(txt_value, six.text_type) or isinstance(value, six.text_type):
            self.assertEqual(six.text_type(txt_value), six.text_type(value), "%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value))
        elif isinstance(txt_value, list) and isinstance(value, list):
            self.assertEqual(len(txt_value), len(value), "%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value))
            for idx in range(len(txt_value)):
                txt_value_item = txt_value[idx]
                value_item = value[idx]
                if (isinstance(txt_value_item, float) and is_number(value_item)) or (isinstance(value_item, float) and is_number(txt_value_item)):
                    self.assertAlmostEqual(float(txt_value_item), float(value_item), msg="%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value), delta=1e-2)
                else:
                    self.assertEqual(txt_value_item, value_item, "%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value))
        elif isinstance(txt_value, dict) and isinstance(value, dict):
            self.assertEqual(len(txt_value), len(value), "%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value))
            for idx in txt_value.keys():
                txt_value_item = txt_value[idx]
                value_item = value[idx]
                if (isinstance(txt_value_item, float) and is_number(value_item)) or (isinstance(value_item, float) and is_number(txt_value_item)):
                    self.assertAlmostEqual(float(txt_value_item), float(value_item), msg="%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value), delta=1e-2)
                else:
                    self.assertEqual(txt_value_item, value_item, "%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value))
        else:
            self.assertEqual(txt_value, value, "%s[%s]: %s => %s" % (comp_type, comp_name, txt_value, value))

    def assert_xml_equal(self, xpath, value, txtrange=None):
        self.assertTrue(self.response_xml is not None)
        xml_value = self.get_first_xpath(xpath)
        txt_value = xml_value.text
        if isinstance(txtrange, tuple):
            txt_value = txt_value[txtrange[0]:txtrange[1]]
        if isinstance(txtrange, bool):
            txt_value = txt_value[0:len(value)]
        self.assertEqual(six.text_type(txt_value).strip(), six.text_type(value).strip(), "%s: %s => %s" % (xpath, txt_value, value))

    def assert_attrib_equal(self, path, name, value):
        if self.response_json is None:
            xml_value = self.get_first_xpath(path)
            attr_value = xml_value.get(name)
        else:
            attr_value = self.json_comp[path][name]
        self.assertEqual(six.text_type(attr_value), six.text_type(value), "%s/@%s: %s => %s" % (path, name, attr_value, value))

    def assert_observer(self, obsname, extension, action):
        self.assertTrue(self.response_json is not None)
        self.assertTrue(self.response_xml is None)
        try:
            self.assertEquals(self.json_meta['observer'], obsname, self.response_json['exception']['message'] if self.json_meta['observer'] == 'core.exception' else None)
            self.assertEquals(self.json_meta['extension'], extension)
            self.assertEquals(self.json_meta['action'], action)
        except AssertionError:
            if self.json_meta['observer'] == 'core.exception':
                six.print_("Error:" + self.response_json['exception']['message'])
                six.print_("Call-stack:" + self.response_json['exception']['debug'].replace("{[br/]}", "\n"))
            if self.json_meta['observer'] == 'core.dialogbox':
                six.print_("Message:" + self.json_data['text'])
            raise

    def assert_comp_equal(self, path, text, coord, txtrange=None):
        self.assertTrue(self.response_json is not None)
        self.assert_json_equal(path[0], path[1], text, txtrange)
        path = path[1]
        self.assert_coordcomp_equal(path, coord)

    def assert_coordcomp_equal(self, path, coord):
        self.assert_attrib_equal(path, "x", six.text_type(coord[0]))
        self.assert_attrib_equal(path, "y", six.text_type(coord[1]))
        self.assert_attrib_equal(path, "colspan", six.text_type(coord[2]))
        self.assert_attrib_equal(path, "rowspan", six.text_type(coord[3]))
        if len(coord) > 4:
            self.assert_attrib_equal(path, "tab", six.text_type(coord[4]))

    def assert_action_equal(self, path, act_desc):
        self.assertTrue(self.response_json is not None)
        act = path
        if isinstance(path, six.text_type):
            act = self.get_json_path(path)
        self.assertEqual(act['text'], act_desc[0])
        if act_desc[1] is None:
            self.assertTrue('icon' not in act.keys())
        elif act_desc[1].startswith('images/'):
            self.assertEqual(act['icon'], '/static/lucterios.CORE/' + act_desc[1])
        else:
            self.assertEqual(act['icon'], '/static/' + act_desc[1])
        if len(act_desc) > 2:
            self.assertEqual(act['extension'], act_desc[2])
            self.assertEqual(act['action'], act_desc[3])
            self.assertEqual(act['close'], six.text_type(act_desc[4]))
            self.assertEqual(act['modal'], six.text_type(act_desc[5]))
            self.assertEqual(act['unique'], six.text_type(act_desc[6]))
            if len(act_desc) > 7:
                try:
                    for key, value in act_desc[7].items():
                        self.assertEqual(six.text_type(act['params'][key]), six.text_type(value))
                except Exception:
                    six.print_(six.text_type(act['params']))
                    raise
        else:
            self.assertTrue('extension' not in act.keys())
            self.assertTrue('action' not in act.keys())
            self.assertEqual(path['close'], six.text_type(1))
            self.assertEqual(path['modal'], six.text_type(1))
            self.assertEqual(path['unique'], six.text_type(1))

    def assert_select_equal(self, path, selects, checked=None):
        if checked is None:
            tag = 'SELECT'
        else:
            tag = 'CHECKLIST'
        self.assertTrue(self.response_json is not None)
        self.assertTrue(self.response_xml is None)
        self.assertEqual(self.json_comp[path]['component'], tag)
        if isinstance(selects, dict):
            self.assertEqual(len(self.json_comp[path]['case']), len(selects))
            try:
                for case in self.json_comp[path]['case']:
                    vid = case[0]
                    self.assertEqual(selects[vid], case[1])
            except Exception:
                six.print_(self.json_comp[path]['case'])
                raise
        else:
            self.assertEqual(len(self.json_comp[path]['case']), selects)

    def assert_grid_equal(self, path, headers, nb_records):
        import json
        self.assertTrue(self.response_json is not None)
        self.assertTrue(self.response_xml is None)
        self.assertEqual(self.json_comp[path]['component'], 'GRID')
        self.assertEqual(len(self.json_comp[path]['headers']), len(headers), json.dumps(self.json_comp[path]['headers']))
        for header in self.json_comp[path]['headers']:
            header_name = header[0]
            self.assertEqual(headers[header_name], header[1])
        self.assert_count_equal(path, nb_records)


class AsychronousLucteriosTest(TransactionTestCase, LucteriosTestAbstract):

    def __init__(self, methodName):
        TransactionTestCase.__init__(self, methodName)
        LucteriosTestAbstract.__init__(self)

    def setUp(self):
        LucteriosTestAbstract.setUp(self)


class LucteriosTest(TestCase, LucteriosTestAbstract):

    def __init__(self, methodName):
        TestCase.__init__(self, methodName)
        LucteriosTestAbstract.__init__(self)

    def setUp(self):
        LucteriosTestAbstract.setUp(self)


def find_free_port():
    with closing(socket(AF_INET, SOCK_STREAM)) as sock:
        sock.bind(('', 0))
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        return sock.getsockname()[1]
