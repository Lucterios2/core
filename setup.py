# -*- coding: utf-8 -*-
'''
Created on fevr. 2015

@author: sd-libre
'''

from setuptools import setup
from lucterios.CORE import __version__

setup(
    name="Lucterios",
    version=__version__,
    author="Lucterios",
    author_email="support@lucterios.org",
    url="http://www.lucterios.org",
    description="Lucterios framework.",
    long_description="""
    Framework to create quickly smart database application.
    """,
    include_package_data=True,
    platforms=('Any',),
    license="GNU General Public License v2",
    # Packages
    packages=["lucterios", "lucterios.CORE", "lucterios.framework", "lucterios.install"],
    scripts=['lucterios/install/lucterios-admin.py'],
    package_data={
       "lucterios.CORE.migrations":['*'],
       "lucterios.CORE":['build', 'images/*', 'locale/*/*/*', 'help/*'],
       "lucterios.framework.migrations":['*'],
       "lucterios.framework":['locale/*/*/*'],
       "lucterios.install":['*'],
    },
    install_requires=["Django >=1.7", "django_jux >=1.0", "lxml >=3.2"],
)

