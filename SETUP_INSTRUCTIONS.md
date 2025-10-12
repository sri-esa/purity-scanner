# Purity Vision Lab - Complete Setup Instructions

## 🚀 Quick Start

### 1. Environment Variables Setup

Create a `.env` file in your project root with the following variables:

```env
# Supabase Configuration (REQUIRED)
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Better Auth Configuration (REQUIRED)
VITE_APP_URL=http://localhost:5173

# Social Auth (OPTIONAL - for Google/GitHub login)
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_client_secret
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_CLIENT_SECRET=your_github_client_secret
```

### 2. Get Your Supabase Credentials

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **Settings** → **API**
4. Copy your:
   - **Project URL** (for `VITE_SUPABASE_URL`)
   - **anon public** key (for `VITE_SUPABASE_ANON_KEY`)

### 3. Run the Database Schema

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the complete database schema from our previous setup
4. Click **Run** to create all tables, policies, and sample data

### 4. Start the Development Server

```bash
npm run dev
```

## 🔧 Optional: Social Authentication Setup

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Set **Application type** to "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:5173/api/auth/callback/google`
   - `http://localhost:5173` (for development)
7. Copy the **Client ID** and **Client Secret** to your `.env` file

### GitHub OAuth Setup

1. Go to [GitHub Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the form:
   - **Application name**: Purity Vision Lab
   - **Homepage URL**: `http://localhost:5173`
   - **Authorization callback URL**: `http://localhost:5173/api/auth/callback/github`
4. Copy the **Client ID** and **Client Secret** to your `.env` file

## 🎯 Features Available

### ✅ Authentication System
- **Email/Password** authentication
- **Social OAuth** (Google & GitHub)
- **Role-based access** (Admin, Operator, Viewer)
- **Automatic Supabase sync** - Users appear in your database

### ✅ Dashboard Features
- **Real-time analytics** with live data from Supabase
- **Analysis sessions** tracking
- **Material catalog** management
- **Device status** monitoring
- **User management** with roles

### ✅ Data Integration
- **Supabase backend** with full CRUD operations
- **Row Level Security** policies
- **Real-time subscriptions** for live updates
- **File storage** for reports and avatars

## 🔗 Available Routes

- `/` - Landing page with authentication links
- `/sign-in` - Sign in page
- `/sign-up` - Sign up page
- `/dashboard` - Protected user dashboard
- `/get-started` - Analysis demo (existing)

## 🛡️ Security Features

- **Row Level Security** policies in Supabase
- **Role-based access control**
- **Email verification** (configurable)
- **Secure session management**
- **CSRF protection**

## 🧪 Testing the System

1. **Start the app**: `npm run dev`
2. **Visit**: `http://localhost:5173`
3. **Sign up** for a new account
4. **Check Supabase** - Your user should appear in the `users` table
5. **Explore the dashboard** with real data integration

## 📊 Database Tables Created

- `users` - User accounts with roles
- `organizations` - Multi-tenant support
- `devices` - Raspberry Pi devices
- `materials` - Chemical catalog
- `analysis_sessions` - Analysis workflow
- `spectral_data` - Raw measurements
- `analysis_results` - ML inference results
- `reports` - Generated reports
- `device_logs` - System logging
- `system_metrics` - Performance data

## 🚨 Troubleshooting

### Common Issues

1. **"Failed to fetch" errors**: Check your Supabase URL and key
2. **Authentication not working**: Verify your environment variables
3. **Database errors**: Ensure you've run the complete SQL schema
4. **Social auth not working**: Check your OAuth app configurations

### Getting Help

- Check the browser console for errors
- Verify your Supabase project is active
- Ensure all environment variables are set correctly
- Check the Supabase logs for database errors

## 🎉 You're Ready!

Your Purity Vision Lab application now has:
- ✅ Complete authentication system
- ✅ Supabase backend integration
- ✅ Real-time data analytics
- ✅ Role-based access control
- ✅ Beautiful, responsive UI

Start building your chemical purity analysis platform! 🧪✨
