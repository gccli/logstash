#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json

class mutate(object):
    def __init__(self, dict_config):
        self.config = dict_config

    def filter(self, d):
        for k, v in self.config.iteritems():
            getattr(self, k)(v, d)

    def rename(self, config, d):
        for k, v in config.iteritems():
            if d.has_key(k): d[v] = d.pop(k)

    def convert(self, config, d):
        for k, v in config.iteritems():
            if not d.has_key(k): continue
            if v in ['int', 'integer']:
                d[k] = int(d[k])
            elif v in ['str', 'string']:
                d[k] = str(d[k])

    def gsub(self, config, d):
        for k, v in config.iteritems():
            if not d.has_key(k): continue
            d[k] = re.sub(v[0], v[1], d[k])

if __name__ == '__main__':
    config = json.loads(open('test/config.json', 'r').read())
    data = json.loads(open('test/data.json', 'r').read())

    print 'config:\n', json.dumps(config, indent=2)
    print 'original data:\n', json.dumps(data)
    mutate(config['mutate']).filter(data)
    print 'after filter:\n', json.dumps(data)
