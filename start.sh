#!/bin/sh
# start.sh — Starts both the FFmpeg merge server and n8n together

set -e

echo "==> Starting FFmpeg merge server on port 3000..."
node /merge/merge_server.js &

echo "==> Starting n8n on port 5678..."
# Use exec so n8n becomes PID 1 and receives Docker signals correctly
exec n8n start
