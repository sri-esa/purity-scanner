# Environment Variables Setup

Create a `.env` file in your project root with the following variables:

```env
# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Better Auth Configuration
VITE_APP_URL=http://localhost:5173

# Social Auth (Optional)
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_client_secret
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_CLIENT_SECRET=your_github_client_secret
```

## Getting Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy your Project URL and anon public key

## Setting Up Social Auth (Optional)

### Google OAuth
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add your domain to authorized origins

### GitHub OAuth
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create a new OAuth App
3. Set Authorization callback URL to: `http://localhost:5173/api/auth/callback/github`
4. Copy Client ID and Client Secret
