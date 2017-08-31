Build logstash image
====================

    docker build . -t logstash

Run logstash container
======================

Basic usage
-----------

        # Show help
        docker run --rm -it logstash bin/logstash --help
        # Run default pipeline
        docker run --rm -it -p 514:514/udp logstash

Run detached mode
-----------------

        docker run --name logx -d -p 5510-5519:5510-5519/udp -v ${PWD}/x:/logstash/pipeline.conf logstash
        docker run --name logy -d -p 5520-5529:5520-5529/udp -v ${PWD}/y:/logstash/pipeline.conf logstash
        docker run --name logz -d -p 5530-5539:5530-5539/udp -v ${PWD}/z:/logstash/pipeline.conf --link redis logstash

        # show log
        docker logs -f logz

Remove running container
------------------------

        docker rm -vf logx logy logz


Redis as logstash output plugin
-------------------------------

    docker run --rm -it --name redis redis:alpine redis-server
    docker run -d --name redis -v /data -p6379:6379 redis:alpine redis-server

    # link from client
    docker run --rm -it --link redis redis:alpine redis-cli -h redis
