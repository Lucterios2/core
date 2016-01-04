# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CORE', '0002_savedcriteria'),
    ]

    operations = [
        migrations.AddField(
            model_name='printmodel',
            name='mode',
            field=models.IntegerField(verbose_name='mode', default=0, choices=[(0, 'Simple'), (1, 'Advanced')]),
        ),
    ]
