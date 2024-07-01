#!/bin/bash
set -e

# Validate service
curl -Lsf -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36" http://ec2-3-135-194-173.us-east-2.compute.amazonaws.com/auth/login || exit 1
