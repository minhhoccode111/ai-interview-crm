#!/bin/bash

# 🚀 AI Interview CRM Platform - Docker Entrypoint Script
# Handles database initialization and application startup

set -e

echo "🎯 Starting AI Interview CRM Platform..."

# 🔍 Check if required environment variables are set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not set. AI features may not work."
fi

# 🗄️ Initialize database if it doesn't exist
if [ ! -f "/app/data/interview.db" ]; then
    echo "🗄️  Initializing database..."
    python -c "
from models.db import init_db
from app import create_app
app = create_app()
with app.app_context():
    init_db(app)
    print('✅ Database initialized successfully!')
"
fi

# 🧪 Run basic health check
echo "🔍 Running system health check..."
python -c "
import sys
try:
    from app import create_app
    app = create_app()
    print('✅ Application imports successful')
except Exception as e:
    print(f'❌ Application health check failed: {e}')
    sys.exit(1)
"

echo "🚀 Starting application with command: $@"

# 🎯 Execute the main command
exec "$@"
