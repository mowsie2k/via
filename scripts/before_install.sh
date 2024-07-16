#!/bin/bash
#set -e

# Save the current state
#python3 /opt/via/backend/scripts/save_load_state.py --save --postgres_container_name relational_db --checkpoint_dir /opt/via/checkpoints

# Install Docker if not installed
#if ! command -v docker &> /dev/null
#then
#    sudo yum update -y
#    sudo yum install -y docker
#    sudo service docker start
#fi

# Install Docker Compose if not installed
#if ! command -v docker-compose &> /dev/null
#then
#    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
#    sudo chmod +x /usr/local/bin/docker-compose
#fi

#!/bin/bash
set -e

# Log the start of the script
echo "Starting before_install.sh script" | tee -a /tmp/before_install.log

# Save the current state
#echo "Saving current state" | tee -a /tmp/before_install.log
#python3 /opt/via/backend/scripts/save_load_state.py --save --postgres_container_name relational_db --checkpoint_dir /opt/via/checkpoints 2>&1 | tee -a /tmp/before_install.log

# Install Docker if not installed
if ! command -v docker &> /dev/null
then
    echo "Installing Docker" | tee -a /tmp/before_install.log
    sudo yum update -y 2>&1 | tee -a /tmp/before_install.log
    sudo yum install -y docker 2>&1 | tee -a /tmp/before_install.log
    sudo service docker start 2>&1 | tee -a /tmp/before_install.log
else
    echo "Docker is already installed" | tee -a /tmp/before_install.log
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null
then
    echo "Installing Docker Compose" | tee -a /tmp/before_install.log
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose 2>&1 | tee -a /tmp/before_install.log
    sudo chmod +x /usr/local/bin/docker-compose 2>&1 | tee -a /tmp/before_install.log
else
    echo "Docker Compose is already installed" | tee -a /tmp/before_install.log
fi

# Log the end of the script
echo "Completed before_install.sh script" | tee -a /tmp/before_install.log
