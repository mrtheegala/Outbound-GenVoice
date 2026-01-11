# 🎨 Streamlit Web Interface Guide

## Overview

The Streamlit interface provides a beautiful, professional web UI for the Healthcare AI Voice Agent, making it perfect for hackathon demos and presentations.

## Features

### 🚀 Make Call Tab
- **Quick Start Examples** - Three pre-configured scenarios for instant demos
- **Interactive Form** - Easy-to-use form for custom call configurations
- **Real-time Feedback** - Immediate response display with success/error handling
- **Patient Management** - Complete patient, provider, and procedure information entry

### 📊 Call History Tab
- **Record Viewer** - Browse all previous calls
- **Status Filtering** - Filter by approved, denied, pending, or failed
- **Detailed Information** - View complete call details and outcomes
- **JSON Export** - Access full structured data for each call

### 📋 Recent Logs Tab
- **Server Logs** - Real-time server log viewing
- **Auto-refresh** - Stay updated with latest activity
- **Last 100 Lines** - Quick access to recent events

### 💡 API Examples Tab
- **cURL Examples** - Ready-to-use command-line examples
- **Python Code** - Integration code for Python applications
- **JavaScript Code** - Frontend integration examples

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `streamlit==1.28.0` - Web framework
- `pandas==2.1.3` - Data handling
- All other existing dependencies

### 2. Setup Ngrok (Required for Twilio)

**Why?** Twilio needs a public URL to send webhooks to your local server.

**Quick Setup:**
```bash
# Install ngrok: https://ngrok.com/download
# Then run:
ngrok http 3000
```

**Configure:** Copy the HTTPS URL from ngrok and add to `.env`:
```env
NGROK_HTTPS_URL=https://your-ngrok-url.ngrok-free.app
```

📖 **Detailed instructions**: See [NGROK_SETUP.md](./NGROK_SETUP.md)

### 3. Verify Server is Running

Make sure your FastAPI server is running first:

```bash
python app.py
```

The server should be running on `http://localhost:3000`

### 4. Launch Streamlit Interface

In a new terminal window:

```bash
streamlit run streamlit_app.py
```

The interface will automatically open in your browser at `http://localhost:8501`

## Usage

### Quick Demo (30 seconds)

1. **Start the server**: `python app.py`
2. **Launch Streamlit**: `streamlit run streamlit_app.py`
3. **Click "📋 MRI Authorization"** in the Make Call tab
4. **Click "📞 Initiate Call"** button
5. **Watch the magic happen!**

### Custom Call

1. Navigate to **Make Call** tab
2. Fill in the form fields:
   - Phone number (recipient)
   - Patient information (name, DOB, member ID)
   - Provider details (name, NPI)
   - Procedure information (CPT, ICD codes)
   - Clinical notes
3. Click **"📞 Initiate Call"**
4. View response and status

### Monitor Call History

1. Navigate to **Call History** tab
2. Use filters to find specific calls
3. Expand records to view details
4. Access full JSON data if needed

## Pre-configured Examples

### 1. MRI Authorization
- **Patient**: John Doe
- **Procedure**: MRI Lumbar Spine (CPT 72148)
- **Diagnosis**: Low back pain (M54.5)
- **Insurance**: Blue Cross Blue Shield

### 2. CT Scan
- **Patient**: Jane Smith
- **Procedure**: CT scan head (CPT 70450)
- **Diagnosis**: Headache (R51)
- **Insurance**: United Healthcare
- **Urgency**: Urgent

### 3. Knee Surgery
- **Patient**: Robert Williams
- **Procedure**: Arthroscopy with meniscectomy (CPT 29881)
- **Diagnosis**: Meniscus tear (M23.205)
- **Insurance**: Aetna

## Troubleshooting

### Server Offline Error

**Problem**: Red "❌ Server Offline" in sidebar

**Solution**:
```bash
# Make sure FastAPI server is running
python app.py
```

### Cannot Connect Error

**Problem**: "Cannot connect to server" when making call

**Solution**:
1. Check server is running: `http://localhost:3000`
2. Verify no firewall blocking port 3000
3. Check server logs for errors

### No Call Records

**Problem**: Call history shows empty

**Solution**:
- Make at least one call first
- Check `prior_auth_records/` directory exists
- Verify call completed successfully

## Hackathon Demo Tips

### 🎯 Presentation Strategy

1. **Open Streamlit first** - Show professional UI immediately
2. **Use example scenarios** - Quick one-click demos
3. **Show call history** - Demonstrate previous successful calls
4. **Live demo** - Make a new call with custom data
5. **Show structured output** - Highlight JSON data extraction

### 🎨 Visual Impact

- Clean, modern interface ✅
- Real-time status indicators ✅
- Color-coded results (green=success, red=error) ✅
- Professional metrics dashboard ✅
- Easy-to-follow workflow ✅

### ⚡ Quick Demo Script (2 minutes)

```
1. "Here's our Streamlit interface..." (5s)
2. Click MRI Authorization example (2s)
3. "All fields pre-populated for quick demo..." (3s)
4. Click Initiate Call (2s)
5. Show response JSON (10s)
6. Switch to Call History tab (2s)
7. "Here's our call tracking..." (5s)
8. Expand a record (5s)
9. "Structured output ready for EHR integration" (5s)
```

## Architecture

### Flow Diagram

```
┌─────────────────┐
│  Streamlit UI   │  (Port 8501)
│  (Frontend)     │
└────────┬────────┘
         │ HTTP Requests
         ↓
┌─────────────────┐
│  FastAPI Server │  (Port 3000)
│  (Backend)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Voice Pipeline │
│  Worker.py      │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────┐
│  External Services              │
│  • Twilio (Telephony)          │
│  • Deepgram (STT)              │
│  • AWS Bedrock (LLM)           │
│  • Eleven Labs (TTS)           │
└─────────────────────────────────┘
```

## Customization

### Change API Base URL

Edit `streamlit_app.py` line 79:

```python
API_BASE_URL = "http://localhost:3000"  # Change if server on different port
```

### Add More Examples

Edit `EXAMPLE_SCENARIOS` dictionary in `streamlit_app.py` (starting line 82):

```python
EXAMPLE_SCENARIOS = {
    "Your New Scenario": {
        "to_number": "+1234567890",
        "patient_name": "Custom Patient",
        # ... add all required fields
    }
}
```

### Customize Styling

Edit CSS in `streamlit_app.py` (starting line 17):

```python
st.markdown("""
<style>
    .main-header {
        color: #YOUR_COLOR;  # Change colors
    }
</style>
""", unsafe_allow_html=True)
```

## Benefits for Judges

### Why Streamlit Interface Wins

✅ **Professional Appearance** - Looks production-ready, not a prototype  
✅ **Easy to Understand** - No technical knowledge needed to use it  
✅ **Interactive Demo** - Judges can try it themselves  
✅ **Visual Proof** - See the system working in real-time  
✅ **Full Stack Skills** - Demonstrates frontend + backend capability  
✅ **User-Focused** - Shows you care about end-user experience  

### Judge Experience

**Without Streamlit**: 
- Black terminal windows
- Copy-paste curl commands
- Hard to follow
- Looks technical/intimidating

**With Streamlit**:
- Beautiful, colorful interface
- One-click demos
- Easy to understand
- Professional and polished

## Performance

### Resource Usage
- **Memory**: ~100MB (lightweight)
- **CPU**: Minimal when idle
- **Startup**: 2-3 seconds
- **Response Time**: Instant UI, call time depends on server

### Scalability
- Handles concurrent users via Streamlit's built-in session management
- No database required (uses file system for call records)
- Can be deployed to Streamlit Cloud for public access

## Deployment (Optional)

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy `streamlit_app.py`
5. Share public URL with judges!

**Note**: Server must be accessible from internet for cloud deployment

## Support

### Common Issues

**Q: Port 8501 already in use?**  
A: Kill existing Streamlit: `Ctrl+C` in terminal, or change port:
```bash
streamlit run streamlit_app.py --server.port 8502
```

**Q: Changes not showing?**  
A: Streamlit auto-reloads. If not, click "Rerun" in top-right corner.

**Q: Server health check failing?**  
A: Add `/health` endpoint to `app.py` if not present.

## Next Steps

1. ✅ Install dependencies
2. ✅ Start FastAPI server
3. ✅ Launch Streamlit
4. ✅ Test with example scenarios
5. ✅ Customize for your demo
6. ✅ Practice presentation flow
7. ✅ Win the hackathon! 🏆

---

**Happy Demoing! 🚀**

*"Show, don't tell - let the interface speak for itself."*
