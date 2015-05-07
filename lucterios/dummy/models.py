# -*- coding: utf-8 -*-
'''
models for Django module dummy

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
along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from django.db import models
from lucterios.framework.models import LucteriosModel
from django.core.validators import MinValueValidator, MaxValueValidator

class Example(LucteriosModel):
    name = models.CharField(max_length=75, unique=True)
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(-5000.0), MaxValueValidator(5000.0)])
    date = models.DateField()
    time = models.TimeField()
    valid = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    example__showfields = ['name', ('value', 'price'), ('date', 'time'), 'valid', 'comment']
    example__editfields = ['name', ('value', 'price'), ('date', 'time'), 'valid', 'comment']
    example__searchfields = ['name', 'value', 'price', 'date', 'time', 'valid', 'comment']
    default_fields = ["name", 'value', 'price']
    print_fields = ['name', 'value', 'price', 'date', 'time', 'valid', 'comment']
