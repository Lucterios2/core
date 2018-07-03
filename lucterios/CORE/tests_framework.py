# -*- coding: utf-8 -*-
'''
Unit test class for Lucterios framework

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

from django.utils import six

from lucterios.framework.test import LucteriosTest
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XFER_DBOX_WARNING, XferContainerCustom
from lucterios.framework.tools import WrapAction

from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamSave


class GenericTest(LucteriosTest):

    def __init__(self, methodName):
        LucteriosTest.__init__(self, methodName)
        self.xfer = None

    def setUp(self):
        self.xfer_class.url_text = "customer/details"
        self.xfer_class.is_view_right = ''
        LucteriosTest.setUp(self)
        self.value = False
        self.xfer = XferContainerCustom()
        Params.clear()

    def callparam(self):
        self.factory.xfer = self.xfer
        self.calljson("/", {}, False)

    def test_help(self):
        response = self.client.get('/Docs', {})
        self.assertEqual(response.status_code, 200, "HTTP error:" + six.text_type(response.status_code))
        help_content = six.text_type(response.content.decode('utf-8'))
        self.assertGreaterEqual(help_content.find('<html>'), 17, help_content)
        self.assertLessEqual(help_content.find('<html>'), 21, help_content)

    def test_simple(self):
        self.calljson('/customer/details', {'id': 12, 'value': 'abc'}, False)
        self.assert_observer('core.acknowledge', 'customer', 'details')
        self.assertEqual(len(self.json_context), 2)
        self.assertEqual(self.json_context['id'], '12')
        self.assertEqual(self.json_context['value'], 'abc')
        self.assertEqual(self.response_json['close'], None)

    def test_close(self):
        def fillresponse_close():
            self.factory.xfer.set_close_action(
                WrapAction("close", "", "customer", "list"))
        self.factory.xfer.fillresponse = fillresponse_close
        self.calljson('/customer/details', {}, False)
        self.assert_observer('core.acknowledge', 'customer', 'details')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 0)
        self.assertTrue('close' in self.response_json.keys())
        self.assert_action_equal(self.response_json['close'], ("close", None, "customer", "list", 1, 1, 1))

    def test_redirect(self):
        def fillresponse_redirect():
            self.factory.xfer.redirect_action(WrapAction("redirect", "", "customer", "list"))
        self.factory.xfer.fillresponse = fillresponse_redirect
        self.calljson('/customer/details', {}, False)
        self.assert_observer('core.acknowledge', 'customer', 'details')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 0)
        self.assertTrue('action' in self.response_json.keys())
        self.assert_action_equal(self.response_json['action'], ("redirect", None, "customer", "list", 1, 1, 1))

    def test_confirme(self):
        self.value = False

        def fillresponse_confirme():
            if self.factory.xfer.confirme("Do you want?"):
                self.value = True
        self.factory.xfer.fillresponse = fillresponse_confirme
        self.calljson('/customer/details', {}, False)
        self.assertEqual(self.value, False)
        self.assert_observer('core.dialogbox', 'customer', 'details')
        self.assert_json_equal('', 'type', '2')
        self.assert_json_equal('', 'text', 'Do you want?')
        self.assertEqual(len(self.json_actions), 2)
        self.assert_action_equal(self.json_actions[0], ('Oui', 'images/ok.png', 'customer', 'details', 1, 1, 1, {'CONFIRME': "YES"}))
        self.assert_action_equal(self.json_actions[1], ('Non', 'images/cancel.png'))

        self.calljson('/customer/details', {'CONFIRME': 'YES'}, False)
        self.assertEqual(self.value, True)
        self.assertEquals(self.json_meta['observer'], 'core.acknowledge')

    def test_message(self):
        def fillresponse_message():
            self.factory.xfer.message("Finished!", XFER_DBOX_WARNING)
        self.factory.xfer.fillresponse = fillresponse_message
        self.calljson('/customer/details', {}, False)
        self.assert_observer('core.dialogbox', 'customer', 'details')
        self.assert_json_equal('', 'type', '3')
        self.assert_json_equal('', 'text', 'Finished!')
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal(self.json_actions[0], ('Ok', 'images/ok.png'))

    def test_traitment(self):
        self.value = False

        def fillresponse_traitment():
            if self.factory.xfer.traitment("customer/images/foo.png", "Traitment{[br/]}Wait...", "Done"):
                self.value = True
        self.factory.xfer.fillresponse = fillresponse_traitment
        self.calljson('/customer/details', {}, False)
        self.assertEqual(self.value, False)
        self.assert_observer('core.custom', 'customer', 'details')
        self.assertEqual(len(self.json_context), 1)
        self.assertEqual(self.json_context['RELOAD'], 'YES')
        self.assert_count_equal('', 3)
        self.assert_json_equal('LABELFORM', "info", '{[br/]}{[center]}Traitment{[br/]}Wait...{[/center]}')
        self.assert_json_equal('IMAGE', "img_title", 'customer/images/foo.png')
        self.assert_action_equal(self.json_comp['Next']['action'], ('Traitement...', None, 'customer', 'details', 1, 1, 1, {'RELOAD': "YES"}))
        self.assert_attrib_equal('Next', 'javascript', 'parent.refresh()')
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal(self.json_actions[0], ('Annuler', 'images/cancel.png'))

        self.calljson('/customer/details', {'RELOAD': 'YES'}, False)
        self.assertEqual(self.value, True)
        self.assert_observer('core.custom', 'customer', 'details')
        self.assertEqual(len(self.json_context), 1)
        self.assertEqual(self.json_context['RELOAD'], 'YES')
        self.assert_count_equal('', 2)
        self.assert_json_equal('IMAGE', "img_title", 'customer/images/foo.png')
        self.assert_json_equal('LABELFORM', "info", '{[br/]}{[center]}Done{[/center]}')
        self.assert_action_equal(self.json_actions[0], ('Fermer', 'images/close.png'))

    def test_parameters_text(self):
        param = Parameter.objects.create(name='param_text', typeparam=0)
        param.args = "{'Multi':False}"
        param.value = 'my value'
        param.save()

        Params.fill(self.xfer, ['param_text'], 1, 1, True)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('LABELFORM', "param_text", 'my value')

        Params.fill(self.xfer, ['param_text'], 1, 1, False)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('EDIT', "param_text", 'my value')

        self.factory.xfer = ParamSave()
        self.calljson('/CORE/paramSave', {'params': 'param_text', 'param_text': 'new value'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')
        self.assertEqual(Params.getvalue('param_text'), 'new value')

    def test_parameters_memo(self):
        param = Parameter.objects.create(name='param_memo', typeparam=0)
        param.args = "{'Multi':True}"
        param.value = 'other value'
        param.save()

        Params.fill(self.xfer, ['param_memo'], 1, 1, True)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('LABELFORM', "param_memo", 'other value')

        Params.fill(self.xfer, ['param_memo'], 1, 1, False)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('MEMO', "param_memo", 'other value')

        self.factory.xfer = ParamSave()
        self.calljson('/CORE/paramSave', {'params': 'param_memo', 'param_memo': 'new special value'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')
        self.assertEqual(Params.getvalue('param_memo'), 'new special value')

    def test_parameters_int(self):
        param = Parameter.objects.create(name='param_int', typeparam=1)
        param.args = "{'Min':5, 'Max':25}"
        param.value = '5'
        param.save()

        Params.fill(self.xfer, ['param_int'], 1, 1, True)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('LABELFORM', "param_int", '5')

        Params.fill(self.xfer, ['param_int'], 1, 1, False)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('FLOAT', "param_int", '5')
        self.assert_attrib_equal("param_int", 'min', '5.0')
        self.assert_attrib_equal("param_int", 'max', '25.0')
        self.assert_attrib_equal("param_int", 'prec', '0')

        self.factory.xfer = ParamSave()
        self.calljson('/CORE/paramSave', {'params': 'param_int', 'param_int': '13'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')
        self.assertEqual(Params.getvalue('param_int'), 13)

    def test_parameters_float(self):
        param = Parameter.objects.create(name='param_float', typeparam=2)
        param.args = "{'Min':20, 'Max':30, 'Prec':2}"
        param.value = '22.25'
        param.save()

        Params.fill(self.xfer, ['param_float'], 1, 1, True)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('LABELFORM', "param_float", '22.25')

        Params.fill(self.xfer, ['param_float'], 1, 1, False)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('FLOAT', "param_float", '22.25')
        self.assert_attrib_equal("param_float", 'min', '20.0')
        self.assert_attrib_equal("param_float", 'max', '30.0')
        self.assert_attrib_equal("param_float", 'prec', '2')

        self.factory.xfer = ParamSave()
        self.calljson('/CORE/paramSave', {'params': 'param_float', 'param_float': '26.87'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')
        self.assertEqual(Params.getvalue('param_float'), 26.87)

    def test_parameters_bool(self):
        param = Parameter.objects.create(name='param_bool', typeparam=3)
        param.args = "{}"
        param.value = 'False'
        param.save()

        Params.fill(self.xfer, ['param_bool'], 1, 1, True)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('LABELFORM', "param_bool", 'Non')

        Params.fill(self.xfer, ['param_bool'], 1, 1, False)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('CHECK', "param_bool", '0')

        self.factory.xfer = ParamSave()
        self.calljson('/CORE/paramSave', {'params': 'param_bool', 'param_bool': '1'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')
        self.assertEqual(Params.getvalue('param_bool'), True)

    def test_parameters_select(self):
        param = Parameter.objects.create(name='param_select', typeparam=4)
        param.args = "{'Enum':4}"
        param.value = '2'
        param.save()

        Params.fill(self.xfer, ['param_select'], 1, 1, True)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('LABELFORM', "param_select", 'param_select.2')

        Params.fill(self.xfer, ['param_select'], 1, 1, False)
        self.callparam()
        self.assert_count_equal('', 1)
        self.assert_json_equal('SELECT', "param_select", '2')
        self.assert_select_equal("param_select", {0: 'param_select.0', 1: 'param_select.1', 2: 'param_select.2', 3: 'param_select.3'})

        self.factory.xfer = ParamSave()
        self.calljson('/CORE/paramSave', {'params': 'param_select', 'param_select': '1'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'paramSave')
        self.assertEqual(Params.getvalue('param_select'), 1)
