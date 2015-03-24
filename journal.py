#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import datetime

class Entry(object):
    def __init__(self,
                 date_created=datetime.datetime.now(),
                 date_modified=datetime.datetime.now(),
                 date_published=datetime.date.today(),
                 title='',
                 body=''):
        self.date_created = date_created
        self.date_modified = date_modified
        self.date_published = date_published
        self.title = title
        self.body = body

        self.extra = dict()
        self.modified = False

    def __repr__(self):
        if self.title:
            return self.title
        else:
            return '(Untitled Entry)'


from plugin import PluginRegistry

class Journal(object):

    name = None

    def __init__(self, config_file=None):
        self.config = configparser.ConfigParser()
        self.current_entry = None
        self.entries = list()
        self.storage_engine = None
        self.to_delete = list()

        if config_file:
            self.config.read(config_file)
            self.init_storage_engine()

    def init_storage_engine(self):
        class_name = self.config['storage']['engine']
        plug = [x for x in PluginRegistry.plugins if x.__name__ == class_name]
        if plug:
            self.storage_engine = plug[0](self)

    def new(self):
        self.storage_engine.new()

    def load(self):
        self.storage_engine.load()

    def save(self):
        self.storage_engine.save()

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
