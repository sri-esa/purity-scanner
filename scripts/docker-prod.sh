#!/bin/bash

# Production Docker script for Purity Vision Lab
echo "🚀 Building Purity Vision Lab Production Image..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your environment variables."
    exit 1
fi

# Build production image
echo "🔨 Building production container..."
docker-compose --profile production up --build -d purity-vision-prod

echo "✅ Production environment started!"
echo "🌐 Application available at: http://localhost:80"
echo "📊 Health check: http://localhost:80/health"

# Show container status
echo "📋 Container status:"
docker-compose ps
