# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LucteriosSession',
            fields=[
            ],
            options={
                'default_permissions': [],
                'proxy': True,
                'verbose_name': 'session',
                'verbose_name_plural': 'sessions'
            },
            bases=('sessions.session',),
        ),
    ]
