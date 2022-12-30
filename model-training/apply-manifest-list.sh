#!/usr/bin/env bash

buildah manifest create ai-for-edge-microshift-demo-model

buildah manifest add \
    --arch amd64 \
    ai-for-edge-microshift-demo-model \
    docker://quay.io/rbohne/ai-for-edge-microshift-demo:model-x86_64

buildah manifest add \
    --arch arm64 \
    ai-for-edge-microshift-demo-model \
    docker://quay.io/rbohne/ai-for-edge-microshift-demo:model-aarch64

buildah manifest push \
    ai-for-edge-microshift-demo-model \
    docker://quay.io/rbohne/ai-for-edge-microshift-demo:model

buildah manifest rm ai-for-edge-microshift-demo-model
