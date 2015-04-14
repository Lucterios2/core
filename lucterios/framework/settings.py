# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from inspect import stack, getmodule
import logging, sys, os, socket
from os.path import dirname, join
from locale import getdefaultlocale

from django.utils import six
from django.utils.module_loading import import_module

from lucterios.framework.filetools import readimage_to_base64

def get_lan_ip():
    if os.name != "nt":
        import fcntl
        import struct
        def get_interface_ip(ifname):
            scket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                if_name_short = six.binary_type(ifname[:15], 'utf-8')
            except TypeError:
                if_name_short = six.binary_type(ifname[:15])
            return socket.inet_ntoa(fcntl.ioctl(scket.fileno(), 0x8915, struct.pack('256s', if_name_short))[20:24])
    ip_address = socket.gethostbyname(socket.gethostname())
    if ip_address.startswith("127.") and os.name != "nt":
        interfaces = ["eth0", "eth1", "eth2", "wlan0", "wlan1", "wifi0", "ath0", "ath1", "ppp0"]
        for ifname in interfaces:
            try:
                ip_address = get_interface_ip(ifname)
                break
            except IOError:
                pass
    return ip_address

DEFAULT_SETTINGS = {
    'MIDDLEWARE_CLASSES': (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
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
        'lucterios.framework',
        'lucterios.CORE',
    ),
    'TEMPLATE_LOADERS': (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ),
    'TEMPLATE_CONTEXT_PROCESSOR': (
        'django.core.context_processors.i18n',
    ),
    'ROOT_URLCONF': 'lucterios.framework.urls',
    'LANGUAGE_CODE': getdefaultlocale()[0],
    'TIME_ZONE': 'UTC',
    'SESSION_COOKIE_AGE': 60 * 60,
    'USE_I18N': True,
    'USE_L10N': True,
    'USE_TZ': True,
    'TEMPLATE_DEBUG': False,
    'ALLOWED_HOSTS': ['localhost', '127.0.0.1', socket.gethostname(), get_lan_ip()],
    'WSGI_APPLICATION' : 'lucterios.framework.wsgi.application',
    'STATIC_URL':'/static/',
    'TEST_RUNNER':'juxd.JUXDTestSuiteRunner',
    'JUXD_FILENAME':'./junit_py%d.xml' % sys.version_info[0],
    'LANGUAGES' : (
        ('en', six.text_type('English')),
        ('fr', six.text_type('Français')),
    ),
}

def fill_appli_settings(appli_name, addon_modules=None):
    last_frm = stack()[1]
    last_mod = getmodule(last_frm[0])
    extra = {}
    for ext_item in dir(last_mod):
        if ext_item == ext_item.upper() and not (ext_item in ['BASE_DIR', 'DATABASES', 'SECRET_KEY']):
            extra[ext_item] = getattr(last_mod, ext_item)
    setattr(last_mod, "EXTRA", extra)
    logging.getLogger(__name__).debug("Add settings from appli '%s' to %s ", appli_name, last_mod.__name__)
    for (key_name, setting_value) in DEFAULT_SETTINGS.items():
        setattr(last_mod, key_name, setting_value)
    setattr(last_mod, "BASE_DIR", dirname(dirname(last_mod.__file__)))
    if isinstance(addon_modules, tuple):
        last_mod.INSTALLED_APPS = last_mod.INSTALLED_APPS + addon_modules
    last_mod.INSTALLED_APPS = last_mod.INSTALLED_APPS + (appli_name,)
    if not hasattr(last_mod, "DEBUG"):
        last_mod.DEBUG = False
    appli_module = import_module(appli_name)
    setattr(last_mod, 'APPLIS_MODULE', appli_module)
    local_path = [join(import_module("lucterios.CORE").__path__[0], 'locale/'), join(appli_module.__path__[0], 'locale/')]
    for addon_module in addon_modules:
        local_path.append(join(import_module(addon_module).__path__[0], 'locale/'))
    setattr(last_mod, 'LOCALE_PATHS', tuple(local_path))
    setting_module = import_module("%s.appli_settings" % appli_name)
    for item in dir(setting_module):
        if item==item.upper():
            setattr(last_mod, item, getattr(setting_module, item))
    if 'APPLIS_LOGO_NAME' in dir(setting_module):
        setattr(last_mod, 'APPLIS_LOGO', readimage_to_base64(setting_module.APPLIS_LOGO_NAME))
    else:
        setattr(last_mod, 'APPLIS_LOGO', '')
