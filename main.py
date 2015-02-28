#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sqlite3

from PyQt5 import QtCore, QtGui, QtPrintSupport, QtWidgets, QtWebKitWidgets
import icons

from journal import Entry, Journal

class EntryEdit(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.edit_layout = QtWidgets.QGridLayout(self)
        self.edit_layout.setObjectName("edit_layout")
        self.edit_layout.setContentsMargins(0, 0, 0, 0)

        self.optToolbar = QtWidgets.QToolBar(self)
        self.edit_layout.addWidget(self.optToolbar, 0, 0, 1, 2)

        self.formToolbar = QtWidgets.QToolBar(self)
        self.edit_layout.addWidget(self.formToolbar, 1, 0, 1, 2)

        self.titlelabel = QtWidgets.QLabel(self)
        self.titlelabel.setObjectName("entry_titlelabel")
        self.titlelabel.setText("Title:")
        self.edit_layout.addWidget(self.titlelabel, 2, 0, 1, 1)

        self.titletext = QtWidgets.QLineEdit(self)
        self.titletext.setObjectName("entry_titletext")
        self.titletext.setMaxLength(255)
        self.edit_layout.addWidget(self.titletext, 2, 1, 1, 1)

        self.bodytext = QtWidgets.QTextEdit(self)
        self.bodytext.setObjectName("entry_bodytext")
        self.edit_layout.addWidget(self.bodytext, 3, 0, 1, 2)

        self.initActions()
        self.initToolbars()

    def initActions(self):
        self.act_aligncenter = QtWidgets.QAction(QtGui.QIcon(':/align-center'),
                                                 'Align Center',
                                                 self,
                                                 statusTip='Align text to center of entry',
                                                 triggered=self.alignCenter)

        self.act_alignjustify = QtWidgets.QAction(QtGui.QIcon(':/align-justify'),
                                                  'Align Justify',
                                                  self,
                                                  statusTip='Align text to justify the width of the entry',
                                                  triggered=self.alignJustify)

        self.act_alignleft = QtWidgets.QAction(QtGui.QIcon(':/align-left'),
                                               'Align Left',
                                               self,
                                               statusTip='Align text to left of entry',
                                               triggered=self.alignLeft)

        self.act_alignright = QtWidgets.QAction(QtGui.QIcon(':/align-right'),
                                                'Align Right',
                                                self,
                                                statusTip='Align text to right of entry',
                                                triggered=self.alignRight)

        self.act_bold = QtWidgets.QAction(QtGui.QIcon(':/font-bold'),
                                          '&Bold',
                                          self,
                                          shortcut='Ctrl+B',
                                          statusTip='Bold text',
                                          triggered=self.bold)

        self.act_bullet = QtWidgets.QAction(QtGui.QIcon(':/list-bullet'),
                                            '&Bullet List',
                                            self,
                                            shortcut='Ctrl+Shift+B',
                                            statusTip='Insert bullet list into entry',
                                            triggered=self.bulletList)

        self.act_copy = QtWidgets.QAction(QtGui.QIcon(':/text-copy'),
                                          'C&opy',
                                          self,
                                          shortcut='Ctrl+C',
                                          statusTip='Copy selected text to clipboard',
                                          triggered=self.bodytext.copy)

        self.act_cut = QtWidgets.QAction(QtGui.QIcon(':/text-cut'),
                                         'C&ut',
                                         self,
                                         shortcut='Ctrl+X',
                                         statusTip='Move selected text to clipboard',
                                         triggered=self.bodytext.cut)

        self.act_dedent = QtWidgets.QAction(QtGui.QIcon(':/text-dedent'),
                                            'Dedent',
                                            self,
                                            statusTip='Dedent text selection',
                                            triggered=self.dedent)

        self.act_fontback = QtWidgets.QAction(QtGui.QIcon(':/color-back'),
                                              'Back&ground Color',
                                              self,
                                              statusTip='Change background color',
                                              triggered=self.changeFontBack)

        self.act_fontfront = QtWidgets.QAction(QtGui.QIcon(':/color-front'),
                                               '&Font Color',
                                               self,
                                               statusTip='Change font color',
                                               triggered=self.changeFontFront)

        self.act_indent = QtWidgets.QAction(QtGui.QIcon(':/text-indent'),
                                            'Indent',
                                            self,
                                            statusTip='Indent text selection',
                                            triggered=self.indent)

        self.act_italics = QtWidgets.QAction(QtGui.QIcon(':/font-italics'),
                                             '&Italics',
                                             self,
                                             shortcut='Ctrl+I',
                                             statusTip='Italics text',
                                             triggered=self.italics)

        self.act_number = QtWidgets.QAction(QtGui.QIcon(':/list-number'),
                                            '&Numbered List',
                                            self,
                                            shortcut='Ctrl+Shift+L',
                                            statusTip='Insert numbered list into entry',
                                            triggered=self.numberedList)

        self.act_paste = QtWidgets.QAction(QtGui.QIcon(':/text-paste'),
                                           'P&aste',
                                           self,
                                           shortcut='Ctrl+V',
                                           statusTip='Paste text from clipboard',
                                           triggered=self.bodytext.paste)

        self.act_strike = QtWidgets.QAction(QtGui.QIcon(':/font-strike'),
                                            '&Strikethrough',
                                            self,
                                            statusTip='Strikethrough text',
                                            triggered=self.strikethrough)

        self.act_subscript = QtWidgets.QAction(QtGui.QIcon(':/font-subscript'),
                                               '&Subscript',
                                               self,
                                               statusTip='Subscript text',
                                               triggered=self.subscript)

        self.act_superscript = QtWidgets.QAction(QtGui.QIcon(':/font-superscript'),
                                                 '&Superscript',
                                                 self,
                                                 statusTip='Superscript text',
                                                 triggered=self.superscript)

        self.act_underline = QtWidgets.QAction(QtGui.QIcon(':/font-underline'),
                                               '&Underline',
                                               self,
                                               shortcut='Ctrl+U',
                                               statusTip='Underline text',
                                               triggered=self.underline)

        self.act_undo = QtWidgets.QAction(QtGui.QIcon(':/text-undo'),
                                          '&Undo',
                                          self,
                                          shortcut='Ctrl+Z',
                                          statusTip='Undo last action',
                                          triggered=self.bodytext.undo)

        self.act_redo = QtWidgets.QAction(QtGui.QIcon(':/text-redo'),
                                          '&Redo',
                                          self,
                                          shortcut='Ctrl+Y',
                                          statusTip='Redo actions undone',
                                          triggered=self.bodytext.redo)

    def initToolbars(self):
        self.optToolbar.setIconSize(QtCore.QSize(24, 24))

        self.optToolbar.addAction(self.act_cut)
        self.optToolbar.addAction(self.act_copy)
        self.optToolbar.addAction(self.act_paste)
        self.optToolbar.addAction(self.act_undo)
        self.optToolbar.addAction(self.act_redo)
        self.optToolbar.addSeparator()
        self.optToolbar.addAction(self.act_bullet)
        self.optToolbar.addAction(self.act_number)

        self.formToolbar.setIconSize(QtCore.QSize(24, 24))

        self.fontname = QtWidgets.QFontComboBox(self)
        self.fontname.setEditable(False)
        self.fontname.currentFontChanged.connect(self.changeFont)

        self.fontsize = QtWidgets.QComboBox(self)
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
        cursor.insertList(QtGui.QTextListFormat.ListDisc)

    def numberedList(self):
        cursor = self.bodytext.textCursor()
        cursor.insertList(QtGui.QTextListFormat.ListDecimal)

    def changeFont(self, font):
        self.bodytext.setCurrentFont(font)

    def changeFontBack(self):
        color = QtWidgets.QColorDialog.getColor()
        self.bodytext.setTextBackgroundColor(color)

    def changeFontFront(self):
        color = QtWidgets.QColorDialog.getColor()
        self.bodytext.setTextColor(color)

    def changeFontSize(self, fontsize):
        self.bodytext.setFontPointSize(int(fontsize))

    def bold(self):
        if self.bodytext.fontWeight() == QtGui.QFont.Bold:
            self.bodytext.setFontWeight(QtGui.QFont.Normal)
        else:
            self.bodytext.setFontWeight(QtGui.QFont.Bold)

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

        if align == QtGui.QTextCharFormat.AlignNormal:
            textformat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSubScript)
        else:
            textformat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        self.bodytext.setCurrentCharFormat(textformat)

    def superscript(self):
        textformat = self.bodytext.currentCharFormat()
        align = textformat.verticalAlignment()

        if align == QtGui.QTextCharFormat.AlignNormal:
            textformat.setVerticalAlignment(QtGui.QTextCharFormat.AlignSuperScript)
        else:
            textformat.setVerticalAlignment(QtGui.QTextCharFormat.AlignNormal)

        self.bodytext.setCurrentCharFormat(textformat)

    def alignCenter(self):
        self.bodytext.setAlignment(QtCore.Qt.AlignCenter)

    def alignJustify(self):
        self.bodytext.setAlignment(QtCore.Qt.AlignJustify)

    def alignLeft(self):
        self.bodytext.setAlignment(QtCore.Qt.AlignLeft)

    def alignRight(self):
        self.bodytext.setAlignment(QtCore.Qt.AlignRight)

    def indent(self):
        cursor = self.bodytext.textCursor()

        if cursor.hasSelection():
            temp = cursor.blockNumber()
            cursor.setPosition(cursor.anchor())
            diff = cursor.blockNumber() - temp
            if diff > 0:
                direction = QtGui.QTextCursor.Up
            else:
                direction = QtGui.QTextCursor.Down

            for line in range(abs(diff) + 1):
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                cursor.insertText('\t')
                cursor.movePosition(direction)
        else:
            cursor.insertText('\t')

    def handleDedent(self, cursor):
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
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
                direction = QtGui.QTextCursor.Up
            else:
                direction = QtGui.QTextCursor.Down

            for line in range(abs(diff) + 1):
                self.handleDedent(cursor)
                cursor.movePosition(direction)
        else:
            self.handleDedent(cursor)


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
        self.act_edit = QtWidgets.QAction(QtGui.QIcon(':/entry-edit'),
                                          '&Edit Entry',
                                          self,
                                          statusTip='Changes the mode to edit your journal entries',
                                          triggered=self.toggleEntry)
        self.act_edit.setVisible(False)

        self.act_preview = QtWidgets.QAction(QtGui.QIcon(':/entry-printpreview'),
                                             '&Print Preview',
                                             self,
                                             shortcut='Ctrl+Shift+P',
                                             statusTip='Preview the current entry before printing',
                                             triggered=self.printPreviewEntry)

        self.act_print = QtWidgets.QAction(QtGui.QIcon(':/entry-print'),
                                           '&Print',
                                           self,
                                           shortcut='Ctrl+P',
                                           statusTip='Prints the current entry',
                                           triggered=self.printEntry)

        self.act_view = QtWidgets.QAction(QtGui.QIcon(':/entry-view'),
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
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Expanding)

        self.toolbar.addAction(self.act_edit)
        self.toolbar.addAction(self.act_view)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(self.act_print)
        self.toolbar.addAction(self.act_preview)

    def printEntry(self):
        dialog = QtPrintSupport.QPrintDialog()

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.entry_viewpage.viewer.print_(dialog.printer())

    def printPreviewEntry(self):
        preview = QtPrintSupport.QPrintPreviewDialog()
        preview.paintRequested.connect(lambda p: self.entry_viewpage.viewer.print_(p))
        preview.exec_()

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
        text = self.entry_editpage.bodytext.toHtml()

        # self.entry_viewpage.viewer.setHtml(text, self.baseUrl)
        self.entry_viewpage.viewer.setHtml('<h1>{0}</h1>{1}'.format(title,
                                                                    text))

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

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendar.sizePolicy().hasHeightForWidth())
        self.calendar.setSizePolicy(sizePolicy)

        spacer = QtWidgets.QSpacerItem(0,
                                       0,
                                       QtWidgets.QSizePolicy.MinimumExpanding,
                                       QtWidgets.QSizePolicy.MinimumExpanding)

        self.dock_widget_layout.addWidget(self.toolbar)
        self.dock_widget_layout.addWidget(self.calendar)
        self.dock_widget_layout.addItem(spacer)

        self.setWidget(self.dock_widget)

        self.topLevelChanged.connect(self.on_move)

        self.initActions()
        self.initToolbars()
        self.reset()

    def initActions(self):
        self.act_previous_entry = QtWidgets.QAction(QtGui.QIcon(':/cal-previous'),
                                                    '&Previous Entry',
                                                    self,
                                                    statusTip='Go back to the previous journal entry',
                                                    triggered=self.prevEntry)

        self.act_next_entry = QtWidgets.QAction(QtGui.QIcon(':/cal-next'),
                                                '&Next Entry',
                                                self,
                                                statusTip='Go to the next journal journal entry',
                                                triggered=self.nextEntry)

        self.act_today = QtWidgets.QAction(QtGui.QIcon(':/cal-today'),
                                           '&Today',
                                           self,
                                           statusTip='Go to today\'s entry',
                                           triggered=self.today)

    def initToolbars(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        # self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        left_spacer = QtWidgets.QWidget()
        left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Expanding)
        right_spacer = QtWidgets.QWidget()
        right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)

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

    @QtCore.pyqtSlot()
    def showEntries(self):
        pubdates = self.parent().journal.publishedDateList(self.calendar.monthShown(),
                                                           self.calendar.yearShown())
        self.calendar.setDateTextFormat(QtCore.QDate(), QtGui.QTextCharFormat())

        dateformat = QtGui.QTextCharFormat()
        dateformat.setFontWeight(QtGui.QFont.Bold)

        for d in pubdates:
            pub = QtCore.QDate(d.year, d.month, d.day)
            self.calendar.setDateTextFormat(pub, dateformat)


class EntryListModel(QtCore.QAbstractTableModel):
    def __init__(self, entries=[], parent=None):
        super().__init__(parent)
        self.__entries = entries
        self.columns = sorted(list(vars(Entry()).keys()))

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.columns)

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self.__entries)

    def data(self, index, role):
        if index.isValid():
            if (role == QtCore.Qt.DisplayRole) or (role == QtCore.Qt.EditRole):
                attr_name = self.columns[index.column()]
                row = self.__entries[index.row()]
                return getattr(row, attr_name)
        return None

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and role == QtCore.Qt.EditRole:
            attr_name = self.columns[index.column()]
            row = self.__entries[index.row()]
            setattr(row, attr_name, value)
            setattr(row, 'date_modified', datetime.datetime.now())
            setattr(row, 'modified', True)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)

        sel_date = self.parent().dock_calendar.calendar.selectedDate().toPyDate()

        for i in range(rows):
            self.__entries.insert(position, Entry(date_published=sel_date))

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
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
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable


class EntryFilterProxy(QtCore.QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow, sourceParent):
        index = self.sourceModel().index(sourceRow,
                                         self.filterKeyColumn(),
                                         sourceParent)
        data = self.sourceModel().data(index, role=QtCore.Qt.DisplayRole)
        return (self.filterRegExp().indexIn(data.strftime('%Y-%m-%d')) >= 0)


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
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Expanding)
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
        self.act_new_entry = QtWidgets.QAction(QtGui.QIcon(':/entry-new'),
                                               '&New',
                                               self,
                                               statusTip='Create a new entry for this date',
                                               triggered=self.parent().new_entry)

        self.act_delete_entry = QtWidgets.QAction(QtGui.QIcon(':/entry-remove'),
                                                  '&Delete',
                                                  self,
                                                  statusTip='Delete the selected entry',
                                                  triggered=self.parent().delete_entry)

    def initToolbars(self):
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        # self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # left_spacer = QtWidgets.QWidget()
        # left_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # right_spacer = QtWidgets.QWidget()
        # right_spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.toolbar.addAction(self.act_new_entry)
        self.toolbar.addAction(self.act_delete_entry)
        # self.toolbar.addWidget(left_spacer)

    def reset(self):
        pass
        # self.entrylist_model.clear()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setObjectName("main_window")
        self.setWindowTitle('Mentarius')
        self.resize(1200, 800)

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

        self.act_about = QtWidgets.QAction('About',
                                           self,
                                           statusTip='About Mentarius',
                                           triggered=self.about)

        self.act_aboutQt = QtWidgets.QAction('About Qt',
                                             self,
                                             statusTip='About Qt',
                                             triggered=self.aboutQt)

        self.act_new = QtWidgets.QAction(QtGui.QIcon(':/journal-new'),
                                         '&New',
                                         self,
                                         shortcut='Ctrl+N',
                                         statusTip='New Journal',
                                         triggered=self.new_journal)

        self.act_open = QtWidgets.QAction(QtGui.QIcon(':/journal-open'),
                                          '&Open',
                                          self,
                                          shortcut='Ctrl+O',
                                          statusTip='Open Journal',
                                          triggered=self.open_journal)

        self.act_quit = QtWidgets.QAction(QtGui.QIcon(':/app-exit'),
                                          '&Quit',
                                          self,
                                          shortcut='Ctrl+Q',
                                          statusTip='Quit Mentarius',
                                          triggered=self.close)

        self.act_save = QtWidgets.QAction(QtGui.QIcon(':/journal-save'),
                                          '&Save',
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

        self.menu_help = QtWidgets.QMenu(self.main_menubar)
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

        bodycol = self.entrymodel.columns.index('body')
        titlecol = self.entrymodel.columns.index('title')
        datepubcol = self.entrymodel.columns.index('date_published')

        self.entryproxy = EntryFilterProxy(self)
        self.entryproxy.setDynamicSortFilter(True)
        self.entryproxy.setSourceModel(self.entrymodel)
        self.entryproxy.setFilterKeyColumn(datepubcol)

        self.entrymapper = QtWidgets.QDataWidgetMapper(self)
        self.entrymapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.ManualSubmit)
        self.entrymapper.setModel(self.entryproxy)
        self.entrymapper.addMapping(self.main_entry.entry_editpage.titletext,
                                    titlecol)
        self.entrymapper.addMapping(self.main_entry.entry_editpage.bodytext,
                                    bodycol)

        self.dock_calendar.calendar.selectionChanged.connect(self.filterDates)

        self.dock_entrylist.entrylist.setModel(self.entryproxy)
        self.dock_entrylist.entrylist.setModelColumn(titlecol)
        self.dock_entrylist.entrylist.activated.connect(self.updateEntry)
        self.dock_entrylist.entrylist.clicked.connect(self.updateEntry)

    def initStatusBar(self):
        self.main_statusbar = QtWidgets.QStatusBar(self)
        self.main_statusbar.setObjectName("main_statusbar")
        self.main_statusbar.showMessage("Ready.")

        self.setStatusBar(self.main_statusbar)

    def about(self):
        QtWidgets.QMessageBox.about(self,
                                    'About Mentarius',
                                    'A personal journal/notebook written in Python')

    def aboutQt(self):
        QtWidgets.QMessageBox.aboutQt(self, 'About Qt')

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def updateEntry(self, index=QtCore.QModelIndex()):
        self.entrymapper.submit()
        if index.isValid():
            self.entrymapper.setCurrentModelIndex(index)
        else:
            self.entrymapper.setCurrentModelIndex(self.dock_entrylist.entrylist.currentIndex())

    def new_entry(self):
        newrow = self.entrymodel.rowCount()
        titlecol = self.entrymodel.columns.index('title')
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
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                            'Create New Journal')

        if not filename:
            return

        if not filename.endswith('.mentdb'):
            filename += '.mentdb'

        self.journal.new(filename)
        self.resetAll()

    def open_journal(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,
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
        self.dock_entrylist.reset()

    def save_journal(self):
        self.journal.save()

    def filterDates(self):
        sel_date = self.dock_calendar.calendar.selectedDate()
        self.entryproxy.setFilterRegExp(sel_date.toString(QtCore.Qt.ISODate))


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
