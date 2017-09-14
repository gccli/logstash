#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import collections

class BaseFilter(object):
    """
    "add_field": {
       "new_field": "new_value", (value can be any type)
        ...
    }
    """
    def add_field(self, config, d):
        for k,v in config.iteritems():
            d[k] = v

    """
    "add_tag": ["string", ...]
    """
    def add_tag(self, config, d):
        if d.hsh_key('tag'):
            d['tag'] = d['tag'] + config
        else:
            d['tag'] = config

    """
    "remove_field": ["string", ...]
    """
    def remove_field(self, config, d):
        for k in config:
            d.pop(k)

    """
    "remove_tag": ["string", ...]
    """
    def remove_tag(self, config, d):
        if d.hsh_key('tag'):
            d['tag'] = d['tag'] - config

class mutate(BaseFilter):
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


class translate(BaseFilter):
    """
    "translate": {
      "field": {
        dictionary: {
           "value_or_pattern": "new_value",
            ...
        },
        "regex": boolean (default false),
        "new_field": string (optinal, add new field),
      },
      ...
    }
    """

    def __init__(self, dict_config):
        self.config = dict_config

    def filter(self, d):
        for k, v in self.config.iteritems():
            if k in ['add_field', 'add_tag', 'remove_field', 'remove_tag']:
                getattr(self, k)(v, d)

        for k, v in self.config.iteritems():
            if not d.has_key(k): continue

            dictionary = v['dictionary']
            dict_key = None

            if v.has_key('regex') and v['regex']:
                for pattern in dictionary.keys():
                    if not re.search(pattern, d[k]): continue
                    dict_key = pattern
                    break
            else:
                for pattern in dictionary.keys():
                    if pattern != d[k]: continue
                    dict_key = pattern
                    break
            if not dict_key:
                continue

            xk = v.get('new_field', k)
            d[xk] = dictionary[pattern]

if __name__ == '__main__':
    # load test log data
    data = json.loads(open('test/data.json', 'r').read())

    # load filter config
    #config = json.loads(open('test/config.json', 'r').read())
    config = json.loads(open('test/config.json', 'r').read(),
                        object_pairs_hook=collections.OrderedDict)

    filters = [eval(k)(config[k]) for k in config.keys()]

    print 'config:\n', json.dumps(config, indent=2)
    print 'original data:\n', json.dumps(data)

    for f in filters: f.filter(data)
    print 'after filter:\n', json.dumps(data)
