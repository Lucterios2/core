# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from os.path import isfile, join, dirname
from base64 import b64encode
from lxml import etree

from django.utils.translation import ugettext as _
from django.utils import six

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework.xfercomponents import XferCompSelect, XferCompLabelForm
from lucterios.framework.tools import CLOSE_YES, FORMTYPE_MODAL, StubAction
from lucterios.framework.reporting import transforme_xml2pdf

class ReportGenerator(object):

    def __init__(self, title):
        self.title = title
        self.modelxml = etree.Element('model')
        page = etree.SubElement(self.modelxml, "page")
        self.header = etree.SubElement(page, "header")
        self.bottom = etree.SubElement(page, "bottom")
        self.body = etree.SubElement(page, "body")
        self.page_width = 210
        self.page_height = 297
        self.horizontal_marge = 10
        self.vertical_marge = 10
        self.header_height = 0
        self.bottom_height = 0

    def fill_attrib(self):
        self.modelxml.attrib['page_width'] = "%d.0" % self.page_width
        self.modelxml.attrib['page_height'] = "%d.0" % self.page_height
        self.modelxml.attrib['margin_right'] = "%d.0" % self.horizontal_marge
        self.modelxml.attrib['margin_left'] = "%d.0" % self.horizontal_marge
        self.modelxml.attrib['margin_bottom'] = "%d.0" % self.vertical_marge
        self.modelxml.attrib['margin_top'] = "%d.0" % self.vertical_marge
        self.header.attrib['extent'] = "%d.0" % self.header_height
        self.bottom.attrib['extent'] = "%d.0" % self.bottom_height

    def fill_content(self):
        pass

    def get_title(self):
        return self.title

    def generate(self):
        self.fill_content()
        self.fill_attrib()
        return etree.tostring(self.modelxml, xml_declaration=True, pretty_print=True, encoding='utf-8')

PRINT_PDF_FILE = 3
PRINT_CSV_FILE = 4

class XferContainerPrint(XferContainerAbstract):

    observer_name = "Core.Print"
    with_text_export = False

    def __init__(self):
        XferContainerAbstract.__init__(self)
        self.report_content = ""
        self.report_mode = 0
        self.selector_desc = ''
        self.selector = None

    def show_selector(self, selector=0, selector_desc=None):
        self.selector = selector
        self.selector_desc = selector_desc
        return self.getparam("PRINT_MODE") is not None

    def _get_from_selector(self):
        if not isinstance(self.selector, dict) and not isinstance(self.selector, tuple) \
                and not isinstance(self.selector, list) and (self.selector is not None) and (self.selector != 0):
            raise LucteriosException(GRAVE, "Error of print selector!")
        dlg = XferContainerCustom()
        dlg.is_view_right = self.is_view_right  # pylint: disable=attribute-defined-outside-init
        dlg.caption = self.caption
        dlg.extension = self.extension
        dlg.action = self.action
        lbl = XferCompLabelForm('lblPrintMode')
        lbl.set_value_as_title(_('Kind of report'))
        lbl.set_location(0, 0)
        dlg.add_component(lbl)
        print_mode = XferCompSelect('PRINT_MODE')
        selector = [(PRINT_PDF_FILE, _('PDF file'))]
        if self.with_text_export:
            selector.append((PRINT_CSV_FILE, _('CSV file')))
        print_mode.set_select(selector)
        print_mode.set_value(1)
        print_mode.set_location(1, 0)
        dlg.add_component(print_mode)
        if (self.selector is not None) and (self.selector != 0):
            lbl = XferCompLabelForm('lblselector')
            lbl.set_value_as_title(self.selector_desc[0])
            lbl.set_location(0, 1)
            dlg.add_component(lbl)
            selector = XferCompSelect(self.selector_desc[1])
            selector.set_select(self.selector)
            selector.set_value(None)
            selector.set_location(1, 1)
            dlg.add_component(selector)
        dlg.add_action(self.get_changed(_("Print"), "images/print.png"), {'modal':FORMTYPE_MODAL, 'close':CLOSE_YES})
        dlg.add_action(StubAction(_("Close"), "images/close.png"), {})
        return dlg

    def print_data(self, report_generator):
        if not isinstance(report_generator, ReportGenerator):
            raise LucteriosException(GRAVE, "Error of print generator!")
        self.caption = report_generator.get_title()
        self.report_content = report_generator.generate()
        if self.report_content == "":
            raise LucteriosException(GRAVE, "report empty!")

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        self.fillresponse(**self._get_params())
        report_mode = self.getparam("PRINT_MODE")
        if (self.selector != 0) or (report_mode is not None):
            if report_mode is not None:
                self.report_mode = int(report_mode)
            return self._finalize()
        else:
            dlg = self._get_from_selector()
            return dlg.get(request, *args, **kwargs)

    def getBodyContent(self):
        if self.report_mode == PRINT_CSV_FILE:
            xsl_file = join(dirname(__file__), "ConvertxlpToCSV.xsl")
            if not isfile(xsl_file):
                raise LucteriosException(GRAVE, "Error:no csv xsl file!")
            rep_content = self.report_content
            with open(xsl_file, 'rb') as xsl_file:
                csv_transform = etree.XSLT(etree.XML(xsl_file.read()))
            content = csv_transform(etree.XML(rep_content))
        else:
            content = transforme_xml2pdf(self.report_content)
        return b64encode(content)

    def _finalize(self):
        printxml = etree.SubElement(self.responsexml, "PRINT")
        printxml.attrib['mode'] = six.text_type(self.report_mode)  # 3=PDF - 4=CSV
        printxml.text = self.getBodyContent()
        etree.SubElement(printxml, "TITLE").text = six.text_type(self.caption)
        return XferContainerAbstract._finalize(self)
