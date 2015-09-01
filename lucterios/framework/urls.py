# -*- coding: utf-8 -*-
'''
Generic generator of Django urls patern for Lucterios

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
from django.conf.urls import url, include
from django.conf import settings
from django.utils.module_loading import import_module
from django.views.static import serve

from os.path import join, dirname, isdir
import logging
import inspect
import pkgutil
from lucterios.framework.help import defaulthelp


def defaultblank(*args):
    from django.http import HttpResponse
    return HttpResponse('')


def defaultview(*args):
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect('/web/index.html')


def _init_url_patterns():
    from django.contrib import admin
    admin.autodiscover()
    res = []
    web_path = join(dirname(dirname(__file__)), 'web')
    res.append(url(r'^$', defaultview))
    res.append(url(r'^web/$', defaultview))
    res.append(url(r'^web/STUB/(.*)$', defaultblank))
    res.append(url(r'^web/(?P<path>.*)$', serve, {'document_root': web_path}))
    res.append(url(r'^Help$', defaulthelp))
    res.append(url(r'^admin/', include(admin.site.urls)))
    return res


def add_url_from_module(url_list, appmodule, lucterios_ext):
    extpath_img = join(dirname(appmodule.__file__), 'images')
    if isdir(extpath_img):
        if lucterios_ext == 'CORE':
            url_list.append(
                url(r'^images/(?P<path>.*)$', serve, {'document_root': extpath_img}))
        else:
            url_list.append(url(r'^%s/images/(?P<path>.*)$' %
                                lucterios_ext, serve, {'document_root': extpath_img}))
    extpath_help = join(dirname(appmodule.__file__), 'help')
    if isdir(extpath_help):
        url_list.append(url(r'^%s/help/(?P<path>.*)$' %
                            lucterios_ext, serve, {'document_root': extpath_help}))


def get_url_patterns():
    res = _init_url_patterns()
    for appname in settings.INSTALLED_APPS:
        if "django" not in appname:
            appmodule = import_module(appname)
            module_items = appname.split('.')
            if (len(module_items) > 1) and (module_items[1] == 'CORE'):
                module_items = module_items[1:]
            lucterios_ext = ".".join(module_items)
            for _, modname, ispkg in pkgutil.iter_modules(appmodule.__path__):
                if (modname[:5] == 'views') and not ispkg:
                    view = import_module(appname + '.' + modname)
                    for obj in inspect.getmembers(view):
                        try:
                            if obj[1].url_text != '':
                                if inspect.isclass(obj[1]):
                                    as_view_meth = getattr(obj[1], "as_view")
                                    res.append(
                                        url(r"^%s$" % obj[1].url_text, as_view_meth()))
                        except AttributeError:
                            pass
            if lucterios_ext is not None:
                add_url_from_module(res, appmodule, lucterios_ext)
    logging.getLogger('lucterios.core.init').debug("Urls:" + str(res))
    return res


urlpatterns = get_url_patterns()
