#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

from journal import Entry
from plugin import StoragePlugin

class Sqlite3Storage(StoragePlugin):
    def __init__(self, journal=None):
        super().__init__(journal)

        self.name = 'sqlite3'
        self.description = 'Sqlite3 Storage Engine'

    def new(self):
        db = sqlite3.connect(self.journal.config['storage']['path'],
                             detect_types=sqlite3.PARSE_DECLTYPES)

        with db:
            cur = db.cursor()
            cur.execute('''
                CREATE TABLE entries (
                    entry_id INTEGER NOT NULL,
                    date_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    date_modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    date_published DATE NOT NULL DEFAULT ( date ( 'now' ) ),
                    body TEXT NOT NULL,
                    title VARCHAR( 255 ) NOT NULL,
                    PRIMARY KEY ( entry_id )
                )
            ''')

    def load(self):
        entries = list()

        db = sqlite3.connect(self.journal.config['storage']['path'],
                             detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row

        with db:
            cur = db.cursor()
            cur.execute('''
                SELECT
                    *
                FROM entries
            ''')
            for row in cur:
                r = dict(zip(row.keys(), row))
                entry = Entry(r['date_created'],
                              r['date_modified'],
                              r['date_published'],
                              r['title'],
                              r['body'])
                entry.extra['entry_id'] = r['entry_id']
                entries.append(entry)

        self.journal.entries = entries

    def save(self):
        db = sqlite3.connect(self.journal.config['storage']['path'],
                             detect_types=sqlite3.PARSE_DECLTYPES)
        modified_entries = [x for x in self.journal.entries if x.modified]

        with db:
            cur = db.cursor()
            for entry in modified_entries:
                if 'entry_id' in entry.extra:
                    cur.execute('''
                        UPDATE entries
                        SET
                            date_modified = ?,
                            date_published = ?,
                            body = ?,
                            title = ?
                        WHERE entry_id = ?
                    ''', (entry.date_modified,
                          entry.date_published,
                          entry.body,
                          entry.title,
                          entry.extra['entry_id']))
                else:
                    cur.execute('''
                        INSERT INTO entries(
                            date_created,
                            date_modified,
                            date_published,
                            body,
                            title
                        )
                        VALUES (?, ?, ?, ?, ?)
                    ''', (entry.date_created,
                          entry.date_modified,
                          entry.date_published,
                          entry.body,
                          entry.title))

            for entry in self.journal.to_delete:
                if 'entry_id' in entry.extra:
                    cur.execute('''
                        DELETE FROM entries
                        WHERE entry_id = ?
                    ''', (entry.extra['entry_id'],))

            self.journal.to_delete = list()
