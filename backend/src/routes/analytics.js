// backend/src/routes/analytics.js
import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { supabase } from '../config/supabase.js';

const router = express.Router();
router.use(authenticate);

router.get('/stats/:userId', async (req, res, next) => {
  try {
    const { userId } = req.params;
    if (req.user.id !== userId) return res.status(403).json({ error: 'Unauthorized' });

    const { count: totalScans } = await supabase
      .from('scans')
      .select('*', { count: 'exact', head: true })
      .eq('user_id', userId);

    const { data: scans } = await supabase
      .from('scans')
      .select('purity_score, scanned_at, sample_type')
      .eq('user_id', userId)
      .order('scanned_at', { ascending: false });

    const avgPurity = scans && scans.length > 0
      ? scans.reduce((sum, s) => sum + s.purity_score, 0) / scans.length
      : 0;

    const purityDistribution = {
      high: scans?.filter(s => s.purity_score >= 90).length || 0,
      medium: scans?.filter(s => s.purity_score >= 70 && s.purity_score < 90).length || 0,
      low: scans?.filter(s => s.purity_score < 70).length || 0
    };

    const sampleTypes = scans?.reduce((acc, s) => {
      const type = s.sample_type || 'unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {});

    res.json({
      success: true,
      stats: {
        total_scans: totalScans || 0,
        average_purity: Math.round(avgPurity * 100) / 100,
        last_scan: scans?.[0]?.scanned_at || null,
        purity_distribution: purityDistribution,
        sample_types: sampleTypes || {}
      }
    });
  } catch (err) {
    next(err);
  }
});

router.get('/trends/:userId', async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { period = 'week' } = req.query;
    if (req.user.id !== userId) return res.status(403).json({ error: 'Unauthorized' });

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

    const { data: scans } = await supabase
      .from('scans')
      .select('purity_score, scanned_at')
      .eq('user_id', userId)
      .gte('scanned_at', startDate.toISOString())
      .order('scanned_at', { ascending: true });

    res.json({
      success: true,
      trends: scans || [],
      period,
      start_date: startDate.toISOString(),
      end_date: now.toISOString()
    });
  } catch (err) {
    next(err);
  }
});

router.get('/activity/:userId', async (req, res, next) => {
  try {
    const { userId } = req.params;
    const { limit = 10 } = req.query;
    if (req.user.id !== userId) return res.status(403).json({ error: 'Unauthorized' });

    const { data: recentScans } = await supabase
      .from('scans')
      .select('id, sample_name, purity_score, scanned_at, is_flagged')
      .eq('user_id', userId)
      .order('scanned_at', { ascending: false })
      .limit(parseInt(limit));

    res.json({ success: true, activity: recentScans || [] });
  } catch (err) {
    next(err);
  }
});

router.get('/flagged/:userId', async (req, res, next) => {
  try {
    const { userId } = req.params;
    if (req.user.id !== userId) return res.status(403).json({ error: 'Unauthorized' });

    const { data: flaggedScans, count } = await supabase
      .from('scans')
      .select('*', { count: 'exact' })
      .eq('user_id', userId)
      .eq('is_flagged', true)
      .order('scanned_at', { ascending: false });

    res.json({ success: true, flagged_scans: flaggedScans || [], total: count || 0 });
  } catch (err) {
    next(err);
  }
});

export default router;


