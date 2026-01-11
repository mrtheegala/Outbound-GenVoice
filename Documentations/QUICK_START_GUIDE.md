# 🚀 QUICK START GUIDE
## AI Voice Agent for Healthcare Insurance Automation

**Get your demo running in under 10 minutes!**

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Twilio account with phone number ([Sign up free](https://www.twilio.com/try-twilio))
- [ ] AWS Account with Bedrock access ([Setup guide](AWS_BEDROCK_SETUP.md))
- [ ] Deepgram API key ([Get free trial](https://deepgram.com/))
- [ ] Eleven Labs API key ([Sign up](https://elevenlabs.io/))
- [ ] ngrok installed ([Download](https://ngrok.com/download))
- [ ] Git (for cloning repository)

---

## Step 1: Clone Repository (1 minute)

```bash
# Clone the repository
git clone https://github.com/your-repo/outbound-phone-gpt
cd outbound-phone-gpt

# Or if you have the ZIP file
unzip Outbound-Phone-GPT-main.zip
cd Outbound-Phone-GPT-main
```

---

## Step 2: Install Dependencies (2 minutes)

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

**Expected output:** All packages install successfully without errors.

---

## Step 3: Configure Environment Variables (3 minutes)

```bash
# Copy example environment file
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux
```

Edit the `.env` file with your credentials:

```ini
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

# Deepgram Configuration
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Eleven Labs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # Default voice (can customize)

# Server Configuration
HTTP_SERVER_PORT=3000
```

**Where to find these values:**

- **Twilio:** Console → Account Info → Account SID & Auth Token
- **AWS:** IAM → Users → Security Credentials → Access Keys
- **Deepgram:** Console → API Keys
- **Eleven Labs:** Profile → API Keys

---

## Step 4: Setup ngrok Tunnel (1 minute)

Open a **new terminal window** and run:

```bash
# Start ngrok tunnel on port 3000
ngrok http 3000
```

**Copy the HTTPS URL** (looks like `https://abc123.ngrok.io`)

Update your Twilio webhook:
1. Go to Twilio Console
2. Phone Numbers → Your Number
3. Voice & Fax → A Call Comes In
4. Set webhook URL to: `https://your-ngrok-url.ngrok.io/incoming-call`
5. Save

**Keep this terminal running!**

---

## Step 5: Test AWS Bedrock Connection (1 minute)

```bash
# Verify AWS Bedrock access
python test_bedrock_connection.py
```

**Expected output:**
```
Testing AWS Bedrock connection...
✓ Successfully connected to AWS Bedrock
✓ Claude 3.5 Sonnet model available
✓ Test completion successful
```

If you see errors, check:
- AWS credentials are correct in `.env`
- Your AWS account has Bedrock enabled
- You've requested Claude 3.5 Sonnet model access in AWS Console

---

## Step 6: Start the Server (30 seconds)

```bash
# Start the FastAPI server
python app.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3000
```

**Keep this terminal running!**

---

## Step 7: Make Your First Test Call (1 minute)

Open a **third terminal window** and run:

### Option A: Windows

```bash
example_prior_auth_curl.bat
```

### Option B: Mac/Linux

```bash
chmod +x example_prior_auth_curl.sh
./example_prior_auth_curl.sh
```

### Option C: Manual curl

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d "{
    \"to_number\": \"+1234567890\",
    \"welcome_message\": \"Hi, this is Sarah Mitchell from HealthCare RCM Solutions calling about a prior authorization request.\",
    \"patient_name\": \"John Doe\",
    \"patient_dob\": \"1975-06-15\",
    \"member_id\": \"ABC123456789\",
    \"provider_name\": \"Dr. Sarah Smith\",
    \"provider_npi\": \"1234567890\",
    \"cpt_code\": \"72148\",
    \"procedure_description\": \"MRI Lumbar Spine without contrast\",
    \"icd_code\": \"M54.5\",
    \"diagnosis_description\": \"Low back pain\",
    \"insurance_company\": \"Blue Cross Blue Shield\",
    \"proposed_date\": \"2025-11-15\",
    \"urgency_level\": \"routine\",
    \"clinical_notes\": \"Patient presents with chronic lower back pain for 8 weeks. Conservative treatment including physical therapy (6 weeks, failed), NSAIDs (minimal relief), muscle relaxants (no improvement). Positive straight leg raise test, radicular symptoms in left leg.\"
  }"
```

**Replace `+1234567890` with your actual test phone number!**

---

## Step 8: Monitor the Call

Watch the server terminal for real-time logs:

```
[INFO] Incoming call initiated
[INFO] Agent initialized with prior auth details
[INFO] STT: "Hello, who am I speaking with?"
[INFO] LLM Response: "Hi! This is Sarah Mitchell from HealthCare RCM Solutions..."
[INFO] TTS: Generating audio...
[INFO] Call in progress...
```

Your phone should ring and you'll hear the AI agent speaking!

---

## Step 9: Review the Results

After the call ends, check:

### Call Records

```bash
# View the saved authorization record
cat prior_auth_records/approved/20251106_*.json   # Or denied/pending folder

# Or on Windows
type prior_auth_records\approved\20251106_*.json
```

### Server Logs

```bash
# View detailed logs
tail -f output.log    # Mac/Linux
type output.log       # Windows
```

**What to look for:**
- Patient name correctly mentioned by agent
- Structured JSON output generated
- Authorization status captured
- Next steps documented

---

## 🎉 Success! You're Running!

You now have a fully functional AI voice agent for healthcare automation!

---

## Next Steps

### Customize for Your Use Case

**Prior Authorization:**
```bash
# Edit agent configuration
notepad example_agent_configs/Prior_Auth_Agent_config.json
```

**Denial Management:**
```bash
# Test denial management workflow
test_denial_mgmt.bat    # Windows
./test_denial_mgmt.sh   # Mac/Linux
```

**Insurance Verification:**
Use `Insurance_Verification_Agent_config.json` as template

### Run Multiple Test Scenarios

```bash
# Test successful authorization
curl -X POST http://localhost:3000/make-call -d @test_cases/approved_auth.json

# Test denied authorization
curl -X POST http://localhost:3000/make-call -d @test_cases/denied_auth.json

# Test pending with clinical review
curl -X POST http://localhost:3000/make-call -d @test_cases/pending_auth.json
```

---

## Troubleshooting

### Issue: "Connection refused" error

**Solution:**
- Ensure server is running (`python app.py`)
- Check port 3000 is not in use
- Verify firewall settings

### Issue: No audio in call

**Solution:**
- Check Eleven Labs API key is valid
- Verify voice ID is correct
- Check API quota/credits

### Issue: Agent says wrong patient name

**Solution:**
- Restart server after changing config
- Verify JSON syntax in curl command
- Check server logs for initialization message

### Issue: Call disconnects immediately

**Solution:**
- Verify ngrok tunnel is running
- Check Twilio webhook URL is correct
- Ensure Twilio account has sufficient credits

### Issue: "AWS Bedrock access denied"

**Solution:**
- Check AWS credentials in `.env`
- Verify Bedrock is enabled in your region
- Request Claude 3.5 Sonnet model access
- See [AWS_BEDROCK_SETUP.md](AWS_BEDROCK_SETUP.md)

### Issue: Long response delays (>5 seconds)

**Solution:**
- Check internet connection speed
- Verify AWS region (use us-east-1 for lowest latency)
- Monitor Deepgram/Eleven Labs API response times

---

## Demo Preparation Checklist

For hackathon presentation:

- [ ] Test call completed successfully
- [ ] Clear old prior_auth_records for clean demo
- [ ] Prepare 2-3 test scenarios
- [ ] Have backup recordings ready
- [ ] Print this guide as reference
- [ ] Charge laptop fully
- [ ] Test on presentation WiFi network
- [ ] Have mobile hotspot backup
- [ ] Silence notifications
- [ ] Bookmark key documentation files

---

## Getting Help

### Documentation
- **Full Proposal:** [HACKATHON_PROPOSAL.md](HACKATHON_PROPOSAL.md)
- **Demo Guide:** [HACKATHON_DEMO_GUIDE.md](HACKATHON_DEMO_GUIDE.md)
- **Architecture:** [ARCHITECTURE_DOCUMENTATION.md](ARCHITECTURE_DOCUMENTATION.md)
- **API Examples:** [PRIOR_AUTH_API_EXAMPLES.md](PRIOR_AUTH_API_EXAMPLES.md)

### Support Channels
- GitHub Issues: [Your Repo URL]
- Email: [Your Email]
- Demo Day: Find us at [Your Booth/Table]

---

## Configuration Reference

### Agent Configuration Fields

```json
{
  "agent_name": "Sarah Mitchell",           // AI agent's name
  "agent_role": "Prior Authorization Specialist",
  "company_name": "HealthCare RCM Solutions",
  "patient_name": "John Doe",              // From API call
  "patient_dob": "1975-06-15",             // Date of birth
  "member_id": "ABC123456789",             // Insurance member ID
  "provider_name": "Dr. Sarah Smith",
  "provider_npi": "1234567890",
  "cpt_code": "72148",                     // Procedure code
  "procedure_description": "MRI Lumbar Spine",
  "icd_code": "M54.5",                     // Diagnosis code
  "diagnosis_description": "Low back pain",
  "insurance_company": "Blue Cross Blue Shield",
  "urgency_level": "routine",              // routine/urgent/stat
  "clinical_notes": "..."                   // Medical necessity
}
```

### Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `TWILIO_ACCOUNT_SID` | Twilio authentication | `ACxxxxxxxxxx` |
| `TWILIO_AUTH_TOKEN` | Twilio secret | `your_token_here` |
| `TWILIO_PHONE_NUMBER` | Your Twilio number | `+12025551234` |
| `AWS_REGION` | AWS Bedrock region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS credentials | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret | `your_secret` |
| `DEEPGRAM_API_KEY` | Speech-to-text | `your_key_here` |
| `ELEVENLABS_API_KEY` | Text-to-speech | `your_key_here` |
| `HTTP_SERVER_PORT` | Server port | `3000` |

---

**🎊 You're all set! Happy demoing!**

---

*Last Updated: November 6, 2025*
