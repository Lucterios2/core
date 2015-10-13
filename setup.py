# -*- coding: utf-8 -*-
'''
setup module to pip integration of Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from setuptools import setup
from lucterios.CORE import __version__

setup(
    name="lucterios",
    version=__version__,
    author="Lucterios",
    author_email="info@lucterios.org",
    url="http://www.lucterios.org",
    description="Lucterios framework.",
    long_description="""
    Framework to create quickly smart database application.
    """,
    include_package_data=True,
    platforms=('Any',),
    license="GNU General Public License v3",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
    ],
    packages=["lucterios", "lucterios.CORE",
              "lucterios.framework", "lucterios.install"],
    scripts=['lucterios/install/lucterios_admin.py',
             'lucterios/install/lucterios_gui.py', 'lucterios/install/lucterios_migration.py'],
    package_data={
        "lucterios.CORE.migrations": ['*'],
        "lucterios.CORE": ['build', 'images/*', 'locale/*/*/*', 'help/*'],
        "lucterios.framework.migrations": ['*'],
        "lucterios.framework": ['locale/*/*/*'],
        "lucterios.install": ['lucterios.png', 'locale/*/*/*'],
    },
    install_requires=[
        "Django ==1.8.*", "lxml >=3.4", 'pycrypto >=2.6', 'reportlab >=3.1'],
)
