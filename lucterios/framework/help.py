# -*- coding: utf-8 -*-
'''
Tools to manage online help in Lucterios

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
from django.utils.translation import ugettext, get_language

from os.path import dirname, join, isdir
from os import listdir
from lucterios import CORE


def find_help(module):
    help_file = []
    help_dico = {}
    help_path = join(dirname(module.__file__), "help")
    if isdir(help_path):
        for hfile in listdir(help_path):
            if hfile.endswith(".html"):
                help_dico[hfile] = ugettext(hfile)
        for hfile in sorted(help_dico.keys()):
            help_file.append(
                ("%s-%s" % (module.__name__, hfile), help_dico[hfile]))
        if hasattr(module, '__title__'):
            return (module.__name__, six.text_type(module.__title__()), help_file)
        else:
            return (module.__name__, module.__name__, help_file)
    return None


def defaulthelp(request):
    from django.shortcuts import render_to_response
    help_id = request.GET.get("helpid")
    if help_id is None:
        dictionary = {}
        dictionary['title'] = six.text_type(settings.APPLIS_NAME)
        dictionary['subtitle'] = settings.APPLIS_SUBTITLE()
        dictionary['applogo'] = settings.APPLIS_LOGO
        dictionary['version'] = six.text_type(settings.APPLIS_VERSION)
        dictionary['menus'] = []
        dictionary['menus'].append(find_help(settings.APPLIS_MODULE))
        for appname in settings.INSTALLED_APPS:
            if ("django" not in appname) and ("lucterios.CORE" not in appname) and (settings.APPLIS_MODULE.__name__ != appname):
                help_item = find_help(import_module(appname))
                if help_item is not None:
                    dictionary['menus'].append(help_item)
        dictionary['menus'].append(find_help(CORE))
        return render_to_response('main_help.html', dirs=[dirname(__file__)], dictionary=dictionary)
    else:
        module_name, help_file = help_id.split('-')
        module = import_module(module_name)
        help_path = join(dirname(module.__file__), "help")
        return render_to_response(help_file, dirs=[help_path])


def find_doc(module):
    mod_id = module.__name__.split('.')[-1]
    doc_path = join(
        dirname(module.__file__), "static", mod_id, 'doc_%s' % get_language())
    if isdir(doc_path):
        if hasattr(module, '__title__'):
            return (mod_id, six.text_type(module.__title__()))
        else:
            return (mod_id, module.__name__)
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
    dictionary['menus'].append(find_doc(settings.APPLIS_MODULE))
    for appname in settings.INSTALLED_APPS:
        if ("django" not in appname) and ("lucterios.CORE" not in appname) and (settings.APPLIS_MODULE.__name__ != appname):
            help_item = find_doc(import_module(appname))
            if help_item is not None:
                dictionary['menus'].append(help_item)
    dictionary['menus'].append(find_doc(CORE))
    return render_to_response('main_docs.html', dirs=[dirname(__file__)], dictionary=dictionary)
