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
from base64 import b64encode
from logging import getLogger
from os.path import join
from zipfile import ZipFile
from _io import BytesIO

from django.utils.translation import ugettext as _

from lucterios.framework.xferbasic import XferContainerAbstract
from lucterios.framework.error import LucteriosException, GRAVE
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework.xfercomponents import XferCompSelect, XferCompFloat, XferCompEdit, XferCompMemo, XferCompCheck, XferCompLabelForm,\
    XferCompDownLoad
from lucterios.framework.tools import CLOSE_YES, FORMTYPE_MODAL, WrapAction
from lucterios.framework.filetools import get_user_dir
from lucterios.framework.xfersearch import get_search_query

PRINT_ODS_FILE = 2
PRINT_PDF_FILE = 3
PRINT_CSV_FILE = 4

PRINT_EXT_FILE = {
    PRINT_ODS_FILE: 'ods',
    PRINT_PDF_FILE: 'pdf',
    PRINT_CSV_FILE: 'csv',
}


class XferContainerPrint(XferContainerAbstract):

    PRINT_REGENERATE_MSG = _("{[hr/]}Regenerate new report")
    PRINT_WARNING_SAVING_MSG = _('{[u]}Warning:{[/u]} Items have saving report but regenerate report will be do.')
    PRINT_DUPLICATA = _('DUPLICATA')

    observer_name = "core.print"
    with_text_export = False
    readonly = True
    methods_allowed = ('GET', )

    def __init__(self):
        XferContainerAbstract.__init__(self)
        self.report_content = b''
        self.report_mode = PRINT_PDF_FILE
        self.report_ext = ''
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

    def _get_persistent_pdfreport(self):
        return None

    def get_persistent_pdfreport(self):
        if not hasattr(self, '_pdfreport'):
            self._pdfreport = self._get_persistent_pdfreport()
        return self._pdfreport

    def show_selector(self):
        return self.getparam("PRINT_MODE") is not None

    def _get_reports_archive(self):
        filename = "pdfreports.zip"
        download_file = join(get_user_dir(), filename)
        with ZipFile(download_file, 'w') as zip_ref:
            for pdf_name, pdf_content in self.get_persistent_pdfreport():
                if isinstance(pdf_content, BytesIO):
                    pdf_content = pdf_content.read()
                if isinstance(pdf_content, str):
                    pdf_content = pdf_content.encode()
                if isinstance(pdf_content, bytes):
                    zip_ref.writestr(zinfo_or_arcname=pdf_name, data=pdf_content)
        return filename

    def _get_zipextract(self):
        filename = self._get_reports_archive()
        gui = XferContainerCustom()
        gui.model = self.model
        gui._initialize(self.request)
        gui.is_view_right = self.is_view_right
        gui.caption = self.caption
        gui.extension = self.extension
        gui.action = self.action
        gui.params = self.params
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0, 6)
        gui.add_component(lbl)
        zipdown = XferCompDownLoad('filename')
        zipdown.compress = False
        zipdown.http_file = True
        zipdown.maxsize = 0
        zipdown.set_value(filename)
        zipdown.set_download(filename)
        zipdown.set_location(1, 15, 2)
        gui.add_component(zipdown)
        gui.add_action(WrapAction(_("Close"), "images/close.png"))
        return gui

    def _add_option_selectors(self, gui):
        row_idx = 3
        for name_selector, title_selector, option_selector in self.selector:
            if isinstance(option_selector, list):
                comp = XferCompSelect(name_selector)
                comp.set_select(option_selector)
                comp.set_value(gui.getparam(name_selector, 0))
            elif isinstance(option_selector, tuple):
                comp = XferCompFloat(name_selector, option_selector[0], option_selector[1], option_selector[2])
                comp.set_value(option_selector[0])
            elif isinstance(option_selector, bytes):
                comp = XferCompEdit(name_selector)
                comp.set_value(option_selector.decode())
            elif isinstance(option_selector, str):
                comp = XferCompMemo(name_selector)
                comp.with_hypertext = True
                comp.set_value(option_selector)
            elif isinstance(option_selector, bool):
                comp = XferCompCheck(name_selector)
                comp.set_value(option_selector)
            else:
                comp = None
            if comp is not None:
                comp.set_location(0, row_idx, 2)
                comp.description = title_selector
                gui.add_component(comp)
                row_idx += 1

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
        pdfreport = self.get_persistent_pdfreport()
        if (pdfreport is not None) and (not isinstance(pdfreport, list) or len(pdfreport) == len(self.items)):
            presitent_report = XferCompCheck('PRINT_PERSITENT')
            presitent_report.set_value(True)
            presitent_report.set_location(0, 0, 2)
            presitent_report.description = _('Get saved report')
            presitent_report.java_script = """
var is_persitent=current.getValue();
parent.get('PRINT_MODE').setEnabled(!is_persitent);
parent.get('print_sep').setEnabled(!is_persitent);
"""
            if self.selector is not None:
                for name_selector, _selector, _selector in self.selector:
                    presitent_report.java_script += "parent.get('%s').setEnabled(!is_persitent);\n" % name_selector
            gui.add_component(presitent_report)
            sep = XferCompLabelForm('print_sep')
            sep.set_value_center(self.PRINT_REGENERATE_MSG)
            sep.set_location(0, 1, 2)
            gui.add_component(sep)
        elif (pdfreport is not None):
            sep = XferCompLabelForm('print_sep')
            sep.set_value_center(self.PRINT_WARNING_SAVING_MSG)
            sep.set_location(0, 1, 2)
            gui.add_component(sep)

        print_mode = XferCompSelect('PRINT_MODE')
        print_mode.set_select(self.print_selector)
        print_mode.set_value(PRINT_PDF_FILE)
        print_mode.set_location(0, 2, 2)
        print_mode.description = _('Kind of report')
        gui.add_component(print_mode)
        if self.selector is not None:
            self._add_option_selectors(gui)
        gui.add_action(self.return_action(_("Print"), "images/print.png"), modal=FORMTYPE_MODAL, close=CLOSE_YES)
        gui.add_action(WrapAction(_("Close"), "images/close.png"))
        return gui

    def request_handling(self, request, *args, **kwargs):
        getLogger("lucterios.core.request").debug(">> %s %s [%s]", request.method, request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            if (self.getparam("PRINT_PERSITENT", False) is True) and isinstance(self.get_persistent_pdfreport(), list):
                dlg = self._get_zipextract()
                return dlg.request_handling(request, *args, **kwargs)
            else:
                report_mode = self.getparam("PRINT_MODE")
                if report_mode is not None:
                    self.report_mode = int(report_mode)
                self.fillresponse(**self._get_params())
                if ((self.selector is not None) or (len(self.print_selector) > 1) or (self.get_persistent_pdfreport() is not None)) and (report_mode is None):
                    dlg = self._get_from_selector()
                    return dlg.request_handling(request, *args, **kwargs)
                else:
                    self._finalize()
                    return self.get_response()
        finally:
            getLogger("lucterios.core.request").debug("<< %s %s [%s]", request.method, request.path, request.user)

    def fillresponse(self):
        self.print_selector = [(PRINT_PDF_FILE, _('PDF file'))]
        if self.with_text_export:
            self.print_selector.append((PRINT_CSV_FILE, _('CSV file')))
            self.print_selector.append((PRINT_ODS_FILE, _('ODS file')))
        if (self.getparam("PRINT_PERSITENT", False) is True):
            self.report_mode = PRINT_PDF_FILE
            self.report_content = b64encode(self.get_persistent_pdfreport())
        elif self.show_selector() or ((len(self.print_selector) == 1) and (self.selector is None)):
            report_generator = self.get_report_generator()
            if report_generator is not None:
                self.report_ext = PRINT_EXT_FILE[self.report_mode] if self.report_mode in PRINT_EXT_FILE else 'pdf'
                if self.get_persistent_pdfreport() is not None:
                    report_generator.watermark = self.PRINT_DUPLICATA
                if report_generator.title == '':
                    report_generator.title = self.caption
                self.report_content = b64encode(report_generator.generate_report(self.request, self.report_ext))

    def get_print_name(self):
        return str(self.caption)

    def _finalize(self):
        self.responsejson['print'] = {'mode': self.report_mode, 'extension': self.report_ext, 'title': self.get_print_name(), 'content': self.report_content.decode()}
        XferContainerAbstract._finalize(self)
