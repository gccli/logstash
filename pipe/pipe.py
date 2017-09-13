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

    def current_index(self):
        today = datetime.datetime.now().strftime("%Y%m%d")
        return 'logstash-{0}'.format(today)



    def process(self, d):
        pass

    def index(self, d):
        try:
            res = self._es.index(index=self.current_index(),
                                 doc_type=d['log_type'], body=d)
        except elasticsearch.ElasticsearchException as e:
            self._db.rpush('_indexfailure', json.dumps(d))
            length = self._db.llen('_indexfailure')
            logging.error("Failed to index {0} - {1}, failure size {2}".format(d, e.error, length))

            return None

        return res

    def run(self):
        while True:
            if not self._es.ping():
                time.sleep(2.0)
                logging.error("Waiting for elasticsearch cluster up...")
                continue

            logdata = self._db.blpop('logstash')[1]
            try:
                d = json.loads(logdata)
            except:
                logging.error("failed to parse {0}".format(logdata))
                continue

            if not (d.has_key('vendor') and d.has_key('log_type')):
                logging.error("Invalid log format {0}".format(logdata))
                continue

            self.process(d)
            res = self.index(d)

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
