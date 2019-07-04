# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
'''
Unit test for simple actions in Lucterios

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
from datetime import datetime
from time import sleep

from django.utils import six
from django.utils.translation import activate
from django.conf import settings

from lucterios.framework.test import LucteriosTest, AsychronousLucteriosTest
from lucterios.CORE.parameters import Params
from lucterios.CORE.views_usergroup import SessionList
from lucterios.framework.tools import format_to_string, set_locale_lang


class DummyTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        set_locale_lang('fr')
        activate(settings.LANGUAGE_CODE)

    def tearDown(self):
        set_locale_lang('fr')
        activate(settings.LANGUAGE_CODE)
        LucteriosTest.tearDown(self)

    def test_bidule1(self):
        self.calljson('/lucterios.dummy/bidule', {})
        self.assert_observer('core.exception', 'lucterios.dummy', 'bidule')
        self.assert_json_equal('', 'message', 'Error of bidule')
        self.assert_json_equal('', 'code', '2')
        self.assert_json_equal('', 'debug', ' in fillresponse : raise LucteriosException(GRAVE, "Error of bidule")', (-76, -7))
        self.assert_json_equal('', 'type', 'LucteriosException')

    def test_bidule2(self):
        self.calljson('/lucterios.dummy/bidule', {'error': 'big'})
        self.assert_observer('core.exception', 'lucterios.dummy', 'bidule')
        self.assert_json_equal('', 'message', 'Other error:big')
        self.assert_json_equal('', 'code', '0')
        self.assert_json_equal('', 'debug', ' in fillresponse : raise AttributeError("Other error:" + error)', (-70, -7))
        self.assert_json_equal('', 'type', 'AttributeError')

    def test_truc(self):
        self.calljson('/lucterios.dummy/truc', {})
        self.assert_observer('core.dialogbox', 'lucterios.dummy', 'truc')
        self.assertEqual(len(self.json_context), 0)
        self.assert_json_equal('', 'type', '1')
        self.assert_json_equal('', 'text', 'Hello world (None,4)!')
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal(self.json_actions[0], ('Ok', 'images/ok.png'))

    def test_multi(self):
        self.calljson('/lucterios.dummy/multi', {})
        self.assert_observer('core.dialogbox', 'lucterios.dummy', 'multi')
        self.assert_json_equal('', 'type', '2')
        self.assert_json_equal('', 'text', 'Do you want?')

        self.calljson('/lucterios.dummy/multi', {'CONFIRME': 'YES'})
        self.assert_observer('core.custom', 'lucterios.dummy', 'multi')
        self.assert_json_equal('LABELFORM', "info", '{[br/]}{[center]}Waiting...{[/center]}')

        self.calljson('/lucterios.dummy/multi', {'CONFIRME': 'YES', 'RELOAD': 'YES'})
        self.assert_observer('core.custom', 'lucterios.dummy', 'multi')
        self.assert_json_equal('LABELFORM', "info", '{[br/]}{[center]}Done!{[/center]}')

    def test_testcomposants(self):

        self.calljson('/lucterios.dummy/testComposants', {})
        self.assert_observer('core.custom', 'lucterios.dummy', 'testComposants')
        self.assert_count_equal('', 24)
        self.assert_json_equal('LABELFORM', "Lbl2", 'editor=aaa')
        self.assert_json_equal('LABELFORM', "Lbl3", 'Real=3.1399999')
        self.assert_json_equal('LABELFORM', "Lbl4", 'Memo=xyz')
        self.assert_json_equal('LABELFORM', "Lbl5", 'Date=2007-04-23')
        self.assert_json_equal('LABELFORM', "Lbl6", 'Hour=12:34:00')
        self.assert_json_equal('LABELFORM', "Lbl7", 'Date Hour=2008-07-12 23:47:31')
        self.assert_json_equal('LABELFORM', "Lbl8", 'Coche=False')
        self.assert_json_equal('LABELFORM', "Lbl9", 'Select=1')
        self.assert_json_equal('LABELFORM', "Lbl10", 'Integer=5')
        self.assert_json_equal('LABELFORM', "Lbl11", "CheckList=['1', '2']")
        self.assert_json_equal('LABELFORM', "Lbl12", "CheckList 2=['b', 'd', 'f']")
        self.assert_json_equal('LABELFORM', "Lbl13", 'Bouton')

        self.assert_json_equal('EDIT', "edt1", 'aaa')
        self.assert_json_equal('FLOAT', "flt1", '3.14')
        self.assert_attrib_equal("flt1", 'min', '0.0')
        self.assert_attrib_equal("flt1", 'max', '10000.0')
        self.assert_attrib_equal("flt1", 'prec', '2')
        self.assert_json_equal('MEMO', "mm1", 'xyz')
        self.assert_attrib_equal("mm1", 'with_hypertext', 'False')
        self.assert_attrib_equal("mm1", 'VMin', '50')
        self.assert_attrib_equal("mm1", 'HMin', '200')
        self.assert_json_equal('DATE', "dt1", '2007-04-23')
        self.assert_json_equal('TIME', "tm1", '12:34:00')
        self.assert_json_equal('DATETIME', "stm1", '2008-07-12 23:47:31')
        self.assert_json_equal('CHECK', "ck1", '0')
        self.assert_json_equal('SELECT', "slct1", '1')
        self.assert_select_equal('slct1', {'1': 'abc', '2': 'def', '3': 'ghij'})
        self.assert_json_equal('FLOAT', "flt2", '5')
        self.assert_attrib_equal("flt2", 'min', '0.0')
        self.assert_attrib_equal("flt2", 'max', '100.0')
        self.assert_attrib_equal("flt2", 'prec', '0')
        self.assert_attrib_equal("cl1", 'simple', '0')
        self.assert_select_equal('cl1', {'1': 'abc', '2': 'def', '3': 'ghij', '4': 'klmn'}, ['1', '2'])

        for (tag, name) in [('EDIT', 'edt1'), ('FLOAT', 'flt1'), ('MEMO', 'mm1'), ('DATE', 'dt1'),
                            ('TIME', 'tm1'), ('DATETIME',
                                              'stm1'), ('CHECK', 'ck1'), ('SELECT', 'slct1'),
                            ('FLOAT', 'flt2'), ('CHECKLIST', 'cl1')]:
            self.assertEqual(self.json_comp[name]['component'], tag)
            act = self.json_comp[name]['action']
            self.assert_action_equal(act, ('Modify', None, 'lucterios.dummy', 'testComposants', '0', '2', '1'))

    def test_testcomposants_again(self):

        self.calljson('/lucterios.dummy/testComposants', {'edt1': 'bbb', 'flt1': '7.896666', 'mm1': 'qwerty', 'dt1': '2015-02-22', 'tm1': '21:05:00',
                                                          'ck1': 'o', 'slct1': '2', 'flt2': '27', 'cl1': '2;4', 'stm1': '2015-03-30 10:00:00'})
        self.assert_observer('core.custom', 'lucterios.dummy', 'testComposants')
        self.assert_count_equal('', 24)

        self.assert_json_equal('EDIT', "edt1", 'bbb')
        self.assert_json_equal('FLOAT', "flt1", '7.90')
        self.assert_json_equal('MEMO', "mm1", 'qwerty')
        self.assertEqual(self.json_comp['mm1']['submenu'], [['Première valeur', 'VALUE_1'], ['Deuxième valeur', 'VALUE_2'], ['Troisième valeur', 'VALUE_3']])
        self.assert_json_equal('DATE', "dt1", '2015-02-22')
        self.assert_json_equal('TIME', "tm1", '21:05:00')
        self.assert_json_equal('DATETIME', "stm1", '2015-03-30 10:00:00')
        self.assert_json_equal('CHECK', "ck1", '1')
        self.assert_json_equal('SELECT', "slct1", '2')
        self.assert_json_equal('FLOAT', "flt2", '27')
        self.assert_select_equal('cl1', {'1': 'abc', '2': 'def', '3': 'ghij', '4': 'klmn'}, ['2', '4'])

    def test_simplegrid(self):
        self.calljson('/lucterios.dummy/simpleGrid', {})
        self.assert_observer('core.custom', 'lucterios.dummy', 'simpleGrid')
        self.assert_count_equal('', 1)
        self.assert_grid_equal("grid", {'col1': 'Integer', 'col2': 'Float', "col3": 'Boolean', "col4": 'String'}, 2)
        self.assert_json_equal("", "grid/@0/col1", 2500)
        self.assert_json_equal("", "grid/@0/col2", 7.54)
        self.assert_json_equal("", "grid/@0/col3", True)
        self.assert_json_equal("", "grid/@0/col4", 'foo')
        self.assert_json_equal("", "grid/@1/col1", 4)
        self.assert_json_equal("", "grid/@1/col2", 789.644)
        self.assert_json_equal("", "grid/@1/col3", False)
        self.assert_json_equal("", "grid/@1/col4", 'string')

    def test_formating_fr(self):
        set_locale_lang('fr')
        activate('fr')
        self.assertEqual(format_to_string(None, None, None), "---", "check None")
        self.assertEqual(format_to_string("abc", None, None), "abc", "check string simple")
        self.assertEqual(format_to_string("abc", None, "{[i]}{[b]}%s{[/b]}{[/i]}"), "{[i]}{[b]}abc{[/b]}{[/i]}", "check string formated")

        self.assertEqual(format_to_string(1234.56, None, "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[i]}1234.56{[/i]}", "check num positive")
        self.assertEqual(format_to_string(-1234.56, None, "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[b]}1234.56{[/b]}", "check num negative")

        self.assertEqual(format_to_string(1234.56, "N3", "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[i]}1 234,560{[/i]}", "check num positive formated")
        self.assertEqual(format_to_string(-1234.56, "N3", "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[b]}1 234,560{[/b]}", "check num negative formated")
        self.assertEqual(format_to_string(1234.56, "N0", "%s"), "1 235", "check int no-formated")

        self.assertEqual(format_to_string(1234.56, "N3", "%s"), "1 234,560", "check num positive no-formated")
        self.assertEqual(format_to_string(-1234.56, "N3", "%s"), "-1 234,560", "check num negative no-formated")
        self.assertEqual(format_to_string(1234.56, "C2EUR", "%s"), "1 234,56 €", "check currency no-formated")

        self.assertEqual(format_to_string("2017-04-23", "D", "%s"), "23 avr. 2017", "check date")
        self.assertEqual(format_to_string("12:54:25.014", "T", "%s"), "12:54", "check time")
        self.assertEqual(format_to_string("2017-04-23T12:54:25.014", "H", "%s"), "dimanche 23 avril 2017 à 12:54", "check date time")

        self.assertEqual(format_to_string(True, "B", "%s"), "Oui", "check bool true")
        self.assertEqual(format_to_string(False, "B", "%s"), "Non", "check bool false")

        self.assertEqual(format_to_string(0, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "aaa", "check select 0")
        self.assertEqual(format_to_string(1, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "bbb", "check select 1")
        self.assertEqual(format_to_string(2, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "ccc", "check select 2")
        self.assertEqual(format_to_string(3, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "3", "check select 3")

    def test_formating_en(self):
        set_locale_lang('en')
        activate('en')
        self.assertEqual(format_to_string(None, None, None), "---", "check None")
        self.assertEqual(format_to_string("abc", None, None), "abc", "check string simple")
        self.assertEqual(format_to_string("abc", None, "{[i]}{[b]}%s{[/b]}{[/i]}"), "{[i]}{[b]}abc{[/b]}{[/i]}", "check string formated")

        self.assertEqual(format_to_string(1234.56, None, "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[i]}1234.56{[/i]}", "check num positive")
        self.assertEqual(format_to_string(-1234.56, None, "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[b]}1234.56{[/b]}", "check num negative")

        self.assertEqual(format_to_string(1234.56, "N3", "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[i]}1,234.560{[/i]}", "check num positive formated")
        self.assertEqual(format_to_string(-1234.56, "N3", "{[i]}%s{[/i]};{[b]}%s{[/b]}"), "{[b]}1,234.560{[/b]}", "check num negative formated")
        self.assertEqual(format_to_string(1234.56, "N0", "%s"), "1,235", "check int no-formated")

        self.assertEqual(format_to_string(1234.56, "N3", "%s"), "1,234.560", "check num positive no-formated")
        self.assertEqual(format_to_string(-1234.56, "N3", "%s"), "-1,234.560", "check num negative no-formated")
        self.assertEqual(format_to_string(1234.56, "C2USD", "%s"), "1,234.56 $US", "check currency no-formated")

        self.assertEqual(format_to_string("2017-04-23", "D", "%s"), "Apr 23, 2017", "check date")
        self.assertEqual(format_to_string("12:54:25.014", "T", "%s"), "12:54", "check time")
        self.assertEqual(format_to_string("2017-04-23T12:54:25.014", "H", "%s"), "Sunday, April 23, 2017 at 12:54", "check date time")

        self.assertEqual(format_to_string(True, "B", "%s"), "Yes", "check bool true")
        self.assertEqual(format_to_string(False, "B", "%s"), "No", "check bool false")

        self.assertEqual(format_to_string(0, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "aaa", "check select 0")
        self.assertEqual(format_to_string(1, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "bbb", "check select 1")
        self.assertEqual(format_to_string(2, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "ccc", "check select 2")
        self.assertEqual(format_to_string(3, {'0': 'aaa', '1': 'bbb', '2': 'ccc'}, "%s"), "3", "check select 3")


class DummyTestAsynchronous(AsychronousLucteriosTest):

    def test_scheduler(self):
        six.print_('-- Begin test_scheduler --')
        self.factory.xfer = SessionList()
        self.calljson('/CORE/sessionList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assert_grid_equal('tasks', {"name": "nom", "trigger": "déclencheur", "nextdate": "date suivante"}, 0)

        self.calljson('/lucterios.dummy/addSchedulerTask', {})
        self.assert_observer('core.acknowledge', 'lucterios.dummy', 'addSchedulerTask')

        value = Params.getvalue('dummy-value')
        self.assertEqual(value, "")

        self.factory.xfer = SessionList()
        self.calljson('/CORE/sessionList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assert_count_equal('tasks', 1)
        self.assert_json_equal('', 'tasks/@0/name', 'Run simple action')
        self.assert_json_equal('', 'tasks/@0/trigger', 'interval[0:00:10]')
        self.assert_json_equal('', 'tasks/@0/nextdate', datetime.now().strftime('%Y-%m-%dT%H:'), True)

        sleep(6 * 10 + .2)
        value = Params.getvalue('dummy-value')
        self.assertEqual(len(value.split('{[br/]}')), 5)

        self.factory.xfer = SessionList()
        self.calljson('/CORE/sessionList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assert_count_equal('tasks', 1)
        self.assert_json_equal('', 'tasks/@0/name', 'Run simple action')
        self.assert_json_equal('', 'tasks/@0/trigger', 'date[' + datetime.now().strftime('%Y-%m-%d %H:'), True)
        self.assert_json_equal('', 'tasks/@0/nextdate', datetime.now().strftime('%Y-%m-%dT%H:'), True)

        sleep(10 + .2)
        value = Params.getvalue('dummy-value')
        self.assertEqual(value, "")

        self.factory.xfer = SessionList()
        self.calljson('/CORE/sessionList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'sessionList')
        self.assert_count_equal('tasks', 0)

        six.print_('-- End test_scheduler --')
