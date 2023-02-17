#!/bin/bash

if [ $# -eq 0 ]; then
    echo "error: file path required"
    exit 1
fi

liveness_probe_file=$1

if [ ! -f "$liveness_probe_file" ]; then
    echo "error: $liveness_probe_file does not exist."
    exit 1
fi

if [[ $( expr $(date +%s) - $(cat $1)) -ge 10 ]]; then
  echo "error: liveness probe appears to be too old... Maybe the service is dead?"
  exit 1
fi