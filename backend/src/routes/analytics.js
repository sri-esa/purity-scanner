// backend/src/routes/analytics.js
import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { withOrg } from '../middleware/withOrg.js';
import { supabase } from '../config/supabase.js';

const router = express.Router();
router.use(authenticate, withOrg);

// Organization-wide stats (no userId param needed, uses req.orgId)
router.get('/stats', async (req, res, next) => {
  try {
    // Get device IDs for this org
    const { data: devices } = await supabase
      .from('devices')
      .select('id')
      .eq('organization_id', req.orgId);
    const deviceIds = (devices || []).map(d => d.id);
    if (deviceIds.length === 0) return res.json({ success: true, stats: { total_sessions: 0, average_purity: 0, last_session: null, purity_distribution: { high: 0, medium: 0, low: 0 }, sample_types: {} } });

    // Count total completed sessions
    const { count: totalSessions } = await supabase
      .from('analysis_sessions')
      .select('*', { count: 'exact', head: true })
      .in('device_id', deviceIds)
      .eq('status', 'completed');

    // Get sessions with results for analysis
    const { data: sessionsWithResults } = await supabase
      .from('analysis_sessions')
      .select(`
        id, started_at, metadata,
        analysis_results!inner(purity_percentage)
      `)
      .in('device_id', deviceIds)
      .eq('status', 'completed')
      .order('started_at', { ascending: false });

    const results = sessionsWithResults?.map(s => ({
      purity_score: s.analysis_results[0]?.purity_percentage || 0,
      started_at: s.started_at,
      sample_type: s.metadata?.sample_type || 'unknown'
    })) || [];

    const avgPurity = results.length > 0
      ? results.reduce((sum, r) => sum + r.purity_score, 0) / results.length
      : 0;

    const purityDistribution = {
      high: results.filter(r => r.purity_score >= 90).length,
      medium: results.filter(r => r.purity_score >= 70 && r.purity_score < 90).length,
      low: results.filter(r => r.purity_score < 70).length
    };

    const sampleTypes = results.reduce((acc, r) => {
      const type = r.sample_type || 'unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});

    res.json({
      success: true,
      stats: {
        total_sessions: totalSessions || 0,
        average_purity: Math.round(avgPurity * 100) / 100,
        last_session: results[0]?.started_at || null,
        purity_distribution: purityDistribution,
        sample_types: sampleTypes
      }
    });
  } catch (err) {
    next(err);
  }
});

router.get('/trends', async (req, res, next) => {
  try {
    const { period = 'week' } = req.query;

    const now = new Date();
    let startDate = new Date();
    switch (period) {
      case 'day':
        startDate.setDate(now.getDate() - 7);
        break;
      case 'week':
        startDate.setDate(now.getDate() - 30);
        break;
      case 'month':
        startDate.setMonth(now.getMonth() - 6);
        break;
    }

    // Get device IDs for this org
    const { data: devices } = await supabase
      .from('devices')
      .select('id')
      .eq('organization_id', req.orgId);
    const deviceIds = (devices || []).map(d => d.id);
    if (deviceIds.length === 0) return res.json({ success: true, trends: [], period, start_date: startDate.toISOString(), end_date: now.toISOString() });

    // Get sessions with results in time range
    const { data: sessionsWithResults } = await supabase
      .from('analysis_sessions')
      .select(`
        started_at,
        analysis_results!inner(purity_percentage)
      `)
      .in('device_id', deviceIds)
      .eq('status', 'completed')
      .gte('started_at', startDate.toISOString())
      .order('started_at', { ascending: true });

    const trends = sessionsWithResults?.map(s => ({
      purity_score: s.analysis_results[0]?.purity_percentage || 0,
      scanned_at: s.started_at
    })) || [];

    res.json({
      success: true,
      trends,
      period,
      start_date: startDate.toISOString(),
      end_date: now.toISOString()
    });
  } catch (err) {
    next(err);
  }
});

router.get('/activity', async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;

    // Get device IDs for this org
    const { data: devices } = await supabase
      .from('devices')
      .select('id')
      .eq('organization_id', req.orgId);
    const deviceIds = (devices || []).map(d => d.id);
    if (deviceIds.length === 0) return res.json({ success: true, activity: [] });

    // Get recent sessions with results
    const { data: recentSessions } = await supabase
      .from('analysis_sessions')
      .select(`
        id, session_name, started_at,
        analysis_results(purity_percentage)
      `)
      .in('device_id', deviceIds)
      .eq('status', 'completed')
      .order('started_at', { ascending: false })
      .limit(parseInt(limit));

    const activity = recentSessions?.map(s => ({
      id: s.id,
      sample_name: s.session_name,
      purity_score: s.analysis_results?.[0]?.purity_percentage || 0,
      scanned_at: s.started_at,
      is_flagged: false // You can add flagging logic based on purity thresholds
    })) || [];

    res.json({ success: true, activity });
  } catch (err) {
    next(err);
  }
});

router.get('/flagged', async (req, res, next) => {
  try {
    // Get device IDs for this org
    const { data: devices } = await supabase
      .from('devices')
      .select('id')
      .eq('organization_id', req.orgId);
    const deviceIds = (devices || []).map(d => d.id);
    if (deviceIds.length === 0) return res.json({ success: true, flagged_sessions: [], total: 0 });

    // Get sessions with low purity (flagged)
    const { data: flaggedSessions, count } = await supabase
      .from('analysis_sessions')
      .select(`
        id, session_name, started_at, metadata,
        analysis_results!inner(purity_percentage)
      `, { count: 'exact' })
      .in('device_id', deviceIds)
      .eq('status', 'completed')
      .lt('analysis_results.purity_percentage', 70) // Flag sessions with purity < 70%
      .order('started_at', { ascending: false });

    const flagged = flaggedSessions?.map(s => ({
      id: s.id,
      session_name: s.session_name,
      started_at: s.started_at,
      purity_percentage: s.analysis_results[0]?.purity_percentage || 0,
      sample_type: s.metadata?.sample_type || 'unknown'
    })) || [];

    res.json({ success: true, flagged_sessions: flagged, total: count || 0 });
  } catch (err) {
    next(err);
  }
});

export default router;


