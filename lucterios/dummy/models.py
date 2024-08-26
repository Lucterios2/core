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
from os.path import join, dirname

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from lucterios.framework.models import LucteriosModel
from lucterios.framework.signal_and_lock import Signal
from lucterios.CORE.models import Parameter, Preference
from lucterios.framework.auditlog import auditlog
from lucterios.framework.model_fields import LucteriosDecimalField, LucteriosVirtualField
from lucterios.framework.tools import get_date_formating
from lucterios.framework.filetools import readimage_to_base64


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
    image = LucteriosVirtualField(verbose_name='image', compute_from='get_image')
    html_info = LucteriosVirtualField(verbose_name='html_info', compute_from='get_html_info')

    def __str__(self):
        return self.name

    def get_virtual(self):
        if self.id is None:
            return None
        elif (self.price is None) or (self.value is None):
            return 0
        else:
            return float(self.price) * float(self.value) / 100.0

    def get_image(self):
        if self.valid:
            return 'mdi:mdi-mailbox-up'
        else:
            return readimage_to_base64(join(dirname(dirname(__file__)), 'CORE', 'static', 'lucterios.CORE', 'images', 'config.png')).decode()

    def get_html_info(self):
        return """<b>name</b> %s<br>
<b>comment</b> %s<br>
<b>date</b> %s<br>
<b>time</b> %s
""" % (self.name, self.comment, get_date_formating(self.date), get_date_formating(self.time))

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

    class Meta(object):
        ordering = ['name']


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
    Parameter.check_and_create(name="dummy-value", typeparam=Parameter.TYPE_STRING, title=_("dummy-value"), args="{}", value='')
    Preference.check_and_create(name="dummy-default-value", typeparam=Preference.TYPE_INTEGER, title=_("dummy-default-value"), args="{'min':0,'max':10}", value='0')
    Preference.check_and_create(name="dummy-default-price", typeparam=Preference.TYPE_REAL, title=_("dummy-default-price"), args="{'min':0,'max':1000,'prec':2}", value='100')
    Preference.check_and_create(name="dummy-default-valid", typeparam=Preference.TYPE_BOOL, title=_("dummy-default-valid"), args="{}", value='False')
