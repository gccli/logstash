System settings
===============

Notes:

Start elasticsearch should modify the kernel parameters, and change the owner of data directory

    sysctl -w vm.max_map_count=262144
    # 1000 is the user id of elasticsearch container
    chown -R 1000 data/es/0/nodes

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

    $ docker-compose exec redis redis-cli
    127.0.0.1:6379> LLEN logstsh
    (integer) 0
