FROM registry.access.redhat.com/ubi9/ubi-minimal:latest

# Versions of Nginx and nginx-rtmp-module to use
ENV NGINX_VERSION nginx-1.25.0
ENV NGINX_RTMP_MODULE_VERSION 1.2.2
ENV NGINX_HOME=/home/nginx
ENV PATH "$PATH:/home/nginx"

RUN microdnf update && \
    microdnf --disableplugin subscription-manager -y install \
    wget tar gzip xz gcc make pcre-devel zlib-devel shadow-utils ca-certificates openssl openssl-devel && \
    microdnf clean all

# ffmpeg static source (https://johnvansickle.com/ffmpeg/)
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz.md5 && \
    md5sum -c ffmpeg-release-amd64-static.tar.xz.md5 && \
    tar Jxf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-6.0-amd64-static/ffmpeg /bin/ && \
    rm -f ffmpeg-release-amd64-static.tar.xz.md5 ffmpeg-release-amd64-static.tar.xz && \
    rm -rf ffmpeg-6.0-amd64-static

# Download and extract Nginx
RUN mkdir -p /tmp/build/nginx && \
    cd /tmp/build/nginx && \
    wget -O ${NGINX_VERSION}.tar.gz https://nginx.org/download/${NGINX_VERSION}.tar.gz && \
    tar -zxf ${NGINX_VERSION}.tar.gz

# Download and extract RTMP module
RUN mkdir -p /tmp/build/nginx-rtmp-module && \
    cd /tmp/build/nginx-rtmp-module && \
    wget -O nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}.tar.gz https://github.com/arut/nginx-rtmp-module/archive/v${NGINX_RTMP_MODULE_VERSION}.tar.gz && \
    tar -zxf nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}.tar.gz && \
    cd nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION}

# Build and install Nginx
# We want to build Nginx into a home folder to better comply with
# openshift security
RUN useradd -U -m nginx && \
    mkdir -p ${NGINX_HOME}/etc && \
    mkdir -p ${NGINX_HOME}/var/lock && \
    mkdir -p ${NGINX_HOME}/var/log && \
    mkdir -p ${NGINX_HOME}/var/run && \
    mkdir -p ${NGINX_HOME}/rec

RUN cd /tmp/build/nginx/${NGINX_VERSION} && \
    ./configure \
        --sbin-path=${NGINX_HOME} \
        --conf-path=${NGINX_HOME}/etc/nginx.conf \
        --error-log-path=${NGINX_HOME}/var/log/error.log \
        --pid-path=${NGINX_HOME}/var/run/nginx.pid \
        --lock-path=${NGINX_HOME}/var/lock/nginx.lock \
        --http-log-path=${NGINX_HOME}/var/log/access.log \
        --http-client-body-temp-path=/tmp/nginx-client-body \
        --with-http_ssl_module \
        --with-threads \
        --with-ipv6 \
        --add-module=/tmp/build/nginx-rtmp-module/nginx-rtmp-module-${NGINX_RTMP_MODULE_VERSION} && \
    make -j $(getconf _NPROCESSORS_ONLN) && \
    make install && \
    rm -rf /tmp/build

# Set up logs output to stdout
RUN ln -sf /dev/stdout ${NGINX_HOME}/var/log/access.log && \
    ln -sf /dev/stdout ${NGINX_HOME}/var/log/rtmp.access.log && \
    ln -sf /dev/stderr ${NGINX_HOME}/var/log/error.log

# Set up config file
COPY nginx.conf ${NGINX_HOME}/etc/nginx.conf
RUN chgrp -R 1000 ${NGINX_HOME} && \
    chmod -R g=u ${NGINX_HOME} && \
    chmod 777 ${NGINX_HOME}/rec

# Set up permissions of record file directory
USER nginx
EXPOSE 1935
CMD ["/home/nginx/nginx", "-g", "daemon off;"]

