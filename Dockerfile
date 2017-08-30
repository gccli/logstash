FROM centos

ADD logstash-5.5.2.tar.gz /
RUN mv logstash-5.5.2 /logstash && yum install -y which net-tools java-1.8.0-openjdk-headless
COPY docker-entrypoint.sh /usr/bin
COPY pipeline.conf /logstash
WORKDIR /logstash

CMD ["bin/logstash", "-f", "pipeline.conf", "-r"]

ENTRYPOINT ["docker-entrypoint.sh"]
