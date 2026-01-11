# AWS Bedrock Setup Guide for Outbound Phone GPT

This guide will help you integrate AWS Bedrock (Claude) with the Outbound Phone GPT system, eliminating the need for OpenAI API keys.

## 🎯 Why AWS Bedrock?

- **No OpenAI dependency** - Use Claude 3.5 Sonnet directly
- **Enterprise-grade** - AWS infrastructure and security
- **Cost-effective** - Pay-as-you-go pricing
- **High performance** - Low latency responses
- **HIPAA compliant** - Perfect for healthcare use cases

## 📋 Prerequisites

1. **AWS Account** with access to Bedrock
2. **IAM User** with Bedrock permissions
3. **Twilio Account** for voice calls
4. **Deepgram Account** for speech-to-text
5. **Eleven Labs Account** for text-to-speech

## 🚀 Setup Steps

### Step 1: Enable AWS Bedrock Access

1. Log into AWS Console
2. Navigate to AWS Bedrock service
3. Go to **Model access** in the left sidebar
4. Request access to **Claude 3.5 Sonnet**
5. Wait for approval (usually instant for most accounts)

### Step 2: Create IAM User with Bedrock Permissions

```bash
# In AWS Console, create IAM user with these permissions:
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

### Step 3: Get AWS Credentials

1. In IAM Console, create access keys for your user
2. Save the **Access Key ID** and **Secret Access Key**
3. Note your preferred AWS region (e.g., `us-east-1`)

### Step 4: Install Dependencies

```bash
cd Outbound-Phone-GPT-main
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### Step 5: Configure Environment

Create `.env` file:

```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
```

Your `.env` should look like:

```bash
# LLM Provider - Use Bedrock
LLM_PROVIDER=bedrock

# AWS Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...your_key...
AWS_SECRET_ACCESS_KEY=your_secret_key_here
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# Twilio Configuration
TWILIO_ACCOUNT_SID=AC...your_sid...
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Deepgram Configuration
DEEPGRAM_API_KEY=your_deepgram_key
DEEPGRAM_MODEL_ID=nova-2

# Eleven Labs Configuration
ELEVEN_LABS_API_KEY=your_eleven_labs_key
ELEVEN_LABS_VOICE_ID=your_voice_id
ELEVEN_LABS_TURBO_MODEL_ID=eleven_turbo_v2
```

### Step 6: Configure Agent for Your Use Case

Edit agent configuration in `example_agent_configs/`:

**For Insurance Claims Follow-up:**
```json
{
  "agent_name": "Sarah",
  "agent_role": "Insurance Verification Specialist",
  "company_name": "ABC Healthcare",
  "company_business": "Healthcare Revenue Cycle Management",
  "conversation_purpose": "to follow up on insurance claim status",
  "conversation_type": "phone call",
  "prompt": "Your name is {agent_name} and you work as a {agent_role} at {company_name}. You are calling to {conversation_purpose}.\n\nYour goal is to:\n1. Verify you're speaking to the right department\n2. Provide claim number and patient information\n3. Ask about claim status\n4. Document any issues or denials\n5. Escalate to human agent if unable to resolve\n\nBe professional, polite, and patient. If you encounter complex issues, transfer to a human agent.\n\nConversation history:\n{conversation_history}\n\nYour response:"
}
```

### Step 7: Update Conversation Stages

Edit `ConversationModel/stages.py`:

```python
# For Insurance Claims Follow-up
INSURANCE_CONVERSATION_STAGES = {
    '1': 'Greeting: Introduce yourself and verify you have the right person/department',
    '2': 'Claim Identification: Provide claim number and patient details',
    '3': 'Status Inquiry: Ask about current claim status',
    '4': 'Information Gathering: Document claim status, denials, or required actions',
    '5': 'Issue Resolution: Attempt to resolve simple issues or get next steps',
    '6': 'Escalation Check: Determine if human agent is needed',
    '7': 'Close: Summarize outcome and thank for their time',
    '8': 'End conversation: Call complete or escalated to human'
}
```

## 🧪 Testing Your Setup

### Test 1: Verify AWS Credentials

```python
# test_bedrock.py
import boto3
import json

bedrock = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1'
)

request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Say 'Hello, Bedrock is working!'"
        }
    ]
}

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',
    body=json.dumps(request_body)
)

response_body = json.loads(response['body'].read())
print(response_body['content'][0]['text'])
```

Run: `python test_bedrock.py`

### Test 2: Start the Application

```bash
python app.py
```

You should see:
```
Initializing with AWS Bedrock model: anthropic.claude-3-5-sonnet-20240620-v1:0
Server started on port 3000
```

### Test 3: Make a Test Call

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{"welcome_message": "Hello, this is Sarah calling about your insurance claim CLM-12345."}'
```

## 💰 Cost Comparison

| Provider | Cost per Call | Notes |
|----------|--------------|-------|
| **AWS Bedrock (Claude 3.5 Sonnet)** | ~$0.001-0.003 | Input: $0.003/1K tokens, Output: $0.015/1K tokens |
| OpenAI GPT-3.5-turbo | ~$0.002 | $0.001/1K tokens |
| OpenAI GPT-4 | ~$0.030 | $0.03/1K input, $0.06/1K output |

**For a 5-minute call with ~2000 tokens:**
- AWS Bedrock: **$0.030-0.045**
- OpenAI GPT-3.5: **$0.002**
- OpenAI GPT-4: **$0.120**

## 🔧 Switching Between Providers

You can easily switch between Bedrock and OpenAI:

```bash
# Use AWS Bedrock
LLM_PROVIDER=bedrock

# Use OpenAI
LLM_PROVIDER=openai
```

## 📊 Available Bedrock Models

| Model | Model ID | Best For |
|-------|----------|----------|
| **Claude 3.5 Sonnet** | `anthropic.claude-3-5-sonnet-20240620-v1:0` | Best balance of speed/quality (Recommended) |
| Claude 3 Opus | `anthropic.claude-3-opus-20240229-v1:0` | Highest quality, slower |
| Claude 3 Haiku | `anthropic.claude-3-haiku-20240307-v1:0` | Fastest, lower cost |

## 🐛 Troubleshooting

### Error: "Could not connect to the endpoint URL"
```bash
# Check AWS region is correct
AWS_REGION=us-east-1

# Verify Bedrock is available in your region
# Bedrock available in: us-east-1, us-west-2, eu-west-1, ap-southeast-1, ap-northeast-1
```

### Error: "AccessDeniedException"
```bash
# Your IAM user needs bedrock:InvokeModel permission
# Go to IAM Console → Users → Your User → Add Permissions
```

### Error: "ValidationException: The provided model identifier is invalid"
```bash
# Check model access in Bedrock Console
# AWS Console → Bedrock → Model access → Enable Claude 3.5 Sonnet
```

### Error: "Module 'boto3' not found"
```bash
pip install boto3 langchain-aws
```

## 🎯 Production Best Practices

1. **Use IAM Roles** instead of access keys (when running on EC2/ECS)
2. **Enable CloudWatch Logs** for monitoring
3. **Set up billing alarms** for unexpected costs
4. **Use VPC endpoints** for better security
5. **Implement rate limiting** to control costs
6. **Cache common responses** to reduce API calls

## 📞 Support

- AWS Bedrock Documentation: https://docs.aws.amazon.com/bedrock/
- Claude Model Documentation: https://docs.anthropic.com/claude/docs
- Project Issues: Create issue in repository

## ✅ Verification Checklist

- [ ] AWS account with Bedrock access
- [ ] IAM credentials configured
- [ ] Claude 3.5 Sonnet access enabled
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Agent configuration updated
- [ ] Test call successful
- [ ] Voice quality acceptable
- [ ] Latency under 2 seconds

---

**🎉 You're now running Outbound Phone GPT with AWS Bedrock (Claude)!**

No OpenAI key needed - you're using enterprise-grade AWS infrastructure for your healthcare voice agent.
