# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext as _
from django.utils import six
from lxml import etree

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.xfercomponents import XferCompTab, XferCompImage, XferCompLabelForm, XferCompButton, \
    XferCompEdit, XferCompFloat, XferCompCheck, XferCompGrid, XferCompCheckList
from lucterios.framework.tools import check_permission, get_action_xml, get_actions_xml, \
    get_dico_from_setquery, icon_path
from lucterios.framework.tools import ifplural, get_value_converted, get_corrected_setquery
from lucterios.framework.tools import FORMTYPE_MODAL, CLOSE_YES, CLOSE_NO
from lucterios.framework.error import LucteriosException, GRAVE
from django.db.utils import IntegrityError

class XferContainerAcknowledge(XferContainerAbstract):

    observer_name = 'Core.Acknowledge'
    title = ""
    msg = ""
    traitment_data = None
    typemsg = 1
    redirect_act = None
    except_msg = ""
    except_classact = None

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.title = ""
        self.msg = ""
        self.traitment_data = None
        self.typemsg = 1
        self.redirect_act = None
        self.except_msg = ""
        self.except_classact = None

    def confirme(self, title):
        self.title = title
        if self.title != "":
            if self.getparam("CONFIRME") is not None:
                return self.params["CONFIRME"] != ""
            else:
                return False
        else:
            return True

    def message(self, title, typemsg=1):
        self.msg = title
        self.typemsg = typemsg

    def traitment(self, icon, waiting_message, finish_message):
        self.traitment_data = [icon, waiting_message, finish_message]
        if self.getparam("RELOAD") is not None:
            return self.params["RELOAD"] != ""
        else:
            return False

    def redirect_action(self, action):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            self.redirect_act = action

    def raise_except(self, error_msg, action=None):
        self.except_msg = error_msg
        self.except_classact = action

    def fillresponse(self):
        pass

    def _get_from_custom(self, request, *args, **kwargs):
        dlg = XferContainerCustom()
        dlg.caption = self.caption
        dlg.extension = self.extension
        dlg.action = self.action
        img_title = XferCompImage('img_title')
        img_title.set_location(0, 0, 1, 2)
        img_title.set_value(self.traitment_data[0])
        dlg.add_component(img_title)

        lbl = XferCompLabelForm("info")
        lbl.set_location(1, 0)
        dlg.add_component(lbl)
        if self.getparam("RELOAD") is not None:
            lbl.set_value("{[br/]}{[center]}" + self.traitment_data[2] + "{[/center]}")
            dlg.add_action(XferContainerAbstract().get_changed(_("Close"), "images/close.png"), {})
        else:
            lbl.set_value("{[br/]}{[center]}" + self.traitment_data[1] + "{[/center]}")
            kwargs["RELOAD"] = "YES"
            btn = XferCompButton("Next")
            btn.set_location(1, 1)
            btn.set_size(50, 300)
            btn.set_action(self.request, self.get_changed(_('Traitment...'), ""), {})
            btn.java_script = "parent.refresh()"
            dlg.add_component(btn)
            dlg.add_action(XferContainerAbstract().get_changed(_("Cancel"), "images/cancel.png"), {})
        return dlg.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        self.fillresponse(**self._get_params())
        if (self.title != '') and (self.getparam("CONFIRME") != "YES"):
            kwargs["CONFIRME"] = "YES"
            dlg = XferContainerDialogBox()
            dlg.caption = "Confirmation"
            dlg.extension = self.extension
            dlg.action = self.action
            dlg.set_dialog(self.title, XFER_DBOX_CONFIRMATION)
            dlg.add_action(self.get_changed(_("Yes"), "images/ok.png"), {'modal':FORMTYPE_MODAL, 'close':CLOSE_YES})
            dlg.add_action(XferContainerAbstract().get_changed(_("No"), "images/cancel.png"), {})
            dlg.closeaction = self.closeaction
            return dlg.get(request, *args, **kwargs)
        elif self.msg != "":
            dlg = XferContainerDialogBox()
            dlg.caption = self.caption
            dlg.set_dialog(self.msg, self.typemsg)
            dlg.add_action(XferContainerAbstract().get_changed(_("Ok"), "images/ok.png"), {})
            dlg.closeaction = self.closeaction
            return dlg.get(request, *args, **kwargs)
        elif self.except_msg != "":
            dlg = XferContainerDialogBox()
            dlg.caption = self.caption
            dlg.set_dialog(self.except_msg, XFER_DBOX_WARNING)
            if self.except_classact is not None:
                except_action = self.except_classact()
                if isinstance(except_action, XferContainerAbstract) and check_permission(except_action, self.request):
                    dlg.add_action(except_action.get_changed(_("Retry"), ""), {})
            dlg.closeaction = self.closeaction
            return dlg.get(request, *args, **kwargs)
        elif self.traitment_data != None:
            return self._get_from_custom(request, *args, **kwargs)
        else:
            return self._finalize()

    def _finalize(self):
        if self.redirect_act != None:
            act_xml = get_action_xml(self.redirect_act, {})
            if act_xml is not None:
                self.responsexml.append(act_xml)
        return XferContainerAbstract._finalize(self)

XFER_DBOX_INFORMATION = 1
XFER_DBOX_CONFIRMATION = 2
XFER_DBOX_WARNING = 3
XFER_DBOX_ERROR = 4

class XferContainerDialogBox(XferContainerAbstract):

    observer_name = "Core.DialogBox"

    msgtype = XFER_DBOX_INFORMATION
    msgtext = ""
    actions = []

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.msgtype = XFER_DBOX_INFORMATION
        self.msgtext = ""
        self.actions = []

    def set_dialog(self, msgtext, msgtype):
        self.msgtype = msgtype
        self.msgtext = msgtext

    def add_action(self, action, options):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            self.actions.append((action, options))

    def _finalize(self):
        text_dlg = etree.SubElement(self.responsexml, "TEXT")
        text_dlg.attrib['type'] = six.text_type(self.msgtype)
        text_dlg.text = six.text_type(self.msgtext)
        if len(self.actions) != 0:
            self.responsexml.append(get_actions_xml(self.actions))
        return XferContainerAbstract._finalize(self)

class XferContainerCustom(XferContainerAbstract):
    # pylint: disable=too-many-public-methods

    observer_name = "Core.Custom"

    def __init__(self, **kwargs):
        XferContainerAbstract.__init__(self, **kwargs)
        self.actions = []
        self.components = {}
        self.tab = 0

    def add_component(self, component):
        component.tab = self.tab
        comp_id = component.get_id()
        self.components[comp_id] = component

    def find_tab(self, tab_name):
        num = -1
        tab_name = six.text_type(tab_name)
        for comp in self.components.values():
            if isinstance(comp, XferCompTab):
                if comp.value == tab_name:
                    num = comp.tab
        return num

    def max_tab(self):
        index = 0
        for comp in self.components.values():
            if isinstance(comp, XferCompTab):
                index = max(index, comp.tab)
        return index

    def new_tab(self, tab_name, num=-1):
        old_num = self.find_tab(tab_name)
        if old_num == -1:
            if num == -1:
                self.tab = self.max_tab() + 1
            else:
                for comp in self.components.values():
                    if comp.tab >= num:
                        comp.tab = comp.tab + 1
                self.tab = num
            new_tab = XferCompTab()
            new_tab.set_value(six.text_type(tab_name))
            new_tab.set_location(-1, -1)
            self.add_component(new_tab)
        else:
            self.tab = old_num

    def get_writing_comp(self, field_name):
        # pylint: disable=protected-access
        from django.db.models.fields import IntegerField, FloatField, BooleanField
        dep_field = self.item._meta.get_field_by_name(field_name)
        if isinstance(dep_field[0], IntegerField):
            comp = XferCompFloat(field_name)
            comp.set_value(getattr(self.item, field_name))
        elif isinstance(dep_field[0], FloatField):
            comp = XferCompFloat(field_name)
            comp.set_value(getattr(self.item, field_name))
        elif isinstance(dep_field[0], BooleanField):
            comp = XferCompCheck(field_name)
            comp.set_value(getattr(self.item, field_name))
        else:
            comp = XferCompEdit(field_name)
            comp.set_value(getattr(self.item, field_name))
        comp.set_needed(dep_field[0].unique or not (dep_field[0].blank or dep_field[0].null))
        comp.description = six.text_type(dep_field[0].verbose_name)
        return comp

    def fill_from_model(self, col, row, readonly, field_names):
        # pylint: disable=protected-access
        for field_name in field_names:
            dep_field = self.item._meta.get_field_by_name(field_name)
            if dep_field[2]:  # field real in model
                lbl = XferCompLabelForm('lbl_' + field_name)
                lbl.set_location(col, row, 1, 1)
                lbl.set_value_as_name(six.text_type(dep_field[0].verbose_name))
                self.add_component(lbl)
                if not dep_field[3]:  # field not many-to-many
                    if readonly:
                        comp = XferCompLabelForm(field_name)
                        comp.set_value(get_value_converted(getattr(self.item, field_name), True))
                    else:
                        comp = self.get_writing_comp(field_name)
                else:
                    comp = XferCompGrid(field_name)
                    comp.add_header("text", six.text_type(dep_field[0].verbose_name))
                    if self.item.id is not None:
                        values = getattr(self.item, field_name).all()
                        for value in values:
                            comp.set_value(value.id, "text", six.text_type(value))
                comp.set_location(col + 1, row, 1, 1)
                self.add_component(comp)
                row += 1

    def _get_scripts_for_selectors(self, field_name, availables):
        sela = get_dico_from_setquery(availables)
        selval = []
        if self.item.id is not None:
            values = getattr(self.item, field_name).all()
            for value in values:
                selval.append(six.text_type(value.id))

        java_script_init = """
    var %(comp)s_current = parent.mContext.get('%(comp)s');
    var %(comp)s_dico = %(sela)s;
    var %(comp)s_valid = '%(selc)s';
    if (%(comp)s_current !== null) {
        %(comp)s_valid = %(comp)s_current;
    }
    """ % {'comp':field_name, 'sela':six.text_type(sela), 'selc':";".join(selval)}
        java_script_init = java_script_init.replace("u'", "'").replace('u"', '"')
        java_script_treat = """
    var valid_list = %(comp)s_valid.split(";")
    var %(comp)s_xml_available = "<SELECT>";
    var %(comp)s_xml_chosen = "<SELECT>";
    for (var key in %(comp)s_dico) {
        var value = %(comp)s_dico[key];
        if (valid_list.indexOf(key) > -1) {
            %(comp)s_xml_chosen += "<CASE id='"+key+"'>"+value+"</CASE>";

        } else {
            %(comp)s_xml_available += "<CASE id='"+key+"'>"+value+"</CASE>";
        }

    }
    %(comp)s_xml_available += "</SELECT>";
    %(comp)s_xml_chosen += "</SELECT>";
    parent.get('%(comp)s_available').setValue(%(comp)s_xml_available);
    parent.get('%(comp)s_chosen').setValue(%(comp)s_xml_chosen);
    if (%(comp)s_current === null) {
        var tmp_cpt = parent.mContext.get('%(comp)s_cpt');
        if (tmp_cpt === null) tmp_cpt=0;
        tmp_cpt += 1;
        if (tmp_cpt === 4) {
            parent.mContext.put('%(comp)s',%(comp)s_valid);
        }
        else {
             parent.mContext.put('%(comp)s_cpt',tmp_cpt);
        }
    }
    """ % {'comp':field_name}
        return java_script_init, java_script_treat

    def selector_from_model(self, col, row, field_name, title_available, title_chosen):
        # pylint: disable=too-many-locals
        dep_field = self.item._meta.get_field_by_name(field_name)  # pylint: disable=protected-access
        if dep_field[2] and dep_field[3]:
            availables = get_corrected_setquery(dep_field[0].rel.to.objects.all())
            java_script_init, java_script_treat = self._get_scripts_for_selectors(field_name, availables)

            lbl = XferCompLabelForm('lbl_' + field_name)
            lbl.set_location(col, row, 1, 1)
            lbl.set_value_as_name(six.text_type(dep_field[0].verbose_name))
            self.add_component(lbl)

            lbl = XferCompLabelForm('hd_' + field_name + '_available')
            lbl.set_location(col + 1, row, 1, 1)
            lbl.set_value_as_header(title_available)
            self.add_component(lbl)

            lista = XferCompCheckList(field_name + '_available')
            lista.set_location(col + 1, row + 1, 1, 5)
            self.add_component(lista)

            lbl = XferCompLabelForm('hd_' + field_name + '_chosen')
            lbl.set_location(col + 3, row, 1, 1)
            lbl.set_value_as_header(title_chosen)
            self.add_component(lbl)

            listc = XferCompCheckList(field_name + '_chosen')
            listc.set_location(col + 3, row + 1, 1, 5)
            self.add_component(listc)

            btn_idx = 0
            for (button_name, button_title, button_script) in [("addall", ">>", """
if (%(comp)s_current !== null) {
    %(comp)s_valid ='';
    for (var key in %(comp)s_dico) {
        if (%(comp)s_valid !== '')
            %(comp)s_valid +=';';
        %(comp)s_valid +=key;
    }
    parent.mContext.put('%(comp)s',%(comp)s_valid);
}
"""), ("add", ">", """
if (%(comp)s_current !== null) {
    var value = parent.get('%(comp)s_available').getValue();
    if (%(comp)s_valid !== '')
        %(comp)s_valid +=';';
    %(comp)s_valid +=value;
parent.mContext.put('%(comp)s',%(comp)s_valid);
}
"""), ("del", "<", """
if (%(comp)s_current !== null) {
    var values = parent.get('%(comp)s_chosen').getValue().split(';');
    var valid_list = %(comp)s_valid.split(';');
    %(comp)s_valid ='';
    for (var key in valid_list) {
        selected_val = valid_list[key];
        if (values.indexOf(selected_val) === -1) {
            if (%(comp)s_valid !== '')
                %(comp)s_valid +=';';
            %(comp)s_valid +=selected_val;
        }
    }
    parent.mContext.put('%(comp)s',%(comp)s_valid);
}
"""), ("delall", "<<", """
if (%(comp)s_current !== null) {
    %(comp)s_valid ='';
    parent.mContext.put('%(comp)s',%(comp)s_valid);
}
""")]:
                btn = XferCompButton(field_name + '_' + button_name)
                btn.set_action(self.request, XferContainerAcknowledge().get_changed(button_title, ""), {'close':CLOSE_NO})
                btn.set_location(col + 2, row + 1 + btn_idx, 1, 1)
                btn.set_is_mini(True)
                btn.java_script = java_script_init + button_script % {'comp':field_name} + java_script_treat
                self.add_component(btn)
                btn_idx += 1

    def add_action(self, action, option, pos_act=-1):
        if isinstance(action, XferContainerAbstract) and check_permission(action, self.request):
            if pos_act != -1:
                self.actions.insert(pos_act, (action, option))
            else:
                self.actions.append((action, option))

    def get_sort_components(self):
        final_components = {}
        sortedkey_components = []
        for comp in self.components.values():
            comp_id = comp.get_id()
            sortedkey_components.append(comp_id)
            final_components[comp_id] = comp
        sortedkey_components.sort()
        return sortedkey_components, final_components

    def _finalize(self):
        if len(self.components) != 0:
            sortedkey_components, final_components = self.get_sort_components()
            xml_comps = etree.SubElement(self.responsexml, "COMPONENTS")
            for key in sortedkey_components:
                comp = final_components[key]
                xml_comp = comp.get_reponse_xml()
                xml_comps.append(xml_comp)
        if len(self.actions) != 0:
            self.responsexml.append(get_actions_xml(self.actions))
        return XferContainerAbstract._finalize(self)

class XferAddEditor(XferContainerCustom):

    caption_add = ''
    caption_modify = ''
    fieldnames = []

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        if self.getparam("SAVE") != "YES":
            if self.is_new:
                self.caption = self.caption_add
            else:
                self.caption = self.caption_modify
            img = XferCompImage('img')
            img.set_value(icon_path(self))
            img.set_location(0, 0, 1, 6)
            self.add_component(img)
            self.fill_from_model(1, 0, False, self.fieldnames)
            self.params["SAVE"] = "YES"
            self.add_action(self.__class__().get_changed(_('Ok'), 'images/ok.png'), {})
            self.add_action(XferContainerAcknowledge().get_changed(_('Cancel'), 'images/cancel.png'), {})
            return self._finalize()
        else:
            del self.params["SAVE"]
            save = XferSave()
            save.model = self.model
            save.field_id = self.field_id
            save.caption = self.caption
            save.raise_except_class = self.__class__

            save.closeaction = self.closeaction
            return save.get(request, *args, **kwargs)

class XferDelete(XferContainerAcknowledge):

    def _search_model(self):
        if self.model is None:
            raise LucteriosException(GRAVE, _("No model"))
        if isinstance(self.field_id, tuple):
            for field_id in self.field_id:
                ids = self.getparam(field_id)
                if ids is not None:
                    self.field_id = field_id

                    break
        else:
            ids = self.getparam(self.field_id)
        if ids is None:
            raise LucteriosException(GRAVE, _("No selection"))
        ids = ids.split(';')
        self.items = self.model.objects.filter(pk__in=ids)

    def fillresponse(self):
        # pylint: disable=protected-access
        if self.confirme(ifplural(len(self.items), _("Do you want delete this %(name)s ?") % {'name':self.model._meta.verbose_name}, \
                                    _("Do you want delete those %(nb)s %(name)s ?") % {'nb':len(self.items), 'name':self.model._meta.verbose_name_plural})):
            for item in self.items:
                item.delete()

class XferSave(XferContainerAcknowledge):

    raise_except_class = None

    def fillresponse(self):
        if self.has_changed:
            try:
                self.item.save()
                self.has_changed = False
                if self.fill_manytomany_fields():
                    self.item.save()
            except IntegrityError:
                self.raise_except(_("This record exists yet!"), self.raise_except_class)
