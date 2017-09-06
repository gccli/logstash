#! /bin/bash

source $(dirname $(readlink -f $0))/common.sh

curl ${es_base}/_cat/indices?v
