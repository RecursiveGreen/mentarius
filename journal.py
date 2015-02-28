#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

class Entry(object):
    def __init__(self,
                 date_created=datetime.datetime.now(),
                 date_modified=datetime.datetime.now(),
                 date_published=datetime.date.today(),
                 entry_id=None,
                 title='',
                 body=''):
        self.date_created = date_created
        self.date_modified = date_modified
        self.date_published = date_published
        self.entry_id = entry_id
        self.title = title
        self.body = body

        self.modified = False

    def __repr__(self):
        if self.title:
            return self.title
        else:
            return '(Untitled Entry)'

from storage import Sqlite3Storage

class Journal(object):
    def __init__(self, config=dict()):
        self.config = config
        self.entries = list()
        self.to_delete = list()
        self.current_entry = None

    def new(self, filename):
        self.config['filename'] = filename
        s = Sqlite3Storage()
        s.new(filename)

    def load(self, filename):
        self.config['filename'] = filename
        s = Sqlite3Storage()
        self.entries = s.load(filename)

    def save(self):
        s = Sqlite3Storage()
        modified_entries = [x for x in self.entries if x.modified]
        s.save(self.config['filename'], modified_entries, self.to_delete)

    def publishedDateList(self,
                          month=datetime.date.today().month,
                          year=datetime.date.today().year):
        pub = [x.date_published
               for x in self.entries
               if x.date_published.month == month and x.date_published.year == year]
        return sorted(list(set(pub)))

    def nextDate(self, date):
        datelist = list(set([x.date_published for x in self.entries]))
        datelist.sort()
        try:
            founddate = datelist.index(date)
            nextdate = datelist[founddate + 1]
        except (IndexError, ValueError):
            nextdate = self.closestNext(datelist, date)

        return nextdate

    def previousDate(self, date):
        datelist = list(set([x.date_published for x in self.entries]))
        datelist.sort()
        try:
            founddate = datelist.index(date)
            # This stops the negative index wrapping.
            prevdate = datelist[founddate - 1] if founddate > 0 else None
        except (IndexError, ValueError):
            prevdate = self.closestPrevious(datelist, date)

        return prevdate

    def closestNext(self, datelist, date):
        def deltafunc(x):
            delta = x - date if x > date else datetime.timedelta.max
            return delta
        if date >= datelist[len(datelist) - 1]:
            return None
        else:
            return min(datelist, key=deltafunc)

    def closestPrevious(self, datelist, date):
        def deltafunc(x):
            delta = date - x if x < date else datetime.timedelta.max
            return delta
        if date <= datelist[0]:
            return None
        else:
            return min(datelist, key=deltafunc)
