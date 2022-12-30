#!/usr/bin/env bash

buildah manifest create ai-for-edge-microshift-demo-cpu-only

buildah manifest add \
    --arch amd64 \
    ai-for-edge-microshift-demo-cpu-only \
    docker://quay.io/rbohne/ai-for-edge-microshift-demo:cpu-only-x86_64

buildah manifest add \
    --arch aarch64 \
    ai-for-edge-microshift-demo-cpu-only \
    docker://quay.io/rbohne/ai-for-edge-microshift-demo:cpu-only-aarch64

buildah manifest push \
    ai-for-edge-microshift-demo-cpu-only \
    docker://quay.io/rbohne/ai-for-edge-microshift-demo:cpu-only

buildah manifest rm ai-for-edge-microshift-demo-cpu-only
