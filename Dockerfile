# MoltLang MCP Server - Dockerfile for Railway deployment
FROM node:22-bookworm

# Install Python3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the entire project (Python source + MCP server)
COPY src ./src
COPY mcp-server/package*.json ./mcp-server/
COPY mcp-server/tsconfig.json ./mcp-server/
COPY mcp-server/src ./mcp-server/src

# Install Python dependencies (pydantic, typing-extensions)
RUN pip3 install --no-cache-dir --break-system-packages pydantic typing-extensions

# Install Node.js dependencies
RUN cd mcp-server && npm ci

# Build TypeScript
RUN cd mcp-server && npm run build

# Expose port
EXPOSE 8080

# Set environment variables
ENV NODE_ENV=production
ENV PORT=8080
ENV PYTHONPATH=/app/src

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8080/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the server
WORKDIR /app/mcp-server
CMD ["npm", "run", "start:http"]
