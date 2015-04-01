# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from django.db import models
from lucterios.framework.models import LucteriosModel
from django.core.validators import MinValueValidator, MaxValueValidator

class Example(LucteriosModel):
    name = models.CharField(max_length=75, unique=True)
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(-5000.0), MaxValueValidator(5000.0)])
    date = models.DateField()
    time = models.TimeField()
    valid = models.BooleanField(default=False)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    example__showfields = ['name', ('value', 'price'), ('date', 'time'), 'valid', 'comment']
    example__editfields = ['name', ('value', 'price'), ('date', 'time'), 'valid', 'comment']
    example__searchfields = ['name', 'value', 'price', 'date', 'time', 'valid', 'comment']
    default_fields = ["name", 'value', 'price']
