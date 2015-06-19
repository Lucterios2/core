# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
'''
Initial django module for dummy

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

from django.db import models, migrations
import django.core.validators
from django.utils import six
from lucterios.CORE.models import PrintModel
from lucterios.dummy.models import Example

def initial_values(*args):
    # pylint: disable=unused-argument, no-member, expression-not-assigned
    prtmdl = PrintModel.objects.create(name="listing", kind=0, modelname=Example.get_long_name())
    prtmdl.change_listing(210, 297, [(10, 'Name', '#name'), \
                                     (20, 'value + price', '#value/#price'), \
                                     (20, 'date + time', '#date{[newline]}#time')])
    prtmdl.save()
    prtmdl = PrintModel.objects.create(name="label", kind=1, modelname=Example.get_long_name())
    prtmdl.value = "#name{[newline]}#value:#price{[newline]}#date #time"
    prtmdl.save()

class Migration(migrations.Migration):

    dependencies = [
        (six.text_type("CORE"), six.text_type("0001_initial")),
    ]

    operations = [
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=75, unique=True)),
                ('value', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)])),
                ('price', models.DecimalField(validators=[django.core.validators.MinValueValidator(-5000.0), django.core.validators.MaxValueValidator(5000.0)], decimal_places=2, max_digits=6)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('valid', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True)),
            ],
            bases=(models.Model,),
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Other',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('text', models.CharField(max_length=75, unique=True)),
                ('integer', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(20)])),
                ('real', models.DecimalField(max_digits=6, decimal_places=2, validators=[django.core.validators.MinValueValidator(-5000.0), django.core.validators.MaxValueValidator(5000.0)])),
                ('bool', models.BooleanField(default=False)),
            ],
            bases=(models.Model,),
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(initial_values),
    ]
