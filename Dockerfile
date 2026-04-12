# Stage 1: Get the static FFmpeg binary
FROM mwader/static-ffmpeg:6.0 AS ffmpeg-source

# Stage 2: Use the official n8n image (Debian version for better script compatibility)
FROM n8nio/n8n:latest-debian

# Copy the binary from the first stage
COPY --from=ffmpeg-source /ffmpeg /usr/local/bin/
COPY --from=ffmpeg-source /ffprobe /usr/local/bin/

# Copy workflow files for automatic import
COPY youtube-ai-factory-workflow.json /home/node/
COPY youtube-ai-factory-analytics-loop.json /home/node/

# Setup startup script
COPY start.sh /usr/local/bin/start.sh
USER root
RUN sed -i 's/\r$//' /usr/local/bin/start.sh && chmod +x /usr/local/bin/start.sh
USER node
EXPOSE 5678

ENTRYPOINT ["/usr/local/bin/start.sh"]
