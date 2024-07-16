#!/bin/bash
#set -e

# Define the full path to the docker-compose directory
#COMPOSE_DIR="/opt/via/deployment/docker_compose"

# Change to the directory where docker-compose.dev.yml is located
#cd $COMPOSE_DIR

# Use the full path to Docker Compose and specify the full path to the compose file
#/usr/local/bin/docker-compose -f $COMPOSE_DIR/docker-compose.dev.yml down
#/usr/local/bin/docker-compose -f $COMPOSE_DIR/docker-compose.dev.yml -p danswer-stack up -d --build

# Load the saved state
#python3 /opt/via/backend/scripts/save_load_state.py --load --postgres_containter_name relational_dbhn --checkpoint_dir /opt/via/checkpoints

#!/bin/bash
set -e

# Define the full path to the docker-compose directory
COMPOSE_DIR="/opt/via/deployment/docker_compose"

# Log the start of the script
echo "Starting start_server.sh script" | tee -a /tmp/start_server.log

# Change to the directory where docker-compose.dev.yml is located
cd $COMPOSE_DIR

# Use the full path to Docker Compose and specify the full path to the compose file
echo "Bringing down existing Docker Compose services" | tee -a /tmp/start_server.log
/usr/local/bin/docker-compose -f $COMPOSE_DIR/docker-compose.dev.yml down 2>&1 | tee -a /tmp/start_server.log

echo "Bringing up Docker Compose services" | tee -a /tmp/start_server.log
/usr/local/bin/docker-compose -f $COMPOSE_DIR/docker-compose.dev.yml -p danswer-stack up -d --build 2>&1 | tee -a /tmp/start_server.log

# Load the saved state
echo "Loading saved state" | tee -a /tmp/start_server.log
python3 /opt/via/backend/scripts/save_load_state.py --load --postgres_container_name relational_db --checkpoint_dir /opt/via/checkpoints 2>&1 | tee -a /tmp/start_server.log

# Log the end of the script
echo "Completed start_server.sh script" | tee -a /tmp/start_server.log
