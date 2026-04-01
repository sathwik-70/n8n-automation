FROM n8nio/n8n:latest

USER root

# Install Python for thumbnail generation
RUN apk add --no-cache python3 py3-pip

# Copy workflow files
WORKDIR /home/node

EXPOSE 5678

CMD ["n8n", "start"]
