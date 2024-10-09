# -*- coding: utf-8 -*-
'''
setup module to pip integration of Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2017 sd-libre.fr
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
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Database :: Front-Ends',
    ],
    packages=["lucterios", "lucterios.CORE",
              "lucterios.framework", "lucterios.install"],
    scripts=['lucterios/install/lucterios_admin.py', 'lucterios/install/lucterios_gui.py', 'lucterios/install/lucterios_qt.py'],
    package_data={
        "lucterios.CORE.migrations": ['*'],
        "lucterios.CORE": ['build', 'images/*', 'locale/*/*/*', 'help/*'],
        "lucterios.framework.migrations": ['*'],
        "lucterios.framework": ['locale/*/*/*', 'fonts/*', 'mdi-icons/*'],
        "lucterios.install": ['lucterios.png', 'locale/*/*/*'],
    },
    install_requires=["pip", "importlib-metadata", "Django ~=4.2", "django-fsm ~=2.8", "lxml ~=5.1", "lxml_html_clean", "Pillow ~=10.2", "CairoSVG ~=2.7", "reportlab ~=4.1", "APScheduler ~=3.10", "Babel ~=2.14", "PyQt6 ~=6.7", "odfpy ~=1.4", "openpyxl ~=3.1", "xlrd ~=2.0", "pandas ~=2.0", "waitress"],
)
