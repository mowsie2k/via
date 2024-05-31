#!/bin/bash
set -e

cd /opt/via/deployment/docker_compose

# Run Docker Compose to start the application
docker-compose down
docker-compose -f docker-compose.dev.yml -p danswer-stack up -d --build --force-recreate
