# OAuth Testing Guide

## Quick Setup Test

1. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Test Google OAuth:**
   - Go to `http://localhost:3001/auth/login`
   - Click "Continue with Google"
   - Should redirect to Google OAuth
   - After authorization, should redirect to `/dashboard`

3. **Test GitHub OAuth:**
   - Go to `http://localhost:3001/auth/login`
   - Click "Continue with GitHub" 
   - Should redirect to GitHub OAuth
   - After authorization, should redirect to `/dashboard`

## Expected Behavior

✅ **Working Flow:**
1. Click OAuth button → Shows loading spinner
2. Redirects to OAuth provider (Google/GitHub)
3. User authorizes the application
4. Redirects back to app
5. Lands on dashboard showing user info

❌ **If Still Not Working:**
- Check browser console for errors
- Verify `.env.local` has correct OAuth credentials
- Ensure OAuth app callback URLs are set to:
  - Google: `http://localhost:3001/api/auth/callback/google`
  - GitHub: `http://localhost:3001/api/auth/callback/github`

## Debug Steps

1. **Check Environment Variables:**
   ```bash
   cd frontend
   cat .env.local
   ```

2. **Check Console Logs:**
   - Open browser dev tools
   - Go to Console tab
   - Look for NextAuth debug messages

3. **Verify OAuth App Settings:**
   - **Google Console**: Authorized redirect URIs must match exactly
   - **GitHub Settings**: Authorization callback URL must match exactly

The authentication flow is now simplified and should work correctly with your existing OAuth credentials.