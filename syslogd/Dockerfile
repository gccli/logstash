FROM python:2.7

COPY docker-entrypoint.sh /usr/bin
COPY syslogd.py /

RUN set -ex && pip install redis

CMD ["/syslogd.py"]
ENTRYPOINT ["docker-entrypoint.sh"]
