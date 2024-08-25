# -*- coding: utf-8 -*-
'''
Views for dummy module

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
from datetime import datetime, timedelta

from django.utils.translation import gettext_lazy as _

from lucterios.framework.tools import MenuManage, WrapAction, ActionsManage, SELECT_SINGLE, SELECT_MULTI,\
    SELECT_NONE
from lucterios.framework.tools import FORMTYPE_NOMODAL, FORMTYPE_REFRESH, FORMTYPE_MODAL, CLOSE_NO, CLOSE_YES
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XFER_DBOX_INFORMATION, XferContainerCustom
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompEdit, XferCompFloat, XferCompMemo, XferCompDate, XferCompGrid, XferCompStep,\
    XferCompImage, XferCompMosaic
from lucterios.framework.xfercomponents import XferCompTime, XferCompDateTime, XferCompCheck, XferCompSelect, XferCompCheckList, XferCompButton
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferShowEditor, XferDelete, \
    TITLE_EDIT, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE, TITLE_PRINT, \
    TITLE_LISTING, TITLE_LABEL, TITLE_CLOSE
from lucterios.framework import signal_and_lock
from lucterios.framework.model_fields import LucteriosScheduler

from lucterios.CORE.xferprint import XferPrintAction, XferPrintListing, XferPrintLabel, XferPrintReporting
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor
from lucterios.CORE.parameters import Params
from lucterios.CORE.models import Parameter, Preference

from lucterios.dummy.models import Example, Other
from lucterios.CORE.views import ObjectImport

MenuManage.add_sub('dummy.foo', None, short_icon='mdi:mdi-numeric-10', caption=_('Dummy'), desc=_('Dummy menu'), pos=20)


@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Bidule action."))
class Bidule(XferContainerAcknowledge):
    caption = _("_Bidule")
    short_icon = 'mdi:mdi-numeric-1'

    def fillresponse(self, error):
        from lucterios.framework.error import LucteriosException, GRAVE
        if error is None:
            raise LucteriosException(GRAVE, "Error of bidule")
        else:
            raise AttributeError("Other error:" + error)


@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Truc action."))
class Truc(XferContainerAcknowledge):
    caption = _("_Truc")
    short_icon = 'mdi:mdi-numeric-2'

    def fillresponse(self, val1, val2=4):
        self.message("Hello world (%s,%s)!" % (str(val1), str(val2)), XFER_DBOX_INFORMATION)


@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Multi action."))
class Multi(XferContainerAcknowledge):
    caption = _("_Multi")
    short_icon = 'mdi:mdi-numeric-3'

    def fillresponse(self):
        if self.confirme("Do you want?"):
            if self.traitment("mdi:mdi-timer-sand", "Waiting...", "Done!"):
                import time
                time.sleep(3)


@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Test of composants."))
class TestComposants(XferContainerCustom):
    caption = _("_Test of composants")
    short_icon = 'mdi:mdi-numeric-4'

    def fillresponse(self, edt1='aaa', flt1=3.1399999, mm1='xyz', dt1='2007-04-23', tm1='12:34:00',
                     ck1=False, slct1='1', flt2=5, cl1=['1', '2'], cl2=['b', 'd', 'f'], stm1='2008-07-12 23:47:31', stp=1):
        act_modif = self.return_action('Modify', '')

        edt = XferCompEdit('edt1')
        edt.set_value(edt1)
        edt.description = 'editor=' + str(edt1)
        edt.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        edt.set_location(1, 1)

        self.add_component(edt)

        flt = XferCompFloat('flt1')
        flt.set_value(flt1)
        flt.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        flt.set_location(1, 2)
        flt.description = 'Real=' + str(flt1)
        self.add_component(flt)

        cmm = XferCompMemo('mm1')
        cmm.set_value(mm1)
        cmm.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        cmm.add_sub_menu('Première valeur', 'VALUE_1')
        cmm.add_sub_menu('Deuxième valeur', 'VALUE_2')
        cmm.add_sub_menu('Troisième valeur', 'VALUE_3')
        cmm.set_location(1, 3)
        cmm.description = 'Memo=' + str(mm1)
        self.add_component(cmm)

        date = XferCompDate('dt1')
        date.set_value(dt1)
        date.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        date.set_location(1, 4)
        date.description = 'Date=' + str(dt1)
        self.add_component(date)

        time = XferCompTime('tm1')
        time.set_value(tm1)
        time.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        time.set_location(1, 5)
        time.description = 'Hour=' + str(tm1)
        self.add_component(time)

        datetime = XferCompDateTime('stm1')
        datetime.set_value(stm1)
        datetime.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        datetime.set_location(1, 6)
        datetime.description = 'Date Hour=' + str(stm1)
        self.add_component(datetime)

        check = XferCompCheck('ck1')
        check.set_value(ck1)
        check.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        check.set_location(1, 7)
        check.description = 'Coche=' + str(ck1)
        self.add_component(check)

        slct = XferCompSelect('slct1')
        if (flt2 is not None) and (flt2 < 2):
            slct.set_select({'1': 'abc', '2': 'def'})
        elif (flt2 is not None) and (flt2 < 10):
            slct.set_select({'1': 'abc', '2': 'def', '3': 'ghij'})
        else:
            slct.set_select({'1': 'abc', '2': 'def', '3': 'ghij', '4': 'klmn'})
        slct.set_value(slct1)
        slct.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        slct.set_location(1, 8)
        slct.description = 'Select=' + str(slct1)
        self.add_component(slct)

        flt = XferCompFloat('flt2', 0, 100, 0)
        flt.set_value(flt2)
        flt.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        flt.set_location(1, 9)
        flt.description = 'Integer=' + str(flt2)
        self.add_component(flt)

        checklist = XferCompCheckList('cl1')
        checklist.set_select(
            {'1': 'abc', '2': 'def', '3': 'ghij', '4': 'klmn'})
        checklist.set_value(cl1)
        checklist.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        checklist.set_location(1, 10)
        checklist.description = 'CheckList=' + str(cl1)
        self.add_component(checklist)

        checklist = XferCompCheckList('cl2')
        checklist.simple = 2
        checklist.set_select(
            {'a': '123', 'b': '456', 'c': '789', 'd': '147', 'e': '258', 'f': '369'})
        checklist.set_value(cl2)
        checklist.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        checklist.set_location(1, 11)
        checklist.description = 'CheckList 2=' + str(cl2)
        self.add_component(checklist)

        step = XferCompStep('stp', 8)
        step.set_value(stp)
        step.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        step.set_location(1, 12)
        step.description = 'Step=' + str(stp)
        self.add_component(step)

        btn = XferCompButton('btn1')
        btn.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        btn.set_location(1, 20)
        btn.description = 'Bouton'
        self.add_component(btn)

        self.add_action(WrapAction('Fin', short_icon='mdi:mdi-close'), modal=FORMTYPE_MODAL, close=CLOSE_YES)

        # self.set_close_action(Xfer_Action('fermeture', '', 'TestValidation', 'CloseEvenement', FORMTYPE_MODAL, CLOSE_YES, SELECT_NONE))


@MenuManage.describ('', FORMTYPE_MODAL, 'dummy.foo', _("Null test of composants."))
class TestNullComposants(XferContainerCustom):
    caption = _("Null test of composants.")
    short_icon = 'mdi:mdi-numeric-5'

    def fillresponse(self, flt1=0.0, flt2=0, dt1='01-01-2010', tm1='12:00', stm1='01-01-2010 12:00'):
        act_modif = self.return_action('Modify', '')

        flt = XferCompFloat('flt1')
        flt.set_value(flt1)
        flt.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        flt.set_location(0, 1)
        flt.needed = False
        flt.description = 'Real=' + str(flt1)
        self.add_component(flt)

        flt = XferCompFloat('flt2', 0, 100, 0)
        flt.set_value(flt2)
        flt.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        flt.set_location(0, 2)
        flt.needed = False
        flt.description = 'Integer=' + str(flt2)
        self.add_component(flt)

        date = XferCompDate('dt1')
        date.set_value(dt1)
        date.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        date.set_location(0, 3)
        date.needed = False
        date.description = 'Date=' + str(dt1)
        self.add_component(date)

        time = XferCompTime('tm1')
        time.set_value(tm1)
        time.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        time.set_location(0, 4)
        time.needed = False
        time.description = 'Hour=' + str(tm1)
        self.add_component(time)

        datetime = XferCompDateTime('stm1')
        datetime.set_value(stm1)
        datetime.set_action(self.request, act_modif, modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        datetime.set_location(0, 5)
        datetime.needed = False
        datetime.description = 'Date Hour=' + str(stm1)
        self.add_component(datetime)


@MenuManage.describ('', FORMTYPE_MODAL, 'dummy.foo', _("Test of grid simple."))
class SimpleGrid(XferContainerCustom):
    caption = _("_Test of grid")
    short_icon = 'mdi:mdi-numeric-5'

    def fillresponse(self):

        grid = XferCompGrid('grid')
        grid.set_location(0, 0)

        grid.add_header('col1', "Integer", 'N0')
        grid.add_header('col2', "Float", 'N3')
        grid.add_header('col3', "Boolean", 'B')
        grid.add_header('col4', "String", None, 0, "{[b]}%s{[/b]}")

        grid.set_value(1, "col1", 2500)
        grid.set_value(1, "col2", 7.54)
        grid.set_value(1, "col3", True)
        grid.set_value(1, "col4", "foo")

        grid.set_value(5, "col1", 4)
        grid.set_value(5, "col2", 789.644)
        grid.set_value(5, "col3", False)
        grid.set_value(5, "col4", "string")

        # grid.add_action(self.return_action('Reopen', ''),-1, {'modal':FORMTYPE_REFRESH})
        self.add_component(grid)


@MenuManage.describ('dummy.change_example', FORMTYPE_MODAL, 'dummy.foo', _("List of example."))
class ExampleList(XferListEditor):
    caption = _("List of example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'


@ActionsManage.affect_grid(TITLE_EDIT, short_icon='mdi:mdi-text-box-outline', unique=SELECT_SINGLE)
@MenuManage.describ('dummy.change_example')
class ExampleShow(XferShowEditor):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@ActionsManage.affect_show(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', close=CLOSE_YES)
@MenuManage.describ('dummy.add_example')
class ExampleAddModify(XferAddEditor):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'

    def fillresponse(self):
        if self.item.id is None:
            self.item.value = Preference.get_value('dummy-default-value', self.request.user)
            self.item.price = Preference.get_value('dummy-default-price', self.request.user)
            self.item.valid = Preference.get_value('dummy-default-valid', self.request.user)
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('dummy.delete_example')
class ExampleDel(XferDelete):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'


@ActionsManage.affect_show(TITLE_PRINT, short_icon='mdi:mdi-printer-outline')
@MenuManage.describ('dummy.change_example')
class ExamplePrint(XferPrintAction):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'
    action_class = ExampleShow


@ActionsManage.affect_list(TITLE_LISTING, short_icon='mdi:mdi-printer-pos-edit-outline')
@MenuManage.describ('dummy.change_example')
class ExampleListing(XferPrintListing):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'


@ActionsManage.affect_list(TITLE_PRINT, short_icon='mdi:mdi-printer-outline')
@MenuManage.describ('dummy.change_example')
class ExamplePrintList(XferPrintAction):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'
    action_class = ExampleList

    def _get_persistent_pdfreport(self, recreate):
        persistent_pdfreport = self.getparam('persistent_pdfreport', 0)
        if persistent_pdfreport == 1:
            return b"aaa"
        elif persistent_pdfreport == 2:
            return [('file1.txt', b"aaa"), ('file2.txt', b"bbb"), ('file3.txt', b"ccc")]
        else:
            return None

    def get_persistent_renew(self):
        return True


@ActionsManage.affect_list("Reporting", short_icon='mdi:mdi-printer-pos-outline')
@MenuManage.describ('dummy.change_example')
class ExampleReporting(XferPrintReporting):
    with_text_export = True
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-10'
    model = Example
    field_id = 'example'

    def items_callback(self):
        return self.model.objects.all()


@ActionsManage.affect_list(TITLE_LABEL, short_icon='mdi:mdi-printer-pos-star-outline')
@MenuManage.describ('dummy.change_example')
class ExampleLabel(XferPrintLabel):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'


@MenuManage.describ('dummy.change_example', FORMTYPE_NOMODAL, 'dummy.foo', _("Find example."))
class ExampleSearch(XferSavedCriteriaSearchEditor):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'


@MenuManage.describ('contacts.add_example', FORMTYPE_MODAL, 'dummy.foo', _('Import example'))
class ExampleImport(ObjectImport):
    caption = _("Import example")
    short_icon = 'mdi:mdi-numeric-9'

    def get_select_models(self):
        return Example.get_select_contact_type()


@MenuManage.describ('dummy.change_example', FORMTYPE_MODAL, 'dummy.foo', _("Mosaic of example."))
class ExampleMosaic(XferContainerCustom):
    caption = _("Mosaic of example")
    short_icon = 'mdi:mdi-numeric-9'
    model = Example
    field_id = 'example'

    def fillresponse(self):
        self.items = self.model.objects.all()
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0)
        self.add_component(lbl)
        mosaic = XferCompMosaic(self.field_id)
        mosaic.set_model(self.items, self, "image", "name", "comment", "valid")
        mosaic.set_location(0, 1, 2)
        mosaic.set_height(350)
        mosaic.description = 'images mosaic'
        mosaic.add_action(self.request, ExampleAddModify.get_action(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline'), modal=FORMTYPE_MODAL, close=CLOSE_NO, unique=SELECT_NONE)
        mosaic.add_action(self.request, ExampleDel.get_action(TITLE_DELETE, short_icon='mdi:mdi-delete-outline'), modal=FORMTYPE_MODAL, close=CLOSE_NO, unique=SELECT_MULTI)

        mosaic.add_action(self.request, ExampleAddModify.get_action(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline'), modal=FORMTYPE_MODAL, close=CLOSE_NO, unique=SELECT_SINGLE, group=False)
        mosaic.add_action(self.request, ExampleShow.get_action(TITLE_EDIT, short_icon='mdi:mdi-text-box-outline'), modal=FORMTYPE_MODAL, close=CLOSE_NO, unique=SELECT_SINGLE, group=True)
        self.add_component(mosaic)
        self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))


@MenuManage.describ('dummy.change_other', FORMTYPE_NOMODAL, 'dummy.foo', _('List of other'))
class OtherList(XferListEditor):
    short_icon = 'mdi:mdi-numeric-10'
    model = Other
    field_id = 'other'
    caption = _("others")


@ActionsManage.affect_grid(TITLE_ADD, short_icon='mdi:mdi-pencil-plus-outline')
@ActionsManage.affect_grid(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', unique=SELECT_SINGLE)
@ActionsManage.affect_show(TITLE_MODIFY, short_icon='mdi:mdi-pencil-outline', close=CLOSE_YES)
@MenuManage.describ('dummy.add_other')
class OtherAddModify(XferAddEditor):
    short_icon = 'mdi:mdi-numeric-10'
    model = Other
    field_id = 'other'
    caption_add = _("Add other")
    caption_modify = _("Modify other")


@ActionsManage.affect_grid(TITLE_EDIT, short_icon='mdi:mdi-text-box-outline', unique=SELECT_SINGLE)
@MenuManage.describ('dummy.change_other')
class OtherShow(XferShowEditor):
    short_icon = 'mdi:mdi-numeric-10'
    model = Other
    field_id = 'other'
    caption = _("Show other")


@ActionsManage.affect_show(TITLE_PRINT, short_icon='mdi:mdi-printer-outline', condition=lambda xfer: xfer.item.bool)
@MenuManage.describ('dummy.change_other')
class OtherPrint(XferPrintAction):
    caption = _("Example")
    short_icon = 'mdi:mdi-numeric-10'
    model = Other
    field_id = 'other'
    action_class = OtherShow

    def __init__(self):
        XferPrintAction.__init__(self)
        self.selector = [('watermark', 'watermark', b'')]

    def get_report_generator(self):
        generator = XferPrintAction.get_report_generator(self)
        if generator is not None:
            generator.watermark = self.getparam('watermark', '')
        return generator


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ('dummy.delete_other')
class OtherDel(XferDelete):
    short_icon = 'mdi:mdi-numeric-10'
    model = Other
    field_id = 'other'
    caption = _("Delete other")


def run_simple_action(timetxt):
    """Run simple action"""
    if timetxt is None:
        Parameter.change_value('dummy-value', '')
        Params.clear()
    else:
        value = Params.getvalue('dummy-value')
        size = len(value.split('{[br/]}'))
        if size >= 5:
            LucteriosScheduler.remove(run_simple_action)
            LucteriosScheduler.add_date(run_simple_action, datetime=datetime.now() + timedelta(seconds=20), timetxt=None)
        else:
            value += timetxt + "{[br/]}"
            Parameter.change_value('dummy-value', value)
            Params.clear()


@MenuManage.describ('')
class AddSchedulerTask(XferContainerAcknowledge):
    short_icon = 'mdi:mdi-numeric-9-plus'
    caption = _("add scheduler task")

    def fillresponse(self):
        Parameter.change_value('dummy-value', '')
        Params.clear()
        LucteriosScheduler.add_task(run_simple_action, minutes=1.0 / 6, timetxt=datetime.now().ctime())


@signal_and_lock.Signal.decorate('summary')
def summary_dummy(xfer):
    if not hasattr(xfer, 'add_component'):
        return True
    else:
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('dummytitle')
        lab.set_value_as_infocenter("Dummy")
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
        lbl = XferCompLabelForm('dummy_time')
        lbl.set_color('blue')
        lbl.set_location(0, row + 1, 4)
        lbl.set_centered()
        lbl.set_value(datetime.now())
        lbl.set_format('H')
        xfer.add_component(lbl)

        btn = XferCompButton('btnscheduler')
        btn.set_action(xfer.request, AddSchedulerTask.get_action('Task', ''), close=CLOSE_NO)
        btn.set_location(0, row + 2, 4)
        xfer.add_component(btn)
        lbl = XferCompLabelForm('dummy-value')
        lbl.set_location(0, row + 3, 4)
        lbl.set_value(Params.getvalue('dummy-value'))
        xfer.add_component(lbl)
        return True
