import * as React from "react";

// Temporary mock auth client to bypass Better Auth issues
// This will let your app run without authentication

export const authClient = {
  Provider: ({ children }: { children: React.ReactNode }) => children
};

// Mock functions
export const signIn = {
  email: async () => ({ data: null, error: { message: "Auth disabled in development" } }),
  social: async () => ({ data: null, error: { message: "Auth disabled in development" } }),
};

export const signUp = {
  email: async () => ({ data: null, error: { message: "Auth disabled in development" } }),
  social: async () => ({ data: null, error: { message: "Auth disabled in development" } }),
};

export const signOut = async () => {
  console.log("Sign out called (mock)");
};

export const useSession = () => ({
  data: null,
  isPending: false,
  error: null,
});

export const getSession = async () => ({
  data: null,
  error: null,
});

console.warn("Using mock auth client - authentication is disabled");