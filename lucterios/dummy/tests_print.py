# -*- coding: utf-8 -*-
'''
Created on april 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from lucterios.framework.test import LucteriosTest
from lucterios.CORE.views import PrintModelList, PrintModelEdit, PrintModelClone, \
    PrintModelDelete, PrintModelSave

class PrintTest(LucteriosTest):
    # pylint: disable=too-many-public-methods

    def setUp(self):
        # pylint: disable=no-member
        LucteriosTest.setUp(self)

    def testlist(self):
        self.factory.xfer = PrintModelList()
        self.call('/CORE/printModelList', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelList')
        self.assert_count_equal('COMPONENTS/*', 5)
        self.assert_comp_equal('COMPONENTS/SELECT[@name="modelname"]', "dummy.Example", (2, 1, 2, 1))
        self.assert_count_equal('COMPONENTS/SELECT[@name="modelname"]/CASE', 1)
        self.assert_coordcomp_equal('COMPONENTS/GRID[@name="print_model"]', (1, 2, 3, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="print_model"]/HEADER', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/HEADER[@name="name"]', "nom")
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/HEADER[@name="kind"]', "Type")
        self.assert_count_equal('COMPONENTS/GRID[@name="print_model"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="name"]', 'listing')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="kind"]', 'Liste')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="name"]', 'label')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="kind"]', 'Etiquette')

        self.factory.xfer = PrintModelList()
        self.call('/CORE/printModelList', {"modelname":"dummy.Example"}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelList')
        self.assert_comp_equal('COMPONENTS/SELECT[@name="modelname"]', "dummy.Example", (2, 1, 2, 1))
        self.assert_count_equal('COMPONENTS/GRID[@name="print_model"]/RECORD', 2)

    def testedit_listing(self):
        self.factory.xfer = PrintModelEdit()
        self.call('/CORE/printModelEdit', {'print_model':1}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelEdit')
        self.assert_count_equal('COMPONENTS/*', 6 + 7 + 6 * 3)
        self.assert_comp_equal('COMPONENTS/EDIT[@name="name"]', "listing", (2, 1, 1, 1))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="kind"]', "Liste", (2, 2, 1, 1))

        self.assert_comp_equal('COMPONENTS/FLOAT[@name="page_width"]', "210", (2, 3, 2, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="page_heigth"]', "297", (2, 4, 2, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_0"]', "10", (1, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_0"]', "Name", (2, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_0"]', "#name", (3, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_1"]', "20", (1, 7, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_1"]', "value + price", (2, 7, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_1"]', "#value/#price", (3, 7, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_2"]', "20", (1, 8, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_2"]', "date + time", (2, 8, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_2"]', "#date{[newline]}#time", (3, 8, 1, 1))
        for col_idx in range(3, 6):
            self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_%d"]' % col_idx, "0", (1, 6 + col_idx, 1, 1))
            self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_%d"]' % col_idx, None, (2, 6 + col_idx, 1, 1))
            self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_%d"]' % col_idx, None, (3, 6 + col_idx, 1, 1))

    def testsave_listing(self):
        self.factory.xfer = PrintModelSave()
        params = {'print_model':1, 'page_width':'297', 'page_heigth':'210'}
        params["col_size_0"] = "10"
        params["col_title_0"] = "Name"
        params["col_text_0"] = "#name"
        params["col_size_1"] = "0"
        params["col_title_1"] = "value + price"
        params["col_text_1"] = "#value/#price"
        params["col_size_2"] = "20"
        params["col_title_2"] = "date + time"
        params["col_text_2"] = "#date{[newline]}#time"
        params["col_size_3"] = "25"
        params["col_title_3"] = "value + price"
        params["col_text_3"] = "#value/#price"
        params["col_size_4"] = "0"
        params["col_title_4"] = ""
        params["col_text_4"] = ""
        params["col_size_5"] = "0"
        params["col_title_5"] = ""
        params["col_text_5"] = ""
        self.call('/CORE/printModelSave', params, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'printModelSave')

        self.factory.xfer = PrintModelEdit()
        self.call('/CORE/printModelEdit', {'print_model':1}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelEdit')
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="page_width"]', "297", (2, 3, 2, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="page_heigth"]', "210", (2, 4, 2, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_0"]', "10", (1, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_0"]', "Name", (2, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_0"]', "#name", (3, 6, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_1"]', "20", (1, 7, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_1"]', "date + time", (2, 7, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_1"]', "#date{[newline]}#time", (3, 7, 1, 1))
        self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_2"]', "25", (1, 8, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_2"]', "value + price", (2, 8, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_2"]', "#value/#price", (3, 8, 1, 1))
        for col_idx in range(3, 6):
            self.assert_comp_equal('COMPONENTS/FLOAT[@name="col_size_%d"]' % col_idx, "0", (1, 6 + col_idx, 1, 1))
            self.assert_comp_equal('COMPONENTS/MEMO[@name="col_title_%d"]' % col_idx, None, (2, 6 + col_idx, 1, 1))
            self.assert_comp_equal('COMPONENTS/MEMO[@name="col_text_%d"]' % col_idx, None, (3, 6 + col_idx, 1, 1))

    def testedit_label(self):
        self.factory.xfer = PrintModelEdit()
        self.call('/CORE/printModelEdit', {'print_model':2}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelEdit')
        self.assert_count_equal('COMPONENTS/*', 6 + 1)
        self.assert_comp_equal('COMPONENTS/EDIT[@name="name"]', "label", (2, 1, 1, 1))

        self.assert_comp_equal('COMPONENTS/LABELFORM[@name="kind"]', "Etiquette", (2, 2, 1, 1))
        self.assert_comp_equal('COMPONENTS/MEMO[@name="value"]', "#name{[newline]}#value:#price{[newline]}#date #time", (1, 3, 2, 1))

    def testsave_label(self):
        self.factory.xfer = PrintModelSave()
        self.call('/CORE/printModelSave', {'print_model':2, 'value':"#name{[newline]}#date #time{[newline]}#value:#price"}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'printModelSave')

        self.factory.xfer = PrintModelEdit()
        self.call('/CORE/printModelEdit', {'print_model':2}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelEdit')
        self.assert_comp_equal('COMPONENTS/MEMO[@name="value"]', "#name{[newline]}#date #time{[newline]}#value:#price", (1, 3, 2, 1))

    def testclonedel_listing(self):
        self.factory.xfer = PrintModelClone()
        self.call('/CORE/printModelClone', {'print_model':1}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'printModelClone')

        self.factory.xfer = PrintModelList()
        self.call('/CORE/printModelList', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelList')
        self.assert_count_equal('COMPONENTS/GRID[@name="print_model"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="name"]', 'listing')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="kind"]', 'Liste')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="name"]', 'label')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="kind"]', 'Etiquette')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=3]/VALUE[@name="name"]', 'copie de listing')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=3]/VALUE[@name="kind"]', 'Liste')

        self.factory.xfer = PrintModelDelete()
        self.call('/CORE/printModelDelete', {'print_model':3, 'CONFIRME':'YES'}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'printModelDelete')

        self.factory.xfer = PrintModelList()
        self.call('/CORE/printModelList', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelList')
        self.assert_count_equal('COMPONENTS/GRID[@name="print_model"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="name"]', 'listing')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="name"]', 'label')

    def testclonedel_label(self):
        self.factory.xfer = PrintModelClone()
        self.call('/CORE/printModelClone', {'print_model':2}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'printModelClone')

        self.factory.xfer = PrintModelList()
        self.call('/CORE/printModelList', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelList')
        self.assert_count_equal('COMPONENTS/GRID[@name="print_model"]/RECORD', 3)
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="name"]', 'listing')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="kind"]', 'Liste')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="name"]', 'label')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="kind"]', 'Etiquette')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=3]/VALUE[@name="name"]', 'copie de label')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=3]/VALUE[@name="kind"]', 'Etiquette')

        self.factory.xfer = PrintModelDelete()
        self.call('/CORE/printModelDelete', {'print_model':3, 'CONFIRME':'YES'}, False)
        self.assert_observer('Core.Acknowledge', 'CORE', 'printModelDelete')

        self.factory.xfer = PrintModelList()
        self.call('/CORE/printModelList', {}, False)
        self.assert_observer('Core.Custom', 'CORE', 'printModelList')
        self.assert_count_equal('COMPONENTS/GRID[@name="print_model"]/RECORD', 2)
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=1]/VALUE[@name="name"]', 'listing')
        self.assert_xml_equal('COMPONENTS/GRID[@name="print_model"]/RECORD[@id=2]/VALUE[@name="name"]', 'label')
