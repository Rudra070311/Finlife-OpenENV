# Deployment Guide: FinLife-OpenEnv to Hugging Face Spaces

## Prerequisites

1. GitHub account with repo code pushed
2. Hugging Face account (free tier OK)
3. OpenAI API key (for inference)

## Step-by-Step HF Spaces Deployment

### Step 1: Create New HF Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `finlife-openenv` (or your choice)
   - **License**: MIT
   - **Select the Space SDK**: Docker
   - **Visibility**: Public

### Step 2: Connect GitHub Repository

After creating the Space:

1. Click **Files** → **⚙ Settings**
2. Scroll to **"Repository URL"**
3. Paste your GitHub repo URL:
   ```
   https://github.com/YOUR_USERNAME/finlife-openenv
   ```
4. Click **"Save"**

HF Spaces will automatically:
- Clone your repo
- Build Docker image
- Deploy on GPU hardware
- Auto-restart on code updates

### Step 3: Set Environment Variables

1. Go to **Settings** → **Repository secrets**
2. Add these secrets:

   | Name | Value | Description |
   |------|-------|---|
   | `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key |
   | `API_BASE_URL` | `https://YOUR-SPACE-URL.hf.space` | Auto-generated after deploy |
   | `MODEL_NAME` | `gpt-4` | LLM model ID |
   | `HF_TOKEN` | `hf_...` | Your HF token (optional) |

3. Click **Save secrets**

### Step 4: Monitor Deployment

1. Click **"Build"** in the Space header
2. Watch the build log for:
   - ✅ Docker build completes
   - ✅ Container starts
   - ✅ Server responds on port 8000

### Step 5: Get Your Space URL

Once deployed (green checkmark):
- Your Space URL: `https://username-finlife-openenv.hf.space`
- Test it:
  ```bash
  curl https://username-finlife-openenv.hf.space/
  ```

Should return the API info JSON.

### Step 6: Submit to Hackathon

1. Go to hackathon submission platform
2. Paste your HF Spaces URL
3. Include your GitHub repo link
4. Hit **Submit**

---

## Troubleshooting

### Build fails
→ Check Docker build logs in Space
→ Verify requirements.txt has all dependencies
→ Ensure inference.py is at root level

### 503 errors
→ Must call `/reset` first to initialize environment
→ Check server logs in Space settings

### Slow response
→ Normal for LLM inference (uses OpenAI API)
→ Each episode takes ~5-10 minutes

### Environment variable issues
→ Verify secrets are set (not in .env file)
→ Restart space after adding secrets

---

## Auto-Restart Configuration

HF Spaces automatically:
- ✅ Rebuilds when you push to GitHub
- ✅ Restarts on API failure (healthcheck at `/status`)
- ✅ Scales resources based on demand

No manual intervention needed!
