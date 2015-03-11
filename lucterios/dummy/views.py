# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils import six

from lucterios.framework.tools import MenuManage
from lucterios.framework.tools import FORMTYPE_NOMODAL, FORMTYPE_REFRESH, FORMTYPE_MODAL, CLOSE_NO, CLOSE_YES, SELECT_NONE
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XFER_DBOX_INFORMATION, XferContainerCustom
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompEdit, XferCompFloat, XferCompMemo, XferCompDate, XferCompGrid
from lucterios.framework.xfercomponents import XferCompTime, XferCompDateTime, XferCompCheck, XferCompSelect, XferCompCheckList, XferCompButton

MenuManage.add_sub('dummy.foo', None, 'dummy/images/10.png', _('Dummy'), _('Dummy menu'), 20)

@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Bidule action."))
class Bidule(XferContainerAcknowledge):

    caption = _("_Bidule")
    icon = "1.png"

    def fillresponse(self, error):
        from lucterios.framework.error import LucteriosException, GRAVE
        if error is None:
            raise LucteriosException(GRAVE, "Error of bidule")
        else:
            raise AttributeError("Other error:" + error)

@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Truc action."))
class Truc(XferContainerAcknowledge):
    caption = _("_Truc")
    icon = "2.png"

    def fillresponse(self, val1, val2=4):
        self.message("Hello world (%s,%s)!" % (str(val1), str(val2)), XFER_DBOX_INFORMATION)

@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Multi action."))
class Multi(XferContainerAcknowledge):
    caption = _("_Multi")
    icon = "3.png"

    def fillresponse(self):
        if self.confirme("Do you want?"):
            if self.traitment("dummy/images/4.png", "Waiting...", "Done!"):
                import time
                time.sleep(3)

@MenuManage.describ('', FORMTYPE_NOMODAL, 'dummy.foo', _("Test of composants."))
class TestComposants(XferContainerCustom):
    # pylint: disable=line-too-long,too-many-arguments,too-many-locals,too-many-statements,dangerous-default-value,too-many-public-methods

    caption = _("_Test of composants")
    icon = "4.png"

    def fillresponse(self, edt1='aaa', flt1=3.1399999, mm1='xyz', dt1='2007-04-23', tm1='12:34:00', \
                     ck1=False, slct1='1', flt2=5, cl1=['1', '2'], stm1='2008-07-12 23:47:31'):
        act_modif = (self.get_changed('Modify', ''), {'modal':FORMTYPE_REFRESH, 'close':CLOSE_NO, 'unique':SELECT_NONE})

        lbl = XferCompLabelForm('Lbl2')
        lbl.set_value('editor=' + six.text_type(edt1))
        lbl.set_location(0, 1)
        self.add_component(lbl)
        edt = XferCompEdit('edt1')
        edt.set_value(edt1)

        edt.set_action(self.request, act_modif[0], act_modif[1])
        edt.set_location(1, 1)

        self.add_component(edt)

        lbl = XferCompLabelForm('Lbl3')
        lbl.set_value('Real=' + six.text_type(flt1))
        lbl.set_location(0, 2)
        self.add_component(lbl)
        flt = XferCompFloat('flt1')
        flt.set_value(flt1)
        flt.set_action(self.request, act_modif[0], act_modif[1])
        flt.set_location(1, 2)
        self.add_component(flt)

        lbl = XferCompLabelForm('Lbl4')
        lbl.set_value('Memo=' + six.text_type(mm1))
        lbl.set_location(0, 3)
        self.add_component(lbl)
        cmm = XferCompMemo('mm1')
        cmm.set_value(mm1)
        cmm.set_action(self.request, act_modif[0], act_modif[1])
        cmm.set_location(1, 3)
        self.add_component(cmm)

        lbl = XferCompLabelForm('Lbl5')
        lbl.set_value('Date=' + six.text_type(dt1))
        lbl.set_location(0, 4)
        self.add_component(lbl)
        date = XferCompDate('dt1')
        date.set_value(dt1)
        date.set_action(self.request, act_modif[0], act_modif[1])
        date.set_location(1, 4)
        self.add_component(date)

        lbl = XferCompLabelForm('Lbl6')
        lbl.set_value('Hour=' + six.text_type(tm1))
        lbl.set_location(0, 5)
        self.add_component(lbl)
        time = XferCompTime('tm1')
        time.set_value(tm1)
        time.set_action(self.request, act_modif[0], act_modif[1])
        time.set_location(1, 5)
        self.add_component(time)

        lbl = XferCompLabelForm('Lbl7')
        lbl.set_value('Date Hour=' + six.text_type(stm1))
        lbl.set_location(0, 6)
        self.add_component(lbl)
        datetime = XferCompDateTime('stm1')
        datetime.set_value(stm1)
        datetime.set_action(self.request, act_modif[0], act_modif[1])
        datetime.set_location(1, 6)
        self.add_component(datetime)

        lbl = XferCompLabelForm('Lbl8')
        lbl.set_value('Coche=' + six.text_type(ck1))
        lbl.set_location(0, 7)
        self.add_component(lbl)
        check = XferCompCheck('ck1')
        check.set_value(ck1)
        check.set_action(self.request, act_modif[0], act_modif[1])
        check.set_location(1, 7)
        self.add_component(check)

        lbl = XferCompLabelForm('Lbl9')
        lbl.set_value('Select=' + six.text_type(slct1))
        lbl.set_location(0, 8)
        self.add_component(lbl)
        slct = XferCompSelect('slct1')
        if flt2 < 2:
            slct.set_select({'1':'abc', '2':'def'})
        elif flt2 < 10:
            slct.set_select({'1':'abc', '2':'def', '3':'ghij'})
        else:
            slct.set_select({'1':'abc', '2':'def', '3':'ghij', '4':'klmn'})
        slct.set_value(slct1)
        slct.set_action(self.request, act_modif[0], act_modif[1])
        slct.set_location(1, 8)
        self.add_component(slct)

        lbl = XferCompLabelForm('Lbl10')
        lbl.set_value('Integer=' + six.text_type(flt2))
        lbl.set_location(0, 9)
        self.add_component(lbl)
        flt = XferCompFloat('flt2', 0, 100, 0)
        flt.set_value(flt2)
        flt.set_action(self.request, act_modif[0], act_modif[1])
        flt.set_location(1, 9)
        self.add_component(flt)

        lbl = XferCompLabelForm('Lbl11')
        lbl.set_value('CheckList=' + six.text_type(cl1))
        lbl.set_location(0, 10)
        self.add_component(lbl)
        checklist = XferCompCheckList('cl1')
        checklist.set_select({'1':'abc', '2':'def', '3':'ghij', '4':'klmn'})
        checklist.set_value(cl1)
        checklist.set_action(self.request, act_modif[0], act_modif[1])
        checklist.set_location(1, 10)
        self.add_component(checklist)

        lbl = XferCompLabelForm('Lbl12')
        lbl.set_value('Bouton')
        lbl.set_location(0, 20)
        self.add_component(lbl)
        btn = XferCompButton('btn1')
        btn.set_action(self.request, act_modif[0], act_modif[1])
        btn.set_location(1, 20)
        self.add_component(btn)

        self.add_action(XferContainerAcknowledge().get_changed('Fin', 'images/close.png'), {'modal':FORMTYPE_MODAL, 'close':CLOSE_YES, 'unique':SELECT_NONE})

        # self.set_close_action(Xfer_Action('fermeture', '', 'TestValidation', 'CloseEvenement', FORMTYPE_MODAL, CLOSE_YES, SELECT_NONE))

@MenuManage.describ('', FORMTYPE_MODAL, 'dummy.foo', _("Test of grid simple."))
class SimpleGrid(XferContainerCustom):
    # pylint: disable=too-many-public-methods

    caption = _("_Test of grid")
    icon = "5.png"

    def fillresponse(self):

        grid = XferCompGrid('grid')
        grid.set_location(0, 0)

        grid.add_header('col1', "Integer", 'int')
        grid.add_header('col2', "Float", 'float')
        grid.add_header('col3', "Boolean", 'bool')
        grid.add_header('col4', "String", 'str')

        grid.set_value(1, "col1", 25)
        grid.set_value(1, "col2", 7.54)
        grid.set_value(1, "col3", True)
        grid.set_value(1, "col4", "foo")

        grid.set_value(5, "col1", 0)
        grid.set_value(5, "col2", 789.644)
        grid.set_value(5, "col3", False)
        grid.set_value(5, "col4", "string")

        # grid.add_action(self.get_changed('Reopen', ''),-1, {'modal':FORMTYPE_REFRESH})
        self.add_component(grid)
