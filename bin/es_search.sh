#! /bin/bash

source $(dirname $(readlink -f $0))/common.sh
echo curl ${es_base}/logstash-$(date +%Y%m%d)/_search?pretty
curl ${es_base}/logstash-$(date +%Y%m%d)/_search?pretty
