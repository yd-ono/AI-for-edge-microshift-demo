#!/usr/bin/env bash

podman build \
  -t default-registry.cluster.local/ai-for-edge/webapp:latest \
  -f Containerfile .

podman push --tls-verify=false \
  default-registry.cluster.local/ai-for-edge/webapp:latest
