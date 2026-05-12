# Code Execution Sandbox - Multi-language runtime environment
FROM python:3.11-slim

# Install Node.js and other runtime dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for code execution
RUN useradd -m -u 1000 sandbox && \
    mkdir -p /app /sandbox && \
    chown -R sandbox:sandbox /sandbox

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sandbox_server/ ./sandbox_server/
COPY main.py .

# Switch to non-root user
RUN chown -R sandbox:sandbox /app
USER sandbox

# Expose port
EXPOSE 8080

ENV PORT=8080
ENV HOST=0.0.0.0

# Run the server
CMD ["python", "main.py"]