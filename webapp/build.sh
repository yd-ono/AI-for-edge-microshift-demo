#!/usr/bin/env bash

podman build \
  -t quay.io/rbohne/ai-for-edge-microshift-demo:webapp \
  -f Containerfile .

