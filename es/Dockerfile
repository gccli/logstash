FROM centos

ADD elasticsearch-5.5.2.tar.gz /

RUN set -ex && mv elasticsearch-5.5.2 /elasticsearch && \
    yum install -y sudo which net-tools java-1.8.0-openjdk-headless && useradd search && \
    chown -R search /elasticsearch

COPY docker-entrypoint.sh /usr/bin
COPY elasticsearch.yml /elasticsearch/config
WORKDIR /elasticsearch


CMD ["sudo", "-u", "search", "bin/elasticsearch"]

EXPOSE 9200 9300

ENTRYPOINT ["docker-entrypoint.sh"]
