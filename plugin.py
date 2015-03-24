#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import importlib
import os

class PluginRegistry(type):
    base_classes = ['StoragePlugin',]
    plugins = []
    def __init__(cls, name, bases, attrs):
        if name not in PluginRegistry.base_classes:
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


def discover_plugins(dirs):
    ''' Find plugin classes contained within a list of directories. Returns
        a list of loaded plugins.
    '''
    for dirname in dirs:
        for dpath, dnames, fnames in os.walk(dirname):
            for fname in fnames:
                if fname != '__init__.py' and fname.endswith('py'):
                    path = dpath.split(os.sep)
                    path = filter(None, path[path.index(dirname):])
                    mod_dir = '.'.join(path)
                    importlib.import_module(mod_dir + '.' + fname[:-3])

    return PluginRegistry.plugins
