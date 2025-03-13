#!/bin/bash
set -e

cleanup() {
    echo "Stopping containers..."
    docker stop flemmarr-sonarr flemmarr-radarr flemmarr-tests >/dev/null 2>&1 || true
    docker network rm test-network
}

trap cleanup EXIT SIGINT SIGTERM

docker network create test-network

echo "Starting Sonarr and Radarr containers..."
docker run -d --rm \
    --name flemmarr-sonarr \
    --network test-network \
    --health-cmd "curl --fail http://localhost:8989 || exit 1" \
    -e PUID=1000 \
    -e PGID=1000 \
    -p 8989:8989 \
    lscr.io/linuxserver/sonarr

docker run -d --rm \
    --name flemmarr-radarr \
    --network test-network \
    --health-cmd "curl --fail http://localhost:7878 || exit 1" \
    -e PUID=1000 \
    -e PGID=1000 \
    -p 7878:7878 \
    lscr.io/linuxserver/radarr

echo "Building test image..."
docker build -t flemmarr-tests -f tests.Dockerfile .

echo "Running tests..."
docker run --rm \
    --name flemmarr-tests \
    --network test-network \
    -e CONFIG_PATH=./tests/data/config.yaml \
    flemmarr-tests

cleanup
