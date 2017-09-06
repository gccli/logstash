#! /usr/bin/env python

import os
import sys
import time
import json
import datetime
import redis
import elasticsearch
import logging

class Pipe(object):
    def __init__(self, **kwargs):
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        es_host = os.environ.get('ES_HOST', 'localhost')

        self._db = redis.Redis(host=redis_host)
        self._es = elasticsearch.Elasticsearch([es_host],
                                               sniff_on_start=True,
                                               sniff_on_connection_fail=True,
                                               sniffer_timeout=60)

    def index(self):
        today = datetime.datetime.now().strftime("%Y%m%d")
        return 'logstash-{0}'.format(today)

    def run(self):
        while True:
            logdata = self._db.blpop('logstash')[1]
            try:
                d = json.loads(logdata)
            except:
                logging.info("failed to parse {0}".format(logdata))
                continue

            try:
                res = self._es.index(index=self.index(), doc_type='log', body=d)
            except elasticsearch.ElasticsearchException as e:
                logging.error("failed to index {0} - {1}".format(logdata, e.error))
                continue

            logging.info('log type {0} has {1}'.format(d['log_type'], res['result']))

if __name__ == '__main__':
    logger = logging.getLogger()
    handle = logging.StreamHandler()

    fmt = logging.Formatter('%(asctime)s - %(levelname)-6s %(filename)12s:%(lineno)-3d - %(message)s')
    handle.setFormatter(fmt)
    logger.setLevel(logging.INFO)
    logger.addHandler(handle)

    logging.info('Starting pipe...')
    pipe = Pipe()
    pipe.run()
