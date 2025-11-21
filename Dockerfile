FROM kjarosh/latex:latest

# Install Python and dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml .
COPY README.md .
COPY latex_server/ latex_server/

# Install the package
RUN pip3 install --no-cache-dir --break-system-packages .

# Create non-root user for security
RUN adduser -D -u 1000 latexuser && \
    chown -R latexuser:latexuser /app

USER latexuser

# Expose port
EXPOSE 9080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9080/')" || exit 1

# Run the application using the installed CLI command
CMD ["latex-server"]
