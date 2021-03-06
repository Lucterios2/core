# -*- coding: utf-8 -*-
'''
Django setting adaptater to Lucterios

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

from __future__ import unicode_literals
from inspect import stack, getmodule
import logging
import sys
import os
import socket
from os.path import dirname, join, isdir
from locale import getdefaultlocale
from importlib import import_module

from django.utils import six

from lucterios.framework.filetools import readimage_to_base64, read_file


def get_local_interfaces():
    """ Returns a dictionary of name:ip key value pairs. """

    import array
    import struct
    import fcntl

    # Max possible bytes for interface result.  Will truncate if more than 4096 characters to describe interfaces.
    MAX_BYTES = 4096

    # We're going to make a blank byte array to operate on.  This is our fill char.
    FILL_CHAR = b'\0'

    SIOCGIFCONF = 0x8912
    ip_dict = {}
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        names = array.array('B', MAX_BYTES * FILL_CHAR)
        names_address, _names_length = names.buffer_info()
        mutable_byte_buffer = struct.pack('iL', MAX_BYTES, names_address)
        mutated_byte_buffer = fcntl.ioctl(sock.fileno(), SIOCGIFCONF, mutable_byte_buffer)
        max_bytes_out, _names_address_out = struct.unpack('iL', mutated_byte_buffer)
        namestr = names.tostring()
        for index in range(0, max_bytes_out, 40):
            name = namestr[index: index + 16].split(FILL_CHAR, 1)[0]
            name = name.decode('utf-8')
            ip_bytes = namestr[index + 20:index + 24]
            full_addr = []
            for netaddr in ip_bytes:
                if isinstance(netaddr, int):
                    full_addr.append(str(netaddr))
                elif isinstance(netaddr, str):
                    full_addr.append(str(ord(netaddr)))
            ip_dict[name] = '.'.join(full_addr)
    except Exception:
        pass
    return ip_dict


def get_lan_ip():
    ip_address = socket.gethostbyname(socket.gethostname())
    if ip_address.startswith("127.") and os.name != "nt":
        for ip_address in get_local_interfaces().values():
            if not ip_address.startswith("127."):
                break
    return ip_address


DEFAULT_LANGUAGES = (
    ('en', six.text_type('English')),
    ('fr', six.text_type('Français')),
)


def get_locale_lang():
    lang_result = DEFAULT_LANGUAGES[0][0]
    try:
        default_locale = getdefaultlocale()[0]
        if default_locale is not None:
            for lang in DEFAULT_LANGUAGES:
                if default_locale.startswith(lang[0]):
                    lang_result = lang[0]
                    break
    except TypeError:
        pass
    return lang_result


DEFAULT_SETTINGS = {
    'MIDDLEWARE': (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'lucterios.framework.middleware.LucteriosErrorMiddleware',
        'lucterios.framework.middleware.AuditlogMiddleware',
    ),
    'INSTALLED_APPS': (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_fsm',
        'lucterios.framework',
        'lucterios.CORE',
    ),
    'PASSWORD_HASHERS': [
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    ],
    'TEMPLATES': [{'BACKEND': 'django.template.backends.django.DjangoTemplates',
                   'DIRS': [dirname(__file__)],
                   'OPTIONS': {'context_processors': (
                               'django.core.context_processors.i18n',
                               'django.contrib.auth.context_processors.auth',
                               'django.contrib.messages.context_processors.messages',
                               ),
                               'loaders': (
                               'django.template.loaders.filesystem.Loader',
                               'django.template.loaders.app_directories.Loader',
                   ), }
                   }, ],
    'ROOT_URLCONF': 'lucterios.framework.urls',
    'LANGUAGE_CODE': get_locale_lang(),
    'TIME_ZONE': 'UTC',
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': True,
    'USE_I18N': True,
    'USE_L10N': True,
    'USE_TZ': True,
    'DEBUG': True,
    'ALLOWED_HOSTS': ['localhost', '127.0.0.1', socket.gethostname(), get_lan_ip()],
    'WSGI_APPLICATION': 'lucterios.framework.wsgi.application',
    'STATIC_URL': '/static/',
    'ADMIN_MEDIA_PREFIX': '/static/admin/',
    'TEST_RUNNER': 'lucterios.framework.juxd.JUXDTestSuiteRunner',
    'JUXD_FILENAME': './junit_py%d.xml' % sys.version_info[0],
    'DEFAULT_PAGE': '/web/index.html',
    'LANGUAGES': DEFAULT_LANGUAGES,
    'LOGGING': {
        'version': 1, 'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': 'error.log',
            },
        },
        'loggers': {
            'django': {'handlers': ['file'], 'level': 'ERROR', 'propagate': True},
            'lucterios': {'handlers': ['file'], 'level': 'ERROR', 'propagate': True},
        },
    },
}

LOCALE_PATH = []


def _get_locale_pathes(appli_name, addon_modules):
    def add_locale_path(new_path):
        if new_path not in LOCALE_PATH:
            LOCALE_PATH.append(new_path)
    module_lang_list = [
        "lucterios.CORE", 'lucterios.framework', "lucterios.install", appli_name]
    if addon_modules is not None:
        module_lang_list.extend(addon_modules)
    for module_lang_item in module_lang_list:
        module_path = import_module(module_lang_item).__path__[0]
        add_locale_path(join(module_path, 'locale', ''))
        for subdir in os.listdir(module_path):
            if isdir(join(module_path, subdir)) and isdir(join(module_path, subdir, 'locale')):
                add_locale_path(join(module_path, subdir, 'locale', ''))
    return tuple(LOCALE_PATH)


def _get_extra(module_to_setup):
    extra = {}
    for ext_item in dir(module_to_setup):
        if ext_item == ext_item.upper() and not (ext_item in ['BASE_DIR', 'DATABASES', 'SECRET_KEY']):
            extra[ext_item] = getattr(module_to_setup, ext_item)
    return extra


def initialize_appli_settings(appli_name, module_to_setup):
    setup_path = dirname(module_to_setup.__file__)
    extra_setting = _get_extra(module_to_setup)
    setattr(module_to_setup, "EXTRA", extra_setting)
    setattr(module_to_setup, "SETUP", module_to_setup)
    logging.getLogger(__name__).debug("Add settings from appli '%s' to %s ", appli_name, module_to_setup.__name__)
    for key_name, setting_value in DEFAULT_SETTINGS.items():
        if key_name not in extra_setting.keys():
            setattr(module_to_setup, key_name, setting_value)
    my_database = getattr(module_to_setup, 'DATABASES', {})
    if ('default' in my_database.keys()):
        if 'ATOMIC_REQUESTS' not in my_database['default']:
            my_database['default']['ATOMIC_REQUESTS'] = True
    setattr(module_to_setup, "BASE_DIR", dirname(setup_path))
    return setup_path


def fill_appli_gui(module_to_setup, setting_module):
    setattr(module_to_setup, 'APPLIS_LOGO', readimage_to_base64(setting_module.APPLIS_LOGO_NAME) if 'APPLIS_LOGO_NAME' in dir(setting_module) else b'')
    if not hasattr(module_to_setup, 'APPLIS_STYLE'):
        setattr(module_to_setup, 'APPLIS_STYLE', read_file(setting_module.APPLIS_STYLE_NAME) if 'APPLIS_STYLE_NAME' in dir(setting_module) else b'')
    if not hasattr(module_to_setup, 'APPLIS_BACKGROUND'):
        setattr(module_to_setup, 'APPLIS_BACKGROUND', readimage_to_base64(setting_module.APPLIS_BACKGROUND_NAME) if 'APPLIS_BACKGROUND_NAME' in dir(setting_module) else b'')
    setattr(module_to_setup, 'APPLI_SUPPORT', setting_module.APPLI_SUPPORT if 'APPLI_SUPPORT' in dir(setting_module) else lambda: "")


def fill_appli_settings(appli_name, addon_modules=None, module_to_setup=None):
    if module_to_setup is None:
        last_frm = stack()[1]
        module_to_setup = getmodule(last_frm[0])
    setup_path = initialize_appli_settings(appli_name, module_to_setup)
    my_log = getattr(module_to_setup, 'LOGGING', {})
    try:
        if my_log['handlers']['file']['filename'] == 'error.log':
            my_log['handlers']['file']['filename'] = join(dirname(setup_path), 'error.log')
    except KeyError:
        pass
    try:
        my_template = getattr(module_to_setup, 'TEMPLATES', [])
        dir_list = []
        for addon_module in addon_modules:
            module = import_module(addon_module)
            dir_list.append(dirname(module.__file__))
        my_template[0]['DIRS'].extend(dir_list)
    except KeyError:
        pass
    if not hasattr(module_to_setup, "MEDIA_ROOT"):
        setattr(module_to_setup, "MEDIA_ROOT", join(setup_path, 'usr'))
    if isinstance(addon_modules, tuple):
        module_to_setup.INSTALLED_APPS = module_to_setup.INSTALLED_APPS + addon_modules
    module_to_setup.INSTALLED_APPS = module_to_setup.INSTALLED_APPS + (appli_name,)
    appli_module = import_module(appli_name)
    setattr(module_to_setup, 'APPLIS_MODULE', appli_module)
    setattr(module_to_setup, 'LOCALE_PATHS', _get_locale_pathes(appli_name, addon_modules))
    setattr(module_to_setup, 'STATIC_ROOT', join(setup_path, 'static'))
    setattr(module_to_setup, 'STATICFILES_DIRS', (setup_path, ))
    setting_module = import_module("%s.appli_settings" % appli_name)
    for item in dir(setting_module):
        if item == item.upper():
            setattr(module_to_setup, item, getattr(setting_module, item))
    fill_appli_gui(module_to_setup, setting_module)
