#!/bin/bash

# Development Docker script for Purity Vision Lab
echo "🧪 Starting Purity Vision Lab Development Environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your environment variables."
    echo "📝 See SETUP_INSTRUCTIONS.md for details."
    exit 1
fi

# Build and run development container
echo "🔨 Building development container..."
docker-compose up --build purity-vision-dev

echo "✅ Development environment started!"
echo "🌐 Application available at: http://localhost:5173"
echo "📊 Supabase Dashboard: https://supabase.com/dashboard"
