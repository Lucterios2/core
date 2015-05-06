# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, StubAction, \
    ActionsManage, FORMTYPE_REFRESH, SELECT_SINGLE, CLOSE_NO, FORMTYPE_MODAL
from lucterios.framework.xferbasic import XferContainerMenu
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom, XFER_DBOX_INFORMATION
from lucterios.framework.xfercomponents import XferCompLABEL, XferCompPassword, XferCompImage, XferCompLabelForm, XferCompGrid, XferCompSelect, \
    XferCompMemo, XferCompFloat
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock, tools
from lucterios.CORE.parameters import Params, secure_mode_connect
from lucterios.CORE.models import Parameter, Label, PrintModel
from django.utils import six
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, \
    XferDelete, XferSave

MenuManage.add_sub('core.general', None, 'images/general.png', _('General'), _('Generality'), 1)
MenuManage.add_sub('core.admin', None, 'images/admin.png', _('Management'), _('Manage settings and configurations.'), 100)

@MenuManage.describ('')
class Unlock(XferContainerAcknowledge):

    def fillresponse(self):
        signal_and_lock.RecordLocker.unlock(self.request, self.params)

signal_and_lock.unlocker_action_class = Unlock

@MenuManage.describ('')
class Menu(XferContainerMenu):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated() or not secure_mode_connect():
            return XferContainerMenu.get(self, request, *args, **kwargs)
        else:
            from lucterios.CORE.views_auth import Authentification
            auth = Authentification()
            return auth.get(request, *args, **kwargs)

@MenuManage.describ(None, FORMTYPE_MODAL, 'core.general', _("To Change your password."))
class ChangePassword(XferContainerCustom):
    caption = _("_Password")
    icon = "passwd.png"

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value('images/passwd.png')
        img.set_location(0, 0, 1, 3)
        self.add_component(img)

        lbl = XferCompLABEL('lbl_oldpass')
        lbl.set_location(1, 0, 1, 1)
        lbl.set_value(_("old password"))
        self.add_component(lbl)
        pwd = XferCompPassword('oldpass')
        pwd.set_location(2, 0, 1, 1)
        self.add_component(pwd)

        lbl = XferCompLABEL('lbl_newpass1')
        lbl.set_location(1, 1, 1, 1)
        lbl.set_value(_("new password"))
        self.add_component(lbl)
        pwd = XferCompPassword('newpass1')
        pwd.set_location(2, 1, 1, 1)
        self.add_component(pwd)

        lbl = XferCompLABEL('lbl_newpass2')
        lbl.set_location(1, 2, 1, 1)
        lbl.set_value(_("new password (again)"))
        self.add_component(lbl)
        pwd = XferCompPassword('newpass2')
        pwd.set_location(2, 2, 1, 1)
        self.add_component(pwd)

        self.add_action(ModifyPassword().get_changed(_('Ok'), 'images/ok.png'), {})
        self.add_action(StubAction(_('Cancel'), 'images/cancel.png'), {})

@MenuManage.describ('')
class ModifyPassword(XferContainerAcknowledge):
    caption = _("_Password")
    icon = "passwd.png"

    def fillresponse(self, oldpass='', newpass1='', newpass2=''):
        if not self.request.user.check_password(oldpass):
            raise LucteriosException(IMPORTANT, _("Bad current password!"))

        if newpass1 != newpass2:

            raise LucteriosException(IMPORTANT, _("The passwords are differents!"))
        self.request.user.set_password(newpass1)
        self.request.user.save()
        self.message(_("Password modify"), XFER_DBOX_INFORMATION)

@signal_and_lock.Signal.decorate('config')
def config_core(xfer):
    Params.fill(xfer, ['CORE-connectmode'], 1, 1)
    xfer.params['params'].append('CORE-connectmode')

@MenuManage.describ('CORE.change_parameter', FORMTYPE_MODAL, 'core.admin', _("To view and to modify main parameters."))
class Configuration(XferContainerCustom):
    caption = _("Main configuration")
    icon = "config.png"

    def fillresponse(self):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 10)
        img_title.set_value('images/config.png')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 3)
        lab.set_value('{[br/]}{[center]}{[b]}{[u]}%s{[/u]}{[/b]}{[/center]}' % _("Software configuration"))
        self.add_component(lab)
        self.params['params'] = []
        signal_and_lock.Signal.call_signal("config", self)
        self.add_action(ParamEdit().get_changed(_('Modify'), 'images/edit.png'), {'close':0})
        self.add_action(StubAction(_('Close'), 'images/close.png'), {})

@MenuManage.describ('CORE.add_parameter')
class ParamEdit(XferContainerCustom):
    caption = _("Parameters")
    icon = "config.png"

    def fillresponse(self, params=()):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0)
        img_title.set_value('images/config.png')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0)
        lab.set_value('{[br/]}{[center]}{[b]}{[u]}%s{[/u]}{[/b]}{[/center]}' % _("Edition of parameters"))
        self.add_component(lab)
        Params.fill(self, params, 1, 1, False)
        self.add_action(ParamSave().get_changed(_('Ok'), 'images/ok.png'), {})
        self.add_action(StubAction(_('Cancel'), 'images/cancel.png'), {})

@MenuManage.describ('CORE.add_parameter')
class ParamSave(XferContainerAcknowledge):
    caption = _("Parameters")
    icon = "config.png"

    def fillresponse(self, params=()):
        for pname in params:
            db_param = Parameter.objects.get(name=pname)  # pylint: disable=no-member
            if db_param.typeparam == 3:
                db_param.value = six.text_type(self.getparam(pname) == '1')
            else:
                db_param.value = self.getparam(pname)
            db_param.save()
        Params.clear()

MenuManage.add_sub("core.extensions", 'core.admin', "images/config_ext.png", _("_Extensions (conf.)"), _("To manage of modules configurations."), 20)

MenuManage.add_sub("core.print", 'core.admin', "images/PrintReport.png", _("Report and print"), _("To manage reports and tools of printing."), 30)

@MenuManage.describ('CORE.change_printmodel', FORMTYPE_NOMODAL, 'core.print', _("To Manage printing models."))
class PrintModelList(XferContainerCustom):
    caption = _("Print models")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self, modelname=''):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 2)
        img_title.set_value('images/PrintReportModel.png')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 3)
        lab.set_value_as_title(_("Print models"))
        self.add_component(lab)

        lab = XferCompLabelForm('lblmodelname')
        lab.set_location(1, 1)
        lab.set_value_as_name(_('model'))
        self.add_component(lab)
        model_list = {}
        for print_model in PrintModel.objects.all():  # pylint: disable=no-member
            if not print_model.modelname in model_list.keys():
                model_list[print_model.modelname] = print_model.model_associated_title()
                if modelname == '':
                    modelname = print_model.modelname
        model_sel = XferCompSelect('modelname')
        model_sel.set_location(2, 1, 2)
        model_sel.set_select(model_list)
        model_sel.set_value(modelname)
        model_sel.set_action(self.request, self.get_changed("", ""), {'modal':FORMTYPE_REFRESH, 'close':CLOSE_NO})
        self.add_component(model_sel)

        items = PrintModel.objects.filter(modelname=modelname)  # pylint: disable=no-member
        grid = XferCompGrid('print_model')
        grid.set_location(1, 2, 3)
        grid.set_model(items, ['name', 'kind'], self)
        grid.add_action(self.request, PrintModelEdit().get_changed(_('edit'), 'images/edit.png'), {'unique':SELECT_SINGLE})
        grid.add_action(self.request, PrintModelClone().get_changed(_('clone'), 'images/add.png'), {'unique':SELECT_SINGLE})
        grid.add_action(self.request, PrintModelDelete().get_changed(_('delete'), 'images/suppr.png'), {'unique':SELECT_SINGLE})
        self.add_component(grid)

        self.add_action(StubAction(_('Close'), 'images/close.png'), {})

@MenuManage.describ('CORE.add_printmodel')
class PrintModelEdit(XferContainerCustom):
    # pylint: disable=too-many-public-methods
    caption_add = _("Add a print model")
    caption_modify = _("Modify a print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fill_menu_memo(self, memo_comp):
        for name, value in self.item.model_associated().get_print_fields():
            memo_comp.add_sub_menu(name, value)

    def fillresponse(self):
        img_title = XferCompImage('img')
        img_title.set_location(0, 0, 1, 6)
        img_title.set_value('images/PrintReportModel.png')
        self.add_component(img_title)
        lab = XferCompLabelForm('title')
        lab.set_location(1, 0, 2)
        lab.set_value_as_title(_("Print models"))
        self.add_component(lab)
        self.fill_from_model(1, 1, False, ['name'])
        self.fill_from_model(1, 2, True, ['kind'])
        if self.item.kind == 0:
            self._fill_listing_editor()
        elif self.item.kind == 1:
            self._fill_label_editor()
        elif self.item.kind == 2:
            self._fill_report_editor()
        self.add_action(PrintModelSave().get_changed(_("ok"), "images/ok.png"), {})
        self.add_action(StubAction(_('cancel'), 'images/cancel.png'), {})

    def _fill_listing_editor(self):
        lab = XferCompLabelForm('lbl_page_width')
        lab.set_location(1, 3)
        lab.set_value_as_name(_("page width"))
        self.add_component(lab)
        edt = XferCompFloat('page_width', 0, 9999, 0)
        edt.set_location(2, 3, 2)
        edt.set_value(self.item.page_width)
        self.add_component(edt)
        lab = XferCompLabelForm('lbl_page_heigth')
        lab.set_location(1, 4)
        lab.set_value_as_name(_("page heigth"))
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
        edit.set_location(1, 3, 2)
        edit.set_size(100, 500)
        edit.with_hypertext = True
        self.fill_menu_memo(edit)
        self.add_component(edit)

    def _fill_report_editor(self):
        pass

@MenuManage.describ('CORE.add_printmodel')
class PrintModelSave(XferSave):
    caption = _("print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
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
        else:
            XferSave.fillresponse(self)

@MenuManage.describ('CORE.add_printmodel')
class PrintModelClone(XferContainerAcknowledge):
    # pylint: disable=too-many-public-methods
    caption = _("Add a print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

    def fillresponse(self):
        new_model = PrintModel()
        new_model.name = _("copy of %s") % self.item.name
        new_model.kind = self.item.kind
        new_model.modelname = self.item.modelname

        new_model.value = self.item.value
        new_model.save()

@MenuManage.describ('CORE.delete_printmodel')
class PrintModelDelete(XferDelete):
    caption = _("Delete print model")
    icon = "PrintReportModel.png"
    model = PrintModel
    field_id = 'print_model'

# @MenuManage.describ('', FORMTYPE_NOMODAL, 'core.print', _("To print old saved report."))
# class FinalreportList(XferContainerAcknowledge):
#     caption = _("_Saved reports")
#     icon = "PrintReportSave.png"
#

@MenuManage.describ('CORE.change_label', FORMTYPE_NOMODAL, 'core.print', _("To manage boards of labels"))
class LabelList(XferListEditor):
    caption = _("Labels")
    icon = "PrintReportLabel.png"
    model = Label
    field_id = 'label'

@ActionsManage.affect('Label', 'edit', 'add')
@MenuManage.describ('CORE.add_label')
class LabelEdit(XferAddEditor):
    # pylint: disable=too-many-public-methods
    caption_add = _("Add a label")
    caption_modify = _("Modify a label")
    icon = "etiquette.png"
    model = Label
    field_id = 'label'

@ActionsManage.affect('Label', 'del')
@MenuManage.describ('CORE.delete_label')
class LabelDelete(XferDelete):
    caption = _("Delete label")
    icon = "PrintReportLabel.png"
    model = Label
    field_id = 'label'

tools.bad_permission_redirect_classaction = Menu
