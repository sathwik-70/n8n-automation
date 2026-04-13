# ── Base: Standard Node.js (Debian Bullseye) ──────────────────────────────────
FROM node:18-bullseye-slim

# Switch to root to install system packages
USER root

# Install FFmpeg and build dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install n8n globally
RUN npm install -g n8n@latest

# Create app directory for merge server
WORKDIR /merge

# Copy merge server source
COPY merge_server.js .
COPY package.json .

# Install merge server dependencies
RUN npm install --production

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Use the 'node' user provided by the base image
USER node

# Expose n8n port
EXPOSE 5678

CMD ["/start.sh"]
