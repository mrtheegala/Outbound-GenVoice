# 🤖 Multi-Agent Healthcare RCM System

Complete guide for using Prior Authorization and Denial Management agents.

---

## 🎯 Available Agents

### 1. Prior Authorization Agent
**Purpose:** Request prior authorization for medical procedures  
**Use Case:** Get approval before procedures  
**Output:** Authorization status, auth number, requirements

### 2. Denial Management Agent  
**Purpose:** Resolve denied insurance claims  
**Use Case:** Appeal or resubmit denied claims  
**Output:** Resolution status, required docs, next steps

---

## 🚀 Quick Start

### Start Server
```bash
python app.py
```

### Test Prior Authorization
```bash
test_prior_auth.bat
```

### Test Denial Management
```bash
test_denial_mgmt.bat
```

---

## 📋 API Reference

### Endpoint
```
POST http://localhost:3000/make-call
Content-Type: application/json
```

### Common Fields (All Agents)
```json
{
  "agent_type": "prior_auth",  // or "denial_mgmt"
  "to_number": "+919550760205",
  "welcome_message": "Hi, calling from healthcare..."
}
```

---

## 🏥 Prior Authorization Agent

### API Request
```json
{
  "agent_type": "prior_auth",
  "to_number": "+919550760205",
  
  // Patient Info
  "patient_name": "Madhav Thakur",
  "patient_dob": "1990-05-12",
  "member_id": "TEST12345",
  
  // Provider Info
  "provider_name": "Dr. Sarah Smith",
  "provider_npi": "1234567890",
  
  // Procedure Info
  "cpt_code": "72148",
  "procedure_description": "MRI Lumbar Spine",
  "icd_code": "M54.5",
  "diagnosis_description": "Low back pain",
  
  // Payer Info
  "insurance_company": "Blue Cross Blue Shield",
  
  // Optional
  "proposed_date": "2024-12-15",
  "urgency_level": "routine",
  "clinical_notes": "Patient has chronic back pain"
}
```

### cURL Example
```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "prior_auth",
    "to_number": "+919550760205",
    "patient_name": "Madhav Thakur",
    "patient_dob": "1990-05-12",
    "member_id": "TEST12345",
    "provider_name": "Dr. Sarah Smith",
    "provider_npi": "1234567890",
    "cpt_code": "72148",
    "procedure_description": "MRI Lumbar Spine",
    "icd_code": "M54.5",
    "diagnosis_description": "Low back pain",
    "insurance_company": "Blue Cross Blue Shield"
  }'
```

### Output Location
```
prior_auth_records/
  ├── success/     # Approved authorizations
  ├── failed/      # Denied authorizations
  └── pending/     # Pending review
```

### Output Structure
```json
{
  "call_id": "uuid-here",
  "timestamp": "2024-10-30T09:00:00",
  "authorization": {
    "status": "approved",
    "authorization_number": "AUTH-12345",
    "valid_from": "2024-10-30",
    "valid_to": "2024-12-30"
  },
  "representative": {
    "name": "John Smith",
    "id": "REP12345"
  },
  "documentation": {
    "required_documents": ["Medical records"],
    "submission_method": "fax",
    "fax_number": "555-1234"
  }
}
```

---

## 🚫 Denial Management Agent

### API Request
```json
{
  "agent_type": "denial_mgmt",
  "to_number": "+919550760205",
  
  // Claim Info
  "claim_number": "CLM-2024-12345",
  "service_date": "2024-03-15",
  
  // Patient Info
  "patient_name": "Madhav Thakur",
  
  // Procedure Info
  "procedure_code": "29881",
  "procedure_name": "Knee Arthroscopy with Meniscectomy",
  "diagnosis_code": "M23.205",
  
  // Denial Info
  "denial_code": "CO-50",
  "denial_reason": "Not deemed medical necessity",
  
  // Payer Info
  "payer_name": "United Healthcare",
  
  // Provider Info
  "provider_name": "Dr. Michael Johnson",
  "provider_npi": "9876543210"
}
```

### cURL Example
```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "denial_mgmt",
    "to_number": "+919550760205",
    "claim_number": "CLM-2024-12345",
    "patient_name": "Madhav Thakur",
    "service_date": "2024-03-15",
    "procedure_code": "29881",
    "procedure_name": "Knee Arthroscopy",
    "diagnosis_code": "M23.205",
    "denial_code": "CO-50",
    "denial_reason": "Medical necessity not established",
    "payer_name": "United Healthcare",
    "provider_name": "Dr. Michael Johnson",
    "provider_npi": "9876543210"
  }'
```

### Output Location
```
denial_mgmt_records/
  ├── success/     # Overturned or resubmittable
  ├── failed/      # Upheld denials
  └── pending/     # Pending review/appeal
```

### Output Structure
```json
{
  "call_id": "uuid-here",
  "timestamp": "2024-10-30T09:00:00",
  "claim": {
    "claim_number": "CLM-2024-12345",
    "patient_name": "Madhav Thakur",
    "service_date": "2024-03-15"
  },
  "denial_info": {
    "denial_code": "CO-50",
    "denial_reason": "Medical necessity",
    "resolution_status": "resubmit_required",
    "resolution_path": "resubmit with documentation"
  },
  "resolution": {
    "required_documents": ["Medical records", "Physician notes"],
    "submission_method": "fax",
    "fax_number": "555-1234",
    "submission_deadline": "2024-12-31"
  },
  "timeline": {
    "reprocessing_time": "10-14 days",
    "appeal_deadline": "2024-12-15"
  }
}
```

---

## 🔍 Monitoring

### Check Logs
```bash
# All logs
type output.log

# Prior auth specific
type output.log | findstr "[PRIOR_AUTH]"

# Denial management specific
type output.log | findstr "[DENIAL_MGMT]"

# Configuration overrides
type output.log | findstr "[CONFIG]"

# Extraction results
type output.log | findstr "[FALLBACK]"
```

### Check Output Files
```bash
# Prior auth records
dir prior_auth_records\*\*.json
type prior_auth_records\success\*.txt

# Denial management records
dir denial_mgmt_records\*\*.json
type denial_mgmt_records\success\*.txt
```

---

## 🛠️ Configuration

### Switch Default Agent
Edit `__config__.py`:
```python
# Default agent for /make-call without agent_type
AGENT_CONFIG_PATH = PRIOR_AUTH_CONFIG_PATH  # or DENIAL_MGMT_CONFIG_PATH
```

### Customize Agent Behavior
Edit agent configs:
- `example_agent_configs/Prior_Auth_Agent_config.json`
- `example_agent_configs/Denial_Management_Agent_config.json`

---

## 🧪 Testing Scenarios

### Prior Auth - Approved
```json
{"agent_type": "prior_auth", "patient_name": "Test Patient", ...}
```
Expected: Authorization number, valid dates

### Prior Auth - Denied
```json
{"agent_type": "prior_auth", "urgency_level": "non-urgent", ...}
```
Expected: Denial reason, appeal process

### Denial - Overturned
```json
{"agent_type": "denial_mgmt", "denial_reason": "missing documentation", ...}
```
Expected: Resubmission instructions

### Denial - Upheld
```json
{"agent_type": "denial_mgmt", "denial_reason": "not covered", ...}
```
Expected: Appeal process, peer-to-peer options

---

## 📊 Success Metrics

### Prior Authorization
- ✅ Authorization number received
- ✅ Valid dates confirmed
- ✅ Requirements documented
- ✅ Representative info captured

### Denial Management
- ✅ Resolution path identified
- ✅ Required documents listed
- ✅ Timelines confirmed
- ✅ Reference number captured

---

## 🐛 Troubleshooting

### Issue: Agent says wrong name
**Solution:** Check logs for `[CONFIG] Overriding` - should show your API values

### Issue: No extraction output
**Solution:** Check `[FALLBACK]` logs - fallback extraction should activate

### Issue: Call doesn't end
**Solution:** Agent must say `<END_OF_CALL>` - check conversation flow

### Issue: Wrong agent type
**Solution:** Verify `agent_type` in request matches: `prior_auth` or `denial_mgmt`

---

## 🔧 Advanced Usage

### Custom Welcome Message
```json
{
  "agent_type": "prior_auth",
  "welcome_message": "Hi, I'm calling from XYZ Healthcare...",
  ...
}
```

### Multiple Calls
```bash
# Prior auth
curl -X POST ... (prior_auth payload)

# Denial mgmt
curl -X POST ... (denial_mgmt payload)

# Check results
dir prior_auth_records\success\*.json
dir denial_mgmt_records\success\*.json
```

---

## 📝 Common CPT/ICD Codes

### Prior Authorization
- **72148** - MRI Lumbar Spine
- **70553** - MRI Brain
- **99285** - ED Visit High Complexity
- **M54.5** - Low back pain
- **G43.909** - Migraine

### Denial Management
- **29881** - Knee Arthroscopy
- **52000** - Cystoscopy
- **27447** - Total Knee Replacement
- **M23.205** - Meniscus tear
- **N20.0** - Kidney stone

---

## 🚀 Production Checklist

- [ ] Test both agents end-to-end
- [ ] Verify config overrides work
- [ ] Check extraction output quality
- [ ] Monitor fallback extraction rate
- [ ] Review output file structure
- [ ] Test error handling
- [ ] Validate representative info capture
- [ ] Confirm timeline extraction

---

## 📞 Support

**Logs:** `output.log`  
**Config:** `__config__.py`  
**Agent Configs:** `example_agent_configs/`  
**Outputs:** `prior_auth_records/`, `denial_mgmt_records/`

---

## ✨ Next Steps

1. **Test Prior Auth:** Run `test_prior_auth.bat`
2. **Test Denial Mgmt:** Run `test_denial_mgmt.bat`
3. **Check Results:** Review JSON and TXT files
4. **Iterate:** Refine based on output quality

**You now have a complete multi-agent healthcare RCM system!** 🎉
