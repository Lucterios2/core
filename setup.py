# -*- coding: utf-8 -*-
'''
Created on fevr. 2015

@author: sd-libre
'''

from setuptools import setup
from lucterios.CORE import __version__

setup(
    name="lucterios",
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
    license="GNU General Public License v3",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.7',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
    ],
    # Packages
    packages=["lucterios", "lucterios.CORE", "lucterios.framework", "lucterios.install"],
    scripts=['lucterios/install/lucterios_admin.py', 'lucterios/install/lucterios_migration.py'],
    package_data={
       "lucterios.CORE.migrations":['*'],
       "lucterios.CORE":['build', 'images/*', 'locale/*/*/*', 'help/*'],
       "lucterios.framework.migrations":['*'],
       "lucterios.framework":['locale/*/*/*'],
       "lucterios.install":['*'],
    },
    install_requires=["Django ==1.7", "django_jux ==1.0", "lxml ==3.4", 'pycrypto ==2.6', 'reportlab ==3.1.44'],
)

