#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import re
import sys
import logging
import SocketServer
import Queue

import json
import thread
import redis
from datetime import tzinfo, timedelta, datetime
from basefilter import mutate
######## Plugin for parsing safekit syslog ########

class TZ(tzinfo):
    def utcoffset(self, dt): return timedelta(hours=+8)

class BasePlugin(object):
    def __init__(self, client_ip, message):
        self.client_ip = client_ip
        self.message = message
        self.setup()

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

    def _add_timestamp(self, log):
        d = datetime.strptime(log['log_time'], '%b %d %H:%M:%S')
        d = d.replace(year=datetime.today().year,
                      tzinfo=TZ())
        log['@timestamp'] = d.isoformat()

    def handle(self):
        try:
            parsed = self._pattern.parseString(self.message)
        except:
            logging.warn("Failed to parse message {0}".format(self.message))
            return

        log = {"vendor": "hsmp"}
        log["log_priority"] = parsed[0]
        log["log_time"] = ' '.join(parsed[1:4])
        log["log_host"] = parsed[4]
        log["log_type"] = parsed[5].lstrip('log_')
        log["log_pid"] = parsed[6]

        try:
            json_dict =json.loads(parsed[7])
        except:
            logging.warn("Invalid json {0}".format(parsed[7]))
            return None

        log.update(json_dict)
        self._add_timestamp(log)

        return log

class vfw(BasePlugin):
    def _add_timestamp(self, log):
        d = datetime.fromtimestamp(float(log['log_time']))
        d = d.replace(tzinfo=TZ())
        log['@timestamp'] = d.isoformat()

    def handle(self):

        try:
            log = re.findall(r'(\S+)="(.*?)"', self.message)
            log = dict(log)
        except:
            logging.warn("Failed to parse message [{0}]".format(self.message))
            return None

        log["vendor"] = "vfw"
        log["log_type"] = log.pop("type")
        log["log_time"] = log.pop("time")

        self._add_timestamp(log)

        return log


class demo(BasePlugin):
    def _add_timestamp(self, log):
        d = datetime.today()
        d = d.replace(tzinfo=TZ())
        log['@timestamp'] = d.isoformat()

    def handle(self):
        try:
            log = json.loads(self.message)
        except:
            logging.warn("Failed to parse message [{0}]".format(self.message))
            return None

        log["vendor"] = "demo"
        log["log_type"] = "test"

        self._add_timestamp(log)

        return log

class waf(BasePlugin):
    def _add_timestamp(self, log):
        d = datetime.strptime(log['log_time'], '%b %d %H:%M:%S')
        d = d.replace(year=datetime.today().year,
                      tzinfo=TZ())
        log['@timestamp'] = d.isoformat()

    def handle(self):
        log = {"vendor": "waf"}

        print self.message; sys.stdout.flush()
        return None

######## Syslog daemon ########
class UDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        self.server.enqueue((self.client_address[0], data))

class Syslogd(SocketServer.UDPServer):
    def __init__(self, port, plugin_class, **kwargs):
        self.plugin_class = plugin_class
        SocketServer.UDPServer.__init__(self, ('0.0.0.0', port), UDPHandler)
        self.queue = Queue.Queue(kwargs.get('qsize'))

        self.redisdb = redis.Redis(host=kwargs.get('redis_host'))

        filter_config = kwargs.get('filter_config', {})
        self.filters = []
        for k in filter_config.keys():
            self.filters.append(eval(k)(filter_config[k]))

        def _process_thread(plugin_class, queue, redisdb):
            while True:
                client_ip, message = queue.get()
                log = plugin_class(client_ip, message).handle()
                if not log:
                    continue
                for filt in self.filters:
                    filt.filter(log)

                try:
                    print json.dumps(log, indent=2); sys.stdout.flush()
                    redisdb.rpush('logstash', json.dumps(log))
                except:
                    logging.error("Failed to add data to redis")


        for i in range(kwargs.get('threads')):
            x = thread.start_new_thread(_process_thread,
                                        (plugin_class, self.queue, self.redisdb))
            logging.info('Starting thread {0}'.format(x))

        logging.info("UDP listen on port {0}, filters:{1}" \
                     .format(port, [f.__class__.__name__ for f in self.filters]))

    def enqueue(self, request):
        self.queue.put(request)
        client_ip, data = request
        logging.info("Got a message from {0}, qsize:{1}".format(client_ip, self.queue.qsize()))

    def run(self):
        self.serve_forever()


def plugin_test(plugin_name):
    try:
        s = open('{0}.log'.format(plugin_name), 'r').readline()
        s = s.strip()
        eval(plugin_name)('1.1.1.1', s).handle()
    except IOError as e:
        print 'failed to exec test case:', e

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
    parser.add_argument('-f', metavar='FILTER', nargs='?', type=str, default=None,
                        help='filter config file, json format')

    parser.add_argument('plugin', nargs='?', choices=['vfw','hsmp','waf', 'demo'])
    args = parser.parse_args()

    filter_config = json.loads(open(args.f, 'r').read()) if args.f else {}

    plugin_test(args.plugin)
    syslogd = Syslogd(args.port, eval(args.plugin),
                      threads=args.threads, qsize=args.qsize,
                      redis_host=args.redis,
                      filter_config=filter_config)
    syslogd.run()
