# -*- coding: utf-8 -*-
'''
Set of tools to manage images in base64

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

from base64 import b64encode, b64decode
from os.path import join, exists, dirname, isfile
from os import makedirs, environ
from Crypto.Hash.MD5 import MD5Hash
from lucterios.framework.tools import get_binay
from _io import BytesIO

BASE64_PREFIX = 'data:image/*;base64,'

def get_tmp_dir():
    from django.conf import settings
    if not environ.get("DJANGO_SETTINGS_MODULE"):
        tmp_path = '/tmp'
    else:
        setting_path = join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0])
        tmp_path = join(setting_path, 'tmp')
    if not exists(tmp_path):
        makedirs(tmp_path)
    return tmp_path

def get_user_dir():
    from django.conf import settings
    setting_path = join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0])
    return join(setting_path, 'usr')

def get_user_path(rootpath, filename):
    root_path = join(get_user_dir(), rootpath)
    if not exists(root_path):
        makedirs(root_path)
    return join(root_path, filename)

def readimage_to_base64(file_path, with_prefix=True):
    with open(file_path, "rb") as image_file:
        if with_prefix:
            return get_binay(BASE64_PREFIX) + b64encode(image_file.read())
        else:
            return b64encode(image_file.read())

def save_from_base64(base64stream):
    if base64stream[:len(BASE64_PREFIX)] == BASE64_PREFIX:
        stream = base64stream[len(BASE64_PREFIX):]
        md_hash = MD5Hash.new(stream)
        file_name = md_hash.hexdigest() + ".jpg"
    else:
        file_name, stream = base64stream.split(";")
    file_path = join(get_tmp_dir(), file_name)
    with open(file_path, "wb") as image_tmp:
        image_tmp.write(b64decode(stream))
    return file_path

def open_from_base64(base64stream):
    if base64stream[:len(BASE64_PREFIX)] == BASE64_PREFIX:
        stream = base64stream[len(BASE64_PREFIX):]
    else:
        _, stream = base64stream.split(";")
    return BytesIO(b64decode(stream))

def open_image_resize(filep, max_width, max_height):
    from PIL import Image
    image = Image.open(filep)
    width, height = image.size
    x_ratio = (max_width * 1.0) / width
    y_ratio = (max_height * 1.0) / height
    if (width > max_width) or (height > max_height):
        if (x_ratio * height) < max_height:
            tn_height = int(x_ratio * height)
            tn_width = int(max_width)
        else:
            tn_width = int(y_ratio * width)
            tn_height = int(max_height)
        image = image.resize((tn_width, tn_height))
    return image

def get_image_absolutepath(icon_path):
    if isfile(icon_path):
        return icon_path
    root_dir = icon_path.split('/')[0]
    if root_dir == 'images':
        root_dir = 'CORE'
        sub_path = icon_path.split('/')
    else:
        sub_path = icon_path.split('/')[1:]
    from django.utils.module_loading import import_module
    try:

        module = import_module(root_dir)
        return join(dirname(module.__file__), *sub_path)
    except ImportError:
        return icon_path

def get_image_size(image_path):
    from PIL import Image
    filep = None
    try:
        if image_path[:len(BASE64_PREFIX)] == BASE64_PREFIX:
            filep = open_from_base64(image_path)
        else:
            filep = open(get_image_absolutepath(image_path), "rb")
        image = Image.open(filep)
        width, height = image.size
    finally:
        if filep is not None:
            filep.close()
    return width, height
