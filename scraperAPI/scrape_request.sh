#!/bin/bash

# Check if both URL and push_to_git arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <URL> <push_to_git>"
    exit 1
fi

# Extract URL and push_to_git from command line arguments
URL=$1
push_to_repo=$2
api_key="1234"

# Create a JSON payload
JSON_PAYLOAD="{\"url\":\"$URL\",\"push_to_repo\":$push_to_repo,\"key\":\"$api_key\"}"

# Send POST request with JSON payload using curl
curl -X POST -H "Content-Type: application/json" -d "$JSON_PAYLOAD" http://localhost:5000/scrape