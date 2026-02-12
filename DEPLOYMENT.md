# 🚀 Deploying Signalist to Vercel

## Frontend Deployment (Vercel)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Vercel configuration"
git push origin main
```

### Step 2: Deploy to Vercel

#### Option A: Vercel CLI (Fastest)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend folder
cd frontend
vercel

# For production
vercel --prod
```

#### Option B: Vercel Dashboard
1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository `Omc12/Signalist`
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: Your backend URL (see below)

### Step 3: Set Backend URL

After deploying your backend (Render/Railway), add the URL to Vercel:
```bash
vercel env add VITE_API_BASE_URL
# Enter: https://your-backend.onrender.com
```

Or in Vercel Dashboard:
- Go to Project Settings → Environment Variables
- Add `VITE_API_BASE_URL` = `https://your-backend-url.com`

---

## Backend Options for Vercel Frontend

### Option 1: Render (Recommended - Free Tier)
```bash
# 1. Create render.yaml in project root (see below)
# 2. Push to GitHub
# 3. Connect to Render.com
# 4. Add environment variables in Render dashboard:
#    - GEMINI_API_KEY (get from https://aistudio.google.com/apikey)
#    - NEWSDATA_API_KEY (get from https://newsdata.io)
#    - FRONTEND_URL (your Vercel URL)
# 5. Copy the backend URL
# 6. Add to Vercel env: VITE_API_BASE_URL
```

### Option 2: Railway.app
```bash
# 1. Connect Railway to GitHub
# 2. Deploy backend folder
# 3. Add environment variables in Railway dashboard:
#    - GEMINI_API_KEY (get from https://aistudio.google.com/apikey)
#    - NEWSDATA_API_KEY (get from https://newsdata.io)
#    - FRONTEND_URL (your Vercel URL)
# 4. Copy provided URL
# 5. Add to Vercel env: VITE_API_BASE_URL
```

### Option 3: Vercel Serverless (Advanced)
Convert FastAPI to serverless functions (requires restructuring)

---

## Important: CORS Configuration

Update your backend CORS to allow Vercel domain:

```python
# backend/core/config.py
CORS_ORIGINS = [
    "http://localhost:5173",
    "https://your-app.vercel.app",  # Add your Vercel URL
    "https://*.vercel.app"          # Allow all Vercel preview deployments
]
```

---

## Testing Your Deployment

1. **Frontend**: `https://your-app.vercel.app`
2. **Backend**: `https://your-backend.onrender.com/health`
3. Required API Keys for Production

### GEMINI_API_KEY (Required for AI Chat)
1. Visit https://aistudio.google.com/apikey
2. Sign in with Google account
3. Create API key
4. Add to backend environment variables

### NEWSDATA_API_KEY (Required for RAG News Features)
1. Visit https://newsdata.io
2. Sign up for free account
3. Copy API key from dashboard
4. Add to backend environment variables

**Note**: Without these keys, the chat and prediction features will return neutral/default responses.

## Common Issues

### CORS Errors
- Add your Vercel URL to backend CORS_ORIGINS
- Redeploy backend after changes

### API Not Found
- Check VITE_API_BASE_URL is set correctly
- Ensure backend is deployed and running

### RAG Features Not Working
- Verify GEMINI_API_KEY and NEWSDATA_API_KEY are set
- Check API key quotas haven't been exceeded
- Review backend logs for API errors

### API Not Found
- Check VITE_API_BASE_URL is set correctly
- Ensure backend is deployed and running

### Build Fails
- Check Node.js version (use 18+)
- Verify package.json scripts

---

## Next Steps

1. ✅ Frontend configured for Vercel
2. 📤 Deploy backend (Render/Railway)
3. 🔗 Update VITE_API_BASE_URL with backend URL
4. 🚀 Deploy to Vercel
5. 🎉 Your app is live!
