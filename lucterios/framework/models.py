# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from django.db import models
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

class LucteriosModel(models.Model):

    @classmethod
    def _get_list_fields_names(cls, current_desc, readonly):
        res = []
        for fieldname in current_desc:
            if fieldname is None:
                for subclass in cls.__bases__:
                    if issubclass(subclass, LucteriosModel):
                        res.extend(subclass.get_fields_names(readonly))
            else:
                res.append(fieldname)
        return res

    @classmethod
    def get_fields_names(cls, readonly):
        res = None
        if readonly:
            dataname = cls.__name__.lower() + '__showfields'
        else:
            dataname = cls.__name__.lower() + '__editfields'
        if hasattr(cls, dataname):
            current_desc = getattr(cls, dataname)
            if isinstance(current_desc, list):
                res = cls._get_list_fields_names(current_desc, readonly)
            elif isinstance(current_desc, dict):
                res = {}
                for (key, value) in current_desc.items():
                    res[key] = cls._get_list_fields_names(value, readonly)

        return res

    class Meta(object):
        # pylint: disable=no-init
        abstract = True

class LucteriosSession(Session):

    @property
    def username(self):
        data = self.get_decoded()
        user_id = data.get('_auth_user_id', None)
        if user_id is None:
            return "---"
        else:
            return User.objects.get(id=user_id).username  # pylint: disable=no-member

    class Meta(object):
        # pylint: disable=no-init
        proxy = True
        default_permissions = []
