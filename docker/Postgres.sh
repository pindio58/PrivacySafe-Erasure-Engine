#!/usr/bin/env bash
set -e

docker run --name pg-client -e POSTGRES_HOST_AUTH_METHOD=trust -d postgres:17.6