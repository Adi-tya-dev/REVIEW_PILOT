# Hardened, isolated Docker sandbox for ReviewPilot pytest execution
FROM python:3.11-slim

# Prevent python from writing pyc files and buffer output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install testing dependencies
RUN pip install --no-cache-dir pytest>=8.0.0 pytest-cov>=5.0.0

# Create unprivileged runner user
RUN groupadd -g 1000 sandboxgroup && \
    useradd -u 1000 -g sandboxgroup -m -s /bin/bash sandboxuser

# Prepare workspace
WORKDIR /workspace
RUN chown -R sandboxuser:sandboxgroup /workspace

USER sandboxuser

# Default execution entrypoint
CMD ["pytest", "-v", "--tb=short"]

