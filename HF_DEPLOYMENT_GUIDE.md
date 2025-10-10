# 🤗 Hugging Face Spaces Deployment Guide

## Quick Deployment (Automated Script)

Run this script to deploy automatically:

```bash
cd /home/arun/Desktop/Hack/Market_intelligence_MCP
./deploy_to_hf.sh
```

---

## Manual Deployment Steps

### Step 1: Create Hugging Face Account
1. Go to https://huggingface.co/join
2. Sign up (GitHub signup recommended)

### Step 2: Create New Space
1. Visit https://huggingface.co/new-space
2. Fill in:
   - **Space name**: `market-intel-api` (or your choice)
   - **License**: Apache 2.0
   - **Select SDK**: **Docker** (Important!)
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public or Private
3. Click **Create Space**

### Step 3: Add Environment Variables
1. Go to your Space settings: `https://huggingface.co/spaces/YOUR_USERNAME/market-intel-api/settings`
2. Click **Repository secrets**
3. Add these secrets:
   - `GEMINI_API_KEY` = Your Gemini API key
   - `FINANCIAL_DATASETS_API_KEY` = Your Financial API key (optional)

### Step 4: Get Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Click **New token**
3. Name: `deploy-token`
4. Role: **Write**
5. Copy the token (you'll need it for git push)

### Step 5: Clone and Deploy
```bash
# Clone your Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/market-intel-api
cd market-intel-api

# Copy project files
cp -r /home/arun/Desktop/Hack/Market_intelligence_MCP/* .

# Rename README for HF
mv .huggingface_readme.md README.md

# Commit and push
git add .
git commit -m "Initial deployment"
git push

# When prompted for username: use your HF username
# When prompted for password: use the token from Step 4
```

### Step 6: Monitor Build
1. Go to your Space: `https://huggingface.co/spaces/YOUR_USERNAME/market-intel-api`
2. Click **Logs** tab
3. Wait 2-5 minutes for build to complete

### Step 7: Test Your Deployment
Once deployed, your API will be at:
```
https://YOUR_USERNAME-market-intel-api.hf.space
```

Test it:
```bash
# Health check
curl https://YOUR_USERNAME-market-intel-api.hf.space/health

# Query
curl -X POST https://YOUR_USERNAME-market-intel-api.hf.space/query \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Bitcoin price?"}'

# Streaming
curl -X POST https://YOUR_USERNAME-market-intel-api.hf.space/query/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Latest Tesla news"}' \
  --no-buffer
```

---

## Updating Your Deployment

When you make changes:
```bash
cd market-intel-api
# Make your changes
git add .
git commit -m "Update: description of changes"
git push
```

HF Spaces will automatically rebuild and redeploy.

---

## Troubleshooting

### Build Failed
- Check Logs tab for error messages
- Ensure Dockerfile is present
- Verify all dependencies in requirements.txt

### API Not Responding
- Check that secrets (GEMINI_API_KEY) are set correctly
- Verify port 7860 is used in Dockerfile
- Check app logs in the Logs tab

### Authentication Issues
- Make sure you're using the HF token (not password) for git push
- Token must have "write" permission
- Username is case-sensitive

---

## Free Tier Limits

Hugging Face Spaces free tier includes:
- ✅ 2 vCPU
- ✅ 16 GB RAM
- ✅ 50 GB Storage
- ✅ Unlimited requests (fair use)
- ✅ Custom domains available

Perfect for your Market Intelligence API! 🚀
