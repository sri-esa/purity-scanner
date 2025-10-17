#!/bin/bash

# Purity Scanner Backend Setup Script
# Run this from your project root directory

echo "🚀 Setting up Purity Scanner Backend..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create backend directory structure
echo -e "${YELLOW}📁 Creating backend directory structure...${NC}"
mkdir -p backend/src/{config,middleware,routes,controllers,services}

# Navigate to backend directory
cd backend

# Initialize npm if package.json doesn't exist
if [ ! -f "package.json" ]; then
    echo -e "${YELLOW}📦 Initializing npm...${NC}"
    npm init -y
fi

# Update package.json to use ES modules
echo -e "${YELLOW}🔧 Configuring package.json...${NC}"
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
pkg.type = 'module';
pkg.scripts = {
  ...pkg.scripts,
  'start': 'node server.js',
  'dev': 'nodemon server.js'
};
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2));
"

# Install dependencies
echo -e "${YELLOW}📥 Installing dependencies...${NC}"
npm install express cors dotenv @supabase/supabase-js helmet express-rate-limit morgan

# Install dev dependencies
echo -e "${YELLOW}📥 Installing dev dependencies...${NC}"
npm install --save-dev nodemon

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    cat > .env << 'EOF'
# Server Configuration
PORT=3001
NODE_ENV=development

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_service_key_here

# CORS
CORS_ORIGIN=http://localhost:5173

# ML Service (optional - for future use)
ML_SERVICE_URL=http://localhost:5000
ML_SERVICE_API_KEY=
EOF
    echo -e "${GREEN}✅ .env file created. Please update with your Supabase credentials!${NC}"
fi

# Create .gitignore
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}📝 Creating .gitignore...${NC}"
    cat > .gitignore << 'EOF'
node_modules/
.env
.env.local
.DS_Store
*.log
dist/
build/
EOF
fi

cd ..

# Update frontend .env
echo -e "${YELLOW}🔧 Updating frontend .env...${NC}"
if ! grep -q "VITE_API_URL" .env 2>/dev/null; then
    echo "" >> .env
    echo "# Backend API" >> .env
    echo "VITE_API_URL=http://localhost:3001" >> .env
    echo -e "${GREEN}✅ Added VITE_API_URL to frontend .env${NC}"
fi

# Create README for backend
echo -e "${YELLOW}📝 Creating backend README...${NC}"
cat > backend/README.md << 'EOF'
# Purity Scanner Backend

Node.js + Express backend for Raman spectroscopy purity analysis.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables in `.env`:
- Add your Supabase URL and service key
- Update CORS_ORIGIN if needed

3. Run development server:
```bash
npm run dev
```

4. Run production server:
```bash
npm start
```

## API Endpoints

### Scans
- `POST /api/scans` - Create new scan
- `GET /api/scans/user/:userId` - Get user's scans
- `GET /api/scans/:scanId` - Get scan details
- `PATCH /api/scans/:scanId` - Update scan
- `DELETE /api/scans/:scanId` - Delete scan
- `POST /api/scans/analyze` - Analyze without saving

### Devices
- `POST /api/devices` - Register device
- `GET /api/devices/user/:userId` - Get user's devices
- `PATCH /api/devices/:deviceId` - Update device
- `DELETE /api/devices/:deviceId` - Delete device
- `POST /api/devices/:deviceId/heartbeat` - Update device last_seen

### Analytics
- `GET /api/analytics/stats/:userId` - Get user statistics
- `GET /api/analytics/trends/:userId` - Get scan trends
- `GET /api/analytics/activity/:userId` - Get recent activity
- `GET /api/analytics/flagged/:userId` - Get flagged scans

## Environment Variables

```env
PORT=3001
NODE_ENV=development
SUPABASE_URL=your_url
SUPABASE_SERVICE_KEY=your_key
CORS_ORIGIN=http://localhost:5173
```

## Project Structure

```
backend/
├── src/
│   ├── config/
│   │   └── supabase.js
│   ├── middleware/
│   │   ├── auth.js
│   │   └── errorHandler.js
│   ├── routes/
│   │   ├── scans.js
│   │   ├── devices.js
│   │   └── analytics.js
│   ├── controllers/
│   │   └── scanController.js
│   └── services/
│       └── mlService.js
├── server.js
├── package.json
└── .env
```
EOF

echo ""
echo -e "${GREEN}✅ Backend setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update backend/.env with your Supabase credentials"
echo "2. Run the SQL schema in your Supabase dashboard"
echo "3. Copy the backend files from the artifacts"
echo "4. Start backend: cd backend && npm run dev"
echo "5. Start frontend: npm run dev"
echo ""
echo -e "${GREEN}🎉 Happy coding!${NC}"