# -*- coding: utf-8 -*-
'''
Describe database model for Django

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

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompPassword, XferCompCheck,\
    XferCompSelect, XferCompButton
from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.error import LucteriosException, IMPORTANT, MINOR
from lucterios.framework.tools import CLOSE_NO, FORMTYPE_REFRESH
from lucterios.framework.xfersearch import XferSearchEditor
from lucterios.framework.signal_and_lock import Signal

from lucterios.CORE.models import SavedCriteria


class LucteriosUserEditor(LucteriosEditor):

    def edit(self, xfer):
        if self.item.id is not None:
            xfer.change_to_readonly('username')
            obj_username = xfer.get_components('username')
            xfer.filltab_from_model(obj_username.col - 1, obj_username.row + 1, True, ['date_joined', 'last_login'])
        xfer.change_to_readonly('is_active')
        obj_email = xfer.get_components('email')
        xfer.tab = obj_email.tab
        new_row = obj_email.row
        lbl0 = XferCompLabelForm('lbl_password_change')
        lbl0.set_location(0, new_row + 1, 1, 1)
        lbl0.set_value_as_name(_("To change password?"))
        xfer.add_component(lbl0)
        ckk = XferCompCheck('password_change')
        ckk.set_location(1, new_row + 1, 1, 1)
        ckk.set_value(True)
        ckk.java_script = """
var pwd_change=current.getValue();
parent.get('password1').setEnabled(pwd_change);
parent.get('password2').setEnabled(pwd_change);
"""
        xfer.add_component(ckk)

        lbl1 = XferCompLabelForm('lbl_password1')
        lbl1.set_location(0, new_row + 2, 1, 1)
        lbl1.set_value_as_name(_("password"))
        xfer.add_component(lbl1)
        lbl2 = XferCompLabelForm('lbl_password2')
        lbl2.set_location(0, new_row + 3, 1, 1)
        lbl2.set_value_as_name(_("password (again)"))
        xfer.add_component(lbl2)
        pwd1 = XferCompPassword('password1')
        pwd1.set_location(1, new_row + 2, 1, 1)
        pwd1.empty = 1
        xfer.add_component(pwd1)
        pwd2 = XferCompPassword('password2')
        pwd2.set_location(1, new_row + 3, 1, 1)
        pwd2.empty = 1
        xfer.add_component(pwd2)
        if Signal.call_signal("send_connection", None, None, None) > 0:
            lbl3 = XferCompLabelForm('lbl_password_generate')
            lbl3.set_location(0, new_row + 4)
            lbl3.set_value_as_name(_("Generate new password?"))
            xfer.add_component(lbl3)
            ckkg = XferCompCheck('password_generate')
            ckkg.set_location(1, new_row + 4)
            ckkg.set_value(False)
            ckkg.java_script = """
    var pwd_change=current.getValue();
    parent.get('password_change').setEnabled(!pwd_change);
    parent.get('password1').setEnabled(!pwd_change);
    parent.get('password2').setEnabled(!pwd_change);
    """
            xfer.add_component(ckkg)
        if xfer.getparam("IDENT_READ") is not None:
            xfer.change_to_readonly('first_name')
            xfer.change_to_readonly('last_name')
            xfer.change_to_readonly('email')
        return LucteriosEditor.edit(self, xfer)

    def before_save(self, xfer):
        if self.item.id is None:
            self.item.last_login = timezone.now()
        return

    def saving(self, xfer):
        password = None
        password_generate = xfer.getparam('password_generate')
        password_change = xfer.getparam('password_change')
        if password_generate == 'o':
            if not self.item.generate_password():
                raise LucteriosException(
                    MINOR, _("The password is not changed!"))
        elif password_change == 'o':
            password = xfer.getparam('password1')
            password_again = xfer.getparam('password2')
            if password != password_again:
                raise LucteriosException(
                    IMPORTANT, _("The passwords are differents!"))
            self.item.set_password(password)
            self.item.save()


class SavedCriteriaEditor(LucteriosEditor):

    def saving(self, xfer):
        saved_list = SavedCriteria.objects.filter(
            modelname=self.item.modelname, name=self.item.name)
        for saved_item in saved_list:
            if saved_item.id != self.item.id:
                saved_item.delete()

    def edit(self, xfer):
        xfer.change_to_readonly('modelname')
        xfer.change_to_readonly('criteria')
        xfer.get_components('modelname').set_value(self.item.model_title)
        xfer.get_components('criteria').set_value(self.item.criteria_desc)


class XferSavedCriteriaSearchEditor(XferSearchEditor):

    def fillresponse_add_title(self):
        XferSearchEditor.fillresponse_add_title(self)
        modelname = self.model.get_long_name()
        saved_list = SavedCriteria.objects.filter(modelname=modelname)
        new_row = self.get_max_row()
        lbl = XferCompLabelForm('lbl_saved_criteria')
        lbl.set_location(1, new_row + 1)
        lbl.set_value_as_name(_("saved criteria"))
        self.add_component(lbl)
        sel = XferCompSelect('saved_criteria')
        sel.set_location(2, new_row + 1, 2)
        sel.set_needed(False)
        sel.set_select_query(saved_list)
        sel.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(sel)
        if len(self.criteria_list) > 0:
            from lucterios.CORE.views import SavedCriteriaAddModify
            btn = XferCompButton('btn_saved_criteria')
            btn.set_location(4, new_row + 1, 2)
            btn.set_is_mini(True)
            btn.set_action(self.request, SavedCriteriaAddModify.get_action("+", ""), close=CLOSE_NO,
                           params={'modelname': modelname, 'criteria': self.getparam('CRITERIA', '')})
            self.add_component(btn)
        if self.getparam('saved_criteria', 0) != 0:
            saved_item = SavedCriteria.objects.get(
                id=self.getparam('saved_criteria', 0))
            self.params['CRITERIA'] = saved_item.criteria
            self.read_criteria_from_params()
