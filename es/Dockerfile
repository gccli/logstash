FROM centos

ADD elasticsearch-5.5.2.tar.gz /

RUN set -ex && mv elasticsearch-5.5.2 /elasticsearch && \
    yum install -y sudo which net-tools java-1.8.0-openjdk-headless

COPY docker-entrypoint.sh /usr/bin
COPY elasticsearch.yml /elasticsearch/config
COPY log4j2.properties /elasticsearch/config
COPY search /etc/sudoers.d

RUN useradd search && chown -R search /elasticsearch

WORKDIR /elasticsearch
EXPOSE 9200 9300
USER search
CMD ["bin/elasticsearch"]
ENTRYPOINT ["docker-entrypoint.sh"]
