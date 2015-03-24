#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sqlite3

from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QAbstractTableModel, QDate,
                          QItemSelection, QMetaObject, QModelIndex, QSize,
                          QSortFilterProxyModel, Qt, QUrl)
from PyQt5.QtGui import (QFont, QIcon, QTextCharFormat, QTextCursor,
                         QTextListFormat)
from PyQt5.QtPrintSupport import QPrintDialog, QPrintPreviewDialog
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import (QAction, QApplication, QCalendarWidget,
                             QColorDialog, QComboBox, QDataWidgetMapper,
                             QDialog, QDockWidget, QFileDialog, QFontComboBox,
                             QGridLayout, QLabel, QLineEdit, QListView,
                             QMainWindow, QMenu, QMenuBar, QMessageBox,
                             QSizePolicy, QSpacerItem, QStackedWidget,
                             QStatusBar, QTextEdit, QToolBar, QVBoxLayout,
                             QWidget)
import icons

from journal import Entry, Journal
from plugin import PluginRegistry, discover_plugins


class EntryTitleText(QLineEdit):
    '''Custom QLineEdit to emit a signal every time a key is pressed.'''
    titlechanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        self.titlechanged.emit()


class EntryEdit(QWidget):
    '''Widget for handling the editing of single entries.'''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.edit_layout = QGridLayout(self)
        self.edit_layout.setObjectName("edit_layout")
        self.edit_layout.setContentsMargins(0, 0, 0, 0)

        self.optToolbar = QToolBar(self)
        self.edit_layout.addWidget(self.optToolbar, 0, 0, 1, 2)

        self.formToolbar = QToolBar(self)
        self.edit_layout.addWidget(self.formToolbar, 1, 0, 1, 2)

        self.titlelabel = QLabel(self)
        self.titlelabel.setObjectName("entry_titlelabel")
        self.titlelabel.setText("Title:")
        self.edit_layout.addWidget(self.titlelabel, 2, 0, 1, 1)

        self.titletext = EntryTitleText(self)
        self.titletext.setObjectName("entry_titletext")
        self.titletext.setMaxLength(255)
        self.edit_layout.addWidget(self.titletext, 2, 1, 1, 1)

        self.bodytext = QTextEdit(self)
        self.bodytext.setObjectName("entry_bodytext")
        self.edit_layout.addWidget(self.bodytext, 3, 0, 1, 2)

        self.initActions()
        self.initToolbars()

    def initActions(self):
        self.act_aligncenter = QAction(QIcon(':/align-center'),
                                       'Align Center',
                                       self,
                                       statusTip='Align text to center of entry',
                                       triggered=self.alignCenter)

        self.act_alignjustify = QAction(QIcon(':/align-justify'),
                                        'Align Justify',
                                        self,
                                        statusTip='Align text to justify the width of the entry',
                                        triggered=self.alignJustify)

        self.act_alignleft = QAction(QIcon(':/align-left'),
                                     'Align Left',
                                     self,
                                     statusTip='Align text to left of entry',
                                     triggered=self.alignLeft)

        self.act_alignright = QAction(QIcon(':/align-right'),
                                      'Align Right',
                                      self,
                                      statusTip='Align text to right of entry',
                                      triggered=self.alignRight)

        self.act_bold = QAction(QIcon(':/font-bold'),
                                '&Bold',
                                self,
                                shortcut='Ctrl+B',
                                statusTip='Bold text',
                                triggered=self.bold)

        self.act_bullet = QAction(QIcon(':/list-bullet'),
                                  '&Bullet List',
                                  self,
                                  shortcut='Ctrl+Shift+B',
                                  statusTip='Insert bullet list into entry',
                                  triggered=self.bulletList)

        self.act_copy = QAction(QIcon(':/text-copy'),
                                'C&opy',
                                self,
                                shortcut='Ctrl+C',
                                statusTip='Copy selected text to clipboard',
                                triggered=self.bodytext.copy)

        self.act_cut = QAction(QIcon(':/text-cut'),
                              'C&ut',
                              self,
                              shortcut='Ctrl+X',
                              statusTip='Move selected text to clipboard',
                              triggered=self.bodytext.cut)

        self.act_dedent = QAction(QIcon(':/text-dedent'),
                                  'Dedent',
                                  self,
                                  statusTip='Dedent text selection',
                                  triggered=self.dedent)

        self.act_fontback = QAction(QIcon(':/color-back'),
                                    'Back&ground Color',
                                    self,
                                    statusTip='Change background color',
                                    triggered=self.changeFontBack)

        self.act_fontfront = QAction(QIcon(':/color-front'),
                                     '&Font Color',
                                     self,
                                     statusTip='Change font color',
                                     triggered=self.changeFontFront)

        self.act_indent = QAction(QIcon(':/text-indent'),
                                  'Indent',
                                  self,
                                  statusTip='Indent text selection',
                                  triggered=self.indent)

        self.act_italics = QAction(QIcon(':/font-italics'),
                                   '&Italics',
                                   self,
                                   shortcut='Ctrl+I',
                                   statusTip='Italics text',
                                   triggered=self.italics)

        self.act_number = QAction(QIcon(':/list-number'),
                                  '&Numbered List',
                                  self,
                                  shortcut='Ctrl+Shift+L',
                                  statusTip='Insert numbered list into entry',
                                  triggered=self.numberedList)

        self.act_paste = QAction(QIcon(':/text-paste'),
                                 'P&aste',
                                 self,
                                 shortcut='Ctrl+V',
                                 statusTip='Paste text from clipboard',
                                 triggered=self.bodytext.paste)

        self.act_redo = QAction(QIcon(':/text-redo'),
                                '&Redo',
                                self,
                                shortcut='Ctrl+Y',
                                statusTip='Redo actions undone',
                                triggered=self.bodytext.redo)

        self.act_strike = QAction(QIcon(':/font-strike'),
                                  '&Strikethrough',
                                  self,
                                  statusTip='Strikethrough text',
                                  triggered=self.strikethrough)

        self.act_subscript = QAction(QIcon(':/font-subscript'),
                                     '&Subscript',
                                     self,
                                     statusTip='Subscript text',
                                     triggered=self.subscript)

        self.act_superscript = QAction(QIcon(':/font-superscript'),
                                       '&Superscript',
                                       self,
                                       statusTip='Superscript text',
                                       triggered=self.superscript)

        self.act_underline = QAction(QIcon(':/font-underline'),
                                     '&Underline',
                                     self,
                                     shortcut='Ctrl+U',
                                     statusTip='Underline text',
                                     triggered=self.underline)

        self.act_undo = QAction(QIcon(':/text-undo'),
                                '&Undo',
                                self,
                                shortcut='Ctrl+Z',
                                statusTip='Undo last action',
                                triggered=self.bodytext.undo)

    def initToolbars(self):
        self.optToolbar.setIconSize(QSize(24, 24))

        self.optToolbar.addAction(self.act_cut)
        self.optToolbar.addAction(self.act_copy)
        self.optToolbar.addAction(self.act_paste)
        self.optToolbar.addAction(self.act_undo)
        self.optToolbar.addAction(self.act_redo)
        self.optToolbar.addSeparator()
        self.optToolbar.addAction(self.act_bullet)
        self.optToolbar.addAction(self.act_number)

        self.formToolbar.setIconSize(QSize(24, 24))

        self.fontname = QFontComboBox(self)
        self.fontname.setEditable(False)
        self.fontname.currentFontChanged.connect(self.changeFont)

        self.fontsize = QComboBox(self)
        self.fontsize.setEditable(True)
        self.fontsize.setMinimumContentsLength(3)
        self.fontsize.activated.connect(self.changeFontSize)
        default_sizes = ['6','7','8','9','10','11','12','13','14','15','16',
                         '18','20','22','24','26','28','32','36','40','44','48',
                         '54','60','66','72','80','88','96']
        for s in default_sizes:
            self.fontsize.addItem(s)

        self.formToolbar.addWidget(self.fontname)
        self.formToolbar.addWidget(self.fontsize)
        self.formToolbar.addSeparator()
        self.formToolbar.addAction(self.act_fontfront)
        self.formToolbar.addAction(self.act_fontback)
        self.formToolbar.addSeparator()
        self.formToolbar.addAction(self.act_bold)
        self.formToolbar.addAction(self.act_italics)
        self.formToolbar.addAction(self.act_underline)
        self.formToolbar.addAction(self.act_strike)
        self.formToolbar.addAction(self.act_subscript)
        self.formToolbar.addAction(self.act_superscript)
        self.formToolbar.addSeparator()
        self.formToolbar.addAction(self.act_alignleft)
        self.formToolbar.addAction(self.act_aligncenter)
        self.formToolbar.addAction(self.act_alignright)
        self.formToolbar.addAction(self.act_alignjustify)
        self.formToolbar.addSeparator()
        self.formToolbar.addAction(self.act_indent)
        self.formToolbar.addAction(self.act_dedent)

    def bulletList(self):
        cursor = self.bodytext.textCursor()
        cursor.insertList(QTextListFormat.ListDisc)

    def numberedList(self):
        cursor = self.bodytext.textCursor()
        cursor.insertList(QTextListFormat.ListDecimal)

    def changeFont(self, font):
        self.bodytext.setCurrentFont(font)

    def changeFontBack(self):
        color = QColorDialog.getColor()
        self.bodytext.setTextBackgroundColor(color)

    def changeFontFront(self):
        color = QColorDialog.getColor()
        self.bodytext.setTextColor(color)

    def changeFontSize(self, fontsize):
        self.bodytext.setFontPointSize(int(fontsize))

    def bold(self):
        if self.bodytext.fontWeight() == QFont.Bold:
            self.bodytext.setFontWeight(QFont.Normal)
        else:
            self.bodytext.setFontWeight(QFont.Bold)

    def italics(self):
        state = self.bodytext.fontItalic()
        self.bodytext.setFontItalic(not state)

    def underline(self):
        state = self.bodytext.fontUnderline()
        self.bodytext.setFontUnderline(not state)

    def strikethrough(self):
        textformat = self.bodytext.currentCharFormat()
        textformat.setFontStrikeOut(not textformat.fontStrikeOut())
        self.bodytext.setCurrentCharFormat(textformat)

    def subscript(self):
        textformat = self.bodytext.currentCharFormat()
        align = textformat.verticalAlignment()

        if align == QTextCharFormat.AlignNormal:
            textformat.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        else:
            textformat.setVerticalAlignment(QTextCharFormat.AlignNormal)

        self.bodytext.setCurrentCharFormat(textformat)

    def superscript(self):
        textformat = self.bodytext.currentCharFormat()
        align = textformat.verticalAlignment()

        if align == QTextCharFormat.AlignNormal:
            textformat.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        else:
            textformat.setVerticalAlignment(QTextCharFormat.AlignNormal)

        self.bodytext.setCurrentCharFormat(textformat)

    def alignCenter(self):
        self.bodytext.setAlignment(Qt.AlignCenter)

    def alignJustify(self):
        self.bodytext.setAlignment(Qt.AlignJustify)

    def alignLeft(self):
        self.bodytext.setAlignment(Qt.AlignLeft)

    def alignRight(self):
        self.bodytext.setAlignment(Qt.AlignRight)

    def indent(self):
        cursor = self.bodytext.textCursor()

        if cursor.hasSelection():
            temp = cursor.blockNumber()
            cursor.setPosition(cursor.anchor())
            diff = cursor.blockNumber() - temp
            if diff > 0:
                direction = QTextCursor.Up
            else:
                direction = QTextCursor.Down

            for line in range(abs(diff) + 1):
                cursor.movePosition(QTextCursor.StartOfLine)
                cursor.insertText('\t')
                cursor.movePosition(direction)
        else:
            cursor.insertText('\t')

    def handleDedent(self, cursor):
        cursor.movePosition(QTextCursor.StartOfLine)
        line = cursor.block().text()
        if line.startswith('\t'):
            cursor.deleteChar()
        else:
            for char in line[:8]:
                if char != ' ':
                    break
                cursor.deleteChar()

    def dedent(self):
        cursor = self.bodytext.textCursor()

        if cursor.hasSelection():
            temp = cursor.blockNumber()
            cursor.setPosition(cursor.anchor())
            diff = cursor.blockNumber() - temp
            if diff > 0:
                direction = QTextCursor.Up
            else:
                direction = QTextCursor.Down

            for line in range(abs(diff) + 1):
                self.handleDedent(cursor)
                cursor.movePosition(direction)
        else:
            self.handleDedent(cursor)


class EntryView(QWidget):
    '''Widget for displaying the entry in a read-only context.'''
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setObjectName("entry_viewpage")

        self.view_layout = QVBoxLayout(self)
        self.view_layout.setObjectName("view_layout")
        self.view_layout.setSpacing(0)
        self.view_layout.setContentsMargins(0, 0, 0, 0)

        self.viewer = QWebView(self)
        self.viewer.setObjectName("entry_viewer")
        self.viewer.setUrl(QUrl("about:blank"))
        self.view_layout.addWidget(self.viewer)


class EntryWidget(QWidget):
    '''Widget that combines both the EntryEdit and EntryView widgets so that
       they can be toggled back and forth.'''
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.setObjectName("main_entry")

        self.entry_widget_layout = QVBoxLayout(self)
        self.entry_widget_layout.setObjectName("entry_widget_layout")
        self.entry_widget_layout.setSpacing(0)
        self.entry_widget_layout.setContentsMargins(4, 0, 0, 0)

        self.toolbar = QToolBar()
        self.entry_widget_layout.addWidget(self.toolbar)

        self.entry_widget = QStackedWidget(self)
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
        self.act_edit = QAction(QIcon(':/entry-edit'),
                                '&Edit Entry',
                                self,
                                statusTip='Changes the mode to edit your journal entries',
                                triggered=self.toggleEntry)
        self.act_edit.setVisible(False)

        self.act_preview = QAction(QIcon(':/entry-printpreview'),
                                   '&Print Preview',
                                   self,
                                   shortcut='Ctrl+Shift+P',
                                   statusTip='Preview the current entry before printing',
                                   triggered=self.printPreviewEntry)

        self.act_print = QAction(QIcon(':/entry-print'),
                                 '&Print',
                                 self,
                                 shortcut='Ctrl+P',
                                 statusTip='Prints the current entry',
                                 triggered=self.printEntry)

        self.act_view = QAction(QIcon(':/entry-view'),
                                '&Preview Entry',
                                self,
                                statusTip='Preview the current journal entry',
                                triggered=self.toggleEntry)

        self.entry_editpage.titletext.textChanged.connect(self.updateViewer)
        self.entry_editpage.bodytext.textChanged.connect(self.updateViewer)

    def initToolbars(self):
        self.toolbar.setIconSize(QSize(24, 24))
        # self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addAction(self.act_edit)
        self.toolbar.addAction(self.act_view)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.act_print)
        self.toolbar.addAction(self.act_preview)

    def printEntry(self):
        dialog = QPrintDialog()

        if dialog.exec_() == QDialog.Accepted:
            self.entry_viewpage.viewer.print_(dialog.printer())

    def printPreviewEntry(self):
        preview = QPrintPreviewDialog()
        preview.paintRequested.connect(lambda p: self.entry_viewpage.viewer.print_(p))
        preview.exec_()

    def reset(self):
        self.entry_editpage.titletext.clear()
        self.entry_editpage.bodytext.clear()
        self.entry_viewpage.viewer.setUrl(QUrl("about:blank"))

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

    @pyqtSlot()
    def updateViewer(self):
        title = self.entry_editpage.titletext.text()
        text = self.entry_editpage.bodytext.toHtml()

        # self.entry_viewpage.viewer.setHtml(text, self.baseUrl)
        self.entry_viewpage.viewer.setHtml('<h1>{0}</h1>{1}'.format(title,
                                                                    text))


class EntryCalendar(QDockWidget):
    '''A dock widget that handles showing which dates contain entries.'''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Entry Calendar')

        self.dock_widget = QWidget(self)
        self.dock_widget_layout = QVBoxLayout(self.dock_widget)
        self.dock_widget_layout.setSpacing(0)
        self.dock_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.dock_widget.setLayout(self.dock_widget_layout)

        self.toolbar = QToolBar()
        self.calendar = QCalendarWidget(self.dock_widget)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendar.sizePolicy().hasHeightForWidth())
        self.calendar.setSizePolicy(sizePolicy)

        spacer = QSpacerItem(0,
                             0,
                             QSizePolicy.MinimumExpanding,
                             QSizePolicy.MinimumExpanding)

        self.dock_widget_layout.addWidget(self.toolbar)
        self.dock_widget_layout.addWidget(self.calendar)
        self.dock_widget_layout.addItem(spacer)

        self.setWidget(self.dock_widget)

        self.topLevelChanged.connect(self.on_move)
        self.calendar.currentPageChanged.connect(self.showEntries)

        self.initActions()
        self.initToolbars()
        self.reset()

    def initActions(self):
        self.act_previous_entry = QAction(QIcon(':/cal-previous'),
                                          '&Previous Entry',
                                          self,
                                          statusTip='Go back to the previous journal entry',
                                          triggered=self.prevEntry)

        self.act_next_entry = QAction(QIcon(':/cal-next'),
                                      '&Next Entry',
                                      self,
                                      statusTip='Go to the next journal journal entry',
                                      triggered=self.nextEntry)

        self.act_today = QAction(QIcon(':/cal-today'),
                                 '&Today',
                                 self,
                                 statusTip='Go to today\'s entry',
                                 triggered=self.today)

    def initToolbars(self):
        self.toolbar.setIconSize(QSize(24, 24))
        # self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.toolbar.addAction(self.act_previous_entry)
        self.toolbar.addWidget(left_spacer)
        self.toolbar.addAction(self.act_today)
        self.toolbar.addWidget(right_spacer)
        self.toolbar.addAction(self.act_next_entry)

    def reset(self):
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

    @pyqtSlot()
    def on_move(self):
        if self.isFloating():
            self.resize(self.sizeHint())

    def prevEntry(self):
        selectdate = self.calendar.selectedDate().toPyDate()
        prevdate = self.parent().journal.previousDate(selectdate)
        if prevdate:
            self.calendar.setSelectedDate(QDate(prevdate.year,
                                                prevdate.month,
                                                prevdate.day))

    def nextEntry(self):
        selectdate = self.calendar.selectedDate().toPyDate()
        nextdate = self.parent().journal.nextDate(selectdate)
        if nextdate:
            self.calendar.setSelectedDate(QDate(nextdate.year,
                                                nextdate.month,
                                                nextdate.day))

    def today(self):
        self.calendar.setSelectedDate(QDate.currentDate())

    @pyqtSlot()
    def showEntries(self):
        pubdates = self.parent().journal.publishedDateList(self.calendar.monthShown(),
                                                           self.calendar.yearShown())
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        dateformat = QTextCharFormat()
        dateformat.setFontWeight(QFont.Bold)

        for d in pubdates:
            pub = QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(pub, dateformat)


class EntryListModel(QAbstractTableModel):
    '''This model is customized for the Entry/Journal objects in a python list.'''
    def __init__(self, entries=[], parent=None):
        super().__init__(parent)
        self.__entries = entries
        self.columns = sorted(list(vars(Entry()).keys()))

    def columnCount(self, parent=QModelIndex()):
        return len(self.columns)

    def rowCount(self, parent=QModelIndex()):
        return len(self.__entries)

    def data(self, index, role):
        if index.isValid():
            if (role == Qt.DisplayRole) or (role == Qt.EditRole):
                attr_name = self.columns[index.column()]
                row = self.__entries[index.row()]
                return getattr(row, attr_name)
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            attr_name = self.columns[index.column()]
            row = self.__entries[index.row()]
            setattr(row, attr_name, value)
            setattr(row, '_date_modified', datetime.datetime.now())
            setattr(row, 'modified', True)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)

        sel_date = self.parent().dock_calendar.calendar.selectedDate().toPyDate()

        for i in range(rows):
            self.__entries.insert(position, Entry(date_published=sel_date))

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)

        for i in range(rows):
            obj = self.__entries[position]
            if obj.entry_id:
                index = self.__entries.index(obj)
                self.parent().journal.to_delete.append(self.__entries.pop(index))
            else:
                self.__entries.remove(obj)

        self.endRemoveRows()
        return True

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


class EntryFilterProxy(QSortFilterProxyModel):
    '''Filter entries based on date, showing the correct ones in EntryList.'''
    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow,
                                         self.filterKeyColumn(),
                                         sourceParent)
        data = self.sourceModel().data(index, role=Qt.DisplayRole)
        return (self.filterRegExp().indexIn(data.strftime('%Y-%m-%d')) >= 0)


class EntryList(QDockWidget):
    '''A dockwidget that displays a list of entries for a given date referenced
       by the EntryCalendar.'''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Entry List')

        self.dock_widget = QWidget(self)
        self.dock_widget_layout = QVBoxLayout(self.dock_widget)
        self.dock_widget_layout.setSpacing(0)
        self.dock_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.toolbar = QToolBar()

        self.entrylist = QListView(self.dock_widget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.entrylist.sizePolicy().hasHeightForWidth())
        self.entrylist.setSizePolicy(sizePolicy)

        self.dock_widget_layout.addWidget(self.toolbar)
        self.dock_widget_layout.addWidget(self.entrylist)

        self.setWidget(self.dock_widget)

        self.initActions()
        self.initToolbars()

    def initActions(self):
        self.act_new_entry = QAction(QIcon(':/entry-new'),
                                     '&New',
                                     self,
                                     statusTip='Create a new entry for this date',
                                     triggered=self.parent().new_entry)

        self.act_delete_entry = QAction(QIcon(':/entry-remove'),
                                        '&Delete',
                                        self,
                                        statusTip='Delete the selected entry',
                                        triggered=self.parent().delete_entry)

    def initToolbars(self):
        self.toolbar.setIconSize(QSize(24, 24))

        self.toolbar.addAction(self.act_new_entry)
        self.toolbar.addAction(self.act_delete_entry)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setObjectName("main_window")
        self.setWindowTitle('Mentarius')
        self.resize(1200, 800)

        self.main_widget = QWidget(self)
        self.main_widget.setObjectName("main_widget")
        self.main_widget_layout = QVBoxLayout(self.main_widget)
        self.main_widget_layout.setObjectName("main_widget_layout")
        self.main_widget_layout.setSpacing(0)
        self.main_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.main_entry = EntryWidget(self.main_widget)
        self.main_entry.setEnabled(False)

        self.main_widget_layout.addWidget(self.main_entry)

        self.setCentralWidget(self.main_widget)

        self.journal = Journal()

        self.initActions()
        self.initDocks()
        self.initMenus()
        self.initModels()
        self.initStatusBar()
        self.resetAll()

        QMetaObject.connectSlotsByName(self)

    def initActions(self):
        # self.action_exit = QAction(main_window)
        # icon = QIcon()
        # icon.addPixmap(QtGui.QPixmap(":/application-exit"), QIcon.Normal, QIcon.Off)
        # self.action_exit.setIcon(icon)
        # self.action_exit.setObjectName("action_exit")

        self.act_about = QAction('About',
                                 self,
                                 statusTip='About Mentarius',
                                 triggered=self.about)

        self.act_aboutQt = QAction('About Qt',
                                   self,
                                   statusTip='About Qt',
                                   triggered=self.aboutQt)

        self.act_new = QAction(QIcon(':/journal-new'),
                               '&New',
                               self,
                               shortcut='Ctrl+N',
                               statusTip='New Journal',
                               triggered=self.new_journal)

        self.act_open = QAction(QIcon(':/journal-open'),
                                '&Open',
                                self,
                                shortcut='Ctrl+O',
                                statusTip='Open Journal',
                                triggered=self.open_journal)

        self.act_quit = QAction(QIcon(':/app-exit'),
                                '&Quit',
                                self,
                                shortcut='Ctrl+Q',
                                statusTip='Quit Mentarius',
                                triggered=self.close)

        self.act_save = QAction(QIcon(':/journal-save'),
                                '&Save',
                                self,
                                shortcut='Ctrl+S',
                                statusTip='Save Journal',
                                triggered=self.save_journal)

    def initDocks(self):
        self.dock_calendar = EntryCalendar(self)
        self.addDockWidget(Qt.DockWidgetArea(Qt.RightDockWidgetArea),
                           self.dock_calendar)

        self.dock_entrylist = EntryList(self)
        self.addDockWidget(Qt.DockWidgetArea(Qt.RightDockWidgetArea),
                           self.dock_entrylist)

    def initMenus(self):
        self.main_menubar = QMenuBar(self)
        self.main_menubar.setObjectName("main_menubar")

        self.menu_file = QMenu(self.main_menubar)
        self.menu_file.setObjectName("menu_file")
        self.menu_file.setTitle("&File")
        self.menu_file.addAction(self.act_new)
        self.menu_file.addAction(self.act_open)
        self.menu_file.addAction(self.act_save)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.act_quit)

        self.menu_view = QMenu(self.main_menubar)
        self.menu_view.setObjectName("menu_view")
        self.menu_view.setTitle("&View")
        self.menu_view.addAction(self.dock_calendar.toggleViewAction())
        self.menu_view.addAction(self.dock_entrylist.toggleViewAction())

        self.menu_help = QMenu(self.main_menubar)
        self.menu_help.setObjectName("menu_help")
        self.menu_help.setTitle("&Help")
        self.menu_help.addAction(self.act_aboutQt)
        self.menu_help.addAction(self.act_about)

        self.main_menubar.addMenu(self.menu_file)
        self.main_menubar.addMenu(self.menu_view)
        self.main_menubar.addMenu(self.menu_help)

        self.setMenuBar(self.main_menubar)

    def initModels(self):
        self.entrymodel = EntryListModel(self.journal.entries, self)
        self.entrymodel.rowsInserted.connect(self.dock_calendar.showEntries)
        self.entrymodel.rowsMoved.connect(self.dock_calendar.showEntries)
        self.entrymodel.rowsRemoved.connect(self.dock_calendar.showEntries)

        bodycol = self.entrymodel.columns.index('_body')
        titlecol = self.entrymodel.columns.index('_title')
        datepubcol = self.entrymodel.columns.index('_date_published')

        self.entryproxy = EntryFilterProxy(self)
        self.entryproxy.setDynamicSortFilter(True)
        self.entryproxy.setSourceModel(self.entrymodel)
        self.entryproxy.setFilterKeyColumn(datepubcol)

        self.entrymapper = QDataWidgetMapper(self)
        self.entrymapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        self.entrymapper.setModel(self.entryproxy)
        self.entrymapper.addMapping(self.main_entry.entry_editpage.titletext,
                                    titlecol)
        self.entrymapper.addMapping(self.main_entry.entry_editpage.bodytext,
                                    bodycol)

        self.dock_calendar.calendar.selectionChanged.connect(self.filterDates)

        self.dock_entrylist.entrylist.setModel(self.entryproxy)
        self.dock_entrylist.entrylist.setModelColumn(titlecol)
        self.dock_entrylist.entrylist.selectionModel().selectionChanged.connect(self.updateEntryWidget)

        self.main_entry.entry_editpage.titletext.titlechanged.connect(self.entrymapper.submit)

    def initStatusBar(self):
        self.main_statusbar = QStatusBar(self)
        self.main_statusbar.setObjectName("main_statusbar")
        self.main_statusbar.showMessage("Ready.")

        self.setStatusBar(self.main_statusbar)

    def about(self):
        QMessageBox.about(self,
                          'About Mentarius',
                          'A personal journal/notebook written in Python')

    def aboutQt(self):
        QMessageBox.aboutQt(self, 'About Qt')

    @pyqtSlot(QItemSelection)
    def updateEntryWidget(self, item=QItemSelection()):
        # PyQt converts QList to python 'lists'.
        if not item.indexes():
            self.main_entry.reset()
            self.main_entry.setEnabled(False)
        else:
            self.entrymapper.submit()
            self.main_entry.setEnabled(True)
            self.entrymapper.setCurrentModelIndex(item.indexes()[0])

    def new_entry(self):
        newrow = self.entrymodel.rowCount()
        titlecol = self.entrymodel.columns.index('_title')
        self.entrymapper.submit()
        self.entrymodel.insertRows(newrow, 1)
        newindex = self.entryproxy.mapFromSource(self.entrymodel.index(newrow,
                                                                       titlecol))
        self.dock_entrylist.entrylist.setCurrentIndex(newindex)
        self.entrymapper.setCurrentModelIndex(newindex)

    def delete_entry(self):
        index = self.entryproxy.mapToSource(self.dock_entrylist.entrylist.currentIndex())
        self.entrymapper.submit()
        self.entrymodel.removeRows(index.row(), 1)
        self.entrymapper.setCurrentModelIndex(self.dock_entrylist.entrylist.currentIndex())

    def new_journal(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Create New Journal')

        if not filename:
            return

        if not filename.endswith('.mentdb'):
            filename += '.mentdb'

        self.journal.new(filename)
        self.resetAll()

    def open_journal(self):
        filename, _ = QFileDialog.getOpenFileName(self,
                                                  'Open Journal',
                                                  '.',
                                                  '(*.mentdb)')

        if not filename:
            return

        self.journal.load(filename)
        self.initModels()
        self.dock_calendar.showEntries()

    def resetAll(self):
        self.main_entry.reset()
        self.dock_calendar.reset()

    def save_journal(self):
        self.journal.save()

    @pyqtSlot()
    def filterDates(self):
        self.entrymapper.submit()
        sel_date = self.dock_calendar.calendar.selectedDate()
        self.entryproxy.setFilterRegExp(sel_date.toString(Qt.ISODate))
        if self.entryproxy.rowCount() > 0:
            titlecol = self.entrymodel.columns.index('_title')
            firstindex = self.entryproxy.index(0, titlecol)
            self.dock_entrylist.entrylist.setCurrentIndex(firstindex)
            self.entrymapper.setCurrentModelIndex(firstindex)


if __name__ == '__main__':
    import sys

    discover_plugins(['plugins'])

    app = QApplication(sys.argv)
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
