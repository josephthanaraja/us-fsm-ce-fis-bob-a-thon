FROM node:22-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl bash tar jq git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Bob Shell
RUN curl -s https://s3.us-south.cloud-object-storage.appdomain.cloud/bobshell/install-bobshell.sh | bash -s -- --pm npm

# Set environment variables
ENV BOB_ACCEPT_LICENSE=true \
    HOME=/workspace

# Create workspace directory with OpenShift-compatible permissions
# Use group 0 (root group) with group permissions matching user permissions
RUN mkdir -p /workspace/.bob && \
    chgrp -R 0 /workspace && \
    chmod -R g=u /workspace

# Set working directory (will be overridden by pod spec, but good default)
WORKDIR /workspace

# Keep container running
CMD ["sleep", "infinity"]
