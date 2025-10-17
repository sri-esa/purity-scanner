import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./useAuth";

export interface Device {
  id: string;
  name: string;
  serial_number: string;
  model: string | null;
  firmware_version: string | null;
  status: "online" | "offline" | "maintenance" | "error";
  last_seen: string | null;
  location: string | null;
  organization_id: string;
  settings: any;
  created_at: string;
  updated_at: string;
}

export const useDevices = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();

  const fetchDevices = async () => {
    if (!isAuthenticated) return;

    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('devices')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        setError(error.message);
        return;
      }

      setDevices(data || []);
    } catch (err) {
      setError('Failed to fetch devices');
    } finally {
      setLoading(false);
    }
  };

  const updateDeviceStatus = async (deviceId: string, status: Device['status']) => {
    try {
      const { data, error } = await supabase
        .from('devices')
        .update({ 
          status,
          last_seen: new Date().toISOString()
        })
        .eq('id', deviceId)
        .select()
        .single();

      if (error) {
        setError(error.message);
        return null;
      }

      setDevices(prev => 
        prev.map(device => 
          device.id === deviceId ? { ...device, ...data } : device
        )
      );

      return data;
    } catch (err) {
      setError('Failed to update device status');
      return null;
    }
  };

  useEffect(() => {
    fetchDevices();
  }, [isAuthenticated]);

  return {
    devices,
    loading,
    error,
    fetchDevices,
    updateDeviceStatus,
  };
};
