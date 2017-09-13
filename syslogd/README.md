Syslogd by python
=================

Multi-thread support
------------

Input plugin support
--------------------

* parsing different log format, syslog, kv, json, ...
* unify log format, output json log data
* add timestamp and vender info

Filter support
--------------

### mutate filter

* rename filed name

        "rename": {"old_field_name": "new_field_name", ...}

* convert field value type, current support convert to int or string

        "convert": {"field1": "int, "field2": "string", ...}

* gsub, sub field value

        gsub": [{"field_name": ["pattern", "repl"]}


Test
====

start syslogd on udp port 3333, using `demo` plugin and filter config load from `test/config.json`

    ./syslogd.py -port 3333 -f test/config.json demo


the `demo` plugin just parse json log message and add timestamp

```
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
```

send test log by `nc`

    $ nc -u 127.0.0.1 3333
    {"server-ip": "8.8.8.8", "client-ip": "10.18.1.12", "direction": 1, "type": "log_operate"}

syslogd output as follow, filters worked

```
2017-09-13 18:13:44,767 - INFO     syslogd.py:195 - Got a message from 127.0.0.1, qsize:1
{
  "direction": "1",
  "@timestamp": "2017-09-13T18:13:44.768344+08:00",
  "destination": "8.8.8.8",
  "source": "10.18.1.12",
  "vendor": "demo",
  "type": "operate",
  "log_type": "test"
}
```
