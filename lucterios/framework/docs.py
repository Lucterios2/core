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

from django.conf import settings
from django.utils.module_loading import import_module
from django.utils.translation import get_language


def find_doc(appname):
    module = import_module(appname)
    if hasattr(module, '__title__') and (hasattr(module, 'get_build') or hasattr(module, 'link')):
        return (appname, str(module.__title__()))
    return None


def defaultDocs(request):
    from django.shortcuts import render
    from django.http.response import JsonResponse
    dictionary = {}
    dictionary['title'] = str(settings.APPLIS_NAME)
    dictionary['subtitle'] = settings.APPLIS_SUBTITLE()
    dictionary['applogo'] = settings.APPLIS_LOGO.decode() if hasattr(settings.APPLIS_LOGO, 'decode') else settings.APPLIS_LOGO
    dictionary['version'] = str(settings.APPLIS_VERSION)
    dictionary['lang'] = get_language()
    dictionary['menus'] = []
    dictionary['menus'].append(find_doc(settings.APPLIS_MODULE.__name__))
    for appname in settings.INSTALLED_APPS:
        if ("django" not in appname) and ("lucterios.CORE" not in appname) and (settings.APPLIS_MODULE.__name__ != appname):
            help_item = find_doc(appname)
            if help_item is not None:
                dictionary['menus'].append(help_item)
    dictionary['menus'].append(find_doc('lucterios.CORE'))
    if 'json' in request.GET:
        return JsonResponse(dictionary, json_dumps_params={'indent': 3})
    else:
        return render(request, 'main_docs.html', context=dictionary)
