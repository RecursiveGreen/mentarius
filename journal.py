#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime

class Entry(object):
    def __init__(self,
                 date_created=datetime.datetime.now(),
                 date_modified=datetime.datetime.now(),
                 date_published=datetime.date.today(),
                 title='',
                 body=''):
        self._date_created = date_created
        self._date_modified = date_modified
        self._date_published = date_published
        # self._entry_id = entry_id
        self._title = title
        self._body = body

        self.modified = False

    def get_date_created(self):
        return self._date_created
    def set_date_created(self, value):
        self._date_created = value
        self.modified = True
    def del_date_created(self):
        del self._date_created
    date_created = property(get_date_created,
                            set_date_created,
                            del_date_created,
                            "A timestamp from when the entry was created.")

    def get_date_modified(self):
        return self._date_modified
    def set_date_modified(self, value):
        self._date_modified = value
        self.modified = True
    def del_date_modified(self):
        del self._date_modified
    date_modified = property(get_date_modified,
                             set_date_modified,
                             del_date_modified,
                             "A timestamp from when the entry was last modified.")

    def get_date_published(self):
        return self._date_published
    def set_date_published(self, value):
        self._date_published = value
        self.modified = True
    def del_date_published(self):
        del self._date_published
    date_published = property(get_date_published,
                              set_date_published,
                              del_date_published,
                              "The date at which the entry is published.")

    def get_title(self):
        return self._title
    def set_title(self, value):
        self._title = value
        self.modified = True
    def del_title(self):
        del self._title
    title = property(get_title,
                     set_title,
                     del_title,
                     "The title of the entry.")

    def get_body(self):
        return self._body
    def set_body(self, value):
        self._body = value
        self.modified = True
    def del_body(self):
        del self._body
    body = property(get_body,
                    set_body,
                    del_body,
                    "The body of the entry.")

    def __repr__(self):
        if self.title:
            return self.title
        else:
            return '(Untitled Entry)'

from storage import Sqlite3Storage

class Journal(object):

    name = None

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
        self.name = filename

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
