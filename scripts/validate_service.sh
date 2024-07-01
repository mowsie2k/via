#!/bin/bash
set -e

# Validate service
curl -Ls http://localhost || exit 1
