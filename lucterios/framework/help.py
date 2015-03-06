# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from django.utils import six
from django.conf import settings
from django.utils.module_loading import import_module
from django.utils.translation import ugettext

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
            help_file.append(("%s-%s" % (module.__name__, hfile), help_dico[hfile]))
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
        dictionary['subtitle'] = six.text_type(settings.APPLIS_SUBTITLE())
        dictionary['applogo'] = settings.APPLIS_LOGO
        dictionary['version'] = six.text_type(settings.APPLIS_VERSION)
        dictionary['menus'] = []
        dictionary['menus'].append(find_help(settings.APPLIS_MODULE))
        for appname in settings.INSTALLED_APPS:
            if (not "django" in appname) and (not "lucterios.CORE" in appname) and (settings.APPLIS_MODULE.__name__ != appname):
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
