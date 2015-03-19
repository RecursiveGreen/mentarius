#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

class PluginRegistry(type):
    plugins = []
    def __init__(cls, name, bases, attrs):
        if name != 'Plugin':
            PluginRegistry.plugins.append(cls)


class StoragePlugin(object, metaclass=PluginRegistry):
    def __init__(self, journal=None):
        self.journal = journal

    def new(self):
        ''' Creates and initializes a new journal within storage. '''
        return None

    def load(self):
        ''' Loads a journal from storage. Returns a list of entries.'''
        return None

    def save(self):
        ''' Saves a journal to storage. '''
        return None
