# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

from lucterios.framework.decorators import url_view

from django.http import HttpResponse

def info_user(title, request, text=''):
    if not request.user.is_authenticated():
        user_text = "No user connected!"
    else:
        user_text = "User %s is connected" % request.user.username
    return "<h1>%s</h1>\n%s<br/>\n%s" % (title, user_text, text)

@url_view('')
def menu(request):
    """action menu"""
    return HttpResponse(info_user('menu', request))
