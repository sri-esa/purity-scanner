// backend/index.js
import dotenv from 'dotenv';
// Load env from backend/.env first, then fallback to repo root .env; override empty compose vars
dotenv.config({ path: './.env', override: true });
dotenv.config({ path: '../.env', override: true });

import express from 'express';
import morgan from 'morgan';
import helmet from 'helmet';
import cors from 'cors';
import rateLimit from 'express-rate-limit';
import devicesRouter from './src/routes/devices.js';
import analyticsRouter from './src/routes/analytics.js';
import scansRouter from './src/routes/scans.js';
import sessionsRouter from './src/routes/sessions.js';
import { supabase, supabaseAuth } from './src/config/supabase.js';
import { errorHandler } from './src/middleware/errorHandler.js';

const app = express();

// Log which env keys are visible to the process (lengths only)
// eslint-disable-next-line no-console
console.log('[backend] Env check:', {
  SUPABASE_URL: !!process.env.SUPABASE_URL || !!process.env.VITE_SUPABASE_URL,
  SUPABASE_ANON_KEY_LEN: (process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_PUBLISHABLE_KEY || '').length,
  HAS_SERVICE_ROLE: !!process.env.SUPABASE_SERVICE_ROLE_KEY,
});

app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.use(morgan('dev'));

const apiLimiter = rateLimit({ windowMs: 60 * 1000, max: 120 });
app.use('/api/', apiLimiter);

app.get('/health', (req, res) => res.status(200).send('ok'));

// Env diagnostics (no secrets) to verify runtime config
app.get('/env-check', (req, res) => {
  res.json({
    SUPABASE_URL: !!(process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL),
    SUPABASE_ANON_KEY_LEN: (process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_PUBLISHABLE_KEY || '').length,
    HAS_SERVICE_ROLE: !!process.env.SUPABASE_SERVICE_ROLE_KEY,
    CWD: process.cwd(),
  });
});

// Root route - API information
app.get('/', (req, res) => {
  const supabaseConfigured = !!(supabase && supabaseAuth);
  res.json({
    name: 'Backend API',
    version: '1.0.0',
    status: 'running',
    supabase: supabaseConfigured ? 'configured' : 'not configured',
    endpoints: {
      health: '/health',
      envCheck: '/env-check',
      devices: supabaseConfigured ? '/api/devices' : 'unavailable (configure Supabase)',
      analytics: supabaseConfigured ? '/api/analytics' : 'unavailable (configure Supabase)',
      scans: supabaseConfigured ? '/api/scans' : 'unavailable (configure Supabase)',
      sessions: supabaseConfigured ? '/api/sessions' : 'unavailable (configure Supabase)'
    },
    timestamp: new Date().toISOString(),
  });
});

// Only mount API routes if Supabase is configured
if (supabase && supabaseAuth) {
  app.use('/api/devices', devicesRouter);
  app.use('/api/analytics', analyticsRouter);
  app.use('/api/scans', scansRouter);
  app.use('/api/sessions', sessionsRouter);
} else {
  app.use('/api', (req, res) => {
    res.status(503).json({ error: 'Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.' });
  });
}

// 404 handler - must be after all other routes
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`,
    hint: 'Visit / for available endpoints',
  });
});

app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`Backend listening on port ${PORT}`);
});