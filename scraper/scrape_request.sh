#!/bin/bash

# Check if URL argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

# Extract URL from command line arguments
URL=$1

# Define the request body
REQUEST_BODY="request_body=$URL"

# Send POST request using curl
curl -X POST -d "$REQUEST_BODY" http://localhost:8080/scrape
