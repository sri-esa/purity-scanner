// backend/src/routes/scans.js
import express from 'express';
import { authenticate } from '../middleware/auth.js';
import { supabase } from '../config/supabase.js';
import { analyzeSpectrum } from '../services/mlservice.js';

const router = express.Router();
router.use(authenticate);

// Create a new scan record
router.post('/', async (req, res, next) => {
  try {
    const { sample_name, sample_type, purity_score, is_flagged, metadata } = req.body;
    const user_id = req.user.id;

    const { data, error } = await supabase
      .from('scans')
      .insert({ user_id, sample_name, sample_type, purity_score, is_flagged: !!is_flagged, metadata })
      .select()
      .single();

    if (error) throw error;
    res.status(201).json({ success: true, scan: data });
  } catch (err) {
    next(err);
  }
});

// List scans for the authenticated user
router.get('/', async (req, res, next) => {
  try {
    const { data, error } = await supabase
      .from('scans')
      .select('*')
      .eq('user_id', req.user.id)
      .order('scanned_at', { ascending: false });
    if (error) throw error;
    res.json({ success: true, scans: data || [] });
  } catch (err) {
    next(err);
  }
});

// Get a single scan by id (ownership enforced)
router.get('/:scanId', async (req, res, next) => {
  try {
    const { scanId } = req.params;
    const { data, error } = await supabase
      .from('scans')
      .select('*')
      .eq('id', scanId)
      .single();
    if (error) throw error;
    if (!data || data.user_id !== req.user.id) {
      return res.status(404).json({ error: 'Scan not found' });
    }
    res.json({ success: true, scan: data });
  } catch (err) {
    next(err);
  }
});

// Update a scan (ownership enforced)
router.patch('/:scanId', async (req, res, next) => {
  try {
    const { scanId } = req.params;
    const { sample_name, sample_type, purity_score, is_flagged, metadata } = req.body || {};

    const { data: existing } = await supabase
      .from('scans')
      .select('user_id')
      .eq('id', scanId)
      .single();
    if (!existing || existing.user_id !== req.user.id) {
      return res.status(404).json({ error: 'Scan not found' });
    }

    const { data, error } = await supabase
      .from('scans')
      .update({ sample_name, sample_type, purity_score, is_flagged, metadata })
      .eq('id', scanId)
      .select()
      .single();
    if (error) throw error;
    res.json({ success: true, scan: data });
  } catch (err) {
    next(err);
  }
});

// Delete a scan (ownership enforced)
router.delete('/:scanId', async (req, res, next) => {
  try {
    const { scanId } = req.params;
    const { data: existing } = await supabase
      .from('scans')
      .select('user_id')
      .eq('id', scanId)
      .single();
    if (!existing || existing.user_id !== req.user.id) {
      return res.status(404).json({ error: 'Scan not found' });
    }
    const { error } = await supabase
      .from('scans')
      .delete()
      .eq('id', scanId);
    if (error) throw error;
    res.json({ success: true, message: 'Scan deleted' });
  } catch (err) {
    next(err);
  }
});

export default router;

// Analyze-only endpoint: does not persist, returns ML result
router.post('/analyze', async (req, res, next) => {
  try {
    const { wavelengths, intensities } = req.body || {};
    const result = await analyzeSpectrum({ wavelengths, intensities });
    res.json({ success: true, result });
  } catch (err) {
    next(err);
  }
});


