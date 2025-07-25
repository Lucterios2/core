# -*- coding: utf-8 -*-
'''
Views for archive/restore in Lucterios

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2025 sd-libre.fr
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
import os.path
from base64 import b64encode

from django.utils.translation import gettext_lazy as _
from django.conf import settings

from lucterios.framework.xfergraphic import XferContainerCustom,\
    XferContainerAcknowledge
from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, WrapAction,\
    CLOSE_YES, ActionsManage, SELECT_MULTI, CLOSE_NO, SELECT_NONE, SELECT_SINGLE
from lucterios.framework.xferadvance import XferAddEditor, TITLE_CLOSE, TITLE_OK,\
    TITLE_CANCEL, TITLE_DELETE, XferDelete, XferListEditor
from lucterios.framework.xfercomponents import XferCompImage, XferCompLabelForm,\
    XferCompUpLoad, XferCompLinkLabel, XferCompEdit
from lucterios.framework.filetools import md5sum
from lucterios.CORE.models import VirtualArchive


def manage_archives(request):
    return not request.user.is_anonymous and request.user.is_superuser and os.path.isdir(settings.BACKUP_DIRECTORY)


def manage_archive_readonly(request):
    return not settings.BACKUP_READONLY and manage_archives(request)


@MenuManage.describ(manage_archives, FORMTYPE_NOMODAL, 'core.admin', _("To view and to modify archives."))
class VirtualArchiveList(XferListEditor):
    caption = _("Archive")
    short_icon = 'mdi:mdi-archive-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        last_file_log = VirtualArchive.get_last_file_log()
        if os.path.isfile(last_file_log):
            down_log = XferCompLinkLabel('backuplog')
            down_log.set_value(_('last backup log'))
            down_log.set_location(1, self.get_max_row() + 1)
            sign_value = md5sum(last_file_log)
            down_log.set_link("%s/CORE/download?filename=%s&sign=%s&name=%s" % (
                settings.FORCE_SCRIPT_NAME if settings.USE_X_FORWARDED_HOST else '',
                b64encode(last_file_log.encode()).decode(),
                sign_value,
                os.path.basename(last_file_log))
            )
            self.add_component(down_log)


@ActionsManage.affect_other(_('Archive'), short_icon='mdi:mdi-pencil-plus-outline')
@MenuManage.describ(manage_archive_readonly)
class VirtualArchiveConfirmAdding(XferContainerAcknowledge):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption = _("Add archive")

    def fillresponse(self):
        self.message(_('Archive creation added in action list.{[br/]}It will be realised in few minutes.'))


@ActionsManage.affect_grid(_('Archive'), short_icon='mdi:mdi-pencil-plus-outline')
@MenuManage.describ(manage_archive_readonly)
class VirtualArchiveAddModify(XferAddEditor):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption_add = _("Create archive")
    redirect_to_show = "ConfirmAdding"


@ActionsManage.affect_grid(TITLE_DELETE, short_icon='mdi:mdi-delete-outline', unique=SELECT_MULTI)
@MenuManage.describ(manage_archive_readonly)
class VirtualArchiveDel(XferDelete):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption = _("Delete archive")

    def _search_model(self):
        self.model.disabled_abstract()
        XferDelete._search_model(self)


@MenuManage.describ(manage_archive_readonly)
class VirtualArchiveImportAct(XferContainerAcknowledge):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption = _("Import archive")

    def fillresponse(self):
        if 'filename' in self.request.FILES.keys():
            self.item = VirtualArchive(name='')
            self.item.upload(self.request.FILES['filename'])


@ActionsManage.affect_grid(_('Import'), short_icon='mdi:mdi-upload', close=CLOSE_NO, unique=SELECT_NONE)
@MenuManage.describ(manage_archive_readonly)
class VirtualArchiveImport(XferContainerCustom):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption = _("Import archive")

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0, 1, 6)
        self.add_component(img)

        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(_('Import archive in this instance'))
        lbl.set_location(1, 0)
        self.add_component(lbl)

        file_name = XferCompUpLoad('filename')
        file_name.http_file = True
        file_name.compress = False
        file_name.maxsize = 2 * 1024 * 1024 * 1024  # 2Go
        file_name.set_value('')
        file_name.add_filter(self.model.EXTENSION)
        file_name.set_location(1, 2)
        self.add_component(file_name)

        self.add_action(VirtualArchiveImportAct.get_action(TITLE_OK, short_icon='mdi:mdi-check'), close=CLOSE_YES)
        self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))


@ActionsManage.affect_grid(_('Export'), short_icon='mdi:mdi-download', close=CLOSE_NO, unique=SELECT_SINGLE)
@MenuManage.describ(manage_archives)
class VirtualArchiveExport(XferContainerCustom):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption = _("Export archive")

    def fillresponse(self):
        img = XferCompImage('img')
        img.set_value(self.short_icon, '#')
        img.set_location(0, 0, 1, 6)
        self.add_component(img)

        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(_('Export archive in this instance'))
        lbl.set_location(1, 0)
        self.add_component(lbl)

        down = XferCompLinkLabel('filename')
        short_filename = str(self.item.name + self.model.EXTENSION)
        down.set_value(short_filename)
        down.set_location(1, 2)
        down.description = _('link to download')
        sign_value = md5sum(self.item.id)
        down.set_link("%s/CORE/download?filename=%s&sign=%s&name=%s" % (
            settings.FORCE_SCRIPT_NAME if settings.USE_X_FORWARDED_HOST else '',
            b64encode(self.item.id.encode()).decode(),
            sign_value,
            short_filename)
        )
        self.add_component(down)
        self.add_action(WrapAction(TITLE_CLOSE, short_icon='mdi:mdi-close'))


@ActionsManage.affect_grid(_('Restore'), short_icon='mdi:mdi-check', close=CLOSE_NO, unique=SELECT_SINGLE)
@MenuManage.describ(manage_archives)
class VirtualArchiveRestore(XferContainerAcknowledge):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption = _("Restore archive")

    def fillresponse(self):
        if self.confirme(_("Do you want to restore the archive '%s'?{[br/]}{[br/]}{[i]}{[u]}Warning:{[/u]} all your current data will be delete.{[/i]}") % self.item.name):
            self.item.to_load()
            self.message(_('Archive restoration added in action list.{[br/]}It will be realised in few minutes.'))


@ActionsManage.affect_grid(_('Rename'), short_icon='mdi:mdi-pencil-outline', close=CLOSE_NO, unique=SELECT_SINGLE)
@MenuManage.describ(manage_archive_readonly)
class VirtualArchiveRename(XferContainerAcknowledge):
    short_icon = 'mdi:mdi-cloud-outline'
    model = VirtualArchive
    field_id = 'virtualarchive'
    caption = _("Rename archive")

    def fillresponse(self, new_name=''):
        if self.getparam('SAVE') is None:
            valid_params = {'SAVE': 'YES'}
            dlg = self.create_custom(self.model)
            dlg.item = self.item
            img = XferCompImage('img')
            img.set_value(self.short_icon, '#')
            img.set_location(0, 0)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0)
            dlg.add_component(lbl)
            if new_name == '':
                new_name = self.item.name
            sel = XferCompEdit('new_name')
            sel.set_value(new_name)
            sel.set_location(1, 2)
            sel.description = _('New name')
            sel.mask = VirtualArchive.MASK
            dlg.add_component(sel)
            dlg.add_action(self.return_action(TITLE_OK, short_icon='mdi:mdi-check'), close=CLOSE_YES, params=valid_params)
            dlg.add_action(WrapAction(TITLE_CANCEL, short_icon='mdi:mdi-cancel'))
        else:
            self.item.change_name(new_name)
