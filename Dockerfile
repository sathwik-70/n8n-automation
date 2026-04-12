# Stage 1: Get the static FFmpeg binary
FROM mwader/static-ffmpeg:6.0 AS ffmpeg-source

# Stage 2: Use the official n8n image
FROM n8nio/n8n:latest

# Copy the binary from the first stage
COPY --from=ffmpeg-source /ffmpeg /usr/local/bin/
COPY --from=ffmpeg-source /ffprobe /usr/local/bin/

# Ensure the node user is correctly set
USER node

EXPOSE 5678
