#! /usr/bin/env python

import os
import sys
import time
import json
import datetime
import redis
import elasticsearch

def current_index():
    today = datetime.datetime.now().strftime("%Y%m%d")
    return 'logstash-{0}'.format(today)

redis = redis.Redis(host='localhost', port=6379)
#es = elasticsearch.Elasticsearch(["localhost"], sniff_on_start=True,
#                   sniff_on_connection_fail=True,
#                   sniffer_timeout=60)
es = elasticsearch.Elasticsearch()
while True:
    x = redis.lpop('logstash')
    if not x:
        time.sleep(0.1)
        continue
    d = json.loads(x) # is a dict
    time.sleep(0.1)
    idx = current_index()
    r = es.index(index=idx, doc_type='log', body=d)
    print type(r), r
