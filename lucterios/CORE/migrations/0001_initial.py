# -*- coding: utf-8 -*-
# pylint: disable=invalid-name,line-too-long
'''
Initial module to configure in Django the Lucterios CORE

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

import django.core.validators
from django.db import models, migrations
from django.contrib.auth.models import User
from django.utils import six, timezone
from lucterios.CORE.models import Label


def initial_values(*args):
    # pylint: disable=unused-argument, no-member, expression-not-assigned
    admin = User.objects.create_user(
        six.text_type('admin'), '', six.text_type('admin'), last_login=timezone.now())
    admin.first_name = six.text_type('administrator')
    admin.last_name = six.text_type('ADMIN')
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.save()

    Label.objects.create(name='Planche 2x4', page_height=297, page_width=210, cell_height=70, cell_width=105,
                         columns=2, rows=4, left_marge=0, top_marge=8, horizontal_space=105, vertical_space=70),
    Label.objects.create(name='Planche 2x5', page_height=297, page_width=210, cell_height=57, cell_width=105,
                         columns=2, rows=5, left_marge=0, top_marge=6, horizontal_space=105, vertical_space=57),
    Label.objects.create(name='Planche 2x6', page_height=297, page_width=210, cell_height=49, cell_width=105,
                         columns=2, rows=6, left_marge=0, top_marge=0, horizontal_space=105, vertical_space=49),
    Label.objects.create(name='Planche 2x8', page_height=297, page_width=210, cell_height=35, cell_width=105,
                         columns=2, rows=8, left_marge=0, top_marge=8, horizontal_space=105, vertical_space=35),
    Label.objects.create(name='Planche 3x8', page_width=210, page_height=297, cell_width=70, cell_height=35,
                         columns=3, rows=8, left_marge=0, top_marge=9, horizontal_space=70, vertical_space=35),
    Label.objects.create(name='Planche 3x10', page_width=210, page_height=297, cell_width=70, cell_height=28,
                         columns=3, rows=10, left_marge=0, top_marge=9, horizontal_space=70, vertical_space=28)


class Migration(migrations.Migration):

    dependencies = [
        (six.text_type("auth"), six.text_type("0001_initial")),
    ]

    operations = [
        migrations.CreateModel(
            name='parameter',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    max_length=100, verbose_name='name', unique=True)),
                ('typeparam', models.IntegerField(choices=[
                 (0, 'String'), (1, 'Integer'), (2, 'Real'), (3, 'Boolean'), (4, 'Select')])),
                ('args', models.CharField(
                    max_length=200, verbose_name='arguments', default="{}")),
                ('value', models.TextField(verbose_name='value', blank=True)),
            ],
            options={
                'verbose_name': 'parameter',
                'default_permissions': ['add', 'change'],
                'verbose_name_plural': 'parameters',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LucteriosGroup',
            fields=[
            ],
            options={
                'verbose_name_plural': 'groups',
                'verbose_name': 'group',
                'proxy': True,
                'default_permissions': [],
            },
            bases=('auth.group', models.Model),
        ),
        migrations.CreateModel(
            name='LucteriosUser',
            fields=[
            ],
            options={
                'verbose_name_plural': 'users',
                'verbose_name': 'user',
                'proxy': True,
                'abstract': False,
                'default_permissions': [],
            },
            bases=('auth.user', models.Model),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(
                    unique=True, max_length=100, verbose_name='name')),
                ('page_width', models.IntegerField(verbose_name='page width', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)])),
                ('page_height', models.IntegerField(verbose_name='page height', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)])),
                ('cell_width', models.IntegerField(verbose_name='cell width', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)])),
                ('cell_height', models.IntegerField(validators=[django.core.validators.MinValueValidator(
                    1), django.core.validators.MaxValueValidator(9999)], verbose_name='cell height')),
                ('columns', models.IntegerField(verbose_name='number of columns', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)])),
                ('rows', models.IntegerField(verbose_name='number of rows', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)])),
                ('left_marge', models.IntegerField(verbose_name='left marge', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)])),
                ('top_marge', models.IntegerField(verbose_name='top marge', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)])),
                ('horizontal_space', models.IntegerField(verbose_name='horizontal space', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)])),
                ('vertical_space', models.IntegerField(verbose_name='vertical space', validators=[
                 django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)])),
            ],
            options={
                'verbose_name_plural': 'labels',
                'verbose_name': 'label',
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PrintModel',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(
                    unique=False, max_length=100, verbose_name='name')),
                ('kind', models.IntegerField(
                    choices=[(0, 'Listing'), (1, 'Label'), (2, 'Report')], verbose_name='kind')),
                ('modelname', models.CharField(
                    max_length=100, verbose_name='model')),
                ('value', models.TextField(verbose_name='value', blank=True)),
            ],
            options={
                'verbose_name_plural': 'models',
                'verbose_name': 'model',
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(initial_values),
    ]
