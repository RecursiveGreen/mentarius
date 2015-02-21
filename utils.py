#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def file_exists(filepath):
    ''' Check if a file exists and can be accessed. '''
    try:
        f = open(filepath, 'r+b')
        f.close()
    except IOError as e:
        return False

    return True
