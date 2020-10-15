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

from lucterios.framework.xfercomponents import XferCompPassword, XferCompCheck,\
    XferCompSelect, XferCompButton, XferCompCheckList
from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.error import LucteriosException, IMPORTANT, MINOR
from lucterios.framework.tools import CLOSE_NO, FORMTYPE_REFRESH
from lucterios.framework.xfersearch import XferSearchEditor
from lucterios.framework.signal_and_lock import Signal

from lucterios.CORE.models import SavedCriteria, Preference
from lucterios.framework.plugins import PluginManager


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
        ckk = XferCompCheck('password_change')
        ckk.set_location(0, new_row + 1, 1, 1)
        ckk.set_value('n')
        ckk.description = _("To change password?")
        ckk.java_script = """
var pwd_change=current.getValue();
parent.get('password1').setEnabled(pwd_change);
parent.get('password2').setEnabled(pwd_change);
"""
        xfer.add_component(ckk)

        pwd1 = XferCompPassword('password1')
        pwd1.set_location(0, new_row + 2, 1, 1)
        pwd1.empty = 1
        pwd1.description = _("password")
        xfer.add_component(pwd1)
        pwd2 = XferCompPassword('password2')
        pwd2.set_location(0, new_row + 3, 1, 1)
        pwd2.empty = 1
        pwd2.description = _("password (again)")
        xfer.add_component(pwd2)
        if Signal.call_signal("send_connection", None, None, None) > 0:
            ckkg = XferCompCheck('password_generate')
            ckkg.set_location(0, new_row + 4)
            ckkg.description = _("Generate new password?")
            ckkg.set_value(False)
            ckkg.java_script = """
    var pwd_generate=current.getValue();
    var pwd_change=parent.get('password_change').getValue();
    parent.get('password_change').setEnabled(!pwd_generate);
    parent.get('password1').setEnabled(!pwd_generate && pwd_change);
    parent.get('password2').setEnabled(!pwd_generate && pwd_change);
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


class LucteriosGroupEditor(LucteriosEditor):

    def edit(self, xfer):
        if (PluginManager.get_instance().count > 0):
            plugin_permission = PluginManager.get_param()
            sel = XferCompCheckList('plugins')
            sel.description = _('plugins')
            sel.set_location(1, 2)
            sel.simple = 2
            sel.set_select([(item.name, item.title) for item in PluginManager.get_instance()])
            sel.set_value([item.name for item in PluginManager.get_instance() if (item.name in plugin_permission) and (self.item.id in plugin_permission[item.name])])
            xfer.add_component(sel)

    def saving(self, xfer):
        if (PluginManager.get_instance().count > 0):
            plugin_permissions = PluginManager.get_param()
            new_plugin = xfer.getparam('plugins', ())
            new_permissions = {}
            for plugin_name in plugin_permissions.keys():
                if plugin_name in new_plugin:
                    new_permissions[plugin_name] = list(set(plugin_permissions[plugin_name] + [xfer.item.id]))
                else:
                    new_permissions[plugin_name] = plugin_permissions[plugin_name]
                    if xfer.item.id in new_permissions[plugin_name]:
                        new_permissions[plugin_name].remove(xfer.item.id)
            PluginManager.set_param(new_permissions)


class PreferenceEditor(LucteriosEditor):

    def edit(self, xfer):
        user_id = xfer.getparam('user_actif', xfer.getparam('user_inactif', 0))
        pname = xfer.getparam('preferences', '')
        if pname != '':
            if (user_id == 0) and not xfer.request.user.is_anonymous:
                user_id = xfer.request.user.id
            xfer.item = Preference.objects.filter(name=pname, user_id=user_id).first()
            if xfer.item is None:
                xfer.item = Preference.objects.get(name=pname, user=None)
            xfer.item.user_id = user_id
        fieldname = ['title']
        if user_id != 0:
            fieldname.append('user')
        xfer.params['user'] = user_id
        xfer.fill_from_model(1, 1, True, fieldname)
        comp = xfer.item.get_write_comp()
        comp.set_location(1, 3)
        comp.description = _('value')
        xfer.add_component(comp)
        if user_id != 0:
            check = XferCompCheck('setdefault')
            check.set_value(False)
            check.set_location(1, 4)
            check.description = _('reset to default')
            check.java_script = """
var check_default=current.getValue();
parent.get('%s').setEnabled(!check_default);
""" % comp.name
            xfer.add_component(check)

    def saving(self, xfer):
        user_id = xfer.getparam('user', 0)
        pname = xfer.getparam('preferences', xfer.item.name)
        if xfer.getparam('setdefault', False) is True:
            Preference.change_value(pname, None, user=user_id)
        else:
            pvalue = xfer.getparam(pname)
            if pvalue is not None:
                Preference.change_value(pname, pvalue, user=user_id)


class SavedCriteriaEditor(LucteriosEditor):

    def saving(self, xfer):
        saved_list = SavedCriteria.objects.filter(modelname=self.item.modelname, name=self.item.name)
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
        sel = XferCompSelect('saved_criteria')
        sel.description = _("saved criteria")
        sel.set_location(1, new_row + 1, 3)
        sel.set_needed(False)
        sel.set_select_query(saved_list)
        sel.set_action(self.request, self.return_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
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
