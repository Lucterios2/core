# -*- coding: utf-8 -*-
'''
Created on 11 fevr. 2015

@author: sd-libre
'''

def url_view(right):
    def wrapper(item):
        item.is_view_right = right
        module_items = item.__module__.split('.')
        if module_items[0] == 'lucterios':
            module_items = module_items[1:]
        if module_items[-1][:5] == 'views':
            module_items = module_items[:-1]
        item.extension = "_".join(module_items)
        item.action = item.__name__[0].lower() + item.__name__[1:]
        item.url_text = r'^%s/%s$' % (item.extension, item.action)
        return item
    return wrapper
