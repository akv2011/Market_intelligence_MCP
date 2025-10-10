# 🚀 Deployment Guide - Market Intelligence API

This guide provides step-by-step instructions for deploying your Market Intelligence API to various platforms.

## 📋 Pre-Deployment Checklist

- [ ] Test locally with `uvicorn api.main:app --reload`
- [ ] Verify both endpoints work: `/query` and `/query/stream`
- [ ] Obtain Gemini API key from https://aistudio.google.com/apikey
- [ ] Test with Google Search grounding enabled
- [ ] Review and commit all code changes

## 🤗 Hugging Face Spaces (Recommended for Streaming)

### Advantages
- ✅ **Free tier with 2 vCPU + 16 GB RAM**
- ✅ Excellent for streaming endpoints (SSE)
- ✅ Persistent storage
- ✅ Built-in secrets management
- ✅ Auto-deploy from GitHub
- ✅ Custom domains available

### Step-by-Step Deployment

#### 1. Create a Hugging Face Account
- Go to https://huggingface.co/join
- Sign up with GitHub for easier integration

#### 2. Create a New Space
1. Visit https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Configure:
   - **Space name**: `market-intel-api` (or your choice)
   - **License**: Apache 2.0 or MIT
   - **SDK**: Select **"Docker"**
   - **Visibility**: Public or Private
4. Click **"Create Space"**

#### 3. Link GitHub Repository
1. Go to your Space settings
2. Under "Repository secrets", add:
   ```
   GEMINI_API_KEY=<your_key_here>
   LLM_PROVIDER=gemini
   USE_GOOGLE_SEARCH=true
   CONTEXT_WINDOW=12
   ```

#### 4. Push Your Code
```bash
# Clone the Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/market-intel-api
cd market-intel-api

# Copy your project files
cp -r /path/to/your/project/* .

# Ensure Dockerfile is present (already in project)

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### 5. Wait for Build
- HF Spaces will automatically build your Docker image
- Check the "Logs" tab for build progress
- Build typically takes 2-5 minutes

#### 6. Test Your Deployment
Once running, test with:

```bash
# Replace with your actual Space URL
SPACE_URL="https://YOUR_USERNAME-market-intel-api.hf.space"

# Health check
curl $SPACE_URL/health

# Non-streaming query
curl -X POST $SPACE_URL/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the current price of Bitcoin?"}'

# Streaming query
curl -X POST $SPACE_URL/query/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me the latest Tesla stock news"}' \
  --no-buffer
```

#### 7. Custom Domain (Optional)
- Go to Space settings → "Domains"
- Add your custom domain
- Update DNS records as instructed

---

## ▲ Vercel Deployment

### Advantages
- ✅ Free tier available
- ✅ Automatic HTTPS and CDN
- ✅ GitHub integration
- ⚠️ 10s timeout on free tier (limits streaming)
- ⚠️ Better for non-streaming `/query` endpoint

### Step-by-Step Deployment

#### 1. Install Vercel CLI
```bash
npm install -g vercel
```

#### 2. Create `vercel.json`
File should already exist in project root. If not:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ]
}
```

#### 3. Deploy
```bash
# Login to Vercel
vercel login

# Deploy (preview)
vercel

# Deploy to production
vercel --prod
```

#### 4. Add Environment Variables
Via Vercel Dashboard or CLI:

```bash
vercel env add GEMINI_API_KEY
vercel env add LLM_PROVIDER production
# Value: gemini

vercel env add USE_GOOGLE_SEARCH production
# Value: true
```

#### 5. Test
```bash
# Your Vercel URL
VERCEL_URL="https://your-project.vercel.app"

curl -X POST $VERCEL_URL/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the top tech stocks today?"}'
```

---

## 🚂 Railway Deployment

### Advantages
- ✅ $5 free credit per month
- ✅ Simple deployment
- ✅ Supports long-running processes
- ✅ Good for streaming

### Step-by-Step Deployment

#### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

#### 2. Login
```bash
railway login
```

#### 3. Initialize Project
```bash
railway init
```

#### 4. Add Environment Variables
```bash
railway variables set GEMINI_API_KEY=your_key_here
railway variables set LLM_PROVIDER=gemini
railway variables set USE_GOOGLE_SEARCH=true
```

#### 5. Deploy
```bash
railway up
```

#### 6. Open Your Service
```bash
railway open
```

---

## 🐳 Google Cloud Run

### Advantages
- ✅ Pay-per-use (cheap for low traffic)
- ✅ Auto-scaling
- ✅ Good for streaming
- ✅ Production-ready

### Step-by-Step Deployment

#### 1. Install Google Cloud SDK
```bash
# macOS
brew install google-cloud-sdk

# Or download from https://cloud.google.com/sdk/docs/install
```

#### 2. Authenticate
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 3. Build and Deploy
```bash
# Build Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/market-intel-api

# Deploy to Cloud Run
gcloud run deploy market-intel-api \
  --image gcr.io/YOUR_PROJECT_ID/market-intel-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key,LLM_PROVIDER=gemini,USE_GOOGLE_SEARCH=true
```

---

## 🔧 Quick Testing: ngrok

For temporary public URL during development:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Run your API locally
uvicorn api.main:app --host 0.0.0.0 --port 8000

# In another terminal
ngrok http 8000

# Use the generated URL (e.g., https://abc123.ngrok.io)
```

---

## 🧪 Testing Your Deployment

### Health Check
```bash
curl https://your-api-url.com/health
```

Expected response:
```json
{"status": "ok"}
```

### Non-Streaming Test
```bash
curl -X POST https://your-api-url.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current stock market trend?"
  }'
```

### Streaming Test
```bash
curl -X POST https://your-api-url.com/query/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Give me live updates on Bitcoin price"
  }' \
  --no-buffer
```

### Context Continuity Test
```bash
# First message
curl -X POST https://your-api-url.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about NVIDIA stock",
    "session_id": "test-123"
  }'

# Follow-up message (same session)
curl -X POST https://your-api-url.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What about their competitors?",
    "session_id": "test-123"
  }'
```

---

## 📊 Monitoring & Maintenance

### Hugging Face Spaces
- Check logs: Space → "Logs" tab
- Restart: Space → "Settings" → "Factory reboot"
- Update: Push to GitHub or HF repo

### Vercel
- Logs: Vercel dashboard → Project → "Logs"
- Redeploy: `vercel --prod`

### Railway
- Logs: `railway logs`
- Redeploy: `railway up`

---

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. Use **environment variables** for all secrets
3. Enable **rate limiting** for production (add middleware)
4. Use **HTTPS** only (all platforms provide this)
5. Consider adding **API key authentication** for your endpoints

---

## 💡 Optimization Tips

1. **Database**: For production, consider PostgreSQL instead of SQLite
2. **Caching**: Add Redis for frequently asked questions
3. **Rate Limiting**: Use `slowapi` to prevent abuse
4. **Monitoring**: Add Sentry or similar for error tracking
5. **Scaling**: Enable auto-scaling based on traffic

---

## 🆘 Troubleshooting

### Port Issues
- HF Spaces uses port **7860**
- Vercel uses serverless (no fixed port)
- Ensure `PORT` env variable is respected

### Timeout Issues
- Increase timeout in deployment config
- For Vercel, use `/query` not `/query/stream` (10s limit)

### Google Search Not Working
- Verify `GEMINI_API_KEY` is set correctly
- Ensure `USE_GOOGLE_SEARCH=true`
- Check Gemini API quotas

### Database Errors
- Ensure `DB_PATH` directory is writable
- For cloud deployments, use persistent volumes

---

## 📚 Additional Resources

- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Vercel Python Docs](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Railway Docs](https://docs.railway.app/)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Need help?** Open an issue on GitHub or contact support for your chosen platform.
