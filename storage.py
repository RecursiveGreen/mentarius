#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

from journal import Entry
from utils import file_exists

class BaseStorage(object):
    def __init__(self):
        pass

    def new(self):
        return None

    def load(self):
        return None

    def save(self):
        return None

class Sqlite3Storage(BaseStorage):
    def __init__(self):
        super().__init__()

        self.name = 'sqlite3'
        self.description = 'Sqlite3 Storage Engine'

    def new(self, dbfile):
        db = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
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
        db.commit()
        db.close()

    def load(self, dbfile):
        entries = list()

        db = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
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
                          r['entry_id'],
                          r['title'],
                          r['body'])
            entries.append(entry)

        db.close()

        return entries

    def save(self, dbfile, entries, to_delete):
        db = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
        cur = db.cursor()
        for entry in entries:
            if entry.entry_id:
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
                      entry.entry_id))
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
            db.commit()

        for entry in to_delete:
            cur.execute('''
                DELETE FROM entries
                WHERE entry_id = ?
            ''', (entry.entry_id,))
            db.commit()

        db.close()
