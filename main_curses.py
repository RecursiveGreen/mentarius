#!/usr/bin/env python3

import curses
from journal import Entry, Journal

class MentariusCurses():

    stdscr = None

    def __init__(self):
        self.journal = Journal()

    def displayEntryTitles(self, journal):
        for entry in journal.entries:
            self.stdscr.addstr("" 
                + entry.date_created.strftime("%c")
                + " - " + entry.title 
                + "\n")

    def cursesInit(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.nocbreak()

    def cursesTeardown(self):
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def cursesMain(self):

        self.stdscr.clear()

        journal = Journal()
        journal.load("test.mentdb")
        self.stdscr.addstr("-" * curses.COLS)
        self.displayEntryTitles(journal);
        self.stdscr.addstr("-" * curses.COLS)
        self.stdscr.addstr("viewing test.mentdb\n")
        self.stdscr.addstr("-" * curses.COLS)
        # self.stdscr.move(curses.LINES, curses.COLS)
        curses.curs_set(False)

        self.stdscr.getkey()

    def run(self):
        try:
            self.cursesInit()
            self.cursesMain()
        finally:
            self.cursesTeardown()

if __name__ == '__main__':
    mentarius = MentariusCurses()
    mentarius.run()
