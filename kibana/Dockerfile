FROM centos

ADD kibana-5.5.2-linux-x86_64.tar.gz /

RUN set -ex && mv kibana-5.5.2-linux-x86_64 /kibana && \
    yum install -y sudo which fontconfig freetype net-tools java-1.8.0-openjdk-headless && \
    useradd kibana && chown -R kibana /kibana

COPY docker-entrypoint.sh /usr/bin
COPY kibana.yml /kibana/config
WORKDIR /kibana

EXPOSE 5601

CMD ["sudo", "-u", "kibana", "bin/kibana"]
ENTRYPOINT ["docker-entrypoint.sh"]
