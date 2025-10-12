import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export interface AnalysisSession {
  id: string;
  device_id: string;
  user_id: string | null;
  material_id: string | null;
  session_name: string | null;
  status: "pending" | "processing" | "completed" | "failed";
  started_at: string;
  completed_at: string | null;
  notes: string | null;
  metadata: any;
  created_at: string;
  materials?: {
    name: string;
    chemical_formula: string | null;
  };
  devices?: {
    name: string;
    serial_number: string;
  };
  analysis_results?: {
    purity_percentage: number;
    confidence_score: number;
  }[];
}

export const useAnalysisSessions = () => {
  const [sessions, setSessions] = useState<AnalysisSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const fetchSessions = async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('analysis_sessions')
        .select(`
          *,
          materials(name, chemical_formula),
          devices(name, serial_number),
          analysis_results(purity_percentage, confidence_score)
        `)
        .order('started_at', { ascending: false });

      if (error) {
        setError(error.message);
        return;
      }

      setSessions(data || []);
    } catch (err) {
      setError('Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  };

  const createSession = async (sessionData: Partial<AnalysisSession>) => {
    try {
      const { data, error } = await supabase
        .from('analysis_sessions')
        .insert(sessionData)
        .select()
        .single();

      if (error) {
        setError(error.message);
        return null;
      }

      setSessions(prev => [data, ...prev]);
      return data;
    } catch (err) {
      setError('Failed to create session');
      return null;
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [isAuthenticated]);

  return {
    sessions,
    loading,
    error,
    fetchSessions,
    createSession,
  };
};
