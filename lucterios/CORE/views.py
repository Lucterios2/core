# -*- coding: utf-8 -*-
'''
View for manage user password, print model and label in Lucterios

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
from os.path import isfile, join, dirname
from logging import getLogger
import mimetypes
import stat
import os

from django.utils.translation import ugettext_lazy as _
from django.utils.http import http_date
from django.utils import six
from django.http.response import StreamingHttpResponse
from django.apps.registry import apps
from django.conf import settings
from django.db.models import Q

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, WrapAction, \
    ActionsManage, FORMTYPE_REFRESH, SELECT_SINGLE, CLOSE_NO, FORMTYPE_MODAL, CLOSE_YES, SELECT_MULTI
from lucterios.framework.xferbasic import XferContainerMenu, XferContainerAbstract
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom, XFER_DBOX_INFORMATION
from lucterios.framework.xfercomponents import XferCompPassword, XferCompImage, XferCompLabelForm, XferCompGrid, XferCompSelect, \
    XferCompMemo, XferCompFloat, XferCompXML, XferCompEdit, XferCompDownLoad,\
    XferCompUpLoad, XferCompButton
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferDelete, XferSave, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE,\
    TITLE_CLONE, TITLE_OK, TITLE_CANCEL, TITLE_CLOSE, TEXT_TOTAL_NUMBER,\
    action_list_sorted
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework.filetools import get_user_dir, xml_validator, read_file, md5sum
from lucterios.framework import signal_and_lock, tools

from lucterios.CORE.parameters import Params, secure_mode_connect, notfree_mode_connect
from lucterios.CORE.models import Parameter, Label, PrintModel, SavedCriteria, LucteriosUser,\
    LucteriosGroup
from lucterios.CORE.views_usergroup import UsersList, GroupsList


MenuManage.add_sub('core.menu', None, '', '', '', 0)
MenuManage.add_sub(
    'core.general', None, 'images/general.png', _('General'), _('Generality'), 1)
MenuManage.add_sub('core.admin', None, 'images/admin.png',
                   _('Management'), _('Manage settings and configurations.'), 100)


@MenuManage.describ('', FORMTYPE_MODAL, 'core.menu', _("Summary"))
class StatusMenu(XferContainerCustom):
    caption = _("Summary")
    icon = "status.png"

    def fillresponse(self):
        signal_and_lock.Signal.call_signal("summary", self)


@MenuManage.describ('')
class Unlock(XferContainerAcknowledge):
    caption = 'unlock'

    def fillresponse(self):
        signal_and_lock.RecordLocker.unlock(self.request, self.params)

signal_and_lock.unlocker_view_class = Unlock


@MenuManage.describ('')
class Download(XferContainerAbstract):

    def get(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(
            ">> get %s [%s]", request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            full_path = join(
                get_user_dir(), six.text_type(self.getparam('filename')))
            if not isfile(full_path):
                raise LucteriosException(IMPORTANT, _("File not found!"))
            sign = self.getparam('sign', '')
            if sign != md5sum(full_path):
                raise LucteriosException(IMPORTANT, _("File invalid!"))
            content_type, encoding = mimetypes.guess_type(full_path)
            content_type = content_type or 'application/octet-stream'
            statobj = os.stat(full_path)
            response = StreamingHttpResponse(open(full_path, 'rb'),
                                             content_type=content_type)
            response["Last-Modified"] = http_date(statobj.st_mtime)
            if stat.S_ISREG(statobj.st_mode):
                response["Content-Length"] = statobj.st_size
            if encoding:
                response["Content-Encoding"] = encoding
            return response
        finally:
            getLogger("lucterios.core.request").debug(
                "<< get %s [%s]", request.path, request.user)


@MenuManage.describ('')
class Menu(XferContainerMenu):
    caption = 'menu'

    def get(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(
            ">> get %s [%s]", request.path, request.user)
        try:
            if request.user.is_authenticated() or not secure_mode_connect():
                return XferContainerMenu.get(self, request, *args, **kwargs)
            else:
                from lucterios.CORE.views_auth import Authentification
                auth = Authentification()
                return auth.get(request, *args, **kwargs)
        finally:
            getLogger("lucterios.core.request").debug(
                "<< get %s [%s]", request.path, request.user)


def right_changepassword(request):
    if (len(settings.AUTHENTICATION_BACKENDS) != 1) or (settings.AUTHENTICATION_BACKENDS[0] != 'django.contrib.auth.backends.ModelBackend'):
        return False
    return request.user.is_authenticated()


@MenuManage.describ(right_changepassword, FORMTYPE_MODAL, 'core.general', _("To Change your password."))
class ChangePassword(XferContainerCustom):
    caption = _("Password")
    icon = "passwd.png"

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)

        lbl = XferCompLabelForm('lbl_oldpass')
        lbl.set_location(1, 0, 1, 1)
        lbl.set_value_as_name(_("old password"))
        self.add_component(lbl)
        pwd = XferCompPassword('oldpass')
        pwd.set_location(2, 0, 1, 1)
        pwd.security = 0
        self.add_component(pwd)

        lbl = XferCompLabelForm('lbl_newpass1')
        lbl.set_location(1, 1, 1, 1)
        lbl.set_value_as_name(_("new password"))
        self.add_component(lbl)
        pwd = XferCompPassword('newpass1')
        pwd.set_location(2, 1, 1, 1)
        self.add_component(pwd)

        lbl = XferCompLabelForm('lbl_newpass2')
        lbl.set_location(1, 2, 1, 1)
        lbl.set_value_as_name(_("new password (again)"))
        self.add_component(lbl)
        pwd = XferCompPassword('newpass2')
        pwd.set_location(2, 2, 1, 1)
        self.add_component(pwd)

        self.add_action(
            ModifyPassword.get_action(_('Ok'), 'images/ok.png'))
        self.add_action(WrapAction(_('Cancel'), 'images/cancel.png'))


@MenuManage.describ('')
class ModifyPassword(XferContainerAcknowledge):
    caption = _("Password")
    icon = "passwd.png"

    def fillresponse(self, oldpass='', newpass1='', newpass2=''):
        if not self.request.user.check_password(oldpass):
            raise LucteriosException(IMPORTANT, _("Bad current password!"))

        if newpass1 != newpass2:
            raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
        self.request.user.set_password(newpass1)
        self.request.user.save()
        self.message(_("Password modify"), XFER_DBOX_INFORMATION)


def right_askpassword(request):
    if not notfree_mode_connect():
        return False
    if (len(settings.AUTHENTICATION_BACKENDS) != 1) or (settings.AUTHENTICATION_BACKENDS[0] != 'django.contrib.auth.backends.ModelBackend'):
        return False
    if (signal_and_lock.Signal.call_signal("send_connection", None, None, None) == 0):
        return False
    return not request.user.is_authenticated()


@MenuManage.describ(right_askpassword, FORMTYPE_MODAL, 'core.general', _("Password or login forget?"))
class AskPassword(XferContainerCustom):
    caption = _("Ask password")
    icon = "passwd.png"

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)
        lbl = XferCompLabelForm('lbl_title')
        lbl.set_location(1, 0, 2)
        lbl.set_value_as_header(
            _("To receive by email your login and a new password."))
        self.add_component(lbl)

        lbl = XferCompLabelForm('lbl_email')
        lbl.set_location(1, 1)
        lbl.set_value_as_name(_("email"))
        self.add_component(lbl)
        email = XferCompEdit('email')
        email.set_location(2, 1)
        email.mask = "[^@]+@[^@]+\.[^@]+"
        self.add_component(email)

        self.add_action(
            AskPasswordAct.get_action(_('Ok'), 'images/ok.png'))
        self.add_action(WrapAction(_('Cancel'), 'images/cancel.png'))


@MenuManage.describ(right_askpassword)
class AskPasswordAct(XferContainerAcknowledge):
    caption = _("Ask password")
    icon = "passwd.png"

    def fillresponse(self, email=''):
        import re
        if re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None:
            for user in LucteriosUser.objects.filter(email=email):
                user.generate_password()


@signal_and_lock.Signal.decorate('config')
def config_core(xfer):
    Params.fill(xfer, ['CORE-connectmode', 'CORE-Wizard'], 1, 1)
    xfer.params['params'].append('CORE-connectmode')
    xfer.params['params'].append('CORE-Wizard')


@signal_and_lock.Signal.decorate('auth_action')
def auth_action_core(actions_basic):
    actions_basic.append(AskPassword.get_action(_("Password or login forget?")))


@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'core.admin', _("To view and to modify main parameters."))
class Configuration(XferContainerCustom):
    caption = _("Main configuration")
    icon = "config.png"

    def fillresponse(self):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 10)
        img_title.set_value(self.icon_path())
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 3)
        lab.set_value(
            '{[br/]}{[center]}{[b]}{[u]}%s{[/u]}{[/b]}{[/center]}' % _("Software configuration"))
        self.add_component(lab)
        self.params['params'] = []
        signal_and_lock.Signal.call_signal("config", self)
        steplist = get_wizard_step_list()
        if steplist != '':
            btn = XferCompButton("conf_wizard")
            btn.set_location(1, self.get_max_row() + 1)
            btn.set_action(self.request, ConfigurationWizard.get_action(
                _("Wizard"), "images/config.png"), close=CLOSE_NO, params={'steplist': steplist})
            self.add_component(btn)
        self.add_action(
            ParamEdit.get_action(_('Modify'), 'images/edit.png'), close=CLOSE_NO)
        self.add_action(WrapAction(_('Close'), 'images/close.png'))


@MenuManage.describ('CORE.add_parameter')
class ParamEdit(XferContainerCustom):
    caption = _("Parameters")
    icon = "config.png"

    def fillresponse(self, params=(), nb_col=1):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0)
        img_title.set_value(self.icon_path())
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 2 * nb_col)
        lab.set_value_as_title(_("Edition of parameters"))
        self.add_component(lab)
        Params.fill(self, params, 1, 1, False, nb_col)
        self.add_action(ParamSave.get_action(_('Ok'), 'images/ok.png'))
        self.add_action(WrapAction(_('Cancel'), 'images/cancel.png'))


@MenuManage.describ('CORE.add_parameter')
class ParamSave(XferContainerAcknowledge):
    caption = _("Parameters")
    icon = "config.png"

    def fillresponse(self, params=()):
        for pname in params:
            pvalue = self.getparam(pname)
            Parameter.change_value(pname, pvalue)
        Params.clear()
        signal_and_lock.Signal.call_signal("param_change", params)

MenuManage.add_sub("core.extensions", 'core.admin', "images/config_ext.png",
                   _("_Extensions (conf.)"), _("To manage of modules configurations."), 20)


@MenuManage.describ('CORE.change_parameter', FORMTYPE_NOMODAL, 'core.extensions', _('Saved criteria list for searching tools'))
class SavedCriteriaList(XferListEditor):
    icon = "config_search.png"
    model = SavedCriteria
    field_id = 'savedcriteria'
    caption = _("Saved criterias")


@MenuManage.describ('CORE.add_parameter')
class SavedCriteriaAddModify(XferAddEditor):
    icon = "config_search.png"
    model = SavedCriteria
    field_id = 'savedcriteria'
    caption_add = _("Add saved criteria")
    caption_modify = _("Modify saved criteria")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('CORE.add_parameter')
class SavedCriteriaDel(XferDelete):
    icon = "config_search.png"
    model = SavedCriteria
    field_id = 'savedcriteria'
    caption = _("Delete Saved criteria")


MenuManage.add_sub("core.print", 'core.admin', "images/PrintReport.png",
                   _("Report and print"), _("To manage reports and tools of printing."), 30)


@MenuManage.describ('CORE.change_printmodel', FORMTYPE_NOMODAL, 'core.print', _("To Manage printing models."))
class PrintModelList(XferListEditor):
    caption = _("Print models")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse_header(self):
        modelname = self.getparam('modelname', "")
        lab = XferCompLabelForm('lblmodelname')
        lab.set_location(0, 1)
        lab.set_value_as_name(_('model'))
        self.add_component(lab)
        model_list = {}
        for print_model in PrintModel.objects.all():
            if print_model.modelname not in model_list.keys():
                try:
                    model_list[print_model.modelname] = print_model.model_associated_title()
                    if modelname == '':
                        modelname = print_model.modelname
                except LookupError:
                    pass
        model_sel = XferCompSelect('modelname')
        model_sel.set_location(1, 1)
        model_sel.set_select(model_list)
        model_sel.set_value(modelname)
        model_sel.set_action(self.request, self.get_action("", ""), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(model_sel)
        self.filter = Q(modelname=modelname)
        self.fieldnames = ['name', 'kind', 'is_default']
        return


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelEdit(XferContainerCustom):
    caption_add = _("Add a print model")
    caption_modify = _("Modify a print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fill_menu_memo(self, memo_comp):
        for name, value in self.item.model_associated().get_all_print_fields():
            memo_comp.add_sub_menu(name, value)

    def fillresponse(self):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 6)
        img_title.set_value(self.icon_path())
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 2)
        lab.set_value_as_title(_("Print models"))
        self.add_component(lab)
        self.fill_from_model(1, 1, False, ['name'])
        self.fill_from_model(1, 2, True, ['kind'])
        self.item.mode = int(self.item.mode)
        if self.item.kind == 1:
            self.fill_from_model(1, 3, False, ['mode'])
            self.get_components('mode').set_action(self.request, self.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            if (self.item.mode == 1) and (self.item.value[:6] != '<model'):
                self.item.value = "<model>\n<body>\n<text>%s</text></body>\n</model>" % self.item.value
        if self.item.kind == 0:
            self._fill_listing_editor()
        elif (self.item.kind == 1) and (self.item.mode == 0):
            self._fill_label_editor()
        elif (self.item.kind == 2) or ((self.item.kind == 1) and (self.item.mode == 1)):
            self._fill_report_editor()
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_EDIT, self, key=action_list_sorted):
            self.add_action(act, **opt)
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))

    def _fill_listing_editor(self):
        lab = XferCompLabelForm('lbl_page_width')
        lab.set_location(1, 3)
        lab.set_value_as_name(_("list page width"))
        self.add_component(lab)
        edt = XferCompFloat('page_width', 0, 9999, 0)
        edt.set_location(2, 3, 2)
        edt.set_value(self.item.page_width)
        self.add_component(edt)
        lab = XferCompLabelForm('lbl_page_height')
        lab.set_location(1, 4)
        lab.set_value_as_name(_("list page height"))
        self.add_component(lab)
        edt = XferCompFloat('page_heigth', 0, 9999, 0)
        edt.set_location(2, 4, 2)
        edt.set_value(self.item.page_height)
        self.add_component(edt)

        lab = XferCompLabelForm('lbl_col_size')
        lab.set_location(1, 5)
        lab.set_value_as_infocenter(_("size"))
        self.add_component(lab)
        lab = XferCompLabelForm('lbl_col_title')
        lab.set_location(2, 5)
        lab.set_value_as_infocenter(_("title"))
        self.add_component(lab)
        lab = XferCompLabelForm('lbl_col_text')
        lab.set_location(3, 5)
        lab.set_value_as_infocenter(_("text"))
        self.add_component(lab)

        col_index = 0
        for col_size, col_title, col_text in (self.item.columns + [[0, '', ''], [0, '', ''], [0, '', '']]):
            edt = XferCompFloat('col_size_%d' % col_index, 0, 999, 0)
            edt.set_location(1, 6 + col_index)
            edt.set_value(col_size)
            self.add_component(edt)
            edt = XferCompMemo('col_title_%d' % col_index)
            edt.set_location(2, 6 + col_index)
            edt.set_value(col_title)
            edt.set_size(75, 200)
            self.add_component(edt)
            edt = XferCompMemo('col_text_%d' % col_index)
            edt.set_location(3, 6 + col_index)
            edt.set_size(50, 300)
            edt.with_hypertext = True
            edt.set_value(col_text)
            self.fill_menu_memo(edt)
            self.add_component(edt)
            col_index += 1

    def _fill_label_editor(self):
        edit = XferCompMemo('value')
        edit.set_value(self.item.value)
        edit.set_location(1, 4, 2)
        edit.set_size(100, 500)
        edit.with_hypertext = True
        self.fill_menu_memo(edit)
        self.add_component(edit)

    def _fill_report_editor(self):
        edit = XferCompXML('value')
        edit.set_value(self.item.value)
        edit.schema = read_file(join(dirname(dirname(__file__)), 'framework', 'template.xsd'))
        edit.set_location(1, 4, 2)
        edit.set_size(400, 700)
        edit.with_hypertext = True
        self.fill_menu_memo(edit)
        self.add_component(edit)


@ActionsManage.affect_grid(_('Reload'), "images/edit.png", close=CLOSE_NO, unique=SELECT_SINGLE)
@ActionsManage.affect_edit(_('Reload'), "images/edit.png", close=CLOSE_NO)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelReload(XferContainerAcknowledge):
    caption = _("reload model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        model_module = ".".join(self.item.model_associated().__module__.split('.')[:-1])
        if self.getparam('SAVE') is None:
            dlg = self.create_custom(self.model)
            dlg.item = self.item
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0, 1, 3)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 6)
            dlg.add_component(lbl)

            lbl = XferCompLabelForm('lbl_default_model')
            lbl.set_value_as_name(_("Model to reload"))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            sel = XferCompSelect('default_model')
            sel.set_select(PrintModel.get_default_model(model_module, self.item.modelname, self.item.kind))
            sel.set_location(2, 1)
            dlg.add_component(sel)

            dlg.add_action(self.get_action(TITLE_OK, "images/ok.png"), close=CLOSE_YES, params={'SAVE': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            if self.item.load_model(model_module, self.getparam("default_model", "")):
                self.message(_('Model reloaded'))


@ActionsManage.affect_edit(_("Import"), "images/right.png", close=CLOSE_NO)
@MenuManage.describ('documents.add_folder')
class PrintModelImport(XferContainerAcknowledge):
    caption = _("reload model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        if self.getparam('SAVE') is None:
            dlg = self.create_custom(self.model)
            dlg.item = self.item
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0, 1, 3)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 6)
            dlg.add_component(lbl)

            lbl = XferCompLabelForm('lbl_import_model')
            lbl.set_value_as_name(_("file to load"))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            upload = XferCompUpLoad('import_model')
            upload.compress = False
            upload.http_file = True
            upload.maxsize = 128 * 1024 * 1024  # 128Mo
            upload.add_filter('.mdl')
            upload.set_location(2, 1)
            dlg.add_component(upload)

            dlg.add_action(self.get_action(TITLE_OK, "images/ok.png"), close=CLOSE_YES, params={'SAVE': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            if 'import_model' in self.request.FILES.keys():
                upload_file = self.request.FILES['import_model']
                if self.item.import_file(upload_file):
                    self.message(_('Model loaded'))


@ActionsManage.affect_edit(_("Extract"), "images/left.png", close=CLOSE_NO)
@MenuManage.describ('documents.add_folder')
class PrintModelExtract(XferContainerCustom):
    caption = _("Extract")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0, 6)
        self.add_component(lbl)
        zipdown = XferCompDownLoad('filename')
        zipdown.compress = False
        zipdown.http_file = True
        zipdown.maxsize = 0
        zipdown.set_value("%s.mdl" % self.item.name)
        zipdown.set_download(self.item.extract_file())
        zipdown.set_location(1, 15, 2)
        self.add_component(zipdown)


@ActionsManage.affect_edit(TITLE_OK, "images/ok.png", close=CLOSE_YES)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelSave(XferSave):
    caption = _("print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        self.item.mode = int(self.item.mode)
        if self.item.kind == 0:
            page_width = int(self.getparam('page_width'))
            page_heigth = int(self.getparam('page_heigth'))
            columns = []
            col_index = 0
            while self.getparam('col_size_%d' % col_index) is not None:
                col_size = int(self.getparam('col_size_%d' % col_index))
                col_title = self.getparam('col_title_%d' % col_index)
                col_text = self.getparam('col_text_%d' % col_index)
                if col_size > 0:
                    columns.append((col_size, col_title, col_text))
                col_index += 1
            self.item.change_listing(page_width, page_heigth, columns)
            self.item.save()
        elif self.item.kind == 2 or (self.item.kind == 1 and self.item.mode == 1):
            error = xml_validator(self.item.value, join(dirname(dirname(__file__)), 'framework', 'template.xsd'))
            if error is not None:
                raise LucteriosException(IMPORTANT, error)
            self.item.save()
        else:
            XferSave.fillresponse(self)


@ActionsManage.affect_grid(TITLE_CLONE, 'images/clone.png', unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelClone(XferContainerAcknowledge):
    caption = _("Add a print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        self.item.clone()


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_SINGLE)
@MenuManage.describ('CORE.delete_printmodel')
class PrintModelDelete(XferDelete):
    caption = _("Delete print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'


@ActionsManage.affect_grid(_("Default"), "", unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_printmodel')
class PrintModelSetDefault(XferContainerAcknowledge):
    caption = _("Set default print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        self.item.change_has_default()


@MenuManage.describ('CORE.change_label', FORMTYPE_NOMODAL, 'core.print', _("To manage boards of labels"))
class LabelList(XferListEditor):
    caption = _("Labels")
    icon = "PrintReportLabel.png"
    model = Label
    field_id = 'label'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('CORE.add_label')
class LabelEdit(XferAddEditor):
    caption_add = _("Add a label")
    caption_modify = _("Modify a label")
    icon = "label_help.png"
    model = Label
    field_id = 'label'


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('CORE.delete_label')
class LabelDelete(XferDelete):
    caption = _("Delete label")
    icon = "PrintReportLabel.png"
    model = Label
    field_id = 'label'


@MenuManage.describ('')
class ObjectMerge(XferContainerAcknowledge):
    caption = _("Merge")
    icon = ""
    model = None
    field_id = 'object'

    def _search_model(self):
        modelname = self.getparam('modelname')
        self.model = apps.get_model(modelname)
        XferContainerAcknowledge._search_model(self)

    def fillresponse(self, field_id):
        self.items = self.model.objects.filter(
            id__in=self.getparam(field_id, ()))
        if len(self.items) < 2:
            raise LucteriosException(
                IMPORTANT, _("Impossible: you must to select many records!"))
        if (self.item is None) or (self.item.id is None):
            self.item = self.items[0]
        if self.getparam("CONFIRME") is None:
            dlg = self.create_custom()
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0)
            dlg.add_component(lbl)
            grid = XferCompGrid(self.field_id)
            grid.add_header('value', _('designation'))
            grid.add_header('select', _('is main?'), 'bool')
            for item in self.items:
                grid.set_value(item.id, 'value', six.text_type(item))
                grid.set_value(item.id, 'select', item.id == self.item.id)
            grid.set_location(1, 1)
            grid.add_action(self.request, self.get_action(_("Edit"), "images/show.png"),
                            modal=FORMTYPE_MODAL, close=CLOSE_NO, unique=SELECT_SINGLE, params={"CONFIRME": 'OPEN'})
            grid.add_action(self.request, self.get_action(_("Select"), "images/ok.png"),
                            modal=FORMTYPE_REFRESH, close=CLOSE_NO, unique=SELECT_SINGLE)
            dlg.add_component(grid)
            dlg.add_action(self.get_action(_('Ok'), "images/ok.png"), close=CLOSE_YES, modal=FORMTYPE_MODAL,
                           params={'CONFIRME': 'YES', self.field_id: self.item.id})
            dlg.add_action(WrapAction(_("Cancel"), "images/cancel.png"))
        elif self.getparam("CONFIRME") == 'YES':
            alias_objects = []
            for item in self.items:
                if item.id != self.item.id:
                    alias_objects.append(item.get_final_child())
            self.item.get_final_child().merge_objects(alias_objects)
            self.redirect_action(ActionsManage.get_action_url(self.model.get_long_name(), 'Show', self), params={field_id: self.item.id})
        else:
            self.redirect_action(ActionsManage.get_action_url(self.model.get_long_name(), 'Show', self), params={field_id: self.item.id})


@MenuManage.describ('')
class ObjectPromote(XferContainerAcknowledge):
    caption = _("Promote")
    icon = "images/config.png"
    model = None
    field_id = ''

    def _search_model(self):
        modelname = self.getparam('modelname')
        self.model = apps.get_model(modelname)
        self.field_id = self.getparam('field_id', modelname.lower())
        XferContainerAcknowledge._search_model(self)

    def fillresponse(self):
        if self.getparam("CONFIRME") is None:
            dlg = self.create_custom()
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 2)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('lbl_record')
            lbl.set_value_as_name(_('record'))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('record')
            lbl.set_value(six.text_type(self.item))
            lbl.set_location(2, 1)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('lbl_current')
            lbl.set_value_as_name(_('current model'))
            lbl.set_location(1, 2)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('current')
            lbl.set_value(self.item.__class__._meta.verbose_name)
            lbl.set_location(2, 2)
            dlg.add_component(lbl)
            lbl = XferCompLabelForm('lbl_newmodel')
            lbl.set_value_as_name(_('new model'))
            lbl.set_location(1, 3)
            dlg.add_component(lbl)
            lbl = XferCompSelect('newmodel')
            lbl.set_select(self.item.__class__.get_select_contact_type(False))
            lbl.set_location(2, 3)
            dlg.add_component(lbl)
            dlg.add_action(self.get_action(_('Ok'), "images/ok.png"), close=CLOSE_YES, modal=FORMTYPE_MODAL, params={'CONFIRME': 'YES'})
            dlg.add_action(WrapAction(_("Cancel"), "images/cancel.png"))
        else:
            new_model = apps.get_model(self.getparam('newmodel'))
            field_id_name = "%s_ptr_id" % self.model.__name__.lower()
            new_object = new_model(**{field_id_name: self.item.pk})
            new_object.save()
            new_object.__dict__.update(self.item.__dict__)
            new_object.save()
            self.redirect_action(ActionsManage.get_action_url(self.model.get_long_name(), 'Show', self))

tools.bad_permission_redirect_classaction = Menu


def right_show_wizard(request):
    return Params.getvalue("CORE-Wizard") and (request.user.is_superuser or not secure_mode_connect())


@MenuManage.describ("CORE.change_parameter")
class ConfigurationWizard(XferListEditor):
    caption = _("Configuration wizard")
    icon = "images/config.png"
    model = None
    field_id = ''

    def add_name(self, pos, name):
        lbl = XferCompLabelForm('name_%d' % pos)
        lbl.set_centered()
        lbl.set_value_as_name(name)
        lbl.set_location(0, pos)
        self.add_component(lbl)

    def add_title(self, title, subtitle, helptext=''):
        lbl = XferCompLabelForm('title')
        lbl.set_centered()
        lbl.set_value_as_info(title)
        lbl.set_location(0, 3, 6)
        self.add_component(lbl)
        lbl = XferCompLabelForm('subtitle')
        lbl.set_centered()
        lbl.set_value_as_name(subtitle)
        lbl.set_location(0, 4, 6)
        self.add_component(lbl)
        lbl = XferCompLabelForm('help')
        lbl.set_italic()
        lbl.set_value(helptext + "{[br/]}")
        lbl.set_location(0, 5, 6)
        self.add_component(lbl)

    def header_title(self, step, steplist):
        if step > 0:
            btn = XferCompButton("prec_wizard")
            btn.set_location(0, 0)
            btn.set_is_mini(True)
            btn.set_action(self.request, self.get_action(_("Prec"), "images/left.png"),
                           modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'step': step - 1})
            self.add_component(btn)
        lbl = XferCompLabelForm('progress')
        lbl.set_centered()
        lbl.set_value_as_name(_("progress steps: %(current)d/%(max)d") % {'current': step + 1, "max": len(steplist)})
        lbl.set_location(1, 0, 4)
        self.add_component(lbl)
        if step < (len(steplist) - 1):
            btn = XferCompButton("next_wizard")
            btn.set_location(5, 0)
            btn.set_is_mini(True)
            btn.set_action(self.request, self.get_action(_("Next"), "images/right.png"),
                           modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'step': step + 1})
            self.add_component(btn)
        lbl = XferCompLabelForm('sep1')
        lbl.set_value("{[hr/]}")
        lbl.set_location(0, 1, 6)
        self.add_component(lbl)

    def fillresponse(self, step=0, steplist=[]):
        self.header_title(step, steplist)
        signal_and_lock.Signal.call_signal("conf_wizard", steplist[step], self)
        self.add_action(WrapAction(TITLE_CLOSE, "images/close.png"))


def get_wizard_step_list():
    wizard_list = []
    signal_and_lock.Signal.call_signal("conf_wizard", wizard_list, None)
    wizard_list.sort(key=lambda item: item[1])
    return ";".join([item[0] for item in wizard_list])


@signal_and_lock.Signal.decorate('summary')
def summary_core(xfer):
    if right_show_wizard(xfer.request):
        steplist = get_wizard_step_list()
        if steplist != '':
            btn = XferCompButton("conf_wizard")
            btn.set_location(0, xfer.get_max_row() + 1, 4)
            btn.set_action(xfer.request, ConfigurationWizard.get_action(
                _("Wizard"), "images/config.png"), close=CLOSE_NO, params={'steplist': steplist})
            btn.java_script = """if (typeof Singleton().hide_wizard === 'undefined') {
    current.actionPerformed();
    Singleton().hide_wizard = 1;
}
"""
            xfer.add_component(btn)


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_core(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("core_home", 0))
        wizard_ident.append(("core_users", 100))
    elif (xfer is not None) and (wizard_ident == "core_home"):
        initial_wizard = Params.getvalue("CORE-Wizard")
        param_wizard = xfer.getparam("CORE-Wizard", initial_wizard)
        if initial_wizard != param_wizard:
            Parameter.change_value("CORE-Wizard", param_wizard)
            Params.clear()
        lbl = XferCompLabelForm('title')
        lbl.set_centered()
        lbl.set_value_as_info(six.text_type(settings.APPLIS_NAME))
        lbl.set_location(0, 3, 6)
        xfer.add_component(lbl)
        lbl = XferCompImage('img')
        lbl.type = 'jpg'
        lbl.set_value(settings.APPLIS_LOGO)
        lbl.set_location(2, 4, 2)
        xfer.add_component(lbl)
        lbl = XferCompLabelForm('home')
        lbl.set_value(_('This wizard will help you to configure this software.'))
        lbl.set_location(0, 5, 6)
        xfer.add_component(lbl)
        Params.fill(xfer, ['CORE-Wizard'], 1, 6, False)
        xfer.get_components("CORE-Wizard").set_action(xfer.request, xfer.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
    elif (xfer is not None) and (wizard_ident == "core_users"):
        xfer.add_title(six.text_type(settings.APPLIS_NAME), _("Groups and users"))
        param_lists = ['CORE-connectmode', 'CORE-Wizard']
        Params.fill(xfer, param_lists, 1, xfer.get_max_row() + 1)
        btn = XferCompButton('editparam')
        btn.set_location(4, xfer.get_max_row())
        btn.set_is_mini(True)
        btn.set_action(xfer.request, ParamEdit.get_action(TITLE_MODIFY, 'images/edit.png'), close=CLOSE_NO,
                       params={'params': param_lists})
        xfer.add_component(btn)
        lbl = XferCompLabelForm("nb_user")
        lbl.set_location(1, xfer.get_max_row() + 1)
        lbl.set_value(TEXT_TOTAL_NUMBER % {'name': LucteriosUser._meta.verbose_name_plural, 'count': len(LucteriosUser.objects.all())})
        xfer.add_component(lbl)
        btn = XferCompButton("btnusers")
        btn.set_location(4, xfer.get_max_row())
        btn.set_action(xfer.request, UsersList.get_action(TITLE_MODIFY, "images/edit.png"), close=CLOSE_NO)
        xfer.add_component(btn)
        lbl = XferCompLabelForm("nb_group")
        lbl.set_location(1, xfer.get_max_row() + 1)
        lbl.set_value(TEXT_TOTAL_NUMBER % {'name': LucteriosGroup._meta.verbose_name_plural, 'count': len(LucteriosGroup.objects.all())})
        xfer.add_component(lbl)
        btn = XferCompButton("btngroups")
        btn.set_location(4, xfer.get_max_row())
        btn.set_action(xfer.request, GroupsList.get_action(TITLE_MODIFY, "images/edit.png"), close=CLOSE_NO)
        xfer.add_component(btn)
