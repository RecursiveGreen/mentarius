#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKitWidgets
import mentarius_rc

from journal import Entry, Journal

class EntryEdit(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setObjectName("entry_editpage")

        self.edit_layout = QtWidgets.QGridLayout(self)
        self.edit_layout.setObjectName("edit_layout")
        self.edit_layout.setContentsMargins(0, 0, 0, 0)

        self.titlelabel = QtWidgets.QLabel(self)
        self.titlelabel.setObjectName("entry_titlelabel")
        self.titlelabel.setText("Title:")
        self.edit_layout.addWidget(self.titlelabel, 0, 0, 1, 1)

        self.titletext = QtWidgets.QLineEdit(self)
        self.titletext.setObjectName("entry_titletext")
        self.titletext.setMaxLength(255)
        self.edit_layout.addWidget(self.titletext, 0, 1, 1, 1)

        self.bodytext = QtWidgets.QPlainTextEdit(self)
        self.bodytext.setObjectName("entry_bodytext")
        self.edit_layout.addWidget(self.bodytext, 1, 0, 1, 2)


class EntryView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setObjectName("entry_viewpage")

        self.view_layout = QtWidgets.QVBoxLayout(self)
        self.view_layout.setObjectName("view_layout")
        self.view_layout.setSpacing(0)
        self.view_layout.setContentsMargins(0, 0, 0, 0)

        self.viewer = QtWebKitWidgets.QWebView(self)
        self.viewer.setObjectName("entry_viewer")
        self.viewer.setUrl(QtCore.QUrl("about:blank"))
        self.view_layout.addWidget(self.viewer)


class EntryWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setObjectName("main_entry")

        self.entry_widget_layout = QtWidgets.QVBoxLayout(self)
        self.entry_widget_layout.setObjectName("entry_widget_layout")
        self.entry_widget_layout.setSpacing(0)
        self.entry_widget_layout.setContentsMargins(4, 0, 0, 0)

        self.toolbar = QtWidgets.QToolBar()
        self.entry_widget_layout.addWidget(self.toolbar)

        self.entry_widget = QtWidgets.QStackedWidget(self)
        self.entry_widget.setObjectName("entry_widget")
        self.entry_widget_layout.addWidget(self.entry_widget)

        self.entry_editpage = EntryEdit(self)
        self.entry_widget.addWidget(self.entry_editpage)

        self.entry_viewpage = EntryView(self)
        self.entry_widget.addWidget(self.entry_viewpage)

        self.entry_widget.setCurrentWidget(self.entry_editpage)

        self.initActions()
        self.initToolbars()
        self.reset()

    def initActions(self):
        self.act_edit = QtWidgets.QAction(QtGui.QIcon(':/document-edit'),
                                          '&Edit Entry',
                                          self,
                                          statusTip='Changes the mode to edit your journal entries',
                                          triggered=self.toggleEntry)
        self.act_edit.setVisible(False)

        self.act_view = QtWidgets.QAction(QtGui.QIcon(':/document-preview'),
                                          '&Preview Entry',
                                          self,
                                          statusTip='Preview the current journal entry',
                                          triggered=self.toggleEntry)

        self.entry_editpage.titletext.textChanged.connect(self.updateViewer)
        self.entry_editpage.bodytext.textChanged.connect(self.updateViewer)

    def initToolbars(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        # self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.toolbar.addAction(self.act_edit)
        self.toolbar.addAction(self.act_view)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(spacer)

    def reset(self):
        self.entry_editpage.titletext.clear()
        self.entry_editpage.bodytext.clear()
        self.entry_viewpage.viewer.setUrl(QtCore.QUrl("about:blank"))
        self.entry_widget.setCurrentWidget(self.entry_editpage)

    def toggleEntry(self):
        if self.act_edit.isVisible():
            self.act_edit.setVisible(False)
            self.act_view.setVisible(True)
            self.entry_widget.setCurrentWidget(self.entry_editpage)
        else:
            self.act_edit.setVisible(True)
            self.act_view.setVisible(False)
            self.updateViewer()
            self.entry_widget.setCurrentWidget(self.entry_viewpage)

    @QtCore.pyqtSlot()
    def updateViewer(self):
        title = self.entry_editpage.titletext.text()
        text = self.entry_editpage.bodytext.toPlainText()
        # self.entry_viewpage.viewer.setHtml(text, self.baseUrl)
        self.entry_viewpage.viewer.setHtml('<h1>{0}</h1><p>{1}</p>'.format(title, text))

class EntryCalendar(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Entry Calendar')

        self.dock_widget = QtWidgets.QWidget(self)
        self.dock_widget_layout = QtWidgets.QVBoxLayout(self.dock_widget)
        self.dock_widget_layout.setSpacing(0)
        self.dock_widget_layout.setContentsMargins(0, 0, 0, 0)
        # self.dock_widget.setLayout(self.dock_widget_layout)

        self.toolbar = QtWidgets.QToolBar()
        self.calendar = QtWidgets.QCalendarWidget(self.dock_widget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendar.sizePolicy().hasHeightForWidth())
        self.calendar.setSizePolicy(sizePolicy)

        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        self.dock_widget_layout.addWidget(self.toolbar)
        self.dock_widget_layout.addWidget(self.calendar)
        self.dock_widget_layout.addItem(spacer)

        self.setWidget(self.dock_widget)

        self.topLevelChanged.connect(self.on_move)

        self.initActions()
        self.initToolbars()
        self.reset()

    def initActions(self):
        self.act_previous_entry = QtWidgets.QAction(QtGui.QIcon(':/go-previous'),
                                                    '&Previous Entry',
                                                    self,
                                                    statusTip='Go back to the previous journal entry',
                                                    triggered=self.prevEntry)

        self.act_next_entry = QtWidgets.QAction(QtGui.QIcon(':/go-next'),
                                                '&Next Entry',
                                                self,
                                                statusTip='Go to the next journal journal entry',
                                                triggered=self.nextEntry)

        self.act_today = QtWidgets.QAction(QtGui.QIcon(':/go-jump-today'),
                                           '&Today',
                                           self,
                                           statusTip='Go to today\'s entry',
                                           triggered=self.today)

    def initToolbars(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        # self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        right_spacer = QtWidgets.QWidget()
        right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.toolbar.addAction(self.act_previous_entry)
        self.toolbar.addWidget(left_spacer)
        self.toolbar.addAction(self.act_today)
        self.toolbar.addWidget(right_spacer)
        self.toolbar.addAction(self.act_next_entry)

    def reset(self):
        self.calendar.setSelectedDate(QtCore.QDate.currentDate())
        self.calendar.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())

    @QtCore.pyqtSlot()
    def on_move(self):
        if self.isFloating():
            self.resize(self.sizeHint())

    def prevEntry(self):
        pass

    def nextEntry(self):
        pass

    def today(self):
        self.calendar.setSelectedDate(QtCore.QDate.currentDate())


class EntryListModel(QtCore.QAbstractTableModel):
    def __init__(self, entries=[], parent=None):
        super().__init__(parent)
        self.__entries = entries
        self.columns = sorted(list(vars(Entry()).keys()))

    def columnCount(self, parent):
        return len(self.columns)

    def rowCount(self, parent):
        return len(self.__entries)

    def data(self, index, role):
        if (role == QtCore.Qt.DisplayRole) or (role == QtCore.Qt.EditRole):
            attr_name = self.columns[index.column()]
            row = self.__entries[index.row()]
            return getattr(row, attr_name)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            attr_name = self.columns[index.column()]
            row = self.__entries[index.row()]
            setattr(row, attr_name, value)
            setattr(row, 'date_modified', datetime.datetime.now())
            setattr(row, 'modified', True)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows, obj=Entry(), parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)

        for i in range(rows):
            self.__entries.insert(position, obj)

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)

        for i in range(rows):
            obj = self.__entries[position]
            self.__entries.remove(obj)

        self.endRemoveRows()
        return True

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable


class EntryList(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Entry List')

        self.dock_widget = QtWidgets.QWidget(self)
        self.dock_widget_layout = QtWidgets.QVBoxLayout(self.dock_widget)
        self.dock_widget_layout.setSpacing(0)
        self.dock_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QtWidgets.QToolBar()

        self.entrylist = QtWidgets.QListView(self.dock_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.entrylist.sizePolicy().hasHeightForWidth())
        self.entrylist.setSizePolicy(sizePolicy)

        self.dock_widget_layout.addWidget(self.toolbar)
        self.dock_widget_layout.addWidget(self.entrylist)

        self.setWidget(self.dock_widget)

        self.initActions()
        self.initToolbars()
        self.reset()

    def initActions(self):
        self.act_new_entry = QtWidgets.QAction('&New',
                                               self,
                                               statusTip='Create a new entry for this date',
                                               triggered=self.parent().new_entry)

    def initToolbars(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        # self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # left_spacer = QtWidgets.QWidget()
        # left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # right_spacer = QtWidgets.QWidget()
        # right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.toolbar.addAction(self.act_new_entry)
        # self.toolbar.addWidget(left_spacer)

    def reset(self):
        pass
        # self.entrylist_model.clear()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setObjectName("main_window")
        self.setWindowTitle('Mentarius')
        self.resize(800, 600)

        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setObjectName("main_widget")
        self.main_widget_layout = QtWidgets.QVBoxLayout(self.main_widget)
        self.main_widget_layout.setObjectName("main_widget_layout")
        self.main_widget_layout.setSpacing(0)
        self.main_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.main_entry = EntryWidget(self.main_widget)
        # self.main_entry.setEnabled(False)

        self.main_widget_layout.addWidget(self.main_entry)

        self.setCentralWidget(self.main_widget)

        self.journal = Journal()

        self.initActions()
        self.initDocks()
        self.initMenus()
        self.initModels()
        self.initStatusBar()
        self.resetAll()

        QtCore.QMetaObject.connectSlotsByName(self)

    def initActions(self):
        # self.action_exit = QtWidgets.QAction(main_window)
        # icon = QtGui.QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/application-exit"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # self.action_exit.setIcon(icon)
        # self.action_exit.setObjectName("action_exit")

        self.act_new = QtWidgets.QAction('&New',
                                         self,
                                         shortcut='Ctrl+N',
                                         statusTip='New Journal',
                                         triggered=self.new_journal)

        self.act_open = QtWidgets.QAction('&Open',
                                          self,
                                          shortcut='Ctrl+O',
                                          statusTip='Open Journal',
                                          triggered=self.open_journal)

        self.act_quit = QtWidgets.QAction(QtGui.QIcon(':/application-exit'),
                                          '&Quit',
                                          self,
                                          shortcut='Ctrl+Q',
                                          statusTip='Quit Mentarius',
                                          triggered=self.close)

        self.act_save = QtWidgets.QAction('&Save',
                                          self,
                                          shortcut='Ctrl+S',
                                          statusTip='Save Journal',
                                          triggered=self.save_journal)

    def initDocks(self):
        self.dock_calendar = EntryCalendar(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dock_calendar)

        self.dock_entrylist = EntryList(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dock_entrylist)

    def initMenus(self):
        self.main_menubar = QtWidgets.QMenuBar(self)
        self.main_menubar.setObjectName("main_menubar")

        self.menu_file = QtWidgets.QMenu(self.main_menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_file.setTitle("&File")
        self.menu_file.addAction(self.act_new)
        self.menu_file.addAction(self.act_open)
        self.menu_file.addAction(self.act_save)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.act_quit)

        self.menu_view = QtWidgets.QMenu(self.main_menubar)
        self.menu_view.setObjectName("menu_view")
        self.menu_view.setTitle("&View")
        self.menu_view.addAction(self.dock_calendar.toggleViewAction())
        self.menu_view.addAction(self.dock_entrylist.toggleViewAction())

        self.main_menubar.addMenu(self.menu_file)
        self.main_menubar.addMenu(self.menu_view)

        self.setMenuBar(self.main_menubar)

    def initModels(self):
        self.entrymodel = EntryListModel(self.journal.entries, self)
        self.entryproxy = QtCore.QSortFilterProxyModel(self)

        self.entrymapper = QtWidgets.QDataWidgetMapper(self)
        self.entrymapper.setModel(self.entrymodel)
        self.entrymapper.addMapping(self.main_entry.entry_editpage.titletext,
                                    self.entrymodel.columns.index('title'))
        self.entrymapper.addMapping(self.main_entry.entry_editpage.bodytext,
                                    self.entrymodel.columns.index('body'))

        self.entryproxy.setSourceModel(self.entrymodel)
        self.entryproxy.setFilterKeyColumn(self.entrymodel.columns.index('date_published'))

        self.dock_calendar.calendar.selectionChanged.connect(self.entryproxy.setFilterWildcard)

        self.dock_entrylist.entrylist.setModel(self.entrymodel)
        self.dock_entrylist.entrylist.setModelColumn(self.entrymodel.columns.index('title'))
        self.main_entry.setEnabled(True)
        self.dock_entrylist.entrylist.clicked.connect(self.entrymapper.setCurrentModelIndex)

        self.entrymapper.toLast()

    def initStatusBar(self):
        self.main_statusbar = QtWidgets.QStatusBar(self)
        self.main_statusbar.setObjectName("main_statusbar")
        self.main_statusbar.showMessage("Ready.")

        self.setStatusBar(self.main_statusbar)

    def new_entry(self):
        self.entrymodel.insertRows(len(self.journal.entries), 1)
        self.dock_entrylist.entrylist.setCurrentIndex(len(self.journal.entries))

    def new_journal(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Create New Journal')

        if not filename:
            return

        if not filename.endswith('.mentdb'):
            filename += '.mentdb'

        self.journal.new(filename)
        self.resetAll()

    def open_journal(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Journal','.','(*.mentdb)')

        if not filename:
            return

        self.journal.load(filename)
        self.initModels()

    def resetAll(self):
        self.main_entry.reset()
        self.dock_calendar.reset()
        self.dock_entrylist.reset()

    def save_journal(self):
        self.journal.save()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mentarius = MainWindow()
    mentarius.show()
    sys.exit(app.exec_())


#        self.retranslateUi(main_window)

#    def retranslateUi(self, main_window):
#        _translate = QtCore.QCoreApplication.translate
#        main_window.setWindowTitle(_translate("main_window", "Mentarius"))
#        self.entry_titlelabel.setText(_translate("main_window", "Title:"))
#        self.menu_File.setTitle(_translate("main_window", "&File"))
#        self.main_toolbar.setWindowTitle(_translate("main_window", "toolBar"))
#        self.action_exit.setText(_translate("main_window", "E&xit"))
#        self.action_exit.setToolTip(_translate("main_window", "Exit the Application"))
#        self.action_editentry.setText(_translate("main_window", "Edit Entry"))
#        self.action_editentry.setToolTip(_translate("main_window", "Changes the mode to edit your journal entries"))
#        self.action_viewentry.setText(_translate("main_window", "View Entry"))
#        self.action_viewentry.setToolTip(_translate("main_window", "Changes the mode to view your journal entries"))


# mayFirst = QDate(self.calendar.yearShown(), 5, 1)

#            mayFirstFormat = QTextCharFormat()
#             mayFirstFormat.setForeground(Qt.red)

#            self.calendar.setDateTextFormat(mayFirst, mayFirstFormat)
