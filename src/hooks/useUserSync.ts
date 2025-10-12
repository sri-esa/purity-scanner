import { useEffect } from "react";
import { useAuth } from "./useAuth";
import { syncUserToSupabase } from "@/lib/supabase-sync";

export const useUserSync = () => {
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    if (isAuthenticated && user) {
      syncUserToSupabase(user);
    }
  }, [isAuthenticated, user]);
};
