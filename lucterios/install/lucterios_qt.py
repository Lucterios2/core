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
from os.path import dirname, join, expanduser
from time import sleep
from traceback import print_exc
from threading import Thread
import sys

from PyQt5.Qt import QApplication, QMainWindow, QFileDialog, QSplashScreen, QMessageBox,\
    QDialog, QDialogButtonBox, QVBoxLayout, QFrame, QLineEdit,\
    QComboBox, QStandardItemModel, QStandardItem, pyqtSignal, QFormLayout
from PyQt5.Qt import Qt, QDesktopWidget, QFont, QAction, QColor, QIcon, QImage, QPainter, QVariant, QAbstractListModel
from PyQt5.Qt import QSplitter, QListView, QLabel, QScrollArea, QPixmap, QTabWidget, QProgressBar

from django.utils.translation import ugettext
from django.utils.module_loading import import_module
from django.utils import six

from lucterios.install.lucterios_admin import setup_from_none, LucteriosGlobal, LucteriosInstance
from lucterios.install.graphic_lib import LucteriosMain, EditorInstance


class InstanceModel(QAbstractListModel):
    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._instance_list = []
        self.current_item = None

    def isExist(self, instance_name):
        return instance_name in self._instance_list

    def findText(self, instance_name):
        return self.index(self._instance_list.index(instance_name), 0)

    def refresh(self):
        self.beginResetModel()
        luct_glo = LucteriosGlobal()
        self._instance_list = luct_glo.listing()
        for instance_name in self._instance_list:
            if instance_name not in self.parent().running_instance.keys():
                self.parent().running_instance[instance_name] = None

        self.current_item = None
        self.endResetModel()
        self.changed(None)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._instance_list)

    def data(self, QModelIndex, role=None):
        try:
            item = self._instance_list[QModelIndex.row()]
            if role == Qt.DisplayRole:
                return item
        except IndexError:
            pass
        return QVariant()

    def changed(self, index):
        if (index is not None) and index.isValid():
            self.current_item = self._instance_list[index.row()]
        else:
            self.current_item = None
        self.parent().reload()


class InstanceDlg(QDialog, EditorInstance):

    def __init__(self, *args, **kwargs):
        super(InstanceDlg, self).__init__(*args, **kwargs)
        self.setWindowTitle(ugettext("Instance editor"))
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        layout = QVBoxLayout()
        tabs = QTabWidget(self)
        general_frame = QFrame(self)
        general_frame.setLayout(self._general_content())
        tabs.addTab(general_frame, ugettext('General'))
        db_frame = QFrame(self)
        db_frame.setLayout(self._database_content())
        tabs.addTab(db_frame, ugettext('Database'))
        layout.addWidget(tabs)
        layout.addWidget(buttonBox)
        self.setLayout(layout)

    def _general_content(self):
        layout = QFormLayout()
        self.inst_name = QLineEdit()
        layout.addRow(ugettext("Name"), self.inst_name)
        self.applis = QComboBox()
        self.applis.currentIndexChanged.connect(self.applischange)
        layout.addRow(ugettext("Appli"), self.applis)
        self.modules = QListView()
        self.modules.setModel(QStandardItemModel())
        layout.addRow(ugettext("Modules"), self.modules)
        self.language = QComboBox()
        layout.addRow(ugettext("Language"), self.language)
        self.mode = QComboBox()
        layout.addRow(ugettext("CORE-connectmode"), self.mode)
        self.password = QLineEdit()
        layout.addRow(ugettext("Password"), self.password)
        return layout

    def _database_content(self):
        layout = QFormLayout()
        self.db_type = QComboBox()
        self.db_type.currentIndexChanged.connect(self.dbtypechange)
        layout.addRow(ugettext("Type"), self.db_type)
        self.db_name = QLineEdit()
        layout.addRow(ugettext("Name"), self.db_name)
        self.db_user = QLineEdit()
        layout.addRow(ugettext("User"), self.db_user)
        self.db_password = QLineEdit()
        layout.addRow(ugettext("Password"), self.db_password)
        return layout

    def applischange(self, appli_id):
        depends_modules = self.mod_applis[appli_id][2]
        for row in range(self.modules.model().rowCount()):
            module = self.module_list[row][1]
            self.modules.model().item(row).setCheckState(Qt.Checked if module in depends_modules else Qt.Unchecked)
        appli_root_name = self.mod_applis[appli_id][0].split('.')[-1]
        if self.is_new_instance:
            default_name_idx = 1
            while appli_root_name + six.text_type(default_name_idx) in self.current_inst_names:
                default_name_idx += 1
            self.inst_name.setText(appli_root_name + six.text_type(default_name_idx))

    def dbtypechange(self, dbtype_id):
        self.db_name.setEnabled(dbtype_id != 0)
        self.db_user.setEnabled(dbtype_id != 0)
        self.db_password.setEnabled(dbtype_id != 0)

    def _load_current_data(self, instance_name):
        from lucterios.framework.settings import DEFAULT_LANGUAGES
        lct_inst, applis_id, mode_id, typedb_index, current_lang = self._get_instance_elements(instance_name)
        self.is_new_instance = False
        self.inst_name.setText(lct_inst.name)
        self.inst_name.setEnabled(False)
        self.applis.setCurrentIndex(applis_id)
        for row in range(self.modules.model().rowCount()):
            module = self.module_list[row][1]
            self.modules.model().item(row).setCheckState(Qt.Checked if module in lct_inst.modules else Qt.Unchecked)
        self.mode.setCurrentIndex(mode_id)
        for lang in DEFAULT_LANGUAGES:
            if lang[0] == current_lang:
                self.language.setCurrentIndex(self.language.findText(lang[1], Qt.MatchFixedString))
        self.password.setText('')
        self.db_type.setCurrentIndex(typedb_index)
        if 'name' in lct_inst.database[1].keys():
            self.db_name.setText(lct_inst.database[1]['name'])
        else:
            self.db_name.setText('')
        if 'user' in lct_inst.database[1].keys():
            self.db_user.setText(lct_inst.database[1]['user'])
        else:
            self.db_user.setText('')
        if 'password' in lct_inst.database[1].keys():
            self.db_password.setText(lct_inst.database[1]['password'])
        else:
            self.db_password.setText('')

    def execute(self, instance_name=None):
        from lucterios.framework.settings import DEFAULT_LANGUAGES, get_locale_lang
        self._define_values()
        self.applis.addItems(self.appli_list)
        self.modules.model().clear()
        for mod_item in self.module_list:
            item = QStandardItem(mod_item[0])
            item.setCheckable(True)
            self.modules.model().appendRow(item)
        self.language.addItems(self.lang_values)
        self.mode.addItems(self.mode_values)
        self.db_type.addItems(self.dbtype_values)
        if instance_name is not None:
            self._load_current_data(instance_name)
        else:
            self.inst_name.setText('')
            self.password.setText('')
            self.db_name.setText('')
            self.db_user.setText('')
            self.db_password.setText('')
            self.db_type.setCurrentIndex(0)
            self.mode.setCurrentIndex(2)
            if len(self.appli_list) > 0:
                self.applis.setCurrentIndex(0)
                self.applischange(0)
            for lang in DEFAULT_LANGUAGES:
                if lang[0] == get_locale_lang():
                    self.language.setCurrentIndex(self.language.findText(lang[1], Qt.MatchFixedString))
        if self.exec_():
            return self.get_result()
        else:
            return None

    def get_result(self):
        from lucterios.framework.settings import DEFAULT_LANGUAGES, get_locale_lang
        if self.is_new_instance and ((self.inst_name.text() == '') or (self.name_rull.match(self.inst_name.text()) is None)):
            QMessageBox.critical(self, ugettext("Instance editor"), ugettext("Name invalid!"))
            return None
        if self.applis.currentText() == '':
            QMessageBox.critical(self, ugettext("Instance editor"), ugettext("No application!"))
            return None

        appli_id = self.applis.currentIndex()
        security = "MODE=%s" % self.mode.currentIndex()
        if self.password.text() != '':
            security += ",PASSWORD=%s" % self.password.text()
        module_list = [self.module_list[row][1] for row in range(self.modules.model().rowCount()) if (self.modules.model().item(row).checkState() == Qt.Checked)]
        db_param = "%s:name=%s,user=%s,password=%s" % (self.db_type.currentText(), self.db_name.text(), self.db_user.text(), self.db_password.text())
        current_lang = get_locale_lang()
        for lang in DEFAULT_LANGUAGES:
            if lang[1] == self.language.currentText():
                current_lang = lang[0]
        return (self.inst_name.text(), self.mod_applis[appli_id][0], ",".join(module_list), security, db_param, current_lang)


class LucteriosQtMain(QMainWindow, LucteriosMain):

    refreshslot = pyqtSignal(str)
    enableslot = pyqtSignal(bool, object)
    progressslot = pyqtSignal()
    ugradestatesslot = pyqtSignal(int)
    showmessageslot = pyqtSignal(bool, str, str)
    runidlesslot = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        LucteriosMain.__init__(self)
        self.img_path = join(dirname(import_module('lucterios.install').__file__), "lucterios.png")
        self.instances_model = InstanceModel(self)
        self.has_checked = False
        self.refreshslot.connect(self.refresh_ex)
        self.enableslot.connect(self.enable_ex)
        self.progressslot.connect(self.step_progress)
        self.ugradestatesslot.connect(self.set_ugrade_state_ex)
        self.showmessageslot.connect(self.show_message)
        self.runidlesslot.connect(self.run_idle)
        self.initUI()
        self.start_up_app()

    def closeEvent(self, event):
        all_stop = True
        instance_names = list(self.running_instance.keys())
        for old_item in instance_names:
            if (self.running_instance[old_item] is not None) and self.running_instance[old_item].is_running():
                all_stop = False
        result = all_stop or (QMessageBox.question(self, ugettext("Lucterios launcher"),
                                                   ugettext("An instance is always running.\nDo you want to close?"), QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes)
        event.ignore()
        if result:
            self.stop_all()
            event.accept()
        else:
            self.refresh()

    def initUI(self):
        self.icon_path = join(dirname(import_module('lucterios.CORE').__file__), 'static', 'lucterios.CORE', 'images')
        self.statusBar()
        self.set_actions()
        self.set_menu()
        self.set_toolsbar()
        self.set_components()
        self.setGeometry(0, 0, 850, 500)
        self.setWindowTitle(ugettext("Lucterios launcher"))
        self.setWindowIcon(QIcon(self.img_path))
        rect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        rect.moveCenter(centerPoint)
        self.move(rect.topLeft())

    def set_actions(self):
        self.refreshAct = QAction(QIcon(join(self.icon_path, 'refresh.png')), ugettext('Refresh'), self)
        self.refreshAct.setShortcut('F5')
        self.refreshAct.triggered.connect(self.instances_model.refresh)
        self.upgradeAct = QAction(QIcon(join(self.icon_path, 'upload.png')), ugettext('Update'), self)
        self.upgradeAct.setShortcut('Ctrl+U')
        self.upgradeAct.setEnabled(False)
        self.upgradeAct.triggered.connect(self.upgrade)
        self.exitAct = QAction(QIcon(join(self.icon_path, 'exit.png')), ugettext('Exit'), self)
        self.exitAct.setShortcut('Ctrl+Q')
        self.exitAct.triggered.connect(self.close)

        self.launchAct = QAction(QIcon(join(self.icon_path, 'right.png')), ugettext("Launch"), self)
        self.launchAct.triggered.connect(lambda: self.open_inst())
        self.modifyAct = QAction(QIcon(join(self.icon_path, 'edit.png')), ugettext("Modify"), self)
        self.modifyAct.triggered.connect(self.modify_inst)
        self.deleteAct = QAction(QIcon(join(self.icon_path, 'delete.png')), ugettext("Delete"), self)
        self.deleteAct.triggered.connect(self.delete_inst)
        self.saveAct = QAction(QIcon(join(self.icon_path, 'save.png')), ugettext("Save"), self)
        self.saveAct.triggered.connect(self.save_inst)
        self.restoreAct = QAction(QIcon(join(self.icon_path, 'open.png')), ugettext("Restore"), self)
        self.restoreAct.triggered.connect(self.restore_inst)
        self.addAct = QAction(QIcon(join(self.icon_path, 'add.png')), ugettext("Add"), self)
        self.addAct.triggered.connect(self.add_inst)

    def set_menu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(ugettext('Main'))
        fileMenu.addAction(self.refreshAct)
        fileMenu.addAction(self.upgradeAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        instanceMenu = menubar.addMenu(ugettext('Instance'))
        instanceMenu.addAction(self.launchAct)
        instanceMenu.addAction(self.modifyAct)
        instanceMenu.addAction(self.saveAct)
        instanceMenu.addAction(self.restoreAct)
        instanceMenu.addAction(self.deleteAct)
        instanceMenu.addAction(self.addAct)

    def set_toolsbar(self):
        self.maintools = self.addToolBar('Main')
        self.maintools.addAction(self.refreshAct)
        self.maintools.addAction(self.upgradeAct)
        self.maintools.addAction(self.exitAct)
        self.instancetools = self.addToolBar('Instance')
        self.instancetools.addAction(self.launchAct)
        self.instancetools.addAction(self.modifyAct)
        self.instancetools.addAction(self.saveAct)
        self.instancetools.addAction(self.restoreAct)
        self.instancetools.addAction(self.deleteAct)
        self.instancetools.addAction(self.addAct)

    def set_components(self):
        tabs = QTabWidget(self)
        splitter = QSplitter(Qt.Horizontal)
        self.instances = QListView(self)
        self.instances.clicked.connect(self.instances_model.changed)
        self.instances.setModel(self.instances_model)
        splitter.addWidget(self.instances)
        self.instance = QLabel(self)
        self.instance.setAlignment(Qt.AlignTop or Qt.AlignRight)
        self.instance.setTextFormat(Qt.RichText)
        scroll1 = QScrollArea(self)
        scroll1.setWidget(self.instance)
        scroll1.setWidgetResizable(True)
        splitter.addWidget(scroll1)
        splitter.setSizes([150, 700])
        tabs.addTab(splitter, ugettext('Instances'))
        self.modules = QLabel(self)
        self.modules.setAlignment(Qt.AlignTop or Qt.AlignRight)
        self.modules.setTextFormat(Qt.RichText)
        scroll2 = QScrollArea(self)
        scroll2.setWidget(self.modules)
        scroll2.setWidgetResizable(True)
        splitter.addWidget(scroll2)
        tabs.addTab(scroll2, ugettext('Modules'))
        self.setCentralWidget(tabs)
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(1)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(1)
        self.progressBar.setTextVisible(False)
        self.progressBar.hide()
        self.progress_thread = None
        self.statusBar().addPermanentWidget(self.progressBar)

    def set_instance_info(self):
        try:
            inst = LucteriosInstance(self.instances_model.current_item)
            inst.read()
            if self.running_instance[inst.name] is not None and self.running_instance[inst.name].is_running():
                inst_status = ugettext("=> Running in http://%(ip)s:%(port)d\n") % {'ip': self.running_instance[inst.name].lan_ip, 'port': self.running_instance[inst.name].port}
                btn_text = ugettext("Stop")
            else:
                inst_status = ugettext("=> Stopped\n")
                btn_text = ugettext("Launch")
            content = "<h1><center>%s</center></h1>" % inst.name
            content += "<p>%s<br/></p>" % inst_status
            self.launchAct.setText(btn_text)
            content += "<table width='100%'>"
            content += "<tr><th style='width:30%%;min-width:150px;'>%s</th><td>%s<br/></td></tr>" % (ugettext("Application"), inst.get_appli_txt())
            content += "<tr><th>%s</th><td>%s<br/></td></tr>" % (ugettext("Modules"), inst.get_module_txt().replace(',', '<br/>'))
            content += "<tr><th>%s</th><td>%s<br/></td></tr>" % (ugettext("Database"), inst.get_database_txt())
            content += "<tr><th>%s</th><td>%s</td></tr>" % (ugettext("Extra"), inst.get_extra_html())
            content += "</table>"
            self.instance.setText(content)
        except Exception:
            self.instance.setText("<h1><center>%s</center></h1>" % self.instances_model.current_item)

    def set_modules_info(self):
        lct_glob = LucteriosGlobal()
        mod_lucterios, mod_applis, mod_modules = lct_glob.installed()
        content = "<tr><th width='30%%'>%s</th><td>%s<br/></td></tr>" % (ugettext('Lucterios core'), mod_lucterios[1])
        appli = ""
        for appli_item in mod_applis:
            appli += "<tr><td style='width:30%%;min-width:100px;'>%s</td><td>%s</td></tr>" % (appli_item[0], appli_item[1])
        content += "<tr><th>%s</th><td><table width='80%%'>%s</table><br/></td></tr>" % (ugettext("Application"), appli)
        modules = ""
        for module_item in mod_modules:
            modules += "<tr><td style='width:30%%;min-width:100px;'>%s</td><td>%s</td></tr>" % (module_item[0], module_item[1])
        content += "<tr><th>%s</th><td><table width='80%%'>%s</table><br/></td></tr>" % (ugettext("Modules"), modules)
        extra_urls = lct_glob.get_extra_urls()
        if len(extra_urls) > 0:
            content += "<tr><th>%s</th><td>%s</td></tr>" % (ugettext('Pypi servers'), "<br/>".join(extra_urls))
        self.modules.setText("<table width='100%'>" + content + "</table>")
        self.has_checked = True
        self.run_after(1000, lambda: Thread(target=self.check).start())
        self.statusBar().showMessage(ugettext("Search upgrade"))

    def refresh(self, instance_name=None):
        if instance_name == '':
            instance_name = None
        self.refreshslot.emit(instance_name)

    def refresh_ex(self, instance_name=None):
        if (instance_name is None) or not self.instances_model.isExist(instance_name):
            self.instances_model.refresh()
        if (instance_name is not None) and (instance_name != ''):
            index = self.instances_model.findText(instance_name)
            self.instances.setCurrentIndex(index)
            self.instances_model.changed(index)

    def reload(self):
        self.launchAct.setEnabled(self.instances_model.current_item is not None)
        self.modifyAct.setEnabled(self.instances_model.current_item is not None)
        self.deleteAct.setEnabled(self.instances_model.current_item is not None)
        self.saveAct.setEnabled(self.instances_model.current_item is not None)
        self.restoreAct.setEnabled(self.instances_model.current_item is not None)
        self.instance.setText("")
        if self.instances_model.current_item is not None:
            self.set_instance_info()
        else:
            self.launchAct.setText(ugettext("Launch"))
            if not self.has_checked:
                self.set_modules_info()

    def get_selected_instance_name(self):
        return self.instances_model.current_item

    def show_info(self, text, message):
        self.showmessageslot.emit(False, str(text), str(message))

    def show_error(self, text, message):
        if isinstance(message, Exception):
            import traceback
            msg = ''.join(traceback.format_exception(etype=type(message), value=message, tb=None))
        else:
            msg = str(message)
        self.showmessageslot.emit(True, str(text), msg)

    def show_message(self, is_error, text, message):
        if is_error:
            QMessageBox.critical(self, text, message)
        else:
            QMessageBox.information(self, text, message)

    def show_splash_screen(self):
        splash_pix = QPixmap(350, 200)
        splash_pix.fill(QColor('white'))
        painter = QPainter()
        painter.begin(splash_pix)
        painter.drawImage(100, 55, QImage(self.img_path))
        painter.end()
        self.splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        self.splash.showMessage(ugettext('Application loading\nWaiting a minute ...'), Qt.AlignHCenter)
        font = QFont(self.splash.font())
        font.setPointSize(font.pointSize() + 3)
        self.splash.setFont(font)
        self.splash.show()

    def remove_splash_screen(self):
        self.instances_model.refresh()
        self.splash.close()
        self.splash = None

    def show(self):
        QMainWindow.show(self)
        if self.instances_model.rowCount() == 0:
            self.run_after(0, self.add_inst)

    def enabled(self, is_enabled, widget=None):
        self.enableslot.emit(is_enabled, widget)

    def enable_ex(self, is_enabled, widget=None):
        if widget is None:
            widget = self
            self.do_progress(not is_enabled)
        widget.setEnabled(is_enabled)

    def do_progress(self, progressing):
        if self.progress_thread is not None:
            self.progress_thread.do_run = False
            self.progress_thread.join()
            self.progressBar.setValue(self.progressBar.minimum())
            self.progressBar.hide()
            self.progress_thread = None
        if progressing:
            self.progress_thread = Thread(target=self.progress_run)
            self.progressBar.setValue(self.progressBar.minimum())
            self.progressBar.show()
            self.progress_thread.start()

    def progress_run(self):
        try:
            while (self.progress_thread is not None) and getattr(self.progress_thread, "do_run", True) and self.progress_thread.is_alive():
                self.progressslot.emit()
                sleep(0.25)
        except Exception:
            print_exc()

    def step_progress(self):
        value = self.progressBar.value() + 1
        if value > self.progressBar.maximum():
            value = self.progressBar.minimum()
        self.progressBar.setValue(value)

    def run_after(self, ms, func=None, *args):
        self.runidlesslot.emit(lambda: func(*args))

    def run_idle(self, func=None):
        func()

    def set_ugrade_state(self, upgrade_mode):
        self.ugradestatesslot.emit(upgrade_mode)

    def set_ugrade_state_ex(self, upgrade_mode):
        if upgrade_mode == 2:
            msg = ugettext("The application must restart")
            self.show_info(ugettext("Lucterios launcher"), msg)
            self.upgradeAct.setEnabled(False)
            self.statusBar().showMessage(msg)
        else:
            self.upgradeAct.setEnabled(upgrade_mode == 1)
            self.statusBar().showMessage(self.ugrade_message(upgrade_mode == 1))

    def modify_inst(self):
        instance_name = self.get_selected_instance_name()
        dlg = InstanceDlg(self)
        result = dlg.execute(instance_name)
        if result is not None:
            self.add_modif_inst_result(result, False)

    def add_inst(self):
        dlg = InstanceDlg(self)
        result = dlg.execute()
        if result is not None:
            self.add_modif_inst_result(result, True)

    def delete_inst(self):
        instance_name = self.get_selected_instance_name()
        if QMessageBox.question(self, ugettext("Lucterios launcher"), ugettext("Do you want to delete '%s'?") % instance_name, QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
            self.delete_inst_name(instance_name)
        else:
            self.refresh()

    def save_inst(self):
        instance_name = self.get_selected_instance_name()
        if instance_name != '':
            file_name = QFileDialog.getSaveFileName(self, ugettext("File to save"), expanduser('~'), 'lbk (*.lbk);;* (.*', options=QFileDialog.HideNameFilterDetails)
            if isinstance(file_name, tuple) and (len(file_name) > 0):
                file_name = file_name[0]
            if isinstance(file_name, str) and (file_name != ''):
                self.save_instance(instance_name, file_name)

    def restore_inst(self):
        instance_name = self.get_selected_instance_name()
        if instance_name != '':
            file_name = QFileDialog.getOpenFileName(self, ugettext("File to load"), expanduser('~'), 'lbk (*.lbk);;* (.*', options=QFileDialog.HideNameFilterDetails)
            if isinstance(file_name, tuple) and (len(file_name) > 0):
                file_name = file_name[0]
            if isinstance(file_name, str) and (file_name != ''):
                self.restore_instance(instance_name, file_name)


def main():
    setup_from_none()
    app = QApplication(sys.argv)
    lct = LucteriosQtMain()
    lct.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
