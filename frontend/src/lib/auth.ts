import { betterAuth } from "better-auth";
import { supabase } from "@/integrations/supabase/client";

export const auth = betterAuth({
  database: {
    provider: "postgresql",
    url: import.meta.env.VITE_SUPABASE_URL + "/rest/v1/",
    auth: {
      type: "bearer",
      token: import.meta.env.VITE_SUPABASE_ANON_KEY,
    },
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
  },
  socialProviders: {
    google: {
      clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || "",
      clientSecret: import.meta.env.VITE_GOOGLE_CLIENT_SECRET || "",
    },
    github: {
      clientId: import.meta.env.VITE_GITHUB_CLIENT_ID || "",
      clientSecret: import.meta.env.VITE_GITHUB_CLIENT_SECRET || "",
    },
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },
  user: {
    additionalFields: {
      fullName: {
        type: "string",
        required: false,
      },
      avatar: {
        type: "string",
        required: false,
      },
      role: {
        type: "string",
        required: false,
        defaultValue: "operator",
      },
      organizationId: {
        type: "string",
        required: false,
      },
    },
  },
  plugins: [],
  trustedOrigins: [import.meta.env.VITE_APP_URL || "http://localhost:5173"],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;
