# 🌐 Ngrok Setup Guide

## Why Ngrok is Required

**Twilio needs a public URL** to send webhooks to your local server. Ngrok creates a secure tunnel from the internet to your `localhost:3000`, allowing Twilio to reach your application.

---

## Quick Setup (3 Steps)

### Step 1: Install Ngrok

If you haven't already, install ngrok:

**Download**: https://ngrok.com/download

**Windows Quick Install**:
```bash
choco install ngrok
```

Or download the ZIP and extract to your PATH.

---

### Step 2: Start Ngrok

#### Option A: Use START_DEMO.bat (Automatic)
```bash
START_DEMO.bat
```
This automatically starts ngrok along with your server!

#### Option B: Manual Start
```bash
ngrok http 3000
```

You'll see output like this:
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Forwarding                    https://abc123xyz.ngrok-free.app -> http://localhost:3000
```

**Copy the HTTPS URL** (e.g., `https://abc123xyz.ngrok-free.app`)

---

### Step 3: Configure Your Application

#### Option A: Using .env file (Recommended)
1. Copy `.env.example` to `.env` (if you haven't already)
2. Open `.env` and update:
```env
NGROK_HTTPS_URL=https://abc123xyz.ngrok-free.app
```
Replace with your actual ngrok URL from Step 2.

#### Option B: Direct Edit (Not Recommended)
Edit `__config__.py` line 63:
```python
NGROK_HTTPS_URL : str = 'https://abc123xyz.ngrok-free.app'
```

---

## Important Notes

### ⚠️ Free Ngrok URLs Change Every Restart

If you're using the free ngrok plan:
- **The URL changes** every time you restart ngrok
- You must **update the URL** in `.env` or `__config__.py` each time
- The application **won't work** with an old ngrok URL

### ✅ Keep It Running

Ngrok must stay running while you use the application:
- ✅ Ngrok window open = Application works
- ❌ Ngrok window closed = Twilio can't reach your server

### 💡 Pro Tip: Static URLs

**Upgrade to ngrok Pro** ($8/month) to get:
- Static subdomain (doesn't change)
- No more manual URL updates
- More concurrent connections

Example with static subdomain:
```bash
ngrok http 3000 --subdomain=healthcare-ai
```
Then your URL is always: `https://healthcare-ai.ngrok.app`

---

## Verification

### Check if Ngrok is Working

1. **Start ngrok**: `ngrok http 3000`
2. **Copy the HTTPS URL** from the terminal
3. **Open in browser**: `https://your-ngrok-url.ngrok-free.app`
4. **You should see**: ngrok waiting screen or your app (if server is running)

### Check Server Connection

1. Make sure all 3 are running:
   - ✅ Ngrok tunnel
   - ✅ FastAPI server (`python app.py`)
   - ✅ Streamlit UI (optional for testing)

2. Visit: `https://your-ngrok-url.ngrok-free.app/health`
3. Should return: `{"status": "healthy", "message": "Server is running"}`

---

## Troubleshooting

### "Session Expired" or 404 Error

**Problem**: Old ngrok URL in configuration

**Solution**: 
1. Check your current ngrok URL in the ngrok terminal
2. Update `.env` with the new URL
3. Restart FastAPI server

### "ERR_NGROK_3200" Error

**Problem**: Ngrok not connected

**Solution**:
1. Make sure ngrok is running: `ngrok http 3000`
2. Check the ngrok terminal shows "Session Status: online"
3. Verify the forwarding URL is displayed

### Port Already in Use

**Problem**: Another process is using port 3000

**Solution**:
```bash
# Windows: Find and kill process
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or change port in __config__.py
HTTP_SERVER_PORT = 3001
# Then start ngrok: ngrok http 3001
```

### Ngrok Command Not Found

**Problem**: Ngrok not in PATH

**Solution**:
1. Find where you extracted ngrok
2. Add to PATH, or run from that directory:
```bash
cd C:\path\to\ngrok
ngrok http 3000
```

---

## Demo Workflow

### Standard Startup Sequence:

```
1. START_DEMO.bat runs
   ↓
2. Ngrok starts → Get HTTPS URL
   ↓
3. Update .env with URL (first time only)
   ↓
4. FastAPI server starts
   ↓
5. Streamlit UI opens
   ↓
6. Ready for demo! 🎉
```

### Before Each Demo:

1. ✅ Ngrok running and showing HTTPS URL
2. ✅ `.env` has correct ngrok URL
3. ✅ FastAPI server running on port 3000
4. ✅ Test `/health` endpoint works
5. ✅ Streamlit UI accessible

---

## Alternatives to Ngrok

If ngrok doesn't work, try these alternatives:

### 1. LocalTunnel
```bash
npm install -g localtunnel
lt --port 3000
```

### 2. Cloudflare Tunnel
```bash
cloudflared tunnel --url http://localhost:3000
```

### 3. Serveo
```bash
ssh -R 80:localhost:3000 serveo.net
```

All provide similar functionality to ngrok.

---

## For Hackathon Demo

### Pre-Demo Checklist:

- [ ] Ngrok installed and working
- [ ] Static subdomain configured (if using Pro)
- [ ] `.env` file configured with stable URL
- [ ] Test call successfully completed
- [ ] Backup plan if ngrok fails (use alternative tunnel service)

### Demo Day Setup (30 minutes before):

1. Start ngrok early
2. Verify URL is working
3. Test a complete call end-to-end
4. Have ngrok dashboard open (http://localhost:4040)
5. Monitor for any connection issues

### Emergency Backup:

If ngrok fails during demo:
1. Use alternative tunnel (LocalTunnel, Cloudflare)
2. Or: Deploy to cloud (Heroku, Railway, Render)
3. Or: Show pre-recorded call demo video

---

## Additional Resources

- **Ngrok Documentation**: https://ngrok.com/docs
- **Twilio Webhooks Guide**: https://www.twilio.com/docs/usage/webhooks
- **Ngrok Dashboard**: http://localhost:4040 (when ngrok is running)

---

**Questions?** Check the ngrok dashboard at `http://localhost:4040` to see real-time request logs and debug webhook issues!
