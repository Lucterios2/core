# -*- coding: utf-8 -*-
'''
Created on march 2015

@author: sd-libre
'''

from __future__ import unicode_literals

from django.utils import six

from base64 import b64encode, b64decode
from os.path import join, exists
from os import makedirs

def get_tmp_dir():
    from django.conf import settings
    setting_path = join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0])
    tmp_path = join(setting_path, 'tmp')
    if not exists(tmp_path):
        makedirs(tmp_path)
    return tmp_path

def get_user_path(rootpath, filename):
    from django.conf import settings
    setting_path = join(settings.BASE_DIR, settings.SETTINGS_MODULE.split('.')[0])
    root_path = join(setting_path, 'usr', rootpath)
    if not exists(root_path):
        makedirs(root_path)
    return join(root_path, filename)

def readimage_to_base64(file_path, with_prefix=True):
    with open(file_path, "rb") as image_file:
        if with_prefix:
            if six.PY2:
                img_prefix = six.binary_type('data:image/*;base64,')
            else:
                img_prefix = six.binary_type('data:image/*;base64,', 'ascii')
            return img_prefix + b64encode(image_file.read())
        else:
            return b64encode(image_file.read())

def save_from_base64(base64stream):
    file_name, stream = base64stream.split(";")
    file_path = join(get_tmp_dir(), file_name)
    with open(file_path, "wb") as image_tmp:
        image_tmp.write(b64decode(stream))
    return file_path

def open_image_resize(filep, max_width, max_height):
    from PIL import Image
    image = Image.open(filep)
    width, height = image.size
    x_ratio = (max_width*1.0) / width
    y_ratio = (max_height*1.0) / height
    if (width > max_width) or (height > max_height):
        if (x_ratio * height) < max_height:
            tn_height = int(x_ratio * height)
            tn_width = int(max_width)
        else:
            tn_width = int(y_ratio * width)
            tn_height = int(max_height)
        image = image.resize((tn_width, tn_height))
    return image
