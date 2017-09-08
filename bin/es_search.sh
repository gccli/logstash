#! /bin/bash

source $(dirname $(readlink -f $0))/common.sh
curl ${es_base}/logstash-$(date +%Y%m%d)/log/_search?pretty
