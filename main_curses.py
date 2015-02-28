#!/usr/bin/env python3

import curses

class MentariusCurses():

    stdscr = None

    def __init__(self):
        pass
    
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
        self.stdscr.addstr(0, 0, "Hello.")
        self.stdscr.addstr(1, 0, "1")
        self.stdscr.addstr(2, 0, "2")
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
