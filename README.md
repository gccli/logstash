System settings
===============

sysctl -w vm.max_map_count=262144


Log collection
==============

build
-----

docker-compose up --build


General operation
=================

elasticsearch
-------------

1. cat api

        # show indices
        curl http://localhost:9200/_cat/indices?v

2. index api

        # get index mapping
        curl http://localhost:9200/logstash-20170906/_mapping?pretty
        # delete indices
        curl -XDELETE http://localhost:9200/logstash-*


redis
-----

    # link from client
    docker run --rm -it --link redis redis:alpine redis-cli -h redis
