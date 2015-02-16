# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from django.utils.translation import ugettext as tt

from lxml import etree

CLOSE_NO = 0
CLOSE_YES = 1
FORMTYPE_NOMODAL = 0
FORMTYPE_MODAL = 1
FORMTYPE_REFRESH = 2
SELECT_NONE = 1
SELECT_SINGLE = 0
SELECT_MULTI = 2

MENU_LIST = {}

def add_sub_menu(ref, parentref, icon, caption, desc):
    class _SubMenu(object):
        # pylint: disable=    too-few-public-methods
        def __init__(self, caption, icon, ref):
            self.caption = caption
            self.icon = icon
            self.modal = FORMTYPE_NOMODAL
            self.is_view_right = ''
            self.extension = ''
            self.action = ''
            self.url_text = ref
    if not MENU_LIST.has_key(parentref):
        MENU_LIST[parentref] = []
    MENU_LIST[parentref].append((_SubMenu(caption, icon, ref), desc))

def describ_action(right, modal=FORMTYPE_NOMODAL, menu_parent=None, menu_desc=None):
    def wrapper(item):
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
            if not MENU_LIST.has_key(menu_parent):
                MENU_LIST[menu_parent] = []
            MENU_LIST[menu_parent].append((item, menu_desc))
        return item
    return wrapper

def check_permission(item, request):
    try:
        if (item.is_view_right != '') and not request.user.has_perm(item.is_view_right):
            return False
    except AttributeError:
        pass
    return True

def raise_bad_permission(item, request):
    if not check_permission(item, request):
        from lucterios.framework.error import LucteriosException
        raise LucteriosException(LucteriosException.IMPORTANT, tt("Bad permission for '%s'") % request.user.username)

def get_action_xml(item, desc='', tag='ACTION', **option):
    try:
        actionxml = etree.Element(tag)
        actionxml.text = item.caption
        actionxml.attrib['id'] = item.url_text
        if hasattr(item, 'icon') and item.icon != "":
            if item.extension == '':
                actionxml.attrib['icon'] = item.icon
            elif item.extension == 'CORE':
                actionxml.attrib['icon'] = "images/"+item.icon
            else:
                actionxml.attrib['icon'] = "%s/images/%s" % (item.extension, item.icon)
            # actionxml.attrib['sizeicon']=filesize(item.icon)
        if item.extension != "":
            actionxml.attrib['extension'] = item.extension
        if item.action != "":
            actionxml.attrib['action'] = item.action
        if desc != "":
            etree.SubElement(actionxml, "HELP").text = desc
        if isinstance(item.modal, int):
            actionxml.attrib['modal'] = str(item.modal)
        for key in option.keys():
            if isinstance(option[key], int):
                actionxml.attrib[key] = str(option[key])
        return actionxml
    except AttributeError:
        return None
