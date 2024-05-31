#!/bin/bash
set -e

# Validate service
curl -f http://localhost || exit 1
