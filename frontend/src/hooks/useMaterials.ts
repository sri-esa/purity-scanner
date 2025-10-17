import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";

export interface Material {
  id: string;
  name: string;
  chemical_formula: string | null;
  cas_number: string | null;
  description: string | null;
  category: string | null;
  expected_purity_range: any;
  spectral_reference: any;
  created_at: string;
  updated_at: string;
}

export const useMaterials = () => {
  const [materials, setMaterials] = useState<Material[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMaterials = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('materials')
        .select('*')
        .order('name', { ascending: true });

      if (error) {
        setError(error.message);
        return;
      }

      setMaterials(data || []);
    } catch (err) {
      setError('Failed to fetch materials');
    } finally {
      setLoading(false);
    }
  };

  const searchMaterials = async (query: string) => {
    try {
      const { data, error } = await supabase
        .from('materials')
        .select('*')
        .or(`name.ilike.%${query}%,chemical_formula.ilike.%${query}%,cas_number.ilike.%${query}%`)
        .order('name', { ascending: true });

      if (error) {
        setError(error.message);
        return;
      }

      setMaterials(data || []);
    } catch (err) {
      setError('Failed to search materials');
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, []);

  return {
    materials,
    loading,
    error,
    fetchMaterials,
    searchMaterials,
  };
};
