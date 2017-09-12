#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging
import SocketServer
import Queue

import json
import thread
import redis
import datetime

redisdb = None
class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        self.server.enqueue((self.client_address[0], data))

class BasePlugin(object):
    def __init__(self, client_ip, message):
        self.client_ip = client_ip
        self.message = message
        self.setup()
        self.handle()

    def setup(self):
        pass

    def handle(self):
        pass

class hsmp(BasePlugin):
    def setup(self):
        from pyparsing import Word, Suppress, Combine, \
            Regex, alphas, nums, alphanums

        ints = Word(nums)

        # priority
        priority = Suppress("<") + ints + Suppress(">")

        # timestamp
        month = Word(alphas, exact=3)
        day   = ints
        time  = Combine(ints + ":" + ints + ":" + ints)
        timestamp = month + day + time

        # hostname
        hostname = Word(alphanums + "_-.")

        # appname
        appname = Word(alphas + "_")
        apppid = Suppress("[") + ints + Suppress("]") + Suppress(":")

        # message
        message = Regex(".*")

        self._pattern = priority + timestamp + hostname + appname + apppid + message

    def handle(self):
        try:
            parsed = self._pattern.parseString(self.message)
        except:
            logging.warn("Failed to parse message {0}".format(self.message))
            return

        log = {}
        log["log_priority"] = parsed[0]
        log["log_time"] = ' '.join(parsed[1:4])
        log["log_host"] = parsed[4]
        log["log_type"] = parsed[5].lstrip('log_')
        log["log_pid"] = parsed[6]

        try:
            log.update(json.loads(parsed[7]))
        except:
            logging.warn("Invalid json {0}".format(parsed[7]))
            return

        print json.dumps(log, indent=2); sys.stdout.flush()
        redisdb.rpush('logstash', json.dumps(log));

class vfw(BasePlugin):
    def handle(self):
        print 'vfw', self.message

class Syslogd(SocketServer.UDPServer):
    def __init__(self, port, plugin_class, **kwargs):
        self.plugin_class = plugin_class
        SocketServer.UDPServer.__init__(self, ('0.0.0.0', port), UDPHandler)
        self.queue = Queue.Queue(kwargs.get('qsize'))

        def _process_thread(plugin_class, queue):
            while True:
                client_ip, message = queue.get()
                plugin_class(client_ip, message)

        for i in range(kwargs.get('threads')):
            x = thread.start_new_thread(_process_thread, (plugin_class, self.queue))
            logging.info('Starting thread {0}'.format(x))

        logging.info("UDP listen on port {0}".format(port))

    def enqueue(self, request):
        self.queue.put(request)
        client_ip, data = request
        logging.info("Got a message from {0}, qsize:{1}".format(client_ip, self.queue.qsize()))

    def run(self):
        self.serve_forever()

def hsmp_test():
    s = '<133>Sep 12 11:35:52 10.95.46.25 log_ips[32007]: {"operation":1,"mid":"01894490abae5e108154df67ee6fb00b","id":9148,"protocol":6,"defense_time":1505187343,"remote_port":56292,"local_mac":"00:50:56:B5:21:9D","local_ip":"10.95.46.66","remote_ip":"10.95.46.91","local_port":1,"remote_mac":"00:50:56:84:16:85"}'

    hsmp('1.1.1.1', s)

if __name__ == "__main__":
    logger = logging.getLogger()
    handle = logging.StreamHandler()

    fmt = logging.Formatter('%(asctime)s - %(levelname)-6s %(filename)12s:%(lineno)-3d - %(message)s')
    handle.setFormatter(fmt)
    logger.setLevel(logging.INFO)
    logger.addHandler(handle)

    parser = argparse.ArgumentParser(description='Logstash')
    parser.add_argument('-port', metavar='PORT', nargs='?', type=int,
                        default=os.environ.get('BIND_PORT', 5510),
                        help='bind port, default is 5510')
    parser.add_argument('-threads', metavar='N', nargs='?', type=int,
                        default=os.environ.get('THREADS', 2),
                        help='Thread count, default is 2')
    parser.add_argument('-qsize', metavar='N', nargs='?', type=int,
                        default=os.environ.get('QSIZE', 0),
                        help='Queue size, default infinite')
    parser.add_argument('-redis', metavar='HOST', nargs='?', type=str,
                        default=os.environ.get('REDIS_HOST', 'localhost'),
                        help='Redis hostname, default localhost')

    parser.add_argument('plugin', nargs='?', choices=['vfw','hsmp','waf'])
    args = parser.parse_args()

    redisdb = redis.Redis(host=args.redis)
    syslogd = Syslogd(args.port, eval(args.plugin),
                      threads=args.threads, qsize=args.qsize)

    hsmp_test()
    sys.exit(0)

    syslogd.run()
