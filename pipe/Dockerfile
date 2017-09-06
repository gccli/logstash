FROM python:2.7

ADD . /pipe
WORKDIR /pipe

RUN set -ex && \
    pip install -r requirements.txt

COPY docker-entrypoint.sh /usr/bin

CMD ["python", "pipe.py"]
ENTRYPOINT ["docker-entrypoint.sh"]
