// backend/src/routes/sessions.js
import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { withOrg } from '../middleware/withOrg.js';
import { supabase } from '../config/supabase.js';
import { analyzeSpectrum } from '../services/mlservice.js';

const router = express.Router();
router.use(authenticate, withOrg);

// List sessions for current user's organization (most recent first)
router.get('/', async (req, res, next) => {
  try {
    const { limit = 50 } = req.query;
    // Step 1: fetch device ids in org
    const { data: devices, error: dErr } = await supabase
      .from('devices')
      .select('id')
      .eq('organization_id', req.orgId);
    if (dErr) throw dErr;
    const deviceIds = (devices || []).map(d => d.id);
    if (deviceIds.length === 0) return res.json({ success: true, sessions: [] });

    // Step 2: fetch sessions for those devices
    const { data: sessions, error } = await supabase
      .from('analysis_sessions')
      .select('id, device_id, user_id, session_name, status, started_at, completed_at, metadata')
      .in('device_id', deviceIds)
      .order('started_at', { ascending: false })
      .limit(parseInt(limit));
    if (error) throw error;
    res.json({ success: true, sessions: sessions || [] });
  } catch (err) {
    next(err);
  }
});

// Create a new analysis session (status pending)
router.post('/', async (req, res, next) => {
  try {
    const { device_id, session_name, sample_type, metadata } = req.body || {};

    // Verify device belongs to org
    const { data: device, error: dErr } = await supabase
      .from('devices')
      .select('organization_id')
      .eq('id', device_id)
      .single();
    if (dErr) throw dErr;
    if (!device || device.organization_id !== req.orgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const { data: session, error } = await supabase
      .from('analysis_sessions')
      .insert({
        device_id,
        user_id: req.user.id,
        session_name: session_name || 'Ad-hoc Session',
        status: 'pending',
        metadata: { ...(metadata || {}), sample_type }
      })
      .select()
      .single();
    if (error) throw error;

    res.status(201).json({ success: true, session });
  } catch (err) {
    next(err);
  }
});

// Analyze spectrum for a session (analyze+save results)
router.post('/:sessionId/analyze', async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const { wavelengths, intensities } = req.body || {};

    // Load session and verify org
    const { data: session, error: sErr } = await supabase
      .from('analysis_sessions')
      .select('id, device_id, user_id, metadata, status')
      .eq('id', sessionId)
      .single();
    if (sErr) throw sErr;

    const { data: device, error: dErr } = await supabase
      .from('devices')
      .select('organization_id')
      .eq('id', session.device_id)
      .single();
    if (dErr) throw dErr;
    if (!device || device.organization_id !== req.orgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    // Move to processing
    await supabase.from('analysis_sessions')
      .update({ status: 'processing' })
      .eq('id', sessionId);

    // Analyze via ML
    const result = await analyzeSpectrum({ wavelengths, intensities });

    // Insert results
    const { error: rErr } = await supabase.from('analysis_results').insert({
      session_id: sessionId,
      purity_percentage: result?.purity_score,
      confidence_score: result?.confidence ?? null,
      ml_model_version: result?.model || 'unknown',
      contaminants: result?.components ? JSON.stringify(result.components) : null
    });
    if (rErr) throw rErr;

    // Complete session
    const { data: updated, error: uErr } = await supabase
      .from('analysis_sessions')
      .update({
        status: 'completed',
        completed_at: new Date().toISOString(),
        metadata: { ...(session.metadata || {}), spectrum: { wavelengths, intensities }, ml_result: result }
      })
      .eq('id', sessionId)
      .select()
      .single();
    if (uErr) throw uErr;

    res.json({ success: true, session: updated, result });
  } catch (err) {
    next(err);
  }
});

// Get a session with latest result
router.get('/:sessionId', async (req, res, next) => {
  try {
    const { sessionId } = req.params;
    const { data: session, error } = await supabase
      .from('analysis_sessions')
      .select('id, device_id, user_id, session_name, status, started_at, completed_at, metadata')
      .eq('id', sessionId)
      .single();
    if (error) throw error;

    // Verify org via device
    const { data: device } = await supabase
      .from('devices')
      .select('organization_id')
      .eq('id', session.device_id)
      .single();
    if (!device || device.organization_id !== req.orgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const { data: results } = await supabase
      .from('analysis_results')
      .select('*')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: false })
      .limit(1);

    res.json({ success: true, session, latest_result: results?.[0] || null });
  } catch (err) {
    next(err);
  }
});

export default router;
