# -*- coding: utf-8 -*-
'''
General tools for Lucterios

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
from datetime import datetime, date, time
from calendar import monthrange
from babel.numbers import format_currency
from babel.dates import format_date, format_time, format_datetime

import threading
import logging
import locale
import sys

from django.utils.translation import ugettext_lazy as _
from django_fsm import FSMFieldMixin
from django.utils.encoding import smart_text


CLOSE_NO = 0
CLOSE_YES = 1
FORMTYPE_NOMODAL = 0
FORMTYPE_MODAL = 1
FORMTYPE_REFRESH = 2
SELECT_NONE = 1
SELECT_SINGLE = 0
SELECT_MULTI = 2

bad_permission_redirect_classaction = None


def get_icon_path(icon_path, url_text='', extension=''):
    from django.conf import settings
    res_icon_path = ""
    if (icon_path is not None) and (icon_path != ""):
        if url_text.find('/') != -1:
            extension = url_text.split('/')[0]
        if icon_path.startswith(settings.STATIC_URL):
            res_icon_path = icon_path
        elif icon_path.startswith('images/'):
            res_icon_path = "%slucterios.CORE/%s" % (
                settings.STATIC_URL, icon_path)
        elif ('images/' in icon_path):
            res_icon_path = "%s%s" % (settings.STATIC_URL, icon_path)
        elif (extension == '') or (extension == 'CORE'):
            res_icon_path = "%slucterios.CORE/images/%s" % (
                settings.STATIC_URL, icon_path)
        else:
            res_icon_path = "%s%s/images/%s" % (
                settings.STATIC_URL, extension, icon_path)
    return res_icon_path


class WrapAction(object):

    mode_connect_notfree = None

    def __init__(self, caption, icon_path, extension='', action='', url_text='', pos=0, is_view_right='', method='POST'):
        self.caption = caption
        self.icon_path = get_icon_path(icon_path, url_text, extension)
        self.modal = None
        self.is_view_right = is_view_right
        self.url_text = url_text
        if (extension == '') and (action == '') and (url_text.find('/') != -1):
            self.extension, self.action = url_text.split('/')
        else:
            self.extension = extension
            self.action = action
        self.method = method
        self.pos = pos

    def set_value(self, caption, icon_path):
        self.caption = caption
        self.icon_path = get_icon_path(icon_path, self.url_text, self.extension)

    def get_action_json(self, desc='', modal=FORMTYPE_MODAL, close=CLOSE_YES, unique=SELECT_NONE, params=None):
        json_res = {}
        json_res['text'] = str(self.caption)
        json_res['id'] = self.url_text
        if self.icon_path != "":
            json_res['icon'] = str(self.icon_path)
        if self.extension != "":
            json_res['extension'] = self.extension
        if self.action != "":
            json_res['action'] = self.action
        if desc != "":
            json_res["help"] = str(desc)
        json_res['modal'] = str(modal)
        json_res['close'] = str(close)
        json_res['unique'] = str(unique)
        json_res['method'] = str(self.method)
        if isinstance(self.modal, int):
            json_res['modal'] = str(self.modal)
        json_res['params'] = params
        return json_res

    def check_permission(self, request):
        right_result = True
        if isinstance(self.is_view_right, tuple):
            view_right_fct = self.is_view_right[0]
            right_result = view_right_fct(request)
        elif self.is_view_right is None:
            right_result = request.user.is_authenticated
        elif self.mode_connect_notfree is None or self.mode_connect_notfree():
            if (self.is_view_right != '') and not request.user.has_perm(self.is_view_right):
                right_result = False
            if (self.caption == '') and not request.user.is_authenticated:
                right_result = False
        logging.getLogger("lucterios.core.right").info(
            "check_permission for '%s' : is_view_right='%s' user='%s' => '%s'", self.url_text, self.is_view_right, request.user, right_result)
        return right_result

    def raise_bad_permission(self, request):
        if not self.check_permission(request):
            from lucterios.framework.error import LucteriosRedirectException
            if request.user.is_authenticated:
                username = request.user.username
            else:
                username = _("Anonymous user")
            raise LucteriosRedirectException(
                _("Bad permission for '%s'") % username, bad_permission_redirect_classaction)

    @classmethod
    def is_permission(cls, request, is_view_right):
        return cls(caption='', icon_path='', is_view_right=is_view_right).check_permission(request)


class ActionsManage(object):

    ACTION_IDENT_LIST = 1
    ACTION_IDENT_GRID = 2
    ACTION_IDENT_SHOW = 3
    ACTION_IDENT_EDIT = 4
    ACTION_IDENT_OTHER = 5

    _VIEW_LIST = {}

    _ACTION_LIST = {}

    _actlock = threading.RLock()

    @classmethod
    def get_actions(cls, ident, xfer, model_name=None, key=None, **args):
        cls._actlock.acquire()
        try:
            acts = []
            if model_name is None:
                model_name = xfer.model.get_long_name()
            if model_name in cls._ACTION_LIST.keys():
                for act_ident, act_xclass, act_title, act_icon, act_condition, act_options in cls._ACTION_LIST[model_name]:
                    try:
                        if (act_ident == ident) and ((act_condition is None) or act_condition(xfer, **args)):
                            acts.append((act_xclass.get_action(act_title, act_icon), dict(act_options)))
                    except Exception:
                        print('error for [%s,%s,%s,%s]' % (act_ident, act_xclass, act_title, act_icon))
                        raise
            if key is not None:
                acts.sort(key=key)
            for act in acts:
                for remove_opt in ['intop', 'model_name']:
                    if remove_opt in act[1]:
                        del act[1][remove_opt]
            return acts
        finally:
            cls._actlock.release()

    @classmethod
    def get_action_url(cls, model_name, url, xfer, **args):
        cls._actlock.acquire()
        try:
            retact = None
            if model_name in cls._ACTION_LIST.keys():
                for act in cls._ACTION_LIST[model_name]:
                    if act[1].url_text.endswith(url) and ((act[4] is None) or act[4](xfer, **args)):
                        retact = act[1].get_action(act[2], act[3])
            return retact
        finally:
            cls._actlock.release()

    @classmethod
    def add_action_generic(cls, xclass, ident, title, icon, condition, **options):
        if 'model_name' in options.keys() and (options['model_name'] is not None):
            model_name = options['model_name']
        else:
            model_name = xclass.model.get_long_name()
        cls._actlock.acquire()
        try:
            if model_name not in cls._ACTION_LIST.keys():
                cls._ACTION_LIST[model_name] = []
            cls._ACTION_LIST[model_name].append((ident, xclass, title, icon, condition, options))
            return xclass
        finally:
            cls._actlock.release()

    @classmethod
    def wrapp_affect_generic(cls, ident, title, icon, condition=None, **options):
        def wrapper(xclass):
            return cls.add_action_generic(xclass, ident, title, icon, condition, **options)
        return wrapper

    @classmethod
    def affect_list(cls, title, icon, condition=None, close=CLOSE_NO, modal=FORMTYPE_MODAL, **options):
        options['close'] = close
        options['modal'] = modal
        options['unique'] = SELECT_NONE
        return cls.wrapp_affect_generic(cls.ACTION_IDENT_LIST, title, icon, condition, **options)

    @classmethod
    def affect_grid(cls, title, icon, condition=None, close=CLOSE_NO, modal=FORMTYPE_MODAL, unique=SELECT_NONE, **options):
        options['close'] = close
        options['modal'] = modal
        options['unique'] = unique
        return cls.wrapp_affect_generic(cls.ACTION_IDENT_GRID, title, icon, condition, **options)

    @classmethod
    def affect_show(cls, title, icon, condition=None, close=CLOSE_NO, modal=FORMTYPE_MODAL, **options):
        options['close'] = close
        options['modal'] = modal
        options['unique'] = SELECT_SINGLE
        return cls.wrapp_affect_generic(cls.ACTION_IDENT_SHOW, title, icon, condition, **options)

    @classmethod
    def affect_edit(cls, title, icon, condition=None, close=CLOSE_NO, modal=FORMTYPE_MODAL, **options):
        options['close'] = close
        options['modal'] = modal
        options['unique'] = SELECT_SINGLE
        return cls.wrapp_affect_generic(cls.ACTION_IDENT_EDIT, title, icon, condition, **options)

    @classmethod
    def affect_other(cls, title, icon, condition=None, close=CLOSE_NO, modal=FORMTYPE_MODAL, unique=SELECT_NONE, **options):
        options['close'] = close
        options['modal'] = modal
        options['unique'] = unique
        return cls.wrapp_affect_generic(cls.ACTION_IDENT_OTHER, title, icon, condition, **options)

    @classmethod
    def affect_transition(cls, state, close=CLOSE_NO, multi_list=None, **options):
        def wrapper(xclass):
            xclass.trans_list = {}
            for field in xclass.model._meta.get_fields():
                if isinstance(field, FSMFieldMixin) and (field.name == state):
                    transitions = list(field.get_all_transitions(xclass.model))
                    transitions.sort(key=lambda item: item.target)
                    for transition in transitions:
                        source_label = [smart_text(name[1]) for name in field.choices if name[0] == transition.source][0]
                        target_label = [smart_text(name[1]) for name in field.choices if name[0] == transition.target][0]
                        title = getattr(xclass.model, 'transitionname__' + transition.name, transition.name)
                        xclass.trans_list[transition.name] = (transition.source, str(source_label),
                                                              transition.target, str(target_label),
                                                              transition.name, str(title))
                        new_dict = dict(options)
                        if 'close' in new_dict:
                            del new_dict['close']
                        if 'params' not in new_dict:
                            new_dict['params'] = {}
                        new_dict['params']['TRANSITION'] = transition.name

                        cmd = "lambda xfer:getattr(xfer.item,'%s')._django_fsm.conditions_met(xfer.item, getattr(xfer.item,'%s'))" % (transition.name, state)
                        cond_fct = eval(cmd)
                        cls.add_action_generic(xclass, cls.ACTION_IDENT_SHOW, title,
                                               "images/transition.png", cond_fct, intop=True, close=close, **new_dict)

                        cmd = "lambda xfer, gridname='': xfer.getparam('%s_filter', -1) == %d" % (state, transition.source)
                        cond_fct = eval(cmd)
                        if isinstance(multi_list, tuple) and (transition.name in multi_list):
                            unique_opt = SELECT_MULTI
                        else:
                            unique_opt = SELECT_SINGLE
                        cls.add_action_generic(xclass, cls.ACTION_IDENT_GRID, title, "images/transition.png",
                                               cond_fct, intop=False, close=CLOSE_NO, unique=unique_opt, **new_dict)
            return xclass
        return wrapper


def menu_key_to_comp(menu_item):
    try:
        return menu_item[0].pos
    except AttributeError:
        return 0


class MenuManage(object):

    _MENU_LIST = {}

    _menulock = threading.RLock()

    @classmethod
    def add_sub(cls, ref, parentref, icon, caption, desc, pos=0):
        from django.conf import settings
        cls._menulock.acquire()
        try:
            if icon.startswith('images/'):
                icon_path = "%slucterios.CORE/%s" % (settings.STATIC_URL, icon)
            elif 'images/' in icon:
                icon_path = "%s%s" % (settings.STATIC_URL, icon)
            else:
                icon_path = icon
            if parentref not in cls._MENU_LIST.keys():
                cls._MENU_LIST[parentref] = []
            add_new_menu = True
            for old_menu in cls._MENU_LIST[parentref]:
                if old_menu[0].url_text == ref:
                    add_new_menu = False
            if add_new_menu:
                logging.getLogger("lucterios.core.menu").debug(
                    "new sub-menu: caption=%s ref=%s", caption, ref)
                cls._MENU_LIST[parentref].append(
                    (WrapAction(caption, icon_path, url_text=ref, pos=pos), desc))
        finally:
            cls._menulock.release()

    @classmethod
    def describ(cls, right, modal=FORMTYPE_MODAL, menu_parent=None, menu_desc=None):
        def wrapper(item):
            cls._menulock.acquire()
            try:
                item.initclass(right)
                if menu_parent is not None:
                    if menu_parent not in cls._MENU_LIST.keys():
                        cls._MENU_LIST[menu_parent] = []
                    logging.getLogger("lucterios.core.menu").debug(
                        "new menu: caption=%s ref=%s", item.caption, item.url_text)
                    act = item.get_action(item.caption, item.icon_path())
                    act.modal = modal
                    cls._MENU_LIST[menu_parent].append((act, menu_desc))
                return item
            finally:
                cls._menulock.release()
        return wrapper

    @classmethod
    def filljson(cls, request, parentref):
        resjson = []
        cls._menulock.acquire()
        try:
            if parentref in cls._MENU_LIST.keys():
                sub_menus = cls._MENU_LIST[parentref]
                sub_menus.sort(key=menu_key_to_comp)
                for sub_menu_item in sub_menus:
                    if sub_menu_item[0].check_permission(request):
                        new_act = sub_menu_item[0].get_action_json(desc=sub_menu_item[1])
                        sub_menu = cls.filljson(request, sub_menu_item[0].url_text)
                        if len(sub_menu) > 0:
                            new_act['menus'] = sub_menu
                        if (len(sub_menu) > 0) or ('extension' in new_act.keys()):
                            resjson.append(new_act)
        finally:
            cls._menulock.release()
        return resjson

    @classmethod
    def fill(cls, request, parentref, parentxml):
        cls._menulock.acquire()
        try:
            if parentref in cls._MENU_LIST.keys():
                sub_menus = cls._MENU_LIST[parentref]
                sub_menus.sort(key=menu_key_to_comp)
                for sub_menu_item in sub_menus:
                    if sub_menu_item[0].check_permission(request):
                        new_xml = sub_menu_item[0].get_action_xml(desc=sub_menu_item[1], tag="MENU")
                        if new_xml is not None:
                            parentxml.append(new_xml)
                            cls.fill(request, sub_menu_item[0].url_text, new_xml)
        finally:
            cls._menulock.release()


def get_actions_json(actions):
    actionsjson = []
    for action, modal, close, unique, params in actions:
        actionsjson.append(action.get_action_json(modal=modal, close=close, unique=unique, params=params))
    return actionsjson


def ifplural(count, test_singular, test_plural):
    if count == 1:
        return test_singular
    else:
        return test_plural


def get_corrected_setquery(setquery):
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    if setquery.model == Permission:
        ctypes = ContentType.objects.all()
        for ctype in ctypes:
            if ctype.model in ('contenttype', 'logentry', 'permission'):
                setquery = setquery.exclude(
                    content_type=ctype, codename__startswith='add_')
                setquery = setquery.exclude(
                    content_type=ctype, codename__startswith='change_')
                setquery = setquery.exclude(
                    content_type=ctype, codename__startswith='delete_')
            if ctype.model in ('session',):
                setquery = setquery.exclude(
                    content_type=ctype, codename__startswith='add_')
    return setquery


def get_dico_from_setquery(setquery):
    def get_app_title(app_label):
        from django.apps import apps
        app_config = apps.get_app_config(app_label)
        if not hasattr(app_config.module, "__title__"):
            app_config = apps.get_app_config("CORE")
        return app_config.module.__title__()
    from django.contrib.auth.models import Permission
    res_dico = []
    if setquery.model == Permission:
        for record in setquery:
            try:
                rigths = str(record.codename).split("_")
                if rigths[0] not in ['add', 'change', 'view', 'delete']:
                    res_dico.append((str(record.id), str(_(record.name))))
                else:
                    if rigths[0] == 'add':
                        rigth_name = _('add')
                    elif (rigths[0] == 'change'):
                        rigth_name = _('view')
                    elif rigths[0] == 'delete':
                        rigth_name = _('delete')
                    elif rigths[0] == 'view':
                        continue
                    res_dico.append((str(record.id),
                                     "[%s] %s : %s" % (get_app_title(record.content_type.app_label),
                                                       record.content_type.name,
                                                       rigth_name)))
            except LookupError:
                pass
        res_dico.sort(key=lambda item: item[1])
    else:
        for record in setquery:
            res_dico.append((str(record.id), str(record)))
    return res_dico


def get_binay(text):
    return bytes(text, 'ascii')


def toHtml(inittext, totext=True, withclean=True):
    from lxml import etree
    from lxml.html.clean import Cleaner
    text = str(inittext).strip()
    pos_in = text.find('&')
    while pos_in != -1:
        pos_out = text.find(';', pos_in, pos_in + 8)
        if pos_out == -1:
            text = text[:pos_in] + '&amp;' + text[pos_in + 1:]
        pos_in = text.find('&', pos_in + 1)
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('{[newline]}', '<br/>')
    text = text.replace('{[bold]}', '<b>')
    text = text.replace('{[/bold]}', '</b>')
    text = text.replace('{[italic]}', '<i>')
    text = text.replace('{[/italic]}', '</i>')
    text = text.replace('{[underline]}', '<u>')
    text = text.replace('{[/underline]}', '</u>')
    text = text.replace('{[', '<')
    text = text.replace(']}', '>')
    if withclean and ('<' in text):
        cleaner = Cleaner(scripts=True, embedded=True, meta=True, page_structure=True, comments=True, forms=True,
                          links=True, inline_style=True, style=True, remove_unknown_tags=True,
                          remove_tags=["area", "base", "col", "img", "input", "param", "source", "track", "wbr"])
        text = cleaner.clean_html(text)
        for sep_tag in ('p', 'span'):
            if text.startswith('<%s>' % sep_tag) and text.endswith('</%s>' % sep_tag):
                text = text[len(sep_tag) + 2:-len(sep_tag) - 3]
    for auto_tag in ('br', 'hr'):
        text = text.replace('<%s>' % auto_tag, '<%s/>' % auto_tag)
    if totext:
        return text
    else:
        html_node = etree.HTML('<div>%s</div>' % text)
        return html_node.find('body/div')


def clean_xml(xmltext):
    xmltext.text = ''
    for subitem in xmltext:
        xmltext.remove(subitem)
    xmltext.tail = ''


def change_with_format(xmltext):
    from json import loads
    currentvalue = xmltext.get('jsonvalue')
    if currentvalue is not None:
        clean_xml(xmltext)
        formatstr = xmltext.get('formatstr')
        formatnum = xmltext.get('formatnum')
        current_html = toHtml(format_to_string(loads(currentvalue), loads(formatnum) if formatnum is not None else None, formatstr), totext=False)
        for sub_html in current_html:
            xmltext.append(sub_html)
        xmltext.text = current_html.text
        xmltext.tail = current_html.tail
        return True
    else:
        return False


def convert_date(current_date, defaultdate=None):
    if isinstance(current_date, date):
        return current_date
    try:
        return datetime.strptime(current_date, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return defaultdate


def same_day_months_after(start_date, months=1):
    month_val = start_date.month - 1 + months
    if month_val < 0:
        target_year = start_date.year + int(month_val / 12) - 1
    else:
        target_year = start_date.year + int(month_val / 12)
    target_month = month_val % 12 + 1
    num_days_target_month = monthrange(target_year, target_month)[1]
    return start_date.replace(year=target_year, month=target_month, day=min(start_date.day, num_days_target_month))


def adapt_value(value):
    from decimal import Decimal
    from lucterios.framework.models import LucteriosModel
    if hasattr(value, 'all'):
        values = []
        for val_item in value.all():
            values.append(str(val_item))
        return values
    elif isinstance(value, LucteriosModel):
        return str(value.get_final_child())
    elif isinstance(value, Decimal):
        return float(value)
    else:
        return value


def get_date_formating(date_value):
    if isinstance(date_value, datetime):
        value = format_datetime(date_value, format='full', locale=locale.getlocale()[0])
        return value[:value.index(':') + 3]
    if isinstance(date_value, date):
        return format_date(date_value, format='long', locale=locale.getlocale()[0])
    if isinstance(date_value, time):
        return format_time(date_value, format='HH:mm', locale=locale.getlocale()[0])
    else:
        return date_value


def get_bool_textual(value):
    if isinstance(value, bool):
        if value:
            return _("Yes")
        else:
            return _("No")
    else:
        return value


def set_locale_lang(lang):
    from django.utils import translation
    try:
        if lang[:2].lower() == 'fr':
            translation.activate('fr')
            try:
                locale.setlocale(locale.LC_ALL, 'french')
            except Exception:
                locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
            return
        if lang[:2].lower() == 'en':
            translation.activate('en')
            try:
                locale.setlocale(locale.LC_ALL, 'english')
            except Exception:
                locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
            return
    except Exception:
        pass
    translation.activate('en')
    locale.setlocale(locale.LC_ALL, 'C.UTF-8')


def _convert_value_B(value, format_num):
    return get_bool_textual(bool(value))


def _convert_value_D(value, format_num):
    if isinstance(value, str):
        value = get_date_formating(datetime.strptime(value.split(' ')[0], "%Y-%m-%d").date())
    else:
        value = get_date_formating(value)
    return value


def _convert_value_T(value, format_num):
    if isinstance(value, str):
        if '.' in value:
            current_time = datetime.strptime(value, "%H:%M:%S.%f").time()
        else:
            current_time = datetime.strptime(value, "%H:%M:%S").time()
        value = get_date_formating(current_time)
    else:
        value = get_date_formating(value)
    return value


def _convert_value_H(value, format_num):
    if isinstance(value, str):
        value = get_date_formating(datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f"))
    else:
        value = get_date_formating(value)
    return value


def _convert_value_N(value, format_num):
    return locale.format("%.*f", (int(format_num[1]), float(value)), True)


def add_currency(value, format_num):
    from django.utils import translation
    tmp_val = format_currency(0, format_num[2:], locale=translation.get_language())
    tmp_val = tmp_val.replace(',', '').replace('.', '')
    for _ in range(6):
        tmp_val = tmp_val.replace('00', '0')
    value = tmp_val.replace('0', value)
    return value


def _convert_value_C(value, format_num):
    value = _convert_value_N(value, format_num)
    try:
        value = add_currency(value, format_num)
    except Exception:
        pass
    return value


def format_value(value, format_num):
    sub_format = None
    if isinstance(value, dict):
        if 'format' in value.keys():
            sub_format = value['format']
        if 'value' in value.keys():
            value = value['value']
        else:
            value = None
    if value is None:
        value = "---"
        format_num = ''
    if isinstance(format_num, dict):
        new_format_num = {}
        for key, val in format_num.items():
            new_format_num[str(key)] = val
        if str(value) in new_format_num.keys():
            value = new_format_num[str(value)]
        format_num = ''
    try:
        fct = getattr(sys.modules[__name__], "_convert_value_%s" % format_num[0:1], None)
        if fct is not None:
            value = fct(value, format_num)
    except Exception:
        pass
    if sub_format is not None:
        value = sub_format.replace('{0}', str(value))
    return value


def _convert_list_of_format(value, format_str):
    format_str = format_str.split(';')
    try:
        if (abs(float(value)) < 1e-5) and (len(format_str) > 2):
            format_str = format_str[2]
            value = float(value)
        elif (float(value) < 1e-5) and (len(format_str) > 1):
            format_str = format_str[1]
            value = abs(float(value))
        else:
            format_str = format_str[0]
    except Exception:
        format_str = format_str[0]
    return value, format_str


def format_to_string(value, format_num, format_str):
    if format_num is None:
        format_num = ''
    if format_str is None:
        format_str = '{0}'
    format_str = format_str.replace('%s', '{0}')
    if ';' in format_str:
        value, format_str = _convert_list_of_format(value, format_str)
    if '{0}' not in format_str:
        return format_str
    if isinstance(value, list) or isinstance(value, tuple):
        value = list(value)
        for val_idx in range(len(value)):
            value[val_idx] = format_value(value[val_idx], format_num)
    else:
        value = [format_value(value, format_num)]

    if '{1}' not in format_str:
        value = ['{[br/]}'.join([str(item) for item in value])]

    res_txt = format_str
    for val_idx in range(len(value)):
        res_txt = res_txt.replace('{%d}' % val_idx, value[val_idx])
    return res_txt


def get_format_from_field(dep_field):
    from django.db.models.fields import BooleanField, DateTimeField, TimeField, DateField, IntegerField
    if dep_field is None:
        return None
    elif hasattr(dep_field, 'format_string'):
        return dep_field.format_string
    elif hasattr(dep_field, 'choices') and (dep_field.choices is not None) and (len(dep_field.choices) > 0):
        choices_dict = {choices_key: str(choices_value) for choices_key, choices_value in dep_field.choices}
        return choices_dict
    elif getattr(dep_field, 'unique_for_year', False) or getattr(dep_field, 'unique_for_month', False) or getattr(dep_field, 'unique_for_date', False):
        return None
    elif hasattr(dep_field, 'decimal_places'):
        return "N%d" % dep_field.decimal_places
    elif isinstance(dep_field, IntegerField):
        return "N0"
    elif isinstance(dep_field, DateTimeField):
        return "H"
    elif isinstance(dep_field, DateField):
        return "D"
    elif isinstance(dep_field, TimeField):
        return "T"
    elif isinstance(dep_field, BooleanField):
        return "B"
    else:
        return None


def extract_format(format_string):
    _formatstr = None
    _formatnum = None
    if isinstance(format_string, str) or isinstance(format_string, dict):
        if isinstance(format_string, str) and (';' in format_string):
            format_string = format_string.split(';')
            _formatnum = format_string[0]
            _formatstr = ";".join(format_string[1:])
        else:
            _formatnum = format_string
    return _formatnum, _formatstr


def get_format_value(dep_field, value):
    formatnum, formatstr = extract_format(get_format_from_field(dep_field))
    value = format_to_string(value, formatnum, formatstr)
    return value
