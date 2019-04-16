# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
'''
Abstract views to simplify printing with action, model or label in Lucterios

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

from django.utils import six
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.printgenerators import ActionGenerator, ListingGenerator, LabelGenerator, ReportingGenerator
from lucterios.framework.xferprinting import XferContainerPrint
from lucterios.CORE.models import PrintModel, Label
from lucterios.framework.xfersearch import get_info_list


class XferPrintAction(XferContainerPrint):

    action_class = None
    tab_change_page = False

    def get_report_generator(self):
        if self.action_class is not None:
            return ActionGenerator(self.action_class(), self.tab_change_page)


class XferPrintListing(XferContainerPrint):

    with_text_export = True

    def __init__(self):
        XferContainerPrint.__init__(self)
        self.selector = PrintModel.get_print_selector(0, self.model)
        self.params['MODEL'] = PrintModel.get_print_default(0, self.model, False)
        self.info = ""
        self.with_num = False

    def filter_callback(self, items):
        return items

    def fillresponse(self):
        if (self.info == '') and (self.getparam('CRITERIA') is not None):
            info_list = get_info_list(self.getparam('CRITERIA'), self.model)
            self.info = '{[br]}'.join(info_list)
        self.selector.append(("TITLE", _('title'), six.text_type(self.getparam("TITLE", self.caption)).encode()))
        self.selector.append(("INFO", _('comment'), six.text_type(self.getparam("INFO", self.info))))
        self.selector.append(("WITHNUM", _('with number?'), self.getparam("WITHNUM", self.with_num is True)))
        self.caption = self.getparam("TITLE", self.caption)
        self.info = self.getparam("INFO", self.info).replace("{[br]}", "{[br/]}")
        while self.info.endswith("{[br/]}"):
            self.info = self.info[:-7]
        self.with_num = self.getparam("WITHNUM", self.with_num is True)
        XferContainerPrint.fillresponse(self)

    def get_report_generator(self):
        dbmodel = PrintModel.get_model_selected(self)
        gen = ListingGenerator(self.model)
        gen.filter = self.get_filter()
        gen.filter_callback = self.filter_callback
        gen.page_height = dbmodel.page_height
        gen.page_width = dbmodel.page_width
        gen.columns = dbmodel.columns
        gen.mode = dbmodel.mode
        gen.info = self.info
        gen.with_num = self.with_num is True
        return gen


class XferPrintLabel(XferContainerPrint):

    with_text_export = False

    def __init__(self):
        XferContainerPrint.__init__(self)
        self.selector = Label.get_print_selector()
        self.selector.extend(PrintModel.get_print_selector(1, self.model))
        self.params['MODEL'] = PrintModel.get_print_default(1, self.model, False)

    def filter_callback(self, items):
        return items

    def get_report_generator(self):
        dblbl, first_label = Label.get_label_selected(self)
        model_value = PrintModel.get_model_selected(self)
        gen = LabelGenerator(self.model, first_label)
        gen.filter = self.get_filter()
        gen.filter_callback = self.filter_callback
        gen.label_text = model_value.value
        gen.mode = model_value.mode
        for lblkey in gen.label_size.keys():
            gen.label_size[lblkey] = getattr(dblbl, lblkey)
        return gen


class XferPrintReporting(XferContainerPrint):

    with_text_export = False

    def __init__(self):
        XferContainerPrint.__init__(self)
        self.selector = PrintModel.get_print_selector(2, self.model)
        self.params['MODEL'] = PrintModel.get_print_default(2, self.model, False)

    def items_callback(self):
        return [self.item]

    def get_report_generator(self):
        model_value = PrintModel.get_model_selected(self)
        gen = ReportingGenerator()
        gen.items_callback = self.items_callback
        gen.model_text = model_value.value
        gen.mode = model_value.mode
        return gen
