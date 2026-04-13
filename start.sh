#!/bin/bash
set -x

echo "--- Starting n8n Deployment Script ---"

# Step 1: Wait for PostgreSQL to be reachable (Internal Network)
echo "Probing PostgreSQL at ${DB_POSTGRESDB_HOST}:${DB_POSTGRESDB_PORT}..."
# Max wait: 60 seconds (12 attempts * 5s)
for i in {1..12}; do
  # Use bash builtin to test TCP connection
  if timeout 5 bash -c "cat < /dev/null > /dev/tcp/${DB_POSTGRESDB_HOST}/${DB_POSTGRESDB_PORT}" 2>/dev/null; then
    echo "PostgreSQL is reachable! Proceeding with import..."
    break
  fi
  echo "Database not ready yet, retrying ($i/12)..."
  sleep 5
done

# Step 2: Push workflows to n8n via CLI
mkdir -p /home/node/workflows
cp /home/node/*.json /home/node/workflows/
echo "Executing CLI workflow import..."
n8n import:workflow --separate --input /home/node/workflows/ || echo "Import warning: CLI import encountered an issue."

# Step 3: Start n8n Server
echo "Starting n8n..."
exec n8n start
