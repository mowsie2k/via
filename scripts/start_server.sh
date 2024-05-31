#!/bin/bash
set -e

cd /opt/via/deployment/docker_compose

# Use the full path to Docker Compose
/usr/local/bin/docker-compose down
/usr/local/bin/docker-compose -f docker-compose.dev.yml -p danswer-stack up -d --build --force-recreate
