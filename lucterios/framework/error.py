# -*- coding: utf-8 -*-
'''
Lucterios exception

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

INTERNAL = 0
CRITIC = 1
GRAVE = 2
IMPORTANT = 3
MINOR = 4


class LucteriosException(Exception):

    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code


class LucteriosRedirectException(LucteriosException):

    def __init__(self, msg, redirectclassaction):
        LucteriosException.__init__(self, IMPORTANT, msg)
        self.redirectclassview = redirectclassaction


def get_error_trace():
    import sys
    import traceback
    trace = traceback.extract_tb(sys.exc_info()[2])[3:]
    res = six.text_type('')
    for item in trace:
        try:
            res += six.text_type("%s in line %d in %s : %s{[br/]}") % item
        except:
            try:
                res += six.text_type("%s in line %d in %s : %s{[br/]}") % (item.filename, item.lineno, item.name, item.line)
            except:
                res += "???{[br/]}"
    return res
