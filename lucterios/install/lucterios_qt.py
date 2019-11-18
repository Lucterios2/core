#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
GUI tool to manage Lucterios instance

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2019 sd-libre.fr
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
from os.path import dirname, join
import sys

from PyQt5.Qt import QApplication, QMainWindow, QAction, QIcon, qApp,\
    QSplitter, Qt, QListView, QLabel,\
    QAbstractListModel, QVariant, QSplashScreen, QPixmap

from django.utils.translation import ugettext
from django.utils.module_loading import import_module

from lucterios.install.lucterios_admin import setup_from_none, LucteriosGlobal,\
    LucteriosInstance


class InstanceModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._data = []
        self.current_item = None

    def refresh(self):
        self.beginResetModel()
        luct_glo = LucteriosGlobal()
        self._data = luct_glo.listing()
        self.current_item = None
        self.endResetModel()
        self.changed(None)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)

    def data(self, QModelIndex, role=None):
        item = self._data[QModelIndex.row()]

        if role == Qt.DisplayRole:
            return "%s" % item
        elif role == Qt.ToolTipRole:
            return "Tool Tip: %s" % item
        return QVariant()

    def changed(self, QModelIndex):
        if (QModelIndex is not None) and QModelIndex.isValid():
            self.current_item = self._data[QModelIndex.row()]
        else:
            self.current_item = None
        print('instance', self.current_item)
        self.parent().reload()


class LucteriosQtMain(QMainWindow):

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.img_path = join(dirname(import_module('lucterios.install').__file__), "lucterios.png")
        splash = QSplashScreen(QPixmap(self.img_path), Qt.WindowStaysOnTopHint)
        splash.show()
        try:
            self.model = InstanceModel(self)
            self.initUI()
            self.model.refresh()
        finally:
            splash.close()

    def initUI(self):
        self.icon_path = join(dirname(import_module('lucterios.CORE').__file__), 'static', 'lucterios.CORE', 'images')
        self.statusBar()
        self.set_actions()
        self.set_menu()
        self.set_toolsbar()
        self.set_components()
        self.setGeometry(300, 300, 475, 260)
        self.setWindowTitle(ugettext("Lucterios launcher"))
        self.setWindowIcon(QIcon(self.img_path))

    def set_actions(self):
        self.refreshAct = QAction(QIcon(join(self.icon_path, 'refresh.png')), ugettext('&Refresh'), self)
        self.refreshAct.setShortcut('F5')
        self.refreshAct.triggered.connect(self.model.refresh)
        self.upgradeAct = QAction(QIcon(join(self.icon_path, 'config.png')), ugettext('&Upgrade'), self)
        self.upgradeAct.setShortcut('Ctrl+U')
        self.upgradeAct.setEnabled(False)
        self.upgradeAct.triggered.connect(self.upgrade)
        self.exitAct = QAction(QIcon(join(self.icon_path, 'close.png')), ugettext('&Exit'), self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.triggered.connect(qApp.quit)

        self.launchAct = QAction(QIcon(join(self.icon_path, 'right.png')), ugettext("Launch"), self)
        self.launchAct.triggered.connect(self.launchInst)
        self.modifyAct = QAction(QIcon(join(self.icon_path, 'edit.png')), ugettext("Modify"), self)
        self.modifyAct.triggered.connect(self.modifyInst)
        self.deleteAct = QAction(QIcon(join(self.icon_path, 'delete.png')), ugettext("Delete"), self)
        self.deleteAct.triggered.connect(self.deleteInst)
        self.saveAct = QAction(QIcon(join(self.icon_path, 'save.png')), ugettext("Save"), self)
        self.saveAct.triggered.connect(self.saveInst)
        self.restoreAct = QAction(QIcon(join(self.icon_path, 'new.png')), ugettext("Restore"), self)
        self.restoreAct.triggered.connect(self.restoreInst)
        self.addAct = QAction(QIcon(join(self.icon_path, 'add.png')), ugettext("Add"), self)
        self.addAct.triggered.connect(self.addInst)

    def set_menu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(ugettext('&Main'))
        fileMenu.addAction(self.refreshAct)
        fileMenu.addAction(self.upgradeAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        instanceMenu = menubar.addMenu(ugettext('&Instance'))
        instanceMenu.addAction(self.launchAct)
        instanceMenu.addAction(self.modifyAct)
        instanceMenu.addAction(self.deleteAct)
        instanceMenu.addAction(self.saveAct)
        instanceMenu.addAction(self.restoreAct)
        instanceMenu.addAction(self.addAct)

    def set_toolsbar(self):
        self.maintools = self.addToolBar('Main')
        self.maintools.addAction(self.refreshAct)
        self.maintools.addAction(self.upgradeAct)
        self.maintools.addAction(self.exitAct)
        self.instancetools = self.addToolBar('Instance')
        self.instancetools.addAction(self.launchAct)
        self.instancetools.addAction(self.modifyAct)
        self.instancetools.addAction(self.deleteAct)
        self.instancetools.addAction(self.saveAct)
        self.instancetools.addAction(self.restoreAct)
        self.instancetools.addAction(self.addAct)

    def set_components(self):
        splitter = QSplitter(Qt.Horizontal)
        self.instances = QListView(self)
        self.instances.clicked.connect(self.model.changed)
        self.instances.setModel(self.model)
        splitter.addWidget(self.instances)
        self.info = QLabel(self)
        self.info.setTextFormat(Qt.RichText)
        splitter.addWidget(self.info)
        splitter.setSizes([100, 200])
        self.setCentralWidget(splitter)

    def reload(self):
        self.launchAct.setEnabled(self.model.current_item is not None)
        self.modifyAct.setEnabled(self.model.current_item is not None)
        self.deleteAct.setEnabled(self.model.current_item is not None)
        self.saveAct.setEnabled(self.model.current_item is not None)
        self.restoreAct.setEnabled(self.model.current_item is not None)
        self.info.setText("")
        if self.model.current_item is not None:
            inst = LucteriosInstance(self.model.current_item)
            inst.read()
            self.info.setText("""
<table>
<tr><th colspan='2'>%s</th></tr>
<tr><th>Database</th><td>%s</td></tr>
<tr><th>Appli</th><td>%s</td></tr>
<tr><th>Modules</th><td>%s</td></tr>
<tr><th>Extra</th><td>%s</td></tr>
""" % (inst.name, inst.get_database_txt(), inst.get_appli_txt(), inst.get_module_txt(), inst.get_extra_txt()))

    def upgrade(self):
        pass

    def launchInst(self):
        pass

    def modifyInst(self):
        pass

    def deleteInst(self):
        pass

    def saveInst(self):
        pass

    def restoreInst(self):
        pass

    def addInst(self):
        pass


def main():
    setup_from_none()
    app = QApplication(sys.argv)
    lct = LucteriosQtMain()
    lct.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
