#!/bin/bash
set -e

# Define the full path to the docker-compose directory
COMPOSE_DIR="/opt/via/deployment/docker_compose"

# Change to the directory where docker-compose.dev.yml is located
cd $COMPOSE_DIR

# Use the full path to Docker Compose and specify the full path to the compose file
/usr/local/bin/docker-compose -f $COMPOSE_DIR/docker-compose.dev.yml down
/usr/local/bin/docker-compose -f $COMPOSE_DIR/docker-compose.dev.yml -p danswer-stack up -d --build

# Load the saved state
python /opt/via/backend/scripts/save_load_state.py --load --postgres_containter_name relational_dbhn --checkpoint_dir /opt/via/checkpoints
