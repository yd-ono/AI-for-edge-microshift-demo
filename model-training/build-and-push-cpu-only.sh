#!/usr/bin/env bash

podman build  \
  -t quay.io/rbohne/ai-for-edge-microshift-demo:model-$(uname -p) \
  -f Containerfile.cpu-only .


podman push \
  quay.io/rbohne/ai-for-edge-microshift-demo:model-$(uname -p)