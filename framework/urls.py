# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.conf.urls import patterns, url, include
from django.conf import settings
from django.utils.module_loading import import_module

from os.path import join, dirname, isdir, isfile
import logging
import inspect
import pkgutil

def defaultblank(_):
    from django.http import HttpResponse
    return HttpResponse('')

def defaultview(_):
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect('/web/index.html')


def _init_url_patterns():
    from django.contrib import admin
    admin.autodiscover()
    res = patterns('')
    web_path = join(dirname(dirname(__file__)), 'web')
    if isdir(web_path) and isfile(join(web_path, 'index.html')):
        res.append(url(r'^$', defaultview))
        res.append(url(r'^web/$', defaultview))
        res.append(url(r'^web/(?P<path>.*)$', 'django.views.static.serve', {'document_root':join(dirname(dirname(__file__)), 'web')}))
    else:
        res.append(url(r'^$', defaultblank))
        res.append(url(r'^web/.*', defaultblank))
    res.append(url(r'^admin/', include(admin.site.urls)))
    return res

def get_url_patterns():
    res = _init_url_patterns()
    for appname in settings.INSTALLED_APPS:
        if not "django" in appname:
            appmodule = import_module(appname)
            lucterios_ext = None
            for _, modname, ispkg in pkgutil.iter_modules(appmodule.__path__):
                if (modname[:5] == 'views') and not ispkg:
                    view = import_module(appname + '.' + modname)
                    for obj in inspect.getmembers(view):
                        try:
                            if obj[1].url_text != '':
                                if inspect.isclass(obj[1]):
                                    as_view_meth = getattr(obj[1], "as_view")
                                    res.append(url(r"^%s$" % obj[1].url_text, as_view_meth()))
                                    lucterios_ext = obj[1].extension
                        except AttributeError:
                            pass
            if lucterios_ext is not None:
                extpath = join(dirname(appmodule.__file__), 'images')
                if isdir(extpath):
                    if lucterios_ext == 'CORE':
                        res.append(url(r'^images/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : extpath}))
                    else:
                        res.append(url(r'^%s/images/(?P<path>.*)$' % lucterios_ext, 'django.views.static.serve', {'document_root' : extpath}))
    logging.getLogger(__name__).debug("Urls:" + str(res))
    return res

# pylint: disable=invalid-name
urlpatterns = get_url_patterns()
