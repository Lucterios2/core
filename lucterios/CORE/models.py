# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

class Parameter(models.Model):

    name = models.CharField(_('name'), max_length=100, unique=True)
    typeparam = models.IntegerField(choices=((0, _('String')), (1, _('Integer')), (2, _('Real')), (3, _('Boolean')), (4, _('Select'))))
    args = models.CharField(_('arguments'), max_length=200, default="{}")
    value = models.TextField(_('value'), blank=True)

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        default_permissions = ['add', 'change']


class LucteriosSession(Session):

    @property
    def username(self):
        data = self.get_decoded()
        user_id = data.get('_auth_user_id', None)
        if user_id is None:
            return "---"
        else:
            return User.objects.get(id=user_id).username # pylint: disable=no-member

    class Meta(object):
        # pylint: disable=no-init
        proxy = True
