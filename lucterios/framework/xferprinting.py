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

    def get_report_generator(self):
        # pylint: disable=no-self-use
        return None

    def show_selector(self, selector=0, selector_desc=None):
        self.selector = selector
        self.selector_desc = selector_desc
        return self.getparam("PRINT_MODE") is not None

    def _get_from_selector(self):
        if not isinstance(self.selector, dict) and not isinstance(self.selector, tuple) \
                and not isinstance(self.selector, list) and (self.selector is not None) and (self.selector != 0):
            raise LucteriosException(GRAVE, "Error of print selector!")
        gui = XferContainerCustom()
        gui.is_view_right = self.is_view_right  # pylint: disable=attribute-defined-outside-init,no-member
        gui.caption = self.caption
        gui.extension = self.extension
        gui.action = self.action
        lbl = XferCompLabelForm('lblPrintMode')
        lbl.set_value_as_name(_('Kind of report'))
        lbl.set_location(0, 0)
        gui.add_component(lbl)
        print_mode = XferCompSelect('PRINT_MODE')
        selector = [(PRINT_PDF_FILE, _('PDF file'))]
        if self.with_text_export:
            selector.append((PRINT_CSV_FILE, _('CSV file')))
        print_mode.set_select(selector)
        print_mode.set_value(PRINT_PDF_FILE)
        print_mode.set_location(1, 0)
        gui.add_component(print_mode)
        if (self.selector is not None) and (self.selector != 0):
            lbl = XferCompLabelForm('lblselector')
            lbl.set_value_as_title(self.selector_desc[0])
            lbl.set_location(0, 1)
            gui.add_component(lbl)
            selector = XferCompSelect(self.selector_desc[1])
            selector.set_select(self.selector)
            selector.set_value(None)
            selector.set_location(1, 1)
            gui.add_component(selector)
        gui.add_action(self.get_changed(_("Print"), "images/print.png"), {'modal':FORMTYPE_MODAL, 'close':CLOSE_YES})
        gui.add_action(StubAction(_("Close"), "images/close.png"), {})
        return gui

    def get(self, request, *args, **kwargs):
        self._initialize(request, *args, **kwargs)
        self.fillresponse(**self._get_params())
        report_mode = self.getparam("PRINT_MODE")
        if (self.selector != 0) or (report_mode is not None):
            if report_mode is not None:
                self.report_mode = int(report_mode)
            self._finalize()
            return self.get_response()
        else:
            dlg = self._get_from_selector()
            return dlg.get(request, *args, **kwargs)

    def get_body_content(self):
        if self.report_mode == PRINT_CSV_FILE:
            xsl_file = join(dirname(__file__), "ConvertxlpToCSV.xsl")
            if not isfile(xsl_file):
                raise LucteriosException(GRAVE, "Error:no csv xsl file!")
            rep_content = self.report_content
            with open(xsl_file, 'rb') as xsl_file:
                csv_transform = etree.XSLT(etree.XML(xsl_file.read()))
            content = six.text_type(csv_transform(etree.XML(rep_content))).encode('utf-8')
        else:
            content = transforme_xml2pdf(self.report_content)
        if len(content) > 0:
            return b64encode(content)
        else:
            return ""

    def fillresponse(self):
        if self.show_selector():
            report_generator = self.get_report_generator()
            if report_generator is not None:
                report_generator.title = self.caption
                self.report_content = report_generator.generate(self.request)

    def _finalize(self):
        printxml = etree.SubElement(self.responsexml, "PRINT")
        printxml.attrib['mode'] = six.text_type(self.report_mode)  # 3=PDF - 4=CSV
        printxml.text = self.get_body_content()
        etree.SubElement(printxml, "TITLE").text = six.text_type(self.caption)
        XferContainerAbstract._finalize(self)
