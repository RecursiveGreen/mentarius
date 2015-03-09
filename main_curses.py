#!/usr/bin/env python3

import sys
import curses
from curses import ascii

from journal import Entry, Journal

CMD_NOOP = 0
CMD_QUIT = 1
CMD_SELECT_NEXT = 2
CMD_SELECT_PREV = 3

class MentariusCursesDriver():

    window = None

    def __init__ (self):
        self.window = curses.initscr()
        curses.noecho()
        curses.raw()
        curses.curs_set(False)

    def cleanup (self):
        curses.noraw()
        curses.echo()
        curses.endwin()

    def clear(self):
        self.window.clear()

    def moveToOrigin(self):
        self.window.move(0, 0)

    def printHorizontalLine(self):
        self.window.addstr("-" * curses.COLS)

    def printEntryTitle(self, index, title, selected = False):
        self.window.move(index + 1, 0)
        if selected == True:
            self.window.addstr(title + "\n", curses.A_STANDOUT)
        else:
            self.window.addstr(title + "\n")

    def printStatusText(self, journal):
        self.window.addstr("viewing " + journal.name + "\n")

    def width(self):
        return curses.COLS

    def input(self):
        key = self.window.getkey()
        if key == ascii.ctrl("c"):
            return CMD_QUIT
        elif key == "j":
            return CMD_SELECT_NEXT
        elif key == "k":
            return CMD_SELECT_PREV
        return CMD_NOOP


class MentariusCurses():

    journal = None
    driver = None
    selected = -1

    def __init__(self):
        self.driver = MentariusCursesDriver()

    def usage(self):
        print("Usage: " + sys.argv[0] + " [JOURNAL FILE]")

    def handleArgs(self):
        numArgs = len(sys.argv)
        if numArgs == 1:
            self.journalOpen()
        elif numArgs == 2:
            self.journalOpen(sys.argv[1])
        else:
            self.usage()
            sys.exit(1)

    def formatEntryTitle(self, entry, width):
        s = ""
        s = s + "| "
        s = s + entry.title
        s2 = ""
        s2 = s2 + ": "
        s2 = s2 + entry.date_created.strftime("%c")
        sfill = " " * (width - (len(s) + len(s2)) - 1)
        return s + sfill + s2

    def selectFirst(self):
        if len(self.journal.entries) > 0:
            self.selected = 0

    def selectNext(self):
        selected = self.selected + 1
        if selected < len(self.journal.entries):
            self.selected = selected
        else:
            self.selectFirst()

    def selectLast(self):
        self.selected = len(self.journal.entries) - 1

    def selectPrev(self):
        selected = self.selected - 1
        if selected >= 0:
            self.selected = selected
        else:
            self.selectLast()

    def isSelected(self, entry):
        return self.journal.entries[self.selected].entry_id == entry.entry_id

    def journalOpen(self, filename = "journal.mentdb"):
        self.journal = Journal()
        self.journal.load(filename)
        self.selected = self.journal.entries[0].entry_id
        pass

    def redrawEntryTitle(self, index, entry):
        selected = self.isSelected(entry)
        width = self.driver.width()
        self.driver.printEntryTitle(index,
            self.formatEntryTitle(entry, width), selected)

    def redrawSelected(self, unselected, selected):
        entry = self.journal.entries[selected]
        self.redrawEntryTitle(selected, entry)
        entry = self.journal.entries[unselected]
        self.redrawEntryTitle(unselected, entry)

    def redraw(self):
        d = self.driver
        d.clear()
        d.moveToOrigin()
        d.printHorizontalLine()

        index = 0
        for entry in self.journal.entries:
            self.redrawEntryTitle(index, entry)
            index = index + 1

        d.printHorizontalLine()
        d.printStatusText(self.journal)

    def main(self):

        self.handleArgs()
        self.redraw()

        while True:
            cmd = self.driver.input()
            if cmd == CMD_QUIT:
                break
            elif cmd == CMD_SELECT_NEXT:
                unselected = self.selected
                self.selectNext()
                self.redrawSelected(unselected, self.selected)
            elif cmd == CMD_SELECT_PREV:
                unselected = self.selected
                self.selectPrev()
                self.redrawSelected(unselected, self.selected)

if __name__ == '__main__':
    try:
        mentarius = MentariusCurses()
        mentarius.main()
    finally:
        mentarius.driver.cleanup();
