# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import User

def initial_values(*_):
    admin = User.objects.create_user('admin', '', 'admin')
    admin.first_name = 'administrator'
    admin.last_name = 'ADMIN'
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0001_initial")
    ]

    operations = [
        migrations.RunPython(initial_values),
    ]
