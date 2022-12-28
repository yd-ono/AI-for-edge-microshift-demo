podman run \
    --runtime /usr/bin/nvidia-container-runtime \
    -ti --rm  --net host --privileged \
    -v $(pwd):/app:z  \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v  ~/.Xauthority:/root/.Xauthority:Z \
    -e VIDEO_DEVICE_ID=0 \
    quay.io/rbohne/jetson-xavier-nx-dlib:base  bash

#    -v /tmp/argus_socket:/tmp/argus_socket \
#    -v /etc/enctune.conf:/etc/enctune.conf \
