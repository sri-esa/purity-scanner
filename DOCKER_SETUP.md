# 🐳 Docker Setup for Purity Vision Lab

This guide will help you set up Docker for your Purity Vision Lab application, enabling easy development and deployment.

## 📋 Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Node.js** (version 18+) - for local development
- **Environment variables** configured in `.env` file

## 🚀 Quick Start

### 1. Development Environment

```bash
# Start development environment
npm run docker:dev

# Or manually
docker-compose up --build purity-vision-dev
```

**Access your app at:** `http://localhost:5173`

### 2. Production Environment

```bash
# Start production environment
npm run docker:prod

# Or manually
docker-compose --profile production up --build -d purity-vision-prod
```

**Access your app at:** `http://localhost:80`

## 🔧 Docker Commands

### Development Commands

```bash
# Start development with hot reload
npm run docker:dev

# Build development image
docker build -f Dockerfile.dev -t purity-vision-dev .

# Run development container
docker run -p 5173:5173 -v $(pwd):/app purity-vision-dev
```

### Production Commands

```bash
# Build production image
npm run docker:build

# Run production container
npm run docker:run

# Build and run with docker-compose
docker-compose --profile production up --build
```

### Utility Commands

```bash
# Clean up Docker resources
npm run docker:clean

# View running containers
docker-compose ps

# View logs
docker-compose logs purity-vision-dev
docker-compose logs purity-vision-prod

# Stop all containers
docker-compose down
```

## 📁 Docker Files Structure

```
purity-vision-lab/
├── Dockerfile              # Production multi-stage build
├── Dockerfile.dev          # Development build
├── docker-compose.yml      # Docker Compose configuration
├── nginx.conf              # Nginx configuration
├── .dockerignore           # Docker ignore file
└── scripts/
    ├── docker-dev.sh       # Development script
    ├── docker-prod.sh      # Production script
    └── docker-clean.sh     # Cleanup script
```

## 🏗️ Docker Architecture

### Development Setup
- **Base Image:** Node.js 18 Alpine
- **Port:** 5173 (Vite dev server)
- **Volume Mounting:** Live code reloading
- **Environment:** Development mode

### Production Setup
- **Multi-stage Build:** Optimized for production
- **Base Image:** Nginx Alpine
- **Port:** 80 (HTTP)
- **Static Files:** Pre-built React app
- **Security:** Nginx security headers

## 🔒 Security Features

### Nginx Security Headers
- **X-Frame-Options:** SAMEORIGIN
- **X-XSS-Protection:** 1; mode=block
- **X-Content-Type-Options:** nosniff
- **Content-Security-Policy:** Strict CSP
- **Referrer-Policy:** no-referrer-when-downgrade

### Docker Security
- **Non-root user:** Nginx runs as non-root
- **Minimal base image:** Alpine Linux
- **No unnecessary packages:** Optimized image size
- **Health checks:** Container health monitoring

## 📊 Performance Optimizations

### Build Optimizations
- **Multi-stage builds:** Separate build and runtime
- **Layer caching:** Optimized Docker layers
- **Gzip compression:** Enabled in Nginx
- **Static asset caching:** 1-year cache for assets

### Runtime Optimizations
- **Nginx reverse proxy:** Efficient request handling
- **Client-side routing:** SPA routing support
- **Asset optimization:** Minified and compressed
- **Memory efficiency:** Alpine Linux base

## 🌐 Environment Variables

Create a `.env` file with the following variables:

```env
# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Application Configuration
VITE_APP_URL=http://localhost:5173

# Social Auth (Optional)
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_client_secret
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_CLIENT_SECRET=your_github_client_secret
```

## 🚀 Deployment Options

### Local Development
```bash
npm run docker:dev
```

### Production Deployment
```bash
npm run docker:prod
```

### Cloud Deployment
```bash
# Build for cloud deployment
docker build -t purity-vision-lab:latest .

# Push to registry
docker tag purity-vision-lab:latest your-registry/purity-vision-lab:latest
docker push your-registry/purity-vision-lab:latest
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change ports in docker-compose.yml
   ports:
     - "3000:5173"  # Use different host port
   ```

2. **Environment variables not loading:**
   ```bash
   # Check .env file exists and has correct format
   cat .env
   ```

3. **Build failures:**
   ```bash
   # Clean Docker cache
   docker system prune -a
   npm run docker:clean
   ```

4. **Permission issues:**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh
   ```

### Debug Commands

```bash
# View container logs
docker-compose logs -f purity-vision-dev

# Access container shell
docker-compose exec purity-vision-dev sh

# Check container status
docker-compose ps

# View resource usage
docker stats
```

## 📈 Monitoring

### Health Checks
- **Health endpoint:** `http://localhost:80/health`
- **Container health:** Docker health checks
- **Application status:** Built-in health monitoring

### Logs
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs purity-vision-prod
```

## 🎯 Best Practices

1. **Use .dockerignore:** Optimize build context
2. **Multi-stage builds:** Separate build and runtime
3. **Security headers:** Implement proper security
4. **Health checks:** Monitor container health
5. **Resource limits:** Set appropriate limits
6. **Environment variables:** Secure configuration
7. **Regular updates:** Keep base images updated

## 🚀 Next Steps

1. **Set up your environment variables**
2. **Run the development environment:** `npm run docker:dev`
3. **Test your application:** `http://localhost:5173`
4. **Deploy to production:** `npm run docker:prod`
5. **Monitor and maintain:** Use the provided scripts

Your Purity Vision Lab application is now Docker-ready! 🧪✨
