-- RLS Policies for Frontend-Backend Sync
-- These policies ensure frontend Supabase queries work with org-scoped data

-- Enable RLS on all tables
ALTER TABLE public.devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.spectral_data ENABLE ROW LEVEL SECURITY;

-- Helper function to get user's organization_id
CREATE OR REPLACE FUNCTION public.get_user_organization_id()
RETURNS uuid
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
  SELECT organization_id 
  FROM public.users 
  WHERE id = auth.uid()
  LIMIT 1;
$$;

-- Devices RLS Policy
DROP POLICY IF EXISTS "Users can access devices in their organization" ON public.devices;
CREATE POLICY "Users can access devices in their organization"
ON public.devices
FOR ALL
TO authenticated
USING (organization_id = public.get_user_organization_id())
WITH CHECK (organization_id = public.get_user_organization_id());

-- Analysis Sessions RLS Policy  
DROP POLICY IF EXISTS "Users can access sessions for their org devices" ON public.analysis_sessions;
CREATE POLICY "Users can access sessions for their org devices"
ON public.analysis_sessions
FOR ALL
TO authenticated
USING (
  device_id IN (
    SELECT id FROM public.devices 
    WHERE organization_id = public.get_user_organization_id()
  )
)
WITH CHECK (
  device_id IN (
    SELECT id FROM public.devices 
    WHERE organization_id = public.get_user_organization_id()
  )
);

-- Analysis Results RLS Policy
DROP POLICY IF EXISTS "Users can access results for their org sessions" ON public.analysis_results;
CREATE POLICY "Users can access results for their org sessions"
ON public.analysis_results
FOR ALL
TO authenticated
USING (
  session_id IN (
    SELECT s.id FROM public.analysis_sessions s
    JOIN public.devices d ON s.device_id = d.id
    WHERE d.organization_id = public.get_user_organization_id()
  )
)
WITH CHECK (
  session_id IN (
    SELECT s.id FROM public.analysis_sessions s
    JOIN public.devices d ON s.device_id = d.id
    WHERE d.organization_id = public.get_user_organization_id()
  )
);

-- Spectral Data RLS Policy
DROP POLICY IF EXISTS "Users can access spectral data for their org sessions" ON public.spectral_data;
CREATE POLICY "Users can access spectral data for their org sessions"
ON public.spectral_data
FOR ALL
TO authenticated
USING (
  session_id IN (
    SELECT s.id FROM public.analysis_sessions s
    JOIN public.devices d ON s.device_id = d.id
    WHERE d.organization_id = public.get_user_organization_id()
  )
)
WITH CHECK (
  session_id IN (
    SELECT s.id FROM public.analysis_sessions s
    JOIN public.devices d ON s.device_id = d.id
    WHERE d.organization_id = public.get_user_organization_id()
  )
);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.devices TO authenticated;
GRANT ALL ON public.analysis_sessions TO authenticated;
GRANT ALL ON public.analysis_results TO authenticated;
GRANT ALL ON public.spectral_data TO authenticated;
GRANT ALL ON public.users TO authenticated;
GRANT ALL ON public.organizations TO authenticated;
GRANT ALL ON public.materials TO authenticated;
