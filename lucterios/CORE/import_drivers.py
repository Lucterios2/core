# -*- coding: utf-8 -*-
'''
View for manage user password, print model and label in Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2023 sd-libre.fr
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

from io import StringIO, TextIOWrapper, BytesIO
from csv import DictReader
from _csv import QUOTE_NONE, QUOTE_ALL
from re import sub
from datetime import datetime
from base64 import b64decode, b64encode
from pandas import read_excel
from logging import getLogger

from django.utils.translation import gettext_lazy as _

from lucterios.framework.error import LucteriosException, IMPORTANT


class ImportDriver(object):

    NAME = ""
    FIELD_LIST = ()
    EXTENSION = ""
    EXTENSION_TITLE = ""

    def __init__(self):
        self.default_values = {}

    def read(self, request_file=None):
        pass

    def get_column_names(self):
        return []

    def get_rows(self):
        return []

    def get_readed_content(self, fields_description):
        return []

    @classmethod
    def subclasses(cls):
        for sub_cls in cls.__subclasses__():
            yield sub_cls
            for sub_sub_cls in sub_cls.subclasses():
                yield sub_sub_cls

    @classmethod
    def factory_list(cls):
        for sub_cls in cls.subclasses():
            if sub_cls.NAME != '':
                yield sub_cls.NAME

    @classmethod
    def factory(cls, name):
        for sub_cls in cls.subclasses():
            if sub_cls.NAME == name:
                return sub_cls()
        return ImportDriverCSV()


class ImportDriverCSV(ImportDriver):

    NAME = "CSV"

    FIELD_LIST = (("encoding", _('encoding')),
                  ("dateformat", _('date format')),
                  ("delimiter", _('delimiter')),
                  ("quotechar", _('quotechar')))
    EXTENSION = ".csv"
    EXTENSION_TITLE = _('CSV file')

    def __init__(self):
        ImportDriver.__init__(self)
        self.quotechar = "'"
        self.delimiter = ";"
        self.encoding = "utf-8"
        self.dateformat = "%d/%m/%Y"
        self.spamreader = None

    def read(self, xfer):
        if self.quotechar == '':
            current_quoting = QUOTE_NONE
        else:
            current_quoting = QUOTE_ALL
        if 'importcontent' in xfer.request.FILES.keys():
            csvfile = TextIOWrapper(xfer.request.FILES['importcontent'].file,
                                    encoding=self.encoding, errors='replace')
            csvcontent = "".join(csvfile.readlines())
            for param_idx in range(0, int(len(csvcontent) / 2048) + 2):
                xfer.params['importcontent%d' % param_idx] = csvcontent[2048 * param_idx:2048 * (param_idx + 1)]
            csvfile.seek(0)
        else:
            csvcontent = ""
            for param_idx in range(0, 1000):
                curent_content = xfer.getparam('importcontent%d' % param_idx)
                if curent_content is None:
                    break
                else:
                    csvcontent += "" + curent_content
            csvfile = StringIO(csvcontent)
        self.spamreader = DictReader(csvfile, delimiter=self.delimiter, quotechar=self.quotechar, quoting=current_quoting)
        try:
            if (self.spamreader.fieldnames is None) or (len(self.spamreader.fieldnames) == 0):
                raise Exception("")
        except Exception:
            getLogger("lucterios.core.request").exception("read CSV")
            raise LucteriosException(IMPORTANT, _('CSV file unvalid!'))

    def get_column_names(self):
        for fieldname in self.spamreader.fieldnames:
            if fieldname != '':
                yield fieldname

    def get_rows(self):
        for row in self.spamreader:
            if row[self.spamreader.fieldnames[0]] is not None:
                new_row = {}
                for fieldname in self.spamreader.fieldnames:
                    if fieldname != '':
                        new_row[fieldname] = row[fieldname]
                yield new_row

    def _convert_record(self, fields_description, row):
        new_row = self.default_values.copy()
        for field_description in fields_description:
            if field_description[2] == 'T':
                try:
                    new_row[field_description[0]] = "%s:%s" % tuple(row[field_description[4]].split(':')[:2])
                except (TypeError, ValueError):
                    new_row[field_description[0]] = "00:00"
            elif field_description[2] in ('D', 'H'):
                try:
                    new_row[field_description[0]] = datetime.strptime(row[field_description[4]], self.dateformat).date()
                except (TypeError, ValueError):
                    new_row[field_description[0]] = datetime.today()
            elif isinstance(field_description[2], str) and (field_description[2].startswith('N') or field_description[2].startswith('C')):
                float_val = row[field_description[4]]
                float_val = float_val.replace(',', '.')
                float_val = sub(r"( |[^0-9.])", "", float_val)
                if float_val == '':
                    float_val = 0
                if field_description[2] == 'N0':
                    new_row[field_description[0]] = int(float_val)
                else:
                    new_row[field_description[0]] = float(float_val)
            elif field_description[2] == 'B':
                value = row[field_description[4]].strip().lower()[0]
                new_row[field_description[0]] = (value != '0') and (value != 'f') and (value != 'n')
            elif row[field_description[4]] is None:
                new_row[field_description[0]] = None
            else:
                new_row[field_description[0]] = row[field_description[4]].strip()
        return new_row

    def get_readed_content(self, fields_description):
        for row in self.spamreader:
            if row[self.spamreader.fieldnames[0]] is not None:
                yield self._convert_record(fields_description, row)


class ImportDriverPandas(ImportDriver):

    def __init__(self):
        ImportDriver.__init__(self)
        self.pandas_content = None

    def read(self, xfer):
        if 'importcontent' in xfer.request.FILES.keys():
            odsfile = xfer.request.FILES['importcontent'].file
            odscontent = b64encode(odsfile.read())
            for param_idx in range(0, int(len(odscontent) / 2048) + 2):
                xfer.params['importcontent%d' % param_idx] = odscontent[2048 * param_idx:2048 * (param_idx + 1)].decode()
            odsfile.seek(0)
        else:
            odscontent = ""
            for param_idx in range(0, 1000):
                curent_content = xfer.getparam('importcontent%d' % param_idx)
                if curent_content is None:
                    break
                else:
                    odscontent += "" + curent_content
            odsfile = BytesIO(b64decode(odscontent.encode()))
        try:
            self.pandas_content = read_excel(odsfile)
        except Exception:
            getLogger("lucterios.core.request").exception("read Pandas")
            raise LucteriosException(IMPORTANT, _('file unvalid!'))

    def get_column_names(self):
        for column in self.pandas_content.columns.array:
            if column != '':
                yield str(column)

    def get_rows(self):
        for row in self.pandas_content.values:
            new_row = {}
            for col_idx, column in enumerate(self.pandas_content.columns.array):
                if hasattr(row[col_idx], 'all'):
                    raise LucteriosException(IMPORTANT, _('file unvalid!'))
                new_row[column] = row[col_idx]
            yield new_row

    def _convert_record(self, fields_description, row):
        new_row = self.default_values.copy()
        columns = list(self.get_column_names())
        for field_description in fields_description:
            col_index = columns.index(field_description[4])
            if field_description[2] == 'T':
                try:
                    new_row[field_description[0]] = "%s:%s" % tuple(str(row[col_index]).split(':')[:2])
                except (TypeError, ValueError):
                    new_row[field_description[0]] = "00:00"
            elif field_description[2] in ('D', 'H'):
                try:
                    new_row[field_description[0]] = row[col_index].date()
                except (TypeError, ValueError):
                    new_row[field_description[0]] = datetime.today()
            elif isinstance(field_description[2], str) and (field_description[2].startswith('N') or field_description[2].startswith('C')):
                float_val = row[col_index]
                if field_description[2] == 'N0':
                    new_row[field_description[0]] = int(float_val)
                else:
                    new_row[field_description[0]] = float(float_val)
            elif field_description[2] == 'B':
                value = str(row[col_index]).strip().lower()[0]
                new_row[field_description[0]] = (value != '0') and (value != 'f') and (value != 'n')
            elif row[col_index] is None:
                new_row[field_description[0]] = None
            else:
                new_row[field_description[0]] = str(row[col_index]).strip()
        return new_row

    def get_readed_content(self, fields_description):
        for row in self.pandas_content.values:
            yield self._convert_record(fields_description, row)


class ImportDriverODS(ImportDriverPandas):

    NAME = "ODS"

    FIELD_LIST = ()
    EXTENSION = ".ods"
    EXTENSION_TITLE = _('ODS file')


class ImportDriverXLS(ImportDriverPandas):

    NAME = "XLS"

    FIELD_LIST = ()
    EXTENSION = ".xls,.xlsx"
    EXTENSION_TITLE = _('XLS file')
