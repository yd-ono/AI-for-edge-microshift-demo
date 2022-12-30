#!/usr/bin/env bash

podman build \
  -t quay.io/rbohne/ai-for-edge-microshift-demo:cpu-only-$(uname -p) \
  -f Containerfile .

podman push quay.io/rbohne/ai-for-edge-microshift-demo:cpu-only-$(uname -p)