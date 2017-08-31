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

        docker run --name logx -d -p 5510-5519:5510-5519/udp -v ${PWD}/x:/logstash/pipeline.conf logstash

        docker run --name logy -d -p 5520-5529:5520-5529/udp -v ${PWD}/y:/logstash/pipeline.conf logstash

        # send udp log to port 5520
        echo -n hello world | nc -q1 -u 127.0.0.1 5520

        docker run --name logz -d -p 5530-5539:5530-5539/udp -v ${PWD}/z:/logstash/pipeline.conf logstash

* Remove running container

    docker rm -vf logx logy
