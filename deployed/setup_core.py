# -*- coding: utf-8 -*-
'''
Created on fevr. 2015

@author: sd-libre
'''

from django.utils.module_loading import import_module
from distutils.core import setup

VERSION = import_module("lucterios.CORE").__version__

setup(
    name="Lucterios",
    version=VERSION,
    author="Lucterios",
    author_email="support@lucterios.org",
    url="http://www.lucterios.org",
    description="Lucterios framework.",
    long_description="""
    Framework to create quickly smart database application.
    """,
    platforms=('Any',),
    license="GNU General Public License v2",
    # Packages
    packages=["lucterios.CORE", "lucterios.framework", "lucterios.install"],
    requires=["Django (>=1.7)", "django_jux (>=1.0)", "lxml (>=3.2)"],
)

