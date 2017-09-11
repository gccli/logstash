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

class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        self.server.enqueue((self.client_address[0], data))

class BaseFilter(object):
    def __init__(self, client_ip, message):
        self.client_ip = client_ip
        self.message = message

        try:
            self.handle()
        except:
            logging.warn("failed to handle message".format(port))

    def handle(self):
        pass

class hsmp(BaseFilter):
    def handle(self):
        o = json.loads(self.message)
        print o

class vfw(BaseFilter):
    def handle(self):
        print 'vfw', self.message

class Syslogd(SocketServer.UDPServer):
    def __init__(self, port, filter_class, **kwargs):
        self.filter_class = filter_class
        SocketServer.UDPServer.__init__(self, ('0.0.0.0', port), UDPHandler)
        self.queue = Queue.Queue(kwargs.get('qsize'))

        def _process_thread(filter_class, queue):
            while True:
                client_ip, message = queue.get()
                filter_class(client_ip, message)

        for i in range(kwargs.get('threads')):
            x = thread.start_new_thread(_process_thread, (filter_class, self.queue))
            logging.info('Starting thread {0}'.format(x))

        logging.info("UDP listen on port {0}".format(port))

    def enqueue(self, request):
        self.queue.put(request)
        client_ip, data = request
        logging.info("Got a message from {0}, qsize:{1}".format(client_ip, self.queue.qsize()))

    def run(self):
        self.serve_forever()

if __name__ == "__main__":
    logger = logging.getLogger()
    handle = logging.StreamHandler()

    fmt = logging.Formatter('%(asctime)s - %(levelname)-6s %(filename)12s:%(lineno)-3d - %(message)s')
    handle.setFormatter(fmt)
    logger.setLevel(logging.INFO)
    logger.addHandler(handle)

    parser = argparse.ArgumentParser(description='Logstash')
    parser.add_argument('-port', metavar='PORT', nargs='?', type=int,
                        default=os.environ.get('PORT', 5510),
                        help='bind port, default is 5510')
    parser.add_argument('-threads', metavar='N', nargs='?', type=int,
                        default=os.environ.get('THREADS', 2),
                        help='Thread count, default is 2')
    parser.add_argument('-qsize', metavar='N', nargs='?', type=int,
                        default=os.environ.get('QSIZE', 0),
                        help='Queue size, default infinite')
    parser.add_argument('plugin', nargs='?', choices=['vfw','hsmp','waf'])

    args = parser.parse_args()

    syslogd = Syslogd(args.port, eval(args.plugin),
                      threads=args.threads, qsize=args.qsize)
    syslogd.run()
