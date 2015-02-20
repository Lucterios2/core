# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from inspect import stack, getmodule
import logging, sys
from django.utils import six
from django.utils.module_loading import import_module
from os.path import dirname

DEFAULT_SETTINGS = {
    'MIDDLEWARE_CLASSES': (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'lucterios.framework.middleware.LucteriosErrorMiddleware',
    ),
    'INSTALLED_APPS' : (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'lucterios.CORE',
    ),
    'ROOT_URLCONF': 'lucterios.framework.urls',
    'LANGUAGE_CODE': 'en-us',
    'TIME_ZONE': 'UTC',
    'USE_I18N': True,
    'USE_L10N': True,
    'USE_TZ': True,
    'TEMPLATE_DEBUG': False,
    'ALLOWED_HOSTS': [],
    'WSGI_APPLICATION' : 'lucterios.framework.wsgi.application',
    'STATIC_URL':'/static/',
    'TEST_RUNNER':'juxd.JUXDTestSuiteRunner',
    'JUXD_FILENAME':'./junit_py%d.xml' % sys.version_info[0],
}

def extract_icon(file_path):
    import base64
    if six.PY2:
        img_prefix = six.binary_type('data:image/*;base64,')
    else:
        img_prefix = six.binary_type('data:image/*;base64,', 'ascii')
    with open(file_path, "rb") as image_file:
        return img_prefix + base64.b64encode(image_file.read())

def fill_appli_settings(appli_name, addon_modules=None):
    last_frm = stack()[1]
    last_mod = getmodule(last_frm[0])
    logging.getLogger(__name__).debug("Add settings from appli '%s' to %s ", appli_name, last_mod.__name__)
    for (key_name, setting_value) in DEFAULT_SETTINGS.items():
        setattr(last_mod, key_name, setting_value)
    setattr(last_mod, "BASE_DIR", dirname(dirname(last_mod.__file__)))
    if isinstance(addon_modules, tuple):
        last_mod.INSTALLED_APPS = last_mod.INSTALLED_APPS + addon_modules
    if not hasattr(last_mod, "DEBUG"):
        last_mod.DEBUG = False

    appli_module = import_module("%s.appli_settings" % appli_name)
    setattr(last_mod, 'APPLIS_MODULE', appli_module)
    for item in dir(appli_module):
        setattr(last_mod, item, getattr(appli_module, item))
    if 'APPLIS_LOGO_NAME' in dir(appli_module):
        setattr(last_mod, 'APPLIS_LOGO', extract_icon(appli_module.APPLIS_LOGO_NAME))
    else:
        setattr(last_mod, 'APPLIS_LOGO', '')

