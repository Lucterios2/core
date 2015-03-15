# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models, migrations
from django.contrib.auth.models import User
from django.utils import six
from lucterios.CORE.models import Parameter

def initial_values(*args):
    # pylint: disable=unused-argument
    admin = User.objects.create_user(six.text_type('admin'), '', six.text_type('admin'))
    admin.first_name = six.text_type('administrator')
    admin.last_name = six.text_type('ADMIN')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    param = Parameter.objects.create(name='CORE-GUID', typeparam=0)  # pylint: disable=no-member
    param.title = _("CORE-GUID")
    param.args = "{'Multi':False}"
    param.value = ''
    param.save()

    param = Parameter.objects.create(name='CORE-connectmode', typeparam=4)  # pylint: disable=no-member
    param.title = _("CORE-connectmode")
    param.param_titles = (_("CORE-connectmode.0"), _("CORE-connectmode.1"), _("CORE-connectmode.2"))
    param.args = "{'Enum':3}"
    param.value = '0'
    param.save()

class Migration(migrations.Migration):

    dependencies = [
        (six.text_type("auth"), six.text_type("0001_initial")),
    ]

    operations = [
        migrations.CreateModel(
            name='parameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name', unique=True)),
                ('typeparam', models.IntegerField(choices=[(0, 'String'), (1, 'Integer'), (2, 'Real'), (3, 'Boolean'), (4, 'Select')])),
                ('args', models.CharField(max_length=200, verbose_name='arguments', default="{}")),
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
        migrations.RunPython(initial_values),
    ]
