# -*- coding: utf-8 -*-
'''
lucterios.framework.management.commands package

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

from django.core.management.base import BaseCommand

from lucterios.framework.management.commands._viewer_generator import Generator, GenForm


class Command(BaseCommand):
    help = 'Generate view for Lucterios model'

    def add_arguments(self, parser):
        parser.add_argument('module_name', type=str)

    def handle(self, module_name, *args, **options):
        gen = Generator(".", module_name)
        gen_form = GenForm()
        gen_form.load(gen.class_model, gen.extract_icons())
        if gen_form.result is not None:
            gen.write_actions(gen_form.get_model_name(), gen_form.get_icon_name(), gen_form.result)
