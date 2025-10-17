// backend/src/config/supabase.js
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.SUPABASE_URL || process.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || process.env.VITE_SUPABASE_PUBLISHABLE_KEY;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

let supabase = undefined;
let supabaseAuth = undefined;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  // eslint-disable-next-line no-console
  console.warn('[backend] Supabase environment variables are missing. API routes will be disabled until configured.');
} else {
  // Admin client for database operations (bypasses RLS). Prefer service role if provided.
  supabase = createClient(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY || SUPABASE_ANON_KEY
  );

  // Public auth client for verifying user tokens
  supabaseAuth = createClient(
    SUPABASE_URL,
    SUPABASE_ANON_KEY
  );
}

export { supabase, supabaseAuth };


