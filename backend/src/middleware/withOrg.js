// backend/src/middleware/withOrg.js
import { supabase } from '../config/supabase.js';

export async function withOrg(req, res, next) {
  try {
    const userId = req.user?.id;
    if (!userId) return res.status(401).json({ error: 'Unauthorized' });

    const { data, error } = await supabase
      .from('users')
      .select('organization_id, role')
      .eq('id', userId)
      .single();

    if (error) throw error;
    if (!data?.organization_id) {
      return res.status(403).json({ error: 'User is not assigned to an organization' });
    }

    req.orgId = data.organization_id;
    req.userRole = data.role;
    next();
  } catch (err) {
    next(err);
  }
}
