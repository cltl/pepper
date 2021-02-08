FROM adoptopenjdk/openjdk11:alpine

# Build time arguments
ARG version=9.3.1
ARG graphdb_parent=/opt/graphdb

ENV GRAPHDB_PARENT_DIR="$graphdb_parent"
ENV GRAPHDB_HOME="${GRAPHDB_PARENT_DIR}/home"

ENV GRAPHDB_INSTALL_DIR=${GRAPHDB_PARENT_DIR}/dist

ADD lib/graphdb-free-${version}-dist.zip /tmp/

RUN apk add --no-cache bash util-linux procps net-tools busybox-extras wget less curl && \
    mkdir -p "${GRAPHDB_PARENT_DIR}" && \
    cd "${GRAPHDB_PARENT_DIR}" && \
    unzip "/tmp/graphdb-free-${version}-dist.zip" && \
    rm "/tmp/graphdb-free-${version}-dist.zip" && \
    mv "graphdb-free-${version}" dist && \
    mkdir -p "${GRAPHDB_HOME}"

ENV PATH="${GRAPHDB_INSTALL_DIR}/bin:$PATH"

CMD graphdb -Dgraphdb.home="$GRAPHDB_HOME"

EXPOSE 7200
