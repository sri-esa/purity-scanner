// backend/src/controllers/deviceController.js
import { supabase } from '../config/supabase.js';

export async function registerDevice(req, res, next) {
  try {
    const { device_name, device_model, serial_number, config } = req.body;
    const user_id = req.user.id;
    const { data, error } = await supabase
      .from('devices')
      .insert({ user_id, device_name: device_name || 'Purity Scanner', device_model, serial_number, config, status: 'active', last_seen: new Date().toISOString() })
      .select()
      .single();
    if (error) throw error;
    res.status(201).json({ success: true, device: data });
  } catch (err) {
    next(err);
  }
}


