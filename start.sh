#!/bin/bash
set -x

echo "--- Starting n8n Recovery Script ---"

# Move workflows to a dedicated directory for robust import
mkdir -p /home/node/workflows
cp /home/node/*.json /home/node/workflows/

echo "Waiting for database to initialize..."
sleep 10

echo "Executing CLI workflow import..."
# Retry import a few times in case DB is still booting
for i in {1..5}; do
  n8n import:workflow --separate --input /home/node/workflows/ && break || { echo "DB not ready, retrying ($i/5)..."; sleep 5; }
done

# Start n8n
echo "Starting n8n server..."
exec n8n start
