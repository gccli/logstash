#! /bin/bash

basedir=$(readlink -f $0 | sed 's|/bin/elk_init.sh||')
datadir=${basedir}/data

mkdir -p ${datadir}/es/{0,1,2}
chown -R 1000 ${datadir}/es/{0,1,2}

mkdir -p ${datadir}/redis
