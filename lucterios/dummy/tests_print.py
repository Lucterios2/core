# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
'''
Unit test for printing in Lucterios

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

from lucterios.framework.test import LucteriosTest
from lucterios.CORE.views import PrintModelList, PrintModelEdit, PrintModelClone, \
    PrintModelDelete, PrintModelSave, PrintModelReload, PrintModelExtract,\
    Download, PrintModelImport, PrintModelSetDefault
from os.path import isfile


class PrintTest(LucteriosTest):

    def setUp(self):

        LucteriosTest.setUp(self)

    def testlist(self):
        self.factory.xfer = PrintModelList()
        self.calljson('/CORE/printModelList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelList')
        self.assert_count_equal('', 5)
        self.assert_comp_equal(('SELECT', "modelname"), "dummy.Example", (1, 1, 1, 1))
        self.assert_select_equal("modelname", {'dummy.Example': 'example'})
        self.assert_coordcomp_equal('print_model', (0, 2, 2, 1))
        self.assert_grid_equal("print_model", {"name": "nom", "kind": "type", "is_default": "défaut"}, 3)
        self.assert_json_equal('', '#print_model/headers/@0/@0', 'name')
        self.assert_json_equal('', '#print_model/headers/@0/@1', 'nom')
        self.assert_json_equal('', '#print_model/headers/@0/@2', None)
        self.assert_json_equal('', '#print_model/headers/@0/@4', "%s")

        self.assert_json_equal('', '#print_model/headers/@1/@0', 'kind')
        self.assert_json_equal('', '#print_model/headers/@1/@1', 'type')
        self.assert_json_equal('', '#print_model/headers/@1/@2', {'0': "Liste", '1': "Etiquette", '2': "Rapport"})
        self.assert_json_equal('', '#print_model/headers/@1/@4', "%s")

        self.assert_json_equal('', '#print_model/headers/@2/@0', 'is_default')
        self.assert_json_equal('', '#print_model/headers/@2/@1', 'défaut')
        self.assert_json_equal('', '#print_model/headers/@2/@2', "B")
        self.assert_json_equal('', '#print_model/headers/@2/@4', "%s")

        self.assert_json_equal('', 'print_model/@0/name', 'listing')
        self.assert_json_equal('', 'print_model/@0/kind', 0)
        self.assert_json_equal('', 'print_model/@0/is_default', True)
        self.assert_json_equal('', 'print_model/@1/name', 'label')
        self.assert_json_equal('', 'print_model/@1/kind', 1)
        self.assert_json_equal('', 'print_model/@1/is_default', False)
        self.assert_json_equal('', 'print_model/@2/name', 'reporting')
        self.assert_json_equal('', 'print_model/@2/kind', 2)
        self.assert_json_equal('', 'print_model/@2/is_default', True)

        self.factory.xfer = PrintModelList()
        self.calljson('/CORE/printModelList', {"modelname": "dummy.Example"}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelList')
        self.assert_comp_equal(('SELECT', "modelname"), "dummy.Example", (1, 1, 1, 1))
        self.assert_count_equal("print_model", 3)

    def testedit_listing(self):
        self.factory.xfer = PrintModelEdit()
        self.calljson('/CORE/printModelEdit', {'print_model': 1}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelEdit')
        self.assert_count_equal('', 2 + 7 + 6 * 3)
        self.assert_comp_equal(('EDIT', "name"), "listing", (2, 1, 1, 1))
        self.assert_comp_equal(('LABELFORM', "kind"), 0, (2, 2, 1, 1))
        self.assert_comp_equal(('FLOAT', "page_width"), "210", (2, 3, 1, 1))
        self.assert_comp_equal(('FLOAT', "page_heigth"), "297", (2, 4, 1, 1))

        self.assert_comp_equal(('FLOAT', "col_size_0"), "10", (1, 6, 1, 1))
        self.assert_comp_equal(('MEMO', "col_title_0"), "Name", (2, 6, 1, 1))
        self.assert_comp_equal(('MEMO', "col_text_0"), "#name", (3, 6, 1, 1))
        self.assert_comp_equal(('FLOAT', "col_size_1"), "20", (1, 7, 1, 1))
        self.assert_comp_equal(('MEMO', "col_title_1"), "value + price", (2, 7, 1, 1))
        self.assert_comp_equal(('MEMO', "col_text_1"), "#value/#price", (3, 7, 1, 1))
        self.assert_comp_equal(('FLOAT', "col_size_2"), "20", (1, 8, 1, 1))
        self.assert_comp_equal(('MEMO', "col_title_2"), "date + time", (2, 8, 1, 1))
        self.assert_comp_equal(('MEMO', "col_text_2"), "#date{[newline]}#time", (3, 8, 1, 1))
        for col_idx in range(3, 6):
            self.assert_comp_equal(('FLOAT', "col_size_%d" % col_idx), "0", (1, 6 + col_idx, 1, 1))
            self.assert_comp_equal(('MEMO', "col_title_%d" % col_idx), '', (2, 6 + col_idx, 1, 1))
            self.assert_comp_equal(('MEMO', "col_text_%d" % col_idx), '', (3, 6 + col_idx, 1, 1))

    def testsave_listing(self):
        self.factory.xfer = PrintModelSave()
        params = {'print_model': 1, 'page_width': '297', 'page_heigth': '210'}
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
        self.calljson('/CORE/printModelSave', params, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelSave')

        self.factory.xfer = PrintModelEdit()
        self.calljson('/CORE/printModelEdit', {'print_model': 1}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelEdit')
        self.assert_comp_equal(('FLOAT', "page_width"), "297", (2, 3, 1, 1))
        self.assert_comp_equal(('FLOAT', "page_heigth"), "210", (2, 4, 1, 1))
        self.assert_comp_equal(('FLOAT', "col_size_0"), "10", (1, 6, 1, 1))
        self.assert_comp_equal(('MEMO', "col_title_0"), "Name", (2, 6, 1, 1))
        self.assert_comp_equal(('MEMO', "col_text_0"), "#name", (3, 6, 1, 1))
        self.assert_comp_equal(('FLOAT', "col_size_1"), "20", (1, 7, 1, 1))
        self.assert_comp_equal(('MEMO', "col_title_1"), "date + time", (2, 7, 1, 1))
        self.assert_comp_equal(('MEMO', "col_text_1"), "#date{[newline]}#time", (3, 7, 1, 1))
        self.assert_comp_equal(('FLOAT', "col_size_2"), "25", (1, 8, 1, 1))
        self.assert_comp_equal(('MEMO', "col_title_2"), "value + price", (2, 8, 1, 1))
        self.assert_comp_equal(('MEMO', "col_text_2"), "#value/#price", (3, 8, 1, 1))
        for col_idx in range(3, 6):
            self.assert_comp_equal(('FLOAT', "col_size_%d" % col_idx), "0", (1, 6 + col_idx, 1, 1))
            self.assert_comp_equal(('MEMO', "col_title_%d" % col_idx), '', (2, 6 + col_idx, 1, 1))
            self.assert_comp_equal(('MEMO', "col_text_%d" % col_idx), '', (3, 6 + col_idx, 1, 1))

    def testedit_label(self):
        self.factory.xfer = PrintModelEdit()
        self.calljson('/CORE/printModelEdit', {'print_model': 2}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelEdit')
        self.assert_count_equal('', 6)
        self.assert_comp_equal(('EDIT', "name"), "label", (2, 1, 1, 1))
        self.assert_comp_equal(('LABELFORM', "kind"), 1, (2, 2, 1, 1))
        self.assert_comp_equal(('MEMO', "value"), "#name{[newline]}#value:#price{[newline]}#date #time", (2, 4, 1, 1))

    def testsave_label(self):
        self.factory.xfer = PrintModelSave()
        self.calljson('/CORE/printModelSave', {'print_model': 2, 'value':
                                               "#name{[newline]}#date #time{[newline]}#value:#price"}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelSave')

        self.factory.xfer = PrintModelEdit()
        self.calljson('/CORE/printModelEdit', {'print_model': 2}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelEdit')
        self.assert_comp_equal(('MEMO', "value"), "#name{[newline]}#date #time{[newline]}#value:#price", (2, 4, 1, 1))

    def testclonedel_listing(self):
        self.factory.xfer = PrintModelClone()
        self.calljson('/CORE/printModelClone', {'print_model': 1}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelClone')

        self.factory.xfer = PrintModelList()
        self.calljson('/CORE/printModelList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelList')
        self.assert_count_equal("print_model", 4)
        self.assert_json_equal("", "print_model/@0/name", 'listing')
        self.assert_json_equal("", "print_model/@0/kind", 0)
        self.assert_json_equal("", "print_model/@0/is_default", True)
        self.assert_json_equal("", "print_model/@1/name", 'label')
        self.assert_json_equal("", "print_model/@1/kind", 1)
        self.assert_json_equal("", "print_model/@1/is_default", False)
        self.assert_json_equal("", "print_model/@2/name", 'reporting')
        self.assert_json_equal("", "print_model/@2/kind", 2)
        self.assert_json_equal("", "print_model/@2/is_default", True)
        self.assert_json_equal("", "print_model/@3/name", 'copie de listing')
        self.assert_json_equal("", "print_model/@3/kind", 0)
        self.assert_json_equal("", "print_model/@3/is_default", False)

        self.factory.xfer = PrintModelSetDefault()
        self.calljson('/CORE/printModelSetDefault', {'print_model': 4}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelSetDefault')

        self.factory.xfer = PrintModelList()
        self.calljson('/CORE/printModelList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelList')
        self.assert_count_equal("print_model", 4)
        self.assert_json_equal("", "print_model/@0/is_default", False)
        self.assert_json_equal("", "print_model/@1/is_default", False)
        self.assert_json_equal("", "print_model/@2/is_default", True)
        self.assert_json_equal("", "print_model/@3/is_default", True)

        self.factory.xfer = PrintModelDelete()
        self.calljson('/CORE/printModelDelete', {'print_model': 4, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelDelete')

        self.factory.xfer = PrintModelList()
        self.calljson('/CORE/printModelList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelList')
        self.assert_count_equal("print_model", 3)
        self.assert_json_equal("", "print_model/@0/name", 'listing')
        self.assert_json_equal("", "print_model/@0/is_default", False)
        self.assert_json_equal("", "print_model/@1/name", 'label')
        self.assert_json_equal("", "print_model/@1/is_default", False)
        self.assert_json_equal("", "print_model/@2/name", 'reporting')
        self.assert_json_equal("", "print_model/@2/is_default", True)

    def testclonedel_label(self):
        self.factory.xfer = PrintModelClone()
        self.calljson('/CORE/printModelClone', {'print_model': 2}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelClone')

        self.factory.xfer = PrintModelList()
        self.calljson('/CORE/printModelList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelList')
        self.assert_count_equal("print_model", 4)
        self.assert_json_equal("", "print_model/@0/name", 'listing')
        self.assert_json_equal("", "print_model/@0/kind", 0)
        self.assert_json_equal("", "print_model/@1/name", 'label')
        self.assert_json_equal("", "print_model/@1/kind", 1)
        self.assert_json_equal("", "print_model/@2/name", 'reporting')
        self.assert_json_equal("", "print_model/@2/kind", 2)
        self.assert_json_equal("", "print_model/@3/name", 'copie de label')
        self.assert_json_equal("", "print_model/@3/kind", 1)

        self.factory.xfer = PrintModelDelete()
        self.calljson('/CORE/printModelDelete', {'print_model': 4, 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelDelete')

        self.factory.xfer = PrintModelList()
        self.calljson('/CORE/printModelList', {}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelList')
        self.assert_count_equal("print_model", 3)
        self.assert_json_equal("", "print_model/@0/name", 'listing')
        self.assert_json_equal("", "print_model/@1/name", 'label')
        self.assert_json_equal("", "print_model/@2/name", 'reporting')

    def testreload_label(self):
        self.factory.xfer = PrintModelSave()
        self.calljson('/CORE/printModelSave', {'print_model': 2, 'name': 'new label', 'value':
                                               "#name{[newline]}#date #time{[newline]}#value:#price"}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelSave')

        self.factory.xfer = PrintModelReload()
        self.calljson('/CORE/printModelReload', {'print_model': 2}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelReload')
        self.assert_json_equal('SELECT', "default_model", "Exemple_0002")

        self.factory.xfer = PrintModelReload()
        self.calljson('/CORE/printModelReload', {'print_model': 2, 'SAVE': 'YES', 'default_model': "Exemple_0015"}, False)
        self.assert_observer('core.acknowledge', 'CORE', 'printModelReload')

        self.factory.xfer = PrintModelReload()
        self.calljson('/CORE/printModelReload', {'print_model': 2, 'SAVE': 'YES', 'default_model': "Exemple_0002"}, False)
        self.assert_observer('core.dialogbox', 'CORE', 'printModelReload')

        self.factory.xfer = PrintModelEdit()
        self.calljson('/CORE/printModelEdit', {'print_model': 2}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelEdit')
        self.assert_json_equal('EDIT', "name", "new label")
        self.assert_json_equal('LABELFORM', "kind", 1)
        self.assert_json_equal('MEMO', "value", "#name{[newline]}#value:#price{[newline]}#date #time")

    def testexportimport_label(self):
        from _io import BytesIO
        from os import unlink
        from zipfile import ZipFile

        self.factory.xfer = PrintModelExtract()
        self.calljson('/CORE/printModelExtract', {'print_model': 2}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelExtract')
        filename = self.json_comp["filename"]["filename"]
        sign = filename[42:]
        self.assertEqual(filename[:42], "CORE/download?filename=extract-2.mdl&sign=")

        self.factory.xfer = Download()
        self.calljson('/CORE/download', {'filename': 'extract-2.mdl', 'sign': 'abcdef'}, False)
        self.assert_observer('core.exception', 'CORE', 'download')
        self.assert_json_equal("", "message", "Fichier invalide!")

        self.factory.xfer = Download()
        self.calljson('/CORE/download', {'filename': 'extract-5.mdl', 'sign': sign}, False)
        self.assert_observer('core.exception', 'CORE', 'download')
        self.assert_json_equal("", "message", "Ficher non trouvé!")

        self.factory.xfer = Download()
        response = self.factory.call('/CORE/download', {'filename': 'extract-2.mdl', 'sign': sign})
        zip_content = b""
        for stream_item in response.streaming_content:
            zip_content += stream_item
        zip_file = BytesIO(zip_content)
        zip_ref = ZipFile(zip_file, 'r')
        file_model = zip_ref.extract('printmodel')
        try:
            with open(file_model, 'r') as mdl:
                model_content = mdl.read()
            self.assertTrue('name = "label"' in model_content, model_content)
            self.assertTrue('kind = 1' in model_content, model_content)
            self.assertTrue('modelname = "dummy.Example"' in model_content, model_content)
            self.assertTrue('mode = 0' in model_content, model_content)
            self.assertTrue('value = """#name{[newline]}#value:#price{[newline]}#date #time"""' in model_content,
                            model_content)

            self.factory.xfer = PrintModelSave()
            self.calljson('/CORE/printModelSave', {'print_model': 2, 'name': 'new label', 'value':
                                                   "#name{[newline]}#date #time{[newline]}#value:#price"}, False)
            self.assert_observer('core.acknowledge', 'CORE', 'printModelSave')

            self.factory.xfer = PrintModelImport()
            self.calljson('/CORE/printModelImport', {'print_model': 2}, False)
            self.assert_observer('core.custom', 'CORE', 'printModelImport')

            with ZipFile('test.mdl', 'w') as new_zip:
                new_zip.writestr('printmodel', model_content)

            with open('test.mdl', 'rb') as new_zip:
                self.factory.xfer = PrintModelImport()
                self.calljson('/CORE/printModelImport', {'print_model': 2, 'SAVE': 'YES',
                                                         'import_model_FILENAME': 'report.mdl', 'import_model': new_zip}, False)
                self.assert_observer('core.dialogbox', 'CORE', 'printModelImport')
        finally:
            if isfile(file_model):
                unlink(file_model)
            if isfile('test.mdl'):
                unlink('test.mdl')

        self.factory.xfer = PrintModelEdit()
        self.calljson('/CORE/printModelEdit', {'print_model': 2}, False)
        self.assert_observer('core.custom', 'CORE', 'printModelEdit')
        self.assert_json_equal('EDIT', "name", "new label")
        self.assert_json_equal('LABELFORM', "kind", 1)
        self.assert_json_equal('MEMO', "value", "#name{[newline]}#value:#price{[newline]}#date #time")

    def testbadimport_label(self):
        from os import unlink
        from zipfile import ZipFile
        try:
            with open('test.mdl', 'w+') as new_zip:
                new_zip.write("bad file name")
            with open('test.mdl', 'rb') as new_zip:
                self.factory.xfer = PrintModelImport()
                self.calljson('/CORE/printModelImport', {'print_model': 2, 'SAVE': 'YES',
                                                         'import_model_FILENAME': 'report.mdl', 'import_model': new_zip}, False)
                self.assert_observer('core.exception', 'CORE', 'printModelImport')
                self.assert_json_equal("", 'message', "Fichier modèle invalide!")

            with ZipFile('test.mdl', 'w') as new_zip:
                new_zip.writestr('truc', "bad file name")
            with open('test.mdl', 'rb') as new_zip:
                self.factory.xfer = PrintModelImport()
                self.calljson('/CORE/printModelImport', {'print_model': 2, 'SAVE': 'YES',
                                                         'import_model_FILENAME': 'report.mdl', 'import_model': new_zip}, False)
                self.assert_observer('core.exception', 'CORE', 'printModelImport')
                self.assert_json_equal("", 'message', "Fichier modèle invalide!")
        finally:
            if isfile('test.mdl'):
                unlink('test.mdl')
