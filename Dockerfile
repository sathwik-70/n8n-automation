# ── Base: official n8n image (Alpine-based) ──────────────────────────────────
FROM n8nio/n8n:latest

# Switch to root to install system packages
USER root

# Install FFmpeg + dependencies for merge server
# n8nio/n8n:latest is Debian-based, so we use apt
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Create app directory for merge server
WORKDIR /merge

# Copy merge server source
COPY merge_server.js .
COPY package.json .

# Install Express + Multer (merge server deps only)
RUN npm install --production

# Copy startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Drop back to n8n's default non-root user for security
USER node

# Expose n8n (5678) — merge server listens on 3000 internally (not exposed externally)
EXPOSE 5678

CMD ["/start.sh"]
