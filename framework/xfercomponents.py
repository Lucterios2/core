# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils import six
from lxml import etree

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.tools import check_permission, get_action_xml

class XferComponent(object):
    # pylint: disable=too-many-instance-attributes

    def __init__(self, name):
        self.name = name
        self._component_ident = ""
        self.value = ""
        self.tab = 0
        self.col = 0
        self.row = 0
        self.vmin = ""
        self.hmin = ""
        self.vmax = ""
        self.hmax = ""
        self.colspan = 1
        self.rowspan = 1
        self.description = ""
        self.needed = False

    def get_ident(self):
        return self._component_ident

    def set_location(self, col, row, colspan=1, rowspan=1):
        self.col = col
        self.row = row
        self.colspan = colspan
        self.rowspan = rowspan

    def set_size(self, vmin, hmin, vmax="", hmax=""):
        self.vmin = vmin
        self.hmin = hmin
        self.vmax = vmax
        self.hmax = hmax

    def set_value(self, value):
        self.value = value

    def set_needed(self, needed):
        self.needed = needed

    def _get_content(self):
        return self.value

    def get_id(self):
        text = ""
        if isinstance(self.tab, six.integer_types):
            text += "tab=%4d" % self.tab
        else:
            text += "tab=%4d" % 0
        if isinstance(self.row, six.integer_types) and (self.row >= 0):
            text += "_y=%4d" % self.row
        else:
            text += "_y=    "
        if isinstance(self.col, six.integer_types) and (self.col >= 0):
            text += "_x=%4d" % self.col
        else:
            text += "_x=    "
        return text

    def _get_attribut(self, compxml):
        compxml.attrib['name'] = self.name
        compxml.attrib['description'] = self.description
        if isinstance(self.tab, six.integer_types):
            compxml.attrib['tab'] = six.text_type(self.tab)
        if isinstance(self.col, six.integer_types):
            compxml.attrib['col'] = six.text_type(self.col)
        if isinstance(self.row, six.integer_types):
            compxml.attrib['row'] = six.text_type(self.row)
        if isinstance(self.colspan, six.integer_types):
            compxml.attrib['colspan'] = six.text_type(self.colspan)
        if isinstance(self.rowspan, six.integer_types):
            compxml.attrib['rowspan'] = six.text_type(self.rowspan)
        if isinstance(self.vmin, six.integer_types):
            compxml.attrib['VMin'] = six.text_type(self.vmin)
        if isinstance(self.hmin, six.integer_types):
            compxml.attrib['HMin'] = six.text_type(self.hmin)
        if isinstance(self.vmax, six.integer_types):
            compxml.attrib['VMax'] = six.text_type(self.vmax)
        if isinstance(self.hmax, six.integer_types):
            compxml.attrib['VMax'] = six.text_type(self.hmax)

    def get_reponse_xml(self):
        compxml = etree.Element(self._component_ident)
        self._get_attribut(compxml)
        compxml.text = self._get_content()
        return compxml

class XferCompTab(XferComponent):

    def __init__(self):
        XferComponent.__init__(self, '')
        self._component_ident = "TAB"

    def set_value(self, value):
        self.value = value.trim()

class XferCompLABEL(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "LABEL"

    def set_value(self, value):
        self.value = value.trim()

class XferCompImage(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "IMAGE"

class XferCompLabelForm(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "LABELFORM"

class XferCompButton(XferComponent):

    def __init__(self, name):
        XferComponent.__init__(self, name)
        self._component_ident = "BUTTON"
        self.action = None
        self.java_script = ""
        self.clickname = ""
        self.clickvalue = ""
        self.is_mini = False

    def set_click_info(self, clickname, clickvalue):
        self.clickname = clickname
        self.clickvalue = clickvalue

    def set_is_mini(self, is_mini):
        if is_mini:
            self.is_mini = True
        else:
            self.is_mini = False

    def set_action(self, request, action, **option):
        if isinstance(action, XferContainerAbstract) and check_permission(action, request):
            self.action = (action, option)

    def _get_attribut(self, compxml):
        XferComponent._get_attribut(self, compxml)
        if self.clickname != '':
            compxml.attrib['clickname'] = six.text_type(self.clickname)
            compxml.attrib['clickvalue'] = six.text_type(self.clickvalue)
        if self.is_mini:
            compxml.attrib['isMini'] = '1'

    def get_reponse_xml(self):
        compxml = XferComponent.get_reponse_xml(self)
        if self.action is not None:
            xml_acts = etree.SubElement(compxml, "ACTIONS")
            new_xml = get_action_xml(self.action[0], self.action[1])
            if new_xml != None:
                xml_acts.append(new_xml)
        if self.java_script != "":
            etree.SubElement(compxml, "JavaScript").text = six.text_type(self.java_script)
        return compxml
