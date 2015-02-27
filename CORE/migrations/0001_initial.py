# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.models import User
from django.utils import six

def initial_values(*_):
    admin = User.objects.create_user(six.text_type('admin'), '', six.text_type('admin'))
    admin.first_name = six.text_type('administrator')
    admin.last_name = six.text_type('ADMIN')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

class Migration(migrations.Migration):

    dependencies = [
        (six.text_type("auth"), six.text_type("0001_initial"))
    ]

    operations = [
        migrations.RunPython(initial_values),
    ]
