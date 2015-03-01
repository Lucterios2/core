# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.auth.models import User
from django.utils import six
from lucterios.CORE.models import Parameter

def initial_values(*_):
    admin = User.objects.create_user(six.text_type('admin'), '', six.text_type('admin'))
    admin.first_name = six.text_type('administrator')
    admin.last_name = six.text_type('ADMIN')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    param = Parameter.objects.create(module='CORE', name='GUI', typeparam=0) # pylint: disable=no-member
    param.value = ''
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
                ('module', models.CharField(max_length=80, verbose_name='module')),
                ('name', models.CharField(max_length=80, verbose_name='name')),
                ('typeparam', models.IntegerField(choices=[(0, 'String'), (1, 'Integer'), (2, 'Real'), (3, 'Boolean'), (4, 'Select')])),
                ('param', models.CharField(max_length=80, verbose_name='name', blank=True)),
                ('value', models.TextField(verbose_name='module', blank=True)),
            ],
            options={
                'verbose_name': 'parameter',
                'default_permissions': ['add', 'change'],
                'verbose_name_plural': 'parameters',
            },
            bases=(models.Model,),
        ),
        migrations.RunPython(initial_values),
    ]
