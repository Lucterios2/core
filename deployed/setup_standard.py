# -*- coding: utf-8 -*-
'''
Created on fevr. 2015

@author: sd-libre
'''

from django.utils.module_loading import import_module
from distutils.core import setup

VERSION = import_module("lucterios.standard").__version__

setup(
    name="Lucterios_standard",
    version=VERSION,
    author="Lucterios",
    author_email="support@lucterios.org",
    url="http://www.lucterios.org",
    description="Standard application for Lucterios.",
    long_description="""
    Standard application for Lucterios.
    """,
    platforms=('Any',),
    license="GNU General Public License v2",
    # Packages
    packages=["lucterios.standard"],
    requires=["lucterios (>=2.0)"],
)

