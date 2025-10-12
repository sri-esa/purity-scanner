import { ReactNode } from "react";

interface AuthProviderProps {
  children: ReactNode;
}

// Temporary: Just pass through children without auth
// This will let your app load so we can debug separately
export const AuthProvider = ({ children }: AuthProviderProps) => {
  return <>{children}</>;
};