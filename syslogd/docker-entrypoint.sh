#! /bin/bash

# Exit immediately if a pipeline exits with a non-zero status.
set -e

while true
do
    echo "check redis ..."
    sleep 1
    break
done

exec "$@"
