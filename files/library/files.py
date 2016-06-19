#!/usr/bin/python

import json

def readConfigFile(file_path):
    try:
        with open(file_path) as f:
            return json.load(f)
    except Exception as e:
        print e
        return None
