import os
import new
import roslib, rospy
roslib.load_manifest('rqt_console')

from qt_gui.plugin import Plugin
from qt_gui.qt_binding_helper import loadUi
from QtGui import QApplication, QDialog, QFileDialog, QHeaderView, QIcon, QInputDialog, QLineEdit, QMenu, QMessageBox, QTableView, QWidget
from QtCore import qDebug, Qt, QTimer, Slot, QEvent

from message_data_model import MessageDataModel
from custom_widgets import MainWindow, SetupDialog, TimeDialog, ComboDialog
from message_proxy_model import MessageProxyModel

class Console(Plugin):
    def __init__(self, context):
        super(Console, self).__init__(context)
        # give QObjects reasonable names
        self.setObjectName('Console')

        # create QWidget
        self._mainwindow = MainWindow()
        # get path to UI file which is a sibling of this file
        ui_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'console.ui')
        # extend the widget with all attributes and children from UI file
        loadUi(ui_file, self._mainwindow)
        # give QObjects reasonable names
        self._mainwindow.setObjectName('ConsoleUi')
        # add widget to the user interface
        context.add_widget(self._mainwindow)
        self._datamodel = MessageDataModel()
        self._proxymodel = MessageProxyModel()

        self._mainwindow.table_view.setModel(self._proxymodel)
        self._proxymodel.setSourceModel(self._datamodel)
        self._proxymodel.setDynamicSortFilter(True);

        self._mainwindow.table_view.setVisible(False)
        self._columnwidth = (600, 140, 200, 360, 200, 600)
        for idx, width in enumerate(self._columnwidth):
            self._mainwindow.table_view.horizontalHeader().resizeSection(idx, width)
        self._mainwindow.table_view.setVisible(True)

        self._mainwindow.table_view.mousePressEvent = self.mouse_press_handler
        self._mainwindow.table_view.keyPressEvent = self.custom_keypress

        self._mainwindow.pause_button.clicked[bool].connect(self.pause_press)
        self._mainwindow.open_button.clicked[bool].connect(self.open_press)
        self._mainwindow.save_button.clicked[bool].connect(self.save_press)

        self._setupdialog = SetupDialog(context, self.message_callback)
        self._timedialog = TimeDialog()
        self._paused = False
        self._mainwindow.table_view.sortByColumn(3,Qt.DescendingOrder)
        self._mainwindow.pause_button.setIcon(QIcon.fromTheme('media-playback-pause'))
        self._mainwindow.open_button.setIcon(QIcon.fromTheme('document-open'))
        self._mainwindow.save_button.setIcon(QIcon.fromTheme('document-save'))

    def pause_press(self, b):
        self._paused = not self._paused
        if self._paused:
            self._mainwindow.pause_button.setIcon(QIcon.fromTheme('media-record'))
            self._mainwindow.pause_button.setText('Resume')
        else:
            self._mainwindow.pause_button.setIcon(QIcon.fromTheme('media-playback-pause'))
            self._mainwindow.pause_button.setText('Pause')
            

    def open_press(self, b):
        filename = QFileDialog.getOpenFileName(self._mainwindow, 'Load File', '.')
        if filename[0] != '':
            fileHandle = open(filename[0])
            self._datamodel.open_from_file(fileHandle)
            fileHandle.close()
            self.reset_status()
    
    def save_press(self, b):
        filename = QFileDialog.getOpenFileName(self._mainwindow, 'Save to File', '.')
        if filename[0] != '':
            fileHandle = open(filename[0], 'w')
            self._datamodel.save_to_file(fileHandle)
            fileHandle.close()
            self.reset_status()

    def show_combo_dialog(self, titletext, labeltext, itemlist, selectedlist):
        dlg = ComboDialog(titletext, labeltext, itemlist, selectedlist)
        ok = dlg.exec_()
        ok = (ok == 1)
        textlist = dlg.list_box.selectedItems()
        text = ''
        for item in textlist:
            text += item.text() + self._proxymodel.get_or()
        text = text[:-1]
        return (text, ok)

    def show_filter_input(self, pos):
        col = self._mainwindow.table_view.columnAt(pos.x())
        if col == 0:
            text, ok = QInputDialog.getText(QWidget(), 'Message filter', 'Enter text (leave blank for no filtering):', QLineEdit.Normal, self._proxymodel.get_filter(col))
        elif col == 1:
            text, ok = self.show_combo_dialog('Severity filter', 'Include only:', ['Debug', 'Info', 'Warning', 'Error', 'Fatal'], self._proxymodel.get_filter(col))
        elif col == 2:
            text, ok = self.show_combo_dialog('Node filter', 'Include only:', self._datamodel.get_unique_col_data(col), self._proxymodel.get_filter(col))
        elif col == 3:
            self._clear_filter = False
            def handle_ignore():
                self._clear_filter = True
            self._timedialog.ignore_button_clicked.connect(handle_ignore)
            
            indexes = self._mainwindow.table_view.selectionModel().selectedIndexes()
            if self._proxymodel.get_filter(col) != '':
            #if there is a current filter use it
                filter_ = self._proxymodel.get_filter(col)
                mintime, maxtime = filter_.split(':')
                self._timedialog.set_time(mintime,maxtime)
            elif len(indexes) != 0:
            #get the current selection get the min and max times from the
            #selected range and set them as the min/max for the dialog
                rowlist = []
                for current in indexes:
                    rowlist.append(self._proxymodel.mapToSource(current).row())
                rowlist = list(set(rowlist))
                rowlist.sort()
                
                mintime, maxtime = self._datamodel.get_time_range(rowlist)
                self._timedialog.set_time(mintime,maxtime)
            else:
                self._timedialog.set_time()
            ok = self._timedialog.exec_()
            self._timedialog.ignore_button_clicked.disconnect(handle_ignore)
            ok = (ok == 1)
            if self._clear_filter:
                text = ''
            else:
                mintime = str(self._timedialog.min_dateedit.dateTime().toTime_t()) + self._timedialog.min_dateedit.dateTime().toString('.zzz')
                maxtime = str(self._timedialog.max_dateedit.dateTime().toTime_t()) + self._timedialog.max_dateedit.dateTime().toString('.zzz')
                text = mintime + ':' + maxtime
        elif col == 4:
            unique_list = set()
            for topiclists in self._datamodel.get_unique_col_data(col):
                for item in topiclists.split(','):
                    unique_list.add(item.strip())
            unique_list = list(unique_list)
            text, ok = self.show_combo_dialog('Topic filter', 'Include only:', unique_list, self._proxymodel.get_filter(col))
        elif col == 5:
            text, ok = QInputDialog.getText(QWidget(), 'Location Filter', 'Enter text (leave blank for no filtering:', QLineEdit.Normal, self._proxymodel.get_filter(col))
        else:
            ok = False
        if ok:
            if text == 'All':
                text = ''
            self._proxymodel.set_filter(col, text)
            self.reset_status()

    def process_inc_exc(self, col, exclude=False):
        prevfilter = self._proxymodel.get_filter(col)
        if prevfilter != '':
            prevfilter = '(' + prevfilter + ')' + self._proxymodel.get_and()
        num_selected = len(self._mainwindow.table_view.selectionModel().selectedIndexes())/6
        nodetext = ''
        for index in range(num_selected):
            addtext = self._mainwindow.table_view.selectionModel().selectedIndexes()[num_selected*col+index].data()
            if exclude:
                addtext = self._proxymodel.get_not() + addtext
            nodetext += addtext
            if exclude:
                nodetext += self._proxymodel.get_and()
            else:
                nodetext += self._proxymodel.get_or()
        nodetext = nodetext[:-1]
        newfilter = prevfilter + nodetext
        if prevfilter.find(nodetext) == -1:
            self._proxymodel.set_filter(col,newfilter)

    def rightclick_menu(self, event):
        # menutext string entries are added as menu items
        # list entries are added as submenues with the second element as subitems
        menutext = []
        menutext.append(['Edit Filter'])
        if len(self._mainwindow.table_view.selectionModel().selectedIndexes()) != 0:
            menutext.append(['Exclude',['Node(s)','Message(s)']])
            menutext.append(['Include',['Node(s)','Message(s)']])
        menutext.append(['Clear Filter'])
        menutext.append(['Copy'])
        
        actions = []
        menu = QMenu()
        submenus = []
        submenuindex = -1
        for index, item in enumerate(menutext):
            if len(item) == 1:
                actions.append((item[0], menu.addAction(item[0])))
            else:
                submenus.append(QMenu())
                for subitem in item[1]:
                    actions.append((item[0] + '>' + subitem, submenus[-1].addAction(subitem)))
                submenus[-1].setTitle(item[0])
                menu.addMenu(submenus[-1])
                                
        actions = dict(actions)
        action = menu.exec_(event.globalPos())

        #actions are accessed by dict index menutext>submenutext
        col = self._mainwindow.table_view.columnAt(event.pos().x())
        if action is None or action == 0:
            return 
        elif action == actions['Clear Filter']:
            self._proxymodel.set_filter(col,'')
        elif action == actions['Edit Filter']:
            self.show_filter_input(event.pos())
        elif action == actions['Copy']:
            rowlist = []
            for current in self._mainwindow.table_view.selectionModel().selectedIndexes():
                rowlist.append(self._proxymodel.mapToSource(current).row())
            copytext = self._datamodel.get_selected_text(rowlist)
            if copytext is not None:
                clipboard = QApplication.clipboard()
                clipboard.setText(copytext)
        elif action == actions['Include>Node(s)']:
            self.process_inc_exc(2)
        elif action == actions['Include>Message(s)']:
            self.process_inc_exc(0)
        elif action == actions['Exclude>Node(s)']:
            self.process_inc_exc(2,True)
        elif action == actions['Exclude>Message(s)']:
            self.process_inc_exc(0,True)
        else:
            raise
        self.reset_status()

    def message_callback(self, data):
        if not self._paused:
            self._datamodel.insertRows(data)
            self.reset_status()
    
    def mouse_press_handler(self, 
                            event,
                            old_pressEvent=QTableView.mousePressEvent):
        if event.buttons() & Qt.RightButton and event.modifiers() == Qt.NoModifier:
            self.rightclick_menu(event)
            return event.accept()
        return old_pressEvent(self._mainwindow.table_view, event)
        
    def custom_keypress(self, event, old_keyPressEvent=QTableView.keyPressEvent):
        if event.key() == Qt.Key_Delete:
            delete = QMessageBox.Yes
            if len(self._mainwindow.table_view.selectionModel().selectedIndexes()) == 0:
                delete = QMessageBox.question(self._mainwindow, 'Message', "Are you sure you want to delete all messages?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if delete == QMessageBox.Yes and event.key() == Qt.Key_Delete and event.modifiers() == Qt.NoModifier:
                rowlist = []
                for current in self._mainwindow.table_view.selectionModel().selectedIndexes():
                    rowlist.append(self._proxymodel.mapToSource(current).row())
                rowlist = list(set(rowlist))
                if self._datamodel.remove_rows(rowlist):
                    self.reset_status()
                    return event.accept()
        return old_keyPressEvent(self._mainwindow.table_view, event)

    def shutdown_plugin(self):
        self._setupdialog.unsub_topic()
        self._setupdialog.close()

    def save_settings(self, plugin_settings, instance_settings):
        for index, member in enumerate(self._datamodel.message_members()):
            instance_settings.set_value(member,self._proxymodel.get_filter(index))

    def restore_settings(self, plugin_settings, instance_settings):
        for index, member in enumerate(self._datamodel.message_members()):
            text = instance_settings.value(member)
            if type(text) is type(None):
                text=''
            self._proxymodel.set_filter(index, text)

    def trigger_configuration(self):
        self._setupdialog.refresh_nodes()
        self._setupdialog.node_list.item(0).setSelected(True)
        self._setupdialog.node_changed(0)
        self._setupdialog.exec_()

    def reset_status(self):
        if self._datamodel.rowCount() == self._proxymodel.rowCount():
            tip = self._mainwindow.tr('Displaying %s Messages' % (self._datamodel.rowCount())) 
        else:
            tip = self._mainwindow.tr('Displaying %s of %s Messages' % (self._proxymodel.rowCount(),self._datamodel.rowCount())) 
        self._mainwindow.messages_label.setText(tip)

