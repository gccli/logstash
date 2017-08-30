Build logstash image
====================

    docker build . -t logstash

Run logstash container
======================

* Show help

    docker run --rm -it logstash bin/logstash --help

* Run default pipeline

    docker run --rm -it -p 514:514/udp logstash

* Run detached mode

    docker run --name logx -d -p 5514:5514/udp -v ${PWD}/x.conf:/logstash/pipeline.conf logstash
