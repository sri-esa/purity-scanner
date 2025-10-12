# 🐳 Docker Quick Start - Purity Vision Lab

## 🚀 Get Started in 3 Steps

### 1. Set Up Environment Variables
```bash
# Create .env file with your Supabase credentials
cp .env.example .env
# Edit .env with your actual values
```

### 2. Start Development Environment
```bash
# Option 1: Using npm scripts
npm run docker:dev

# Option 2: Using docker-compose directly
docker-compose up --build purity-vision-dev
```

### 3. Access Your Application
- **Development:** http://localhost:5173
- **Health Check:** http://localhost:80/health

## 🔧 Available Commands

```bash
# Development
npm run docker:dev          # Start development environment
npm run docker:clean        # Clean up Docker resources

# Production
npm run docker:prod         # Start production environment
npm run docker:build        # Build production image
npm run docker:run          # Run production container

# Manual Docker commands
docker-compose up --build purity-vision-dev     # Development
docker-compose --profile production up --build  # Production
docker-compose down                              # Stop all containers
docker-compose logs -f                          # View logs
```

## 📁 What's Included

✅ **Multi-stage Dockerfile** - Optimized production builds  
✅ **Docker Compose** - Easy development and production setup  
✅ **Nginx Configuration** - Production-ready web server  
✅ **Security Headers** - XSS protection, CSP, and more  
✅ **Health Checks** - Container and application monitoring  
✅ **Gzip Compression** - Optimized asset delivery  
✅ **Hot Reload** - Development with live code updates  
✅ **Environment Variables** - Secure configuration management  

## 🎯 Your Docker Setup is Ready!

Your Purity Vision Lab application now has:
- **Development environment** with hot reload
- **Production environment** with Nginx
- **Security features** and optimizations
- **Easy deployment** scripts
- **Comprehensive documentation**

Start building your chemical purity analysis platform! 🧪✨
