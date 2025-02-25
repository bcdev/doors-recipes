#!/bin/bash
docker build -f docker/doors.Dockerfile --build-arg CACHE_ID=$2 -t xcube-doors-stable:$1 .
docker tag xcube-doors-stable:$1 quay.io/bcdev/xcube-doors-stable:$1
docker push quay.io/bcdev/xcube-doors-stable:$1