# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CORE', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedCriteria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=100)),
                ('modelname', models.CharField(verbose_name='model', max_length=100)),
                ('criteria', models.TextField(verbose_name='criteria', blank=True)),
            ],
            options={
                'verbose_name': 'Saved criteria',
                'default_permissions': [],
                'verbose_name_plural': 'Saved criterias',
            },
        ),
    ]
