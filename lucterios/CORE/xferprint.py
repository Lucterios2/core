# -*- coding: utf-8 -*-
'''
Created on april 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from lucterios.framework.printgenerators import ActionGenerator, \
    ListingGenerator, LabelGenerator
from lucterios.framework.xferprinting import XferContainerPrint
from lucterios.CORE.models import PrintModel, Label

class XferPrintAction(XferContainerPrint):

    action_class = None

    def get_report_generator(self):
        if self.action_class is not None:
            return ActionGenerator(self.action_class()) # pylint: disable=not-callable

class XferPrintListing(XferContainerPrint):

    with_text_export = True

    def __init__(self):
        XferContainerPrint.__init__(self)
        self.selector = PrintModel.get_print_selector(0, self.model)

    def get_report_generator(self):
        model_value = PrintModel.get_model_selected(self)
        gen = ListingGenerator(self.model)
        gen.filter = self.get_filter()
        gen.initial(model_value.split('\n'))
        return gen

class XferPrintLabel(XferContainerPrint):

    def __init__(self):
        XferContainerPrint.__init__(self)
        self.selector = Label.get_print_selector()
        self.selector.extend(PrintModel.get_print_selector(1, self.model))

    def get_report_generator(self):
        dblbl, first_label = Label.get_label_selected(self)
        model_value = PrintModel.get_model_selected(self)
        gen = LabelGenerator(self.model, first_label)
        gen.filter = self.get_filter()
        gen.label_text = model_value
        for lblkey in gen.label_size.keys():
            gen.label_size[lblkey] = getattr(dblbl, lblkey)
        return gen
