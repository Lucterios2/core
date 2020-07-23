# -*- coding: utf-8 -*-
'''
lucterios.framework.management.commands package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2020 sd-libre.fr
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
from importlib import import_module

from django.core.management.base import BaseCommand

from lucterios.framework.urls import urlpatterns


class Command(BaseCommand):
    help = 'Return API REST url list'

    right_association = {'': ('GET',), 'change': ('GET',), 'add': ('POST', 'PUT'), 'delete': ('DELETE',)}

    def add_arguments(self, parser):
        parser.add_argument('-o', '--only_warning', action='store_true')
        parser.add_argument('-f', '--filterurl', type=str)

    def handle(self, only_warning, filterurl, *args, **options):
        self.stdout.write(self.style.SUCCESS('*** API REST ***'))
        url_list = list({str(urlpattern.pattern).replace("^", "").replace("$", ""): urlpattern.callback for urlpattern in urlpatterns}.items())
        url_list.sort(key=lambda item: item[0])
        if filterurl is not None:
            url_list = filter(lambda url_item: url_item[0].startswith(filterurl), url_list)
        for url_item in url_list:
            url = url_item[0]
            view = url_item[1]
            try:
                view_mod = import_module(view.__module__)
                class_view = getattr(view_mod, view.__name__, None)
                if getattr(class_view, "url_text", "") == url:
                    default_method = class_view.methods_allowed[0]
                    if isinstance(class_view.is_view_right, tuple):
                        right = 'add'
                    if (class_view.is_view_right is None):
                        right = 'change'
                    else:
                        right = class_view.is_view_right.split('.')[-1].split('_')[0]
                    text = "%s [%s] %s (%s)" % (url.ljust(50, ' '), default_method, class_view.is_view_right, right)
                    if (((right == '') and (default_method == 'GET')) or (default_method in self.right_association[right])):
                        if only_warning is False:
                            self.stdout.write(text)
                    else:
                        self.stdout.write(self.style.WARNING(text))
            except (ModuleNotFoundError, AttributeError):
                pass
        self.stdout.write(self.style.SUCCESS('****************'))
