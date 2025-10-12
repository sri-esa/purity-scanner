import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export interface AnalyticsData {
  purityTrends: Array<{
    time: string;
    purity: number;
    baseline: number;
  }>;
  materialComparison: Array<{
    material: string;
    purity: number;
    samples: number;
  }>;
  accuracyMetrics: Array<{
    metric: string;
    accuracy: number;
  }>;
  systemHealth: {
    averagePurity: number;
    modelAccuracy: number;
    samplesAnalyzed: number;
  };
}

export const useRealtimeAnalytics = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const fetchAnalytics = async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);

      // Fetch recent analysis results
      const { data: results, error: resultsError } = await supabase
        .from('analysis_results')
        .select(`
          purity_percentage,
          confidence_score,
          created_at,
          analysis_sessions!inner(
            materials(name),
            devices(name)
          )
        `)
        .gte('created_at', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString())
        .order('created_at', { ascending: true });

      if (resultsError) {
        setError(resultsError.message);
        return;
      }

      // Process data for charts
      const purityTrends = results?.slice(0, 7).map((result, index) => ({
        time: `${index * 0.5}s`,
        purity: result.purity_percentage,
        baseline: 95 + Math.random() * 5, // Simulated baseline
      })) || [];

      // Group by material
      const materialGroups = results?.reduce((acc, result) => {
        const material = result.analysis_sessions?.materials?.name || 'Unknown';
        if (!acc[material]) {
          acc[material] = { purity: 0, count: 0 };
        }
        acc[material].purity += result.purity_percentage;
        acc[material].count += 1;
        return acc;
      }, {} as Record<string, { purity: number; count: number }>) || {};

      const materialComparison = Object.entries(materialGroups).map(([material, data]) => ({
        material,
        purity: data.purity / data.count,
        samples: data.count,
      }));

      // Calculate accuracy metrics (simulated weekly data)
      const accuracyMetrics = [
        { metric: "Week 1", accuracy: 92.3 },
        { metric: "Week 2", accuracy: 93.8 },
        { metric: "Week 3", accuracy: 94.5 },
        { metric: "Week 4", accuracy: 95.2 },
        { metric: "Week 5", accuracy: 96.1 },
        { metric: "Week 6", accuracy: 95.8 },
      ];

      const systemHealth = {
        averagePurity: results?.reduce((sum, r) => sum + r.purity_percentage, 0) / (results?.length || 1),
        modelAccuracy: 95.8,
        samplesAnalyzed: results?.length || 0,
      };

      setAnalyticsData({
        purityTrends,
        materialComparison,
        accuracyMetrics,
        systemHealth,
      });
    } catch (err) {
      setError('Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [isAuthenticated]);

  return {
    analyticsData,
    loading,
    error,
    refetch: fetchAnalytics,
  };
};
