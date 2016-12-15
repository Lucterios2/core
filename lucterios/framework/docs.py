# -*- coding: utf-8 -*-
'''
Tools to manage online doc in Lucterios

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

from django.utils import six
from django.conf import settings
from django.utils.module_loading import import_module
from django.utils.translation import get_language

from os.path import dirname, join, isdir


def find_doc(appname):
    module = import_module(appname)
    doc_path = join(
        dirname(module.__file__), "static", appname, 'doc_%s' % get_language())
    if isdir(doc_path):
        if hasattr(module, '__title__'):
            return (appname, six.text_type(module.__title__()))
        else:
            return (appname, appname)
    return None


def defaultDocs(request):
    from django.shortcuts import render_to_response
    dictionary = {}
    dictionary['title'] = six.text_type(settings.APPLIS_NAME)
    dictionary['subtitle'] = settings.APPLIS_SUBTITLE()
    dictionary['applogo'] = settings.APPLIS_LOGO
    dictionary['version'] = six.text_type(settings.APPLIS_VERSION)
    dictionary['lang'] = get_language()
    dictionary['menus'] = []
    dictionary['menus'].append(find_doc(settings.APPLIS_MODULE.__name__))
    for appname in settings.INSTALLED_APPS:
        if ("django" not in appname) and ("lucterios.CORE" not in appname) and (settings.APPLIS_MODULE.__name__ != appname):
            help_item = find_doc(appname)
            if help_item is not None:
                dictionary['menus'].append(help_item)
    dictionary['menus'].append(find_doc('lucterios.CORE'))
    return render_to_response('main_docs.html', context=dictionary)
