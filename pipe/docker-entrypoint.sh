#! /bin/bash

# Exit immediately if a pipeline exits with a non-zero status.
set -e

while true
do
    status=$(curl "http://${ES_HOST:-localhost}:9200/_cat/health" 2>/dev/null | awk '{ print $4 }')
    if [ $? -ne 0 ]; then
        echo "elasticsearch is unavailable"
        sleep 1
        continue
    fi

    if [ "$status"x == "x" ]; then
        echo "elasticsearch status can not get"
        sleep 1
        continue
    fi

    if [ $status != "red" ]; then
        echo "elasticsearch is ready, status:$status"
        break
    fi
done

exec "$@"
