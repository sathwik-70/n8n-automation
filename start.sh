#!/bin/sh
# Import the workflow into the n8n database
n8n import:workflow --separate --input=/home/node/youtube-ai-factory-workflow.json

# Start n8n
n8n start
