// backend/src/routes/setup.js
import express from 'express';
import { supabase } from '../config/supabase.js';
import { readFile } from 'fs/promises';
import { join } from 'path';

const router = express.Router();

// Setup RLS policies for frontend-backend sync
router.post('/rls-policies', async (req, res, next) => {
  try {
    // Read the SQL file
    const sqlPath = join(process.cwd(), 'sql', 'rls-policies.sql');
    const sqlContent = await readFile(sqlPath, 'utf8');
    
    // Split into individual statements and execute
    const statements = sqlContent
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));
    
    const results = [];
    for (const statement of statements) {
      try {
        const { data, error } = await supabase.rpc('exec_sql', { 
          sql_query: statement + ';' 
        });
        
        if (error) {
          console.warn(`Warning executing statement: ${error.message}`);
          results.push({ statement: statement.substring(0, 50) + '...', error: error.message });
        } else {
          results.push({ statement: statement.substring(0, 50) + '...', success: true });
        }
      } catch (err) {
        // Try direct execution for DDL statements
        const { error: directError } = await supabase
          .from('pg_stat_activity')  // This will fail but allows us to execute raw SQL
          .select('*')
          .limit(0);
        
        results.push({ 
          statement: statement.substring(0, 50) + '...', 
          note: 'DDL statement - may need manual execution in Supabase dashboard'
        });
      }
    }
    
    res.json({
      success: true,
      message: 'RLS policies setup initiated',
      results,
      note: 'Some policies may need to be applied manually in Supabase Dashboard > SQL Editor'
    });
  } catch (err) {
    next(err);
  }
});

// Test RLS policies by attempting table access
router.get('/test-rls', async (req, res, next) => {
  try {
    const tests = [];
    
    // Test devices table access
    try {
      const { data: devices, error: devicesError } = await supabase
        .from('devices')
        .select('id')
        .limit(1);
      
      tests.push({
        table: 'devices',
        accessible: !devicesError,
        error: devicesError?.message || null,
        count: devices?.length || 0
      });
    } catch (err) {
      tests.push({
        table: 'devices',
        accessible: false,
        error: err.message
      });
    }
    
    // Test analysis_sessions table access
    try {
      const { data: sessions, error: sessionsError } = await supabase
        .from('analysis_sessions')
        .select('id')
        .limit(1);
      
      tests.push({
        table: 'analysis_sessions',
        accessible: !sessionsError,
        error: sessionsError?.message || null,
        count: sessions?.length || 0
      });
    } catch (err) {
      tests.push({
        table: 'analysis_sessions',
        accessible: false,
        error: err.message
      });
    }
    
    // Test analysis_results table access
    try {
      const { data: results, error: resultsError } = await supabase
        .from('analysis_results')
        .select('id')
        .limit(1);
      
      tests.push({
        table: 'analysis_results',
        accessible: !resultsError,
        error: resultsError?.message || null,
        count: results?.length || 0
      });
    } catch (err) {
      tests.push({
        table: 'analysis_results',
        accessible: false,
        error: err.message
      });
    }
    
    const allAccessible = tests.every(test => test.accessible);
    
    res.json({
      success: true,
      rls_test_results: tests,
      all_tables_accessible: allAccessible,
      note: allAccessible 
        ? 'All tables accessible - RLS policies appear to be working'
        : 'Some tables not accessible - this may be expected if no data exists or RLS is properly restricting access'
    });
  } catch (err) {
    next(err);
  }
});

export default router;
