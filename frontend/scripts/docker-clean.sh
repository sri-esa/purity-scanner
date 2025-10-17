#!/bin/bash

# Docker cleanup script for Purity Vision Lab
echo "🧹 Cleaning up Docker resources..."

# Stop and remove containers
echo "🛑 Stopping containers..."
docker-compose down

# Remove unused images
echo "🗑️ Removing unused images..."
docker image prune -f

# Remove unused volumes
echo "🗑️ Removing unused volumes..."
docker volume prune -f

# Remove unused networks
echo "🗑️ Removing unused networks..."
docker network prune -f

echo "✅ Docker cleanup completed!"
echo "💡 Run 'docker system df' to see space usage"
