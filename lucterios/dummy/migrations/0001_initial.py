# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from lucterios.CORE.models import PrintModel
from django.utils import six

def initial_values(*args):
    # pylint: disable=unused-argument, no-member, expression-not-assigned
    prtmdl = PrintModel.objects.create(name="listing", kind=0, modelname='Example')
    prtmdl.value = """210
297
10//Name//#name
20//value + price//#value/#price
20//date + time//#date<br/>#time"""
    prtmdl.save()
    prtmdl = PrintModel.objects.create(name="label", kind=1, modelname='Example')
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
        migrations.RunPython(initial_values),
    ]
