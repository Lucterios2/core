# -*- coding: utf-8 -*-
'''
Basic abstract viewer classes for Lucterios

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
from lxml import etree
from inspect import isfunction
from logging import getLogger

from django.utils.translation import ugettext as _
from django.utils import translation, six
from django.http import HttpResponse
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.fields.related import ForeignKey

from lucterios.framework.tools import fill_param_xml, get_icon_path, WrapAction, FORMTYPE_MODAL,\
    CLOSE_YES
from lucterios.framework.error import LucteriosException, get_error_trace, IMPORTANT
from lucterios.framework import signal_and_lock

NULL_VALUE = 'NULL'


class XferContainerAbstract(View):

    observer_name = ''
    extension = ""
    action = ""
    caption = ""
    closeaction = None
    icon = ""
    url_text = ""
    # is_view_right = ""
    modal = None

    model = None
    field_id = ''
    locked = False
    readonly = False

    def __init__(self, **kwargs):
        View.__init__(self, **kwargs)
        self.language = ''
        self.request = None
        self.params = {}
        self.responsesxml = etree.Element('REPONSES')
        self.responsexml = etree.SubElement(self.responsesxml, 'REPONSE')
        self.items = None
        self.item = None
        self.is_new = False
        self.has_changed = False

    @classmethod
    def initclass(cls, right):
        module_items = cls.__module__.split('.')
        if module_items[1] == 'CORE':
            module_items = module_items[1:]
        if module_items[-1][:5] == 'views':
            module_items = module_items[:-1]
        extension = ".".join(module_items)
        action = cls.__name__[0].lower() + cls.__name__[1:]
        if isfunction(right):
            cls.is_view_right = (right,)
        else:
            cls.is_view_right = right
        cls.url_text = r'%s/%s' % (extension, action)

    @classmethod
    def icon_path(cls, icon_path=None):
        if icon_path is None:
            icon_path = getattr(cls, 'icon', '')
        res_icon_path = get_icon_path(icon_path, cls.url_text, cls.extension)
        return res_icon_path

    @classmethod
    def get_action(cls, caption=None, icon_path=None):
        if caption is None:
            caption = cls.caption
        if icon_path is None:
            icon_path = getattr(cls, 'icon', '')
        ret_act = WrapAction(caption, icon_path, url_text=cls.url_text,
                             is_view_right=getattr(cls, 'is_view_right', None))
        return ret_act

    def getparam(self, key, default_value=None):
        if key in self.params.keys():
            param_value = self.params[key]
            try:
                if isinstance(default_value, bool):
                    param_value = (param_value != 'False') and (param_value != '0') and (
                        param_value != '') and (param_value != 'n')
                elif isinstance(default_value, int):
                    if param_value == NULL_VALUE:
                        param_value = None
                    else:
                        param_value = int(param_value)
                elif isinstance(default_value, float):
                    if param_value == NULL_VALUE:
                        param_value = None
                    else:
                        param_value = float(param_value)
                elif isinstance(default_value, tuple):
                    if param_value == '':
                        param_value = ()
                    else:
                        param_value = tuple(param_value.split(';'))
                elif isinstance(default_value, list):
                    if param_value == '':
                        param_value = []
                    else:
                        param_value = param_value.split(';')
            except ValueError:
                param_value = default_value
            return param_value
        else:
            return default_value

    def _load_unique_record(self, itemid):
        try:
            self.item = self.model.objects.get(id=itemid).get_final_child()
            self.item.set_context(self)
            if not self.readonly:
                self.fill_simple_fields()
                self.fill_manytomany_fields()
            else:
                self.clear_fields_in_params()
            if self.locked:
                lock_params = signal_and_lock.RecordLocker.lock(
                    self.request, self.item)
                self.params.update(lock_params)
                if signal_and_lock.unlocker_view_class is not None:
                    self.set_close_action(
                        signal_and_lock.unlocker_view_class.get_action())
        except ObjectDoesNotExist:
            raise LucteriosException(
                IMPORTANT, _("This record not exist!\nRefresh your application."))

    def _search_model(self):
        self.has_changed = False
        if self.model is not None:
            if isinstance(self.field_id, six.integer_types):
                ids = six.text_type(self.field_id)
            else:
                ids = self.getparam(self.field_id)
            if ids is not None:
                ids = ids.split(';')
                if len(ids) == 1:
                    self._load_unique_record(ids[0])
                    self.items = [self.item]
                else:
                    self.items = self.model.objects.filter(id__in=ids)
            else:
                self.item = self.model()
                self.is_new = True
                self.fill_simple_fields()

    def clear_fields_in_params(self):
        field_names = [
            f.name for f in self.item._meta.get_fields()]
        for field_name in field_names:
            dep_field = self.item._meta.get_field(
                field_name)
            if not dep_field.auto_created or dep_field.concrete:
                if field_name in self.params.keys():
                    del self.params[field_name]

    def fill_simple_fields(self):
        field_names = [
            f.name for f in self.item._meta.get_fields()]
        for field_name in field_names:
            dep_field = self.item._meta.get_field(
                field_name)
            if not dep_field.auto_created or dep_field.concrete:
                new_value = self.getparam(field_name)
                if new_value is not None:
                    if not (dep_field.is_relation and dep_field.many_to_many):
                        from django.db.models.fields import BooleanField
                        if new_value == NULL_VALUE:
                            new_value = None
                        if isinstance(dep_field, BooleanField):
                            new_value = new_value != '0' and new_value != 'n'
                        if isinstance(dep_field, ForeignKey):
                            try:
                                pk_id = int(new_value)
                                if pk_id <= 0:
                                    new_value = None
                                else:
                                    new_value = dep_field.remote_field.model.objects.get(
                                        pk=pk_id)
                            except ValueError:
                                new_value = None
                        if dep_field.null or (new_value is not None):
                            setattr(self.item, field_name, new_value)
                        self.has_changed = True
        return self.has_changed

    def fill_manytomany_fields(self):
        field_names = [
            f.name for f in self.item._meta.get_fields()]
        for field_name in field_names:
            dep_field = self.item._meta.get_field(
                field_name)
            if (not dep_field.auto_created or dep_field.concrete) and (dep_field.is_relation and dep_field.many_to_many):
                new_value = self.getparam(field_name)
                if new_value is not None:
                    relation_model = dep_field.remote_field.model
                    if new_value != '':
                        new_value = relation_model.objects.filter(
                            id__in=new_value.split(';'))
                    else:
                        new_value = relation_model.objects.filter(id__in=[])
                    setattr(self.item, field_name, new_value)
                    self.has_changed = True
        return self.has_changed

    def _initialize(self, request, *_, **kwargs):
        if hasattr(self.__class__, 'is_view_right'):
            self.get_action().raise_bad_permission(request)
        if hasattr(request, 'session'):
            request.session.set_expiry(12 * 60)  # 12 min of idle timeout
        path_list = request.path.split('/')
        self.extension, self.action = path_list[-2:]
        self.request = request
        for key in kwargs.keys():
            self.params[key] = kwargs[key]
        for key in request.GET.keys():
            self.params[key] = request.GET[key]
        for key in request.POST.keys():
            self.params[key] = request.POST[key]
        self.language = translation.get_language_from_request(request)
        translation.activate(self.language)
        self._search_model()

    def check_action_permission(self, action):
        assert (action is None) or isinstance(action, WrapAction)
        return isinstance(action, WrapAction) and action.check_permission(self.request)

    def set_close_action(self, action, modal=FORMTYPE_MODAL, close=CLOSE_YES, params=None):
        if self.check_action_permission(action):
            self.closeaction = (action, modal, close, params)

    def fillresponse(self):
        pass

    def _finalize(self):
        self.responsexml.attrib['observer'] = self.observer_name
        self.responsexml.attrib['source_extension'] = self.extension
        self.responsexml.attrib['source_action'] = self.action
        titlexml = etree.Element("TITLE")
        titlexml.text = self.caption.replace('_', '')
        if titlexml.text != '':
            self.responsexml.insert(0, titlexml)
        if len(self.params) > 0:
            context = etree.Element("CONTEXT")
            fill_param_xml(context, self.params)
            self.responsexml.insert(1, context)
        if self.closeaction is not None:
            etree.SubElement(self.responsexml, "CLOSE_ACTION").append(
                self.closeaction[0].get_action_xml(modal=self.closeaction[1], close=self.closeaction[2], params=self.closeaction[3]))

    def get_response(self):
        return HttpResponse(etree.tostring(self.responsesxml, xml_declaration=True, pretty_print=True, encoding='utf-8'))

    def _get_params(self):
        params = {}
        import inspect
        spec = inspect.getargspec(self.fillresponse)
        if isinstance(spec.defaults, tuple):
            diff = len(spec.args) - len(spec.defaults)
        else:
            diff = len(spec.args)
        for arg_id in range(1, len(spec.args)):
            arg_name = spec.args[arg_id]
            if arg_id >= diff:
                default_val = spec.defaults[arg_id - diff]
            else:
                default_val = None
            params[arg_name] = self.getparam(arg_name, default_val)
        return params

    def get(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(
            ">> get %s [%s]", request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            getLogger("lucterios.core.request").debug(
                "... get params=%s", self.params)
            self.fillresponse(**self._get_params())
            self._finalize()
            res = self.get_response()
            return res
        finally:
            getLogger("lucterios.core.request").debug(
                "<< get %s [%s]", request.path, request.user)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class XferContainerMenu(XferContainerAbstract):

    observer_name = 'core.menu'

    def fillresponse(self):
        from lucterios.framework.tools import MenuManage
        main_menu = etree.SubElement(self.responsexml, "MENUS")
        MenuManage.fill(self.request, None, main_menu)


class XferContainerException(XferContainerAbstract):

    observer_name = 'core.exception'
    exception = None

    def __init__(self):
        XferContainerAbstract.__init__(self)
        self.exception = None

    def set_except(self, exception):
        if not isinstance(exception, LucteriosException):
            getLogger(__name__).exception(exception)
        self.exception = exception

    def fillresponse(self):
        type_text = self.exception.__class__.__name__
        msg_text = six.text_type(self.exception)
        if isinstance(self.exception, LucteriosException):
            code_text = six.text_type(self.exception.code)
        else:
            code_text = '0'
        expt = etree.SubElement(self.responsexml, "EXCEPTION")
        etree.SubElement(expt, 'MESSAGE').text = msg_text
        etree.SubElement(expt, 'CODE').text = code_text
        etree.SubElement(expt, 'DEBUG_INFO').text = get_error_trace()
        etree.SubElement(expt, 'TYPE').text = type_text
        getLogger("lucterios.core.exception").warning(
            "type %s: code=%s - message=%s", type_text, code_text, msg_text)
