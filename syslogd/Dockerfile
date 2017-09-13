FROM python:2.7

COPY basefilter.py syslogd.py docker-entrypoint.sh /usr/bin/

RUN set -ex && pip install redis pyparsing

CMD ["syslogd.py"]
ENTRYPOINT ["docker-entrypoint.sh"]
