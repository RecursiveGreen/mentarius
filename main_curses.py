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
