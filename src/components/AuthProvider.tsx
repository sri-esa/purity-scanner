import { ReactNode } from "react";
import { authClient } from "@/lib/auth-client";

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  return (
    <authClient.Provider>
      {children}
    </authClient.Provider>
  );
};
