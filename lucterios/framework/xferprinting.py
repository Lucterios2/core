# -*- coding: utf-8 -*-
'''
Printing abstract viewer classes for Lucterios

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
from base64 import b64encode
from logging import getLogger

from django.utils.translation import ugettext as _
from django.utils import six

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework.xfercomponents import XferCompSelect, XferCompLabelForm, \
    XferCompFloat
from lucterios.framework.tools import CLOSE_YES, FORMTYPE_MODAL, WrapAction
from lucterios.framework.xfersearch import get_search_query

PRINT_PDF_FILE = 3
PRINT_CSV_FILE = 4


class XferContainerPrint(XferContainerAbstract):

    observer_name = "core.print"
    with_text_export = False

    def __init__(self):
        XferContainerAbstract.__init__(self)
        self.report_content = ""
        self.report_mode = PRINT_PDF_FILE
        self.print_selector = []
        self.selector = None

    def get_filter(self):
        new_filter = None
        criteria = self.getparam('CRITERIA')
        if criteria is not None:
            new_filter = get_search_query(criteria, self.item)[0]
        return new_filter

    def get_report_generator(self):

        return None

    def show_selector(self):
        return self.getparam("PRINT_MODE") is not None

    def _get_from_selector(self):
        if not isinstance(self.selector, list) and (self.selector is not None):
            raise LucteriosException(GRAVE, "Error of print selector!")
        gui = XferContainerCustom()
        gui.model = self.model
        gui._initialize(self.request)
        gui.is_view_right = self.is_view_right
        gui.caption = self.caption
        gui.extension = self.extension
        gui.action = self.action
        gui.params = self.params
        lbl = XferCompLabelForm('lblPrintMode')
        lbl.set_value_as_name(_('Kind of report'))
        lbl.set_location(0, 0)
        gui.add_component(lbl)
        print_mode = XferCompSelect('PRINT_MODE')
        print_mode.set_select(self.print_selector)
        print_mode.set_value(PRINT_PDF_FILE)
        print_mode.set_location(1, 0)
        gui.add_component(print_mode)
        if self.selector is not None:
            row_idx = 1
            for name_selector, title_selector, option_selector in self.selector:
                lbl = XferCompLabelForm('lbl' + name_selector)
                lbl.set_value_as_name(title_selector)
                lbl.set_location(0, row_idx)
                gui.add_component(lbl)
                if isinstance(option_selector, list):
                    comp = XferCompSelect(name_selector)
                    comp.set_select(option_selector)
                    comp.set_value(gui.getparam(name_selector, 0))
                elif isinstance(option_selector, tuple):
                    comp = XferCompFloat(
                        name_selector, option_selector[0], option_selector[1], option_selector[2])
                    comp.set_value(option_selector[0])
                comp.set_location(1, row_idx)
                gui.add_component(comp)
                row_idx += 1
        gui.add_action(self.get_action(
            _("Print"), "images/print.png"), modal=FORMTYPE_MODAL, close=CLOSE_YES)
        gui.add_action(WrapAction(_("Close"), "images/close.png"))
        return gui

    def get(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(
            ">> get %s [%s]", request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            report_mode = self.getparam("PRINT_MODE")
            if report_mode is not None:
                self.report_mode = int(report_mode)
            self.fillresponse(**self._get_params())
            if ((self.selector is not None) or (len(self.print_selector) > 1)) and (report_mode is None):
                dlg = self._get_from_selector()
                return dlg.get(request, *args, **kwargs)
            else:
                self._finalize()
                return self.get_response()
        finally:
            getLogger("lucterios.core.request").debug(
                "<< get %s [%s]", request.path, request.user)

    def fillresponse(self):
        self.print_selector = [(PRINT_PDF_FILE, _('PDF file'))]
        if self.with_text_export:
            self.print_selector.append((PRINT_CSV_FILE, _('CSV file')))
        if self.show_selector() or ((len(self.print_selector) == 1) and (self.selector is None)):
            report_generator = self.get_report_generator()
            if report_generator is not None:
                if report_generator.title == '':
                    report_generator.title = self.caption
                self.report_content = b64encode(report_generator.generate_report(
                    self.request, self.report_mode == PRINT_CSV_FILE))

    def get_print_name(self):
        return six.text_type(self.caption)

    def _finalize(self):
        printxml = etree.SubElement(self.responsexml, "PRINT")
        printxml.attrib['mode'] = six.text_type(
            self.report_mode)  # 3=PDF - 4=CSV
        printxml.text = self.report_content
        etree.SubElement(printxml, "TITLE").text = self.get_print_name()
        XferContainerAbstract._finalize(self)
