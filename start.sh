#!/bin/bash
set -x

echo "--- Starting n8n Recovery Script ---"

# Move workflows to a dedicated directory for robust import
mkdir -p /home/node/workflows
cp /home/node/*.json /home/node/workflows/

echo "Importing workflows from /home/node/workflows/..."
n8n import:workflow --separate --input /home/node/workflows/ || echo "Import warning: Some workflows might not have imported correctly."

# Start n8n
echo "Starting n8n server..."
n8n start
