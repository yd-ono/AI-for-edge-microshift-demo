#!/usr/bin/env bash

podman build --runtime /usr/bin/nvidia-container-runtime \
  -t quay.io/rbohne/ai-for-edge-microshift-demo:model-aarch64 \
  -f Containerfile.jetson .
