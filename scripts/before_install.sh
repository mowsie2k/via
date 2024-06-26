#!/bin/bash
set -e

# Install Docker if not installed
if ! command -v docker &> /dev/null
then
    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null
then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi
