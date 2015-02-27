# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models

class Parameter(models.Model):

    module = models.CharField(_('module'), max_length=80)
    name = models.CharField(_('name'), max_length=80)
    typeparam = models.IntegerField(choices=((0, _('String')), (1, _('Integer')), (2, _('Real')), (3, _('Boolean')), (4, _('Select'))))
    param = models.CharField(_('name'), max_length=80, blank=True)
    value = models.TextField(_('module'), blank=True)

    class Meta(object):
        # pylint: disable=no-init
        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        default_permissions = ('add', 'change')
