# -*- coding: utf-8 -*-
'''
Created on feb. 2015

@author: sd-libre
'''

from __future__ import unicode_literals
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory
from lxml import etree

def check(condition, msg):
    if not condition:
        raise AssertionError(msg)

def add_admin_user():
    from django.contrib.auth.models import User
    user = User.objects.create_user(username='admin', password='admin')
    user.first_name = 'administrator'
    user.last_name = 'ADMIN'
    user.is_staff = True
    user.is_active = True
    user.save()

def add_empty_user():
    from django.contrib.auth.models import User
    user = User.objects.create_user(username='empty', password='empty')
    user.first_name = 'empty'
    user.last_name = 'NOFULL'
    user.is_staff = False
    user.is_active = True
    user.save()

class XmlClient(Client):

    def call(self, path, data):
        response = self.post(path, data, HTTP_ACCEPT_LANGUAGE='fr')
        check(response.status_code == 200, "HTTP error:" + str(response.status_code))
        contentxml = etree.fromstring(response.content)
        check(contentxml.getchildren()[0].tag == 'REPONSE', "NOT REPONSE")
        return contentxml.getchildren()[0]

class XmlRequestFactory(RequestFactory):

    def __init__(self, xfer):
        RequestFactory.__init__(self)
        self.xfer = xfer

    def call(self, url, data):
        request = self.get(url, data)
        request.user = AnonymousUser()
        response = self.xfer.get(request)
        check(response.status_code == 200, "HTTP error:" + str(response.status_code))
        contentxml = etree.fromstring(response.content)
        check(contentxml.getchildren()[0].tag == 'REPONSE', "NOT REPONSE")
        return contentxml.getchildren()[0]
