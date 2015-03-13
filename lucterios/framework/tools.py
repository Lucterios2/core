# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils import six, formats
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

def icon_path(item):
    res_icon_path = ""
    if hasattr(item, 'icon') and item.icon != "":
        if (item.extension == '') or ('images/' in item.icon):
            res_icon_path = item.icon
        elif item.extension == 'CORE':
            res_icon_path = "images/" + item.icon
        else:
            res_icon_path = "%s/images/%s" % (item.extension, item.icon)
    return res_icon_path

def menu_key_to_comp(menu_item):
    try:
        return menu_item[0].pos
    except AttributeError:
        return 0

class MenuManage(object):

    _MENU_LIST = {}

    _menulock = threading.RLock()

    @classmethod
    def add_sub(cls, ref, parentref, icon, caption, desc, pos=0):
        class _SubMenu(object):
            # pylint: disable=too-few-public-methods
            def __init__(self, caption, icon, ref):
                self.caption = caption
                self.icon = icon
                self.modal = FORMTYPE_NOMODAL
                self.is_view_right = ''
                self.extension = ''
                self.action = ''
                self.url_text = ref
                self.pos = pos
        cls._menulock.acquire()
        try:
            if parentref not in cls._MENU_LIST.keys():
                cls._MENU_LIST[parentref] = []
            cls._MENU_LIST[parentref].append((_SubMenu(caption, icon, ref), desc))
        finally:
            cls._menulock.release()

    @classmethod
    def describ(cls, right, modal=FORMTYPE_NOMODAL, menu_parent=None, menu_desc=None):
        def wrapper(item):
            cls._menulock.acquire()
            try:
                item.is_view_right = right
                module_items = item.__module__.split('.')
                if module_items[0] == 'lucterios':
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

notfree_mode_connect = None # pylint: disable=invalid-name
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
    if isinstance(item.modal, int):
        actionxml.attrib['modal'] = six.text_type(item.modal)
    actionxml.attrib['modal'] = six.text_type(FORMTYPE_MODAL)
    actionxml.attrib['close'] = six.text_type(CLOSE_YES)
    actionxml.attrib['unique'] = six.text_type(SELECT_NONE)
    for key in option.keys():  # modal, close, unique
        if isinstance(option[key], six.integer_types):
            actionxml.attrib[key] = six.text_type(option[key])
    return actionxml

def ifplural(count, test_singular, test_plural):
    if count == 1:
        return test_singular
    else:
        return test_plural

def get_value_converted(value, bool_textual=False):
    # pylint: disable=too-many-return-statements
    import datetime
    if isinstance(value, datetime.datetime):
        return formats.date_format(value, "SHORT_DATETIME_FORMAT")
    elif isinstance(value, datetime.date):
        return formats.date_format(value, "SHORT_DATE_FORMAT")
    elif isinstance(value, datetime.time):
        return formats.date_format(value, "SHORT_TIME_FORMAT")
    elif isinstance(value, bool):
        if bool_textual:
            if value:
                return _("Yes")
            else:
                return _("No")
        else:
            if value:
                return six.text_type("1")
            else:
                return six.text_type("0")
    elif value is None:
        return six.text_type("---")
    else:
        return six.text_type(value)

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
