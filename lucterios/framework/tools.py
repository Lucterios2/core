# -*- coding: utf-8 -*-
'''
General tools for Lucterios

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
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from lxml import etree
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import threading

CLOSE_NO = 0
CLOSE_YES = 1
FORMTYPE_NOMODAL = 0
FORMTYPE_MODAL = 1
FORMTYPE_REFRESH = 2
SELECT_NONE = 1
SELECT_SINGLE = 0
SELECT_MULTI = 2

class StubAction(object):
    # pylint: disable=too-few-public-methods
    def __init__(self, caption, icon, extension='', action='', url_text='', pos=0, is_view_right=''):
        self.caption = caption
        self.icon = icon
        self.modal = FORMTYPE_MODAL
        self.is_view_right = is_view_right
        self.url_text = url_text
        if (extension == '') and (action == '') and (url_text.find('/') != -1):
            self.extension, self.action = url_text.split('/')
        else:
            self.extension = extension
            self.action = action
        self.pos = pos

def icon_path(item):
    res_icon_path = ""
    if hasattr(item, 'icon') and item.icon != "":
        if item.url_text.find('/') != -1:
            extension = item.url_text.split('/')[0]
        else:
            extension = item.extension
        if (extension == '') or ('images/' in item.icon):
            res_icon_path = item.icon
        elif extension == 'CORE':
            res_icon_path = "images/" + item.icon
        else:
            res_icon_path = "%s/images/%s" % (extension, item.icon)
    return res_icon_path

def menu_key_to_comp(menu_item):
    try:
        return menu_item[0].pos
    except AttributeError:
        return 0

class ActionsManage(object):

    _ACT_LIST = {}

    _actlock = threading.RLock()

    @classmethod
    def affect(cls, *arg_tuples):
        def wrapper(item):
            cls._actlock.acquire()
            try:
                model_name = arg_tuples[0]
                action_types = arg_tuples[1:]
                for action_type in action_types:
                    ident = "%s@%s" % (model_name, action_type)
                    cls._ACT_LIST[ident] = item
                return item
            finally:
                cls._actlock.release()
        return wrapper

    @classmethod
    def get_act_changed(cls, model_name, action_type, title, icon):
        cls._actlock.acquire()
        try:
            ident = "%s@%s" % (model_name, action_type)
            if ident in cls._ACT_LIST.keys():
                act_class = cls._ACT_LIST[ident]
                return act_class().get_changed(title, icon)
            else:
                return None
        finally:
            cls._actlock.release()

class MenuManage(object):

    _MENU_LIST = {}

    _menulock = threading.RLock()

    @classmethod
    def add_sub(cls, ref, parentref, icon, caption, desc, pos=0):
        cls._menulock.acquire()
        try:
            if parentref not in cls._MENU_LIST.keys():
                cls._MENU_LIST[parentref] = []
            cls._MENU_LIST[parentref].append((StubAction(caption, icon, url_text=ref, pos=pos), desc))
        finally:
            cls._menulock.release()

    @classmethod
    def describ(cls, right, modal=FORMTYPE_MODAL, menu_parent=None, menu_desc=None):
        def wrapper(item):
            cls._menulock.acquire()
            try:
                item.is_view_right = right
                module_items = item.__module__.split('.')
                if module_items[1] == 'CORE':
                    module_items = module_items[1:]
                if module_items[-1][:5] == 'views':
                    module_items = module_items[:-1]
                item.extension = ".".join(module_items)
                item.modal = modal
                item.action = item.__name__[0].lower() + item.__name__[1:]
                item.url_text = r'%s/%s' % (item.extension, item.action)
                if menu_parent != None:
                    if menu_parent not in cls._MENU_LIST.keys():
                        cls._MENU_LIST[menu_parent] = []
                    cls._MENU_LIST[menu_parent].append((item, menu_desc))
                return item
            finally:
                cls._menulock.release()
        return wrapper

    @classmethod
    def fill(cls, request, parentref, parentxml):
        cls._menulock.acquire()
        try:
            if parentref in cls._MENU_LIST.keys():
                sub_menus = cls._MENU_LIST[parentref]
                sub_menus.sort(key=menu_key_to_comp)  # menu_comp)
                for sub_menu_item in sub_menus:
                    if check_permission(sub_menu_item[0], request):
                        new_xml = get_action_xml(sub_menu_item[0], {}, sub_menu_item[1], "MENU")
                        if new_xml != None:
                            parentxml.append(new_xml)
                            cls.fill(request, sub_menu_item[0].url_text, new_xml)
        finally:
            cls._menulock.release()

notfree_mode_connect = None  # pylint: disable=invalid-name
bad_permission_redirect_classaction = None  # pylint: disable=invalid-name

def check_permission(item, request):
    try:
        if item.is_view_right == None:
            return request.user.is_authenticated()
        if notfree_mode_connect is None or notfree_mode_connect():
            if (item.is_view_right != '') and not request.user.has_perm(item.is_view_right):
                return False
    except AttributeError:
        pass
    return True

def raise_bad_permission(item, request):
    if not check_permission(item, request):
        from lucterios.framework.error import LucteriosRedirectException
        if request.user.is_authenticated():
            username = request.user.username
        else:
            username = _("Anonymous user")
        raise LucteriosRedirectException(_("Bad permission for '%s'") % username, bad_permission_redirect_classaction)

def get_actions_xml(actions):
    actionsxml = etree.Element("ACTIONS")
    for (action, options) in actions:
        new_xml = get_action_xml(action, options)
        if new_xml != None:
            actionsxml.append(new_xml)
    return actionsxml

def fill_param_xml(context, params):
    for key, value in params.items():
        new_param = etree.SubElement(context, 'PARAM')
        if isinstance(value, tuple) or isinstance(value, list):
            new_param.text = ";".join(value)
        else:
            new_param.text = value
        new_param.attrib['name'] = key

def get_action_xml(item, option, desc='', tag='ACTION'):
    actionxml = etree.Element(tag)
    actionxml.text = six.text_type(item.caption)
    actionxml.attrib['id'] = item.url_text
    if hasattr(item, 'icon') and item.icon != "":
        actionxml.attrib['icon'] = six.text_type(icon_path(item))
        # actionxml.attrib['sizeicon']=filesize(item.icon)
    if item.extension != "":
        actionxml.attrib['extension'] = item.extension
    if item.action != "":
        actionxml.attrib['action'] = item.action
    if desc != "":
        etree.SubElement(actionxml, "HELP").text = six.text_type(desc)
    actionxml.attrib['modal'] = six.text_type(FORMTYPE_MODAL)
    actionxml.attrib['close'] = six.text_type(CLOSE_YES)
    actionxml.attrib['unique'] = six.text_type(SELECT_NONE)
    if isinstance(item.modal, int):
        actionxml.attrib['modal'] = six.text_type(item.modal)
    if 'params' in option:
        fill_param_xml(actionxml, option['params'])
        del option['params']
    for key in option.keys():  # modal, close, unique
        if isinstance(option[key], six.integer_types):
            actionxml.attrib[key] = six.text_type(option[key])
    return actionxml

def ifplural(count, test_singular, test_plural):
    if count == 1:
        return test_singular
    else:
        return test_plural

def get_corrected_setquery(setquery):
    if setquery.model == Permission:
        ctypes = ContentType.objects.all()  # pylint: disable=no-member
        for ctype in ctypes:
            if ctype.model in ('contenttype', 'logentry', 'permission'):
                setquery = setquery.exclude(content_type=ctype, codename__startswith='add_')
                setquery = setquery.exclude(content_type=ctype, codename__startswith='change_')
                setquery = setquery.exclude(content_type=ctype, codename__startswith='delete_')
            if ctype.model in ('session',):
                setquery = setquery.exclude(content_type=ctype, codename__startswith='add_')
    return setquery

def get_dico_from_setquery(setquery):
    res_dico = {}
    if setquery.model == Permission:
        for record in setquery:
            rigths = six.text_type(record.name).split(" ")
            if rigths[1] == 'add':
                rigth_name = _('add')
            if rigths[1] == 'change':
                rigth_name = _('view')
            if rigths[1] == 'delete':
                rigth_name = _('delete')
            res_dico[six.text_type(record.id)] = "%s | %s %s" % (six.text_type(record.content_type), _("Can"), rigth_name)
    else:
        for record in setquery:
            res_dico[six.text_type(record.id)] = six.text_type(record)
    return res_dico

def get_binay(text):
    if six.PY2:
        return six.binary_type(text)
    else:
        return six.binary_type(text, 'ascii')
