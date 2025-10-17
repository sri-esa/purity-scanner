// ============================================
// backend/src/routes/devices.js
// ============================================
import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { supabase } from '../config/supabase.js';
import { analyzeSpectrum } from '../services/mlservice.js';
import { withOrg } from '../middleware/withOrg.js';

const router = express.Router();
router.use(authenticate, withOrg);

// List devices for current user's organization
router.get('/', async (req, res, next) => {
  try {
    const { data, error } = await supabase
      .from('devices')
      .select('*')
      .eq('organization_id', req.orgId)
      .order('created_at', { ascending: false });
    if (error) throw error;
    res.json({ success: true, devices: data || [] });
  } catch (error) {
    next(error);
  }
});

// Register new device
router.post('/', async (req, res, next) => {
  try {
    const { device_name, device_model, serial_number, firmware_version, config } = req.body;

    const { data, error } = await supabase
      .from('devices')
      .insert({
        name: device_name || 'Purity Scanner',
        model: device_model,
        serial_number,
        firmware_version,
        settings: config,
        status: 'online',
        last_seen: new Date().toISOString(),
        organization_id: req.orgId
      })
      .select()
      .single();

    if (error) throw error;

    res.status(201).json({ success: true, device: data });
  } catch (error) {
    next(error);
  }
});

// Get user's devices
router.get('/user/:userId', async (req, res, next) => {
  try {
    const { userId } = req.params;
    if (req.user.id !== userId) return res.status(403).json({ error: 'Unauthorized' });
    const { data, error } = await supabase
      .from('devices')
      .select('*')
      .eq('organization_id', req.orgId)
      .order('registered_at', { ascending: false });
    if (error) throw error;
    res.json({ success: true, devices: data || [] });
  } catch (error) {
    next(error);
  }
});

// Update device
router.patch('/:deviceId', async (req, res, next) => {
  try {
    const { deviceId } = req.params;
    const { device_name, status, config, firmware_version, location } = req.body;

    // Verify ownership
    const { data: device } = await supabase
      .from('devices')
      .select('organization_id')
      .eq('id', deviceId)
      .single();

    if (!device || device.organization_id !== req.orgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const { data, error } = await supabase
      .from('devices')
      .update({
        name: device_name,
        status,
        settings: config,
        firmware_version,
        location,
        last_seen: new Date().toISOString()
      })
      .eq('id', deviceId)
      .select()
      .single();

    if (error) throw error;

    res.json({ success: true, device: data });
  } catch (error) {
    next(error);
  }
});

// Device heartbeat (update last_seen)
router.post('/:deviceId/heartbeat', async (req, res, next) => {
  try {
    const { deviceId } = req.params;
    // Verify ownership
    const { data: device } = await supabase
      .from('devices')
      .select('organization_id')
      .eq('id', deviceId)
      .single();
    if (!device || device.organization_id !== req.orgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const { error } = await supabase
      .from('devices')
      .update({ last_seen: new Date().toISOString() })
      .eq('id', deviceId);

    if (error) throw error;

    res.json({ success: true, message: 'Heartbeat recorded' });
  } catch (error) {
    next(error);
  }
});

// Device ingestion: analyze spectra and persist scan
router.post('/:deviceId/ingest', async (req, res, next) => {
  try {
    const { deviceId } = req.params;
    const { wavelengths, intensities, sample_name, sample_type, metadata } = req.body || {};

    // Verify ownership
    const { data: device } = await supabase
      .from('devices')
      .select('organization_id')
      .eq('id', deviceId)
      .single();
    if (!device || device.organization_id !== req.orgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    // Create analysis session (processing)
    const { data: session, error: sErr } = await supabase
      .from('analysis_sessions')
      .insert({
        device_id: deviceId,
        user_id: req.user.id,
        session_name: sample_name || 'Device Ingest',
        status: 'processing',
        metadata: { ...(metadata || {}), sample_type }
      })
      .select()
      .single();
    if (sErr) throw sErr;

    // Analyze with ML
    const result = await analyzeSpectrum({ wavelengths, intensities });

    // Insert analysis result and mark session completed
    const { error: rErr } = await supabase.from('analysis_results').insert({
      session_id: session.id,
      purity_percentage: result?.purity_score,
      confidence_score: result?.confidence ?? null,
      ml_model_version: result?.model || 'unknown',
      contaminants: result?.components ? JSON.stringify(result.components) : null,
      spectral_quality_score: null,
      baseline_correction_applied: false,
      denoising_applied: false
    });
    if (rErr) throw rErr;

    const { data: updated, error: uErr } = await supabase
      .from('analysis_sessions')
      .update({ status: 'completed', completed_at: new Date().toISOString(), metadata: { ...(session.metadata || {}), spectrum: { wavelengths, intensities }, ml_result: result } })
      .eq('id', session.id)
      .select()
      .single();
    if (uErr) throw uErr;

    res.status(201).json({ success: true, session: updated, result });
  } catch (error) {
    next(error);
  }
});

// Delete device
router.delete('/:deviceId', async (req, res, next) => {
  try {
    const { deviceId } = req.params;

    // Verify ownership
    const { data: device } = await supabase
      .from('devices')
      .select('organization_id')
      .eq('id', deviceId)
      .single();

    if (!device || device.organization_id !== req.orgId) {
      return res.status(403).json({ error: 'Unauthorized' });
    }

    const { error } = await supabase
      .from('devices')
      .delete()
      .eq('id', deviceId);

    if (error) throw error;

    res.json({ success: true, message: 'Device deleted' });
  } catch (error) {
    next(error);
  }
});

export default router;