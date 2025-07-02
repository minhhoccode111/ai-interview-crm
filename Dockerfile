# 🐳 AI Interview CRM Platform - Dockerfile
# Production-ready containerization for the AI-powered interview platform

FROM python:3.9-slim

# 📋 Set metadata
LABEL maintainer="AI Interview CRM Team"
LABEL version="1.0.0"
LABEL description="AI-powered interview practice platform with Google Gemini and OpenAI Whisper"

# 🔧 Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    DEBIAN_FRONTEND=noninteractive

# 📁 Create app directory
WORKDIR /app

# 🏗️ Install system dependencies
RUN apt-get update && apt-get install -y \
    # Audio processing
    ffmpeg \
    # PDF processing
    poppler-utils \
    # System utilities
    curl \
    git \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 📦 Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 👤 Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 📁 Copy application code
COPY . .

# 🔒 Set proper permissions
RUN mkdir -p /app/static/uploads /app/instance && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# 🗄️ Initialize database directory
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# 👤 Switch to non-root user
USER appuser

# 🌐 Expose port
EXPOSE 5000

# 🔧 Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

# 📊 Add startup script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# 🚀 Start the application
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
