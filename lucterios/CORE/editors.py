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

from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompPassword, XferCompCheck
from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.error import LucteriosException, IMPORTANT

class LucteriosUserEditor(LucteriosEditor):

    def edit(self, xfer):
        if self.item.id is not None:  # pylint: disable=no-member
            xfer.change_to_readonly('username')
            obj_username = xfer.get_components('username')
            xfer.filltab_from_model(obj_username.col - 1, obj_username.row + 1, True, ['date_joined', 'last_login'])
        obj_email = xfer.get_components('email')
        xfer.tab = obj_email.tab
        new_row = obj_email.row
        lbl0 = XferCompLabelForm('lbl_password_change')
        lbl0.set_location(0, new_row + 1, 1, 1)
        lbl0.set_value_as_name(_("To change password?"))
        xfer.add_component(lbl0)
        ckk = XferCompCheck('password_change')
        ckk.set_location(1, new_row + 1, 1, 1)
        ckk.set_value(False)
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
        xfer.add_component(pwd1)
        pwd2 = XferCompPassword('password2')
        pwd2.set_location(1, new_row + 3, 1, 1)
        xfer.add_component(pwd2)
        if xfer.getparam("IDENT_READ") is not None:
            xfer.change_to_readonly('first_name')
            xfer.change_to_readonly('last_name')
            xfer.change_to_readonly('email')
        return LucteriosEditor.edit(self, xfer)

    def before_save(self, xfer):
        if self.item.id is None:  # pylint: disable=no-member
            self.item.last_login = timezone.now()
        return

    def saving(self, xfer):
        password_change = xfer.getparam('password_change')
        if password_change == 'o':
            password1 = xfer.getparam('password1')
            password2 = xfer.getparam('password2')
            if password1 != password2:
                raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
            if password1 is not None:
                self.item.set_password(password1)
                self.item.save()
