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
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from lucterios.framework.models import LucteriosModel
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.models import Parameter
from lucterios.framework.auditlog import auditlog
from lucterios.framework.model_fields import LucteriosDecimalField,\
    LucteriosVirtualField


class Example(LucteriosModel):

    name = models.CharField(max_length=75, unique=True)
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    price = LucteriosDecimalField(max_digits=6, decimal_places=2, default=100.0,
                                  validators=[MinValueValidator(-5000.0), MaxValueValidator(5000.0)],
                                  format_string="C2EUR;{[font color='green']}%s{[/font]};{[font color='red']}%s{[/font]}")
    date = models.DateField(null=True)
    time = models.TimeField()
    valid = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    virtual = LucteriosVirtualField(verbose_name='reduction', compute_from='get_virtual', format_string="N4")

    def __str__(self):
        return self.name

    def get_virtual(self):
        if self.id is None:
            return None
        elif (self.price is None) or (self.value is None):
            return 0
        else:
            return float(self.price) * float(self.value) / 100.0

    @classmethod
    def get_show_fields(cls):
        return ['name', ('value', 'price'), ('date', 'time'), 'virtual', 'valid', 'comment']

    @classmethod
    def get_edit_fields(cls):
        return ['name', ('value', 'price'), ('date', 'time'), 'valid', 'comment']

    @classmethod
    def get_search_fields(cls):
        return ['name', 'value', 'price', 'date', 'time', 'valid', 'comment']

    @classmethod
    def get_default_fields(cls):
        return ["name", 'value', 'price']

    @classmethod
    def get_print_fields(cls):
        return cls.get_search_fields()


class Other(LucteriosModel):

    text = models.CharField(max_length=75, unique=True)
    integer = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(2000)])
    real = LucteriosDecimalField(max_digits=6, decimal_places=2,
                                 format_string=lambda: "N4",
                                 validators=[MinValueValidator(-5000.0), MaxValueValidator(5000.0)])
    bool = models.BooleanField(default=False)


@Signal.decorate('auditlog_register')
def dummy_auditlog_register():
    auditlog.register(Example)
    auditlog.register(Other)


@Signal.decorate('checkparam')
def dummy_checkparam():
    Parameter.check_and_create(name="dummy-value", typeparam=0, title=_("dummy-value"), args="{}", value='')
