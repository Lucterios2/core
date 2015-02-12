# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from django.conf.urls import patterns, url
from inspect import getmembers
from django.conf import settings
from django.utils.module_loading import import_module

import logging
import inspect
import pkgutil

def defaultview(_):
    from django.http import HttpResponse
    return HttpResponse('<h1>DEFAULT</h1>')

def get_url_patterns():
    res = patterns('')
    res.append(url(r'^$', defaultview))
    res.append(url(r'^web/$', defaultview))
    for appname in settings.INSTALLED_APPS:
        if not "django" in appname:
            appmodule = import_module(appname)
            for _, modname, ispkg in pkgutil.iter_modules(appmodule.__path__):
                if (modname[:5] == 'views') and not ispkg:
                    view = import_module(appname + '.' + modname)
                    for obj in getmembers(view):
                        try:
                            if obj[1].url_text != '':
                                if inspect.isclass(obj[1]):
                                    as_view_meth = getattr(obj[1], "as_view")
                                    res.append(url(obj[1].url_text, as_view_meth()))
                                else:
                                    res.append(url(obj[1].url_text, obj[1]))
                        except AttributeError:
                            raise
    logging.getLogger(__name__).debug("Urls:" + str(res))
    return res

# pylint: disable=invalid-name
urlpatterns = get_url_patterns()
