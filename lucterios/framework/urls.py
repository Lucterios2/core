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
from django.conf.urls import url, include, patterns
from django.conf import settings
from django.utils.module_loading import import_module
from django.views.static import serve

from os.path import join, dirname, isdir, basename
import logging
import inspect
import pkgutil
from lucterios.framework.docs import defaultDocs


def defaultblank(request, *args):
    from django.http import HttpResponse
    if request.path == '/favicon.ico':
        if hasattr(settings, 'APPLIS_FAVICON'):
            return serve(request, basename(settings.APPLIS_FAVICON), document_root=dirname(settings.APPLIS_LOGO_NAME))
    return HttpResponse('')


def defaultview(*args):
    from django.http import HttpResponseRedirect
    web_page = settings.DEFAULT_PAGE
    if settings.USE_X_FORWARDED_HOST:
        web_page = settings.FORCE_SCRIPT_NAME + web_page
    return HttpResponseRedirect(web_page)


def _init_url_patterns():
    from django.contrib import admin
    admin.autodiscover()
    res = []
    web_path = join(dirname(__file__), 'static', 'framework', 'web')
    res.append(url(r'^$', defaultview))
    res.append(url(r'^favicon.ico$', defaultblank))
    res.append(url(r'^web/$', defaultview))
    res.append(url(r'^web/STUB/(.*)$', defaultblank))
    res.append(url(r'^web/(?P<path>.*)$', serve, {'document_root': web_path}))
    res.append(url(r'^Docs$', defaultDocs))
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
    mod_id = appmodule.__name__.split('.')[-1]
    extpath_static = join(dirname(appmodule.__file__), 'static', mod_id)
    if isdir(extpath_static):
        url_list.append(url(r'^static/%s/(?P<path>.*)$' %
                            mod_id, serve, {'document_root': extpath_static}))


def get_url_patterns():
    res = _init_url_patterns()
    for appname in settings.INSTALLED_APPS:
        appmodule = import_module(appname)
        module_items = appname.split('.')
        if (len(module_items) > 1) and (module_items[1] == 'CORE'):
            module_items = module_items[1:]
        is_lucterios_ext = False
        lucterios_ext = ".".join(module_items)
        for _, modname, ispkg in pkgutil.iter_modules(appmodule.__path__):
            if (modname[:5] == 'views') and not ispkg:
                view = import_module(appname + '.' + modname)
                for obj in inspect.getmembers(view):
                    try:
                        if obj[1].url_text != '':
                            if inspect.isclass(obj[1]):
                                is_lucterios_ext = True
                                as_view_meth = getattr(obj[1], "as_view")
                                res.append(
                                    url(r"^%s$" % obj[1].url_text, as_view_meth()))
                    except AttributeError:
                        pass
            elif settings.APPLIS_MODULE == appmodule:
                is_lucterios_ext = True
        if is_lucterios_ext:
            add_url_from_module(res, appmodule, lucterios_ext)
        else:
            try:
                patterns = getattr(
                    import_module('%s.urls' % appname), 'urlpatterns', None)
                if isinstance(patterns, (list, tuple)):
                    for url_pattern in patterns:
                        if module_items[0] == 'django':
                            res.append(url_pattern)
                        else:
                            res.append(url(r"^%s/%s" % (module_items[-1], url_pattern._regex[1:]),
                                           url_pattern._callback or url_pattern._callback_str,
                                           url_pattern.default_args, url_pattern.name))
            except ImportError:
                pass
    try:
        from django.contrib.admin.sites import site
        res.append(url(r'^accounts/login/$', site.login))
    except ImportError:
        pass
    logging.getLogger('lucterios.core.init').debug(
        "Urls:" + '\n'.join(str(res_item) for res_item in res))
    return res


urlpatterns = get_url_patterns()
