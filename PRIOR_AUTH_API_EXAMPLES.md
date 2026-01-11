# 🏥 Prior Authorization API - curl Examples

## ✅ Complete Implementation

**No JSON editing required!** Pass all prior auth details directly in your API call.

---

## 📋 Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `to_number` | Phone number to call | `"+917013017884"` |
| `patient_name` | Patient full name | `"John Doe"` |
| `cpt_code` | Procedure code | `"72148"` |
| `insurance_company` | Insurance name | `"Blue Cross Blue Shield"` |

## 🎯 Recommended Fields

| Field | Description | Example |
|-------|-------------|---------|
| `member_id` | Insurance member ID | `"ABC123456789"` |
| `patient_dob` | Date of birth | `"1975-06-15"` |
| `provider_name` | Provider name | `"Dr. Sarah Smith"` |
| `provider_npi` | NPI number | `"1234567890"` |
| `icd_code` | Diagnosis code | `"M54.5"` |
| `proposed_date` | Service date | `"2025-11-15"` |

---

## 🚀 Example 1: MRI Lumbar Spine (Most Common)

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+917013017884",
    "welcome_message": "Hi, this is Sarah Mitchell from HealthCare RCM Solutions.",
    
    "patient_name": "John Doe",
    "patient_dob": "1975-06-15",
    "member_id": "ABC123456789",
    
    "provider_name": "Dr. Sarah Smith",
    "provider_npi": "1234567890",
    
    "cpt_code": "72148",
    "procedure_description": "MRI Lumbar Spine without contrast",
    
    "icd_code": "M54.5",
    "diagnosis_description": "Low back pain",
    
    "insurance_company": "Blue Cross Blue Shield",
    "proposed_date": "2025-11-15",
    "urgency_level": "routine"
  }'
```

**Windows Command Prompt:**
```batch
curl -X POST "http://localhost:3000/make-call" -H "Content-Type: application/json" -d "{\"to_number\": \"+917013017884\", \"patient_name\": \"John Doe\", \"patient_dob\": \"1975-06-15\", \"member_id\": \"ABC123456789\", \"provider_name\": \"Dr. Sarah Smith\", \"provider_npi\": \"1234567890\", \"cpt_code\": \"72148\", \"procedure_description\": \"MRI Lumbar Spine\", \"icd_code\": \"M54.5\", \"insurance_company\": \"Blue Cross Blue Shield\"}"
```

---

## 🦴 Example 2: Knee Arthroscopy

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+917013017884",
    "welcome_message": "Hello, this is Sarah Mitchell calling about a prior authorization.",
    
    "patient_name": "Jane Smith",
    "patient_dob": "1980-03-12",
    "member_id": "XYZ987654321",
    
    "provider_name": "Dr. Michael Johnson",
    "provider_npi": "9876543210",
    
    "cpt_code": "29881",
    "procedure_description": "Knee Arthroscopy with Meniscectomy",
    
    "icd_code": "M23.2",
    "diagnosis_description": "Meniscus tear",
    
    "insurance_company": "United Healthcare",
    "proposed_date": "2025-11-20",
    "urgency_level": "routine",
    
    "clinical_notes": "Patient with chronic knee pain, MRI confirms medial meniscus tear, failed conservative treatment."
  }'
```

---

## 💊 Example 3: Sleep Study

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+917013017884",
    
    "patient_name": "Robert Wilson",
    "patient_dob": "1965-07-22",
    "member_id": "DEF456789012",
    
    "provider_name": "Dr. Emily Chen",
    "provider_npi": "5555555555",
    
    "cpt_code": "95810",
    "procedure_description": "Polysomnography (Sleep Study)",
    
    "icd_code": "G47.33",
    "diagnosis_description": "Obstructive sleep apnea",
    
    "insurance_company": "Aetna",
    "proposed_date": "2025-11-25",
    "urgency_level": "routine"
  }'
```

---

## 🫀 Example 4: Cardiac Catheterization (Urgent)

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+917013017884",
    
    "patient_name": "Michael Brown",
    "patient_dob": "1955-11-30",
    "member_id": "GHI123456789",
    
    "provider_name": "Dr. David Lee",
    "provider_npi": "2222222222",
    
    "cpt_code": "93458",
    "procedure_description": "Cardiac Catheterization",
    
    "icd_code": "I25.1",
    "diagnosis_description": "Coronary artery disease",
    
    "insurance_company": "Medicare",
    "proposed_date": "2025-11-08",
    "urgency_level": "urgent",
    
    "clinical_notes": "Patient with unstable angina, positive stress test, requires urgent cardiac catheterization."
  }'
```

---

## 🩺 Example 5: Physical Therapy (Multiple Sessions)

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+917013017884",
    
    "patient_name": "Sarah Davis",
    "patient_dob": "1992-04-18",
    "member_id": "JKL789012345",
    
    "provider_name": "Dr. Amanda White",
    "provider_npi": "3333333333",
    
    "cpt_code": "97110",
    "procedure_description": "Physical Therapy - Therapeutic Exercises (12 sessions)",
    
    "icd_code": "M54.5",
    "diagnosis_description": "Low back pain",
    
    "insurance_company": "Cigna",
    "proposed_date": "2025-11-10",
    "urgency_level": "routine"
  }'
```

---

## 📱 Example 6: Minimal Fields (Quick Test)

```bash
curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+917013017884",
    "patient_name": "Test Patient",
    "cpt_code": "99213",
    "insurance_company": "Test Insurance"
  }'
```

---

## 🔄 What Happens After You Make the Call

1. **Call is initiated** via Twilio
2. **Agent converses** with insurance representative
3. **END_OF_CALL detected** when conversation finishes
4. **Automatic processing** extracts:
   - ✅ Authorization number
   - ✅ Reference number
   - ✅ Representative name
   - ✅ Documentation requirements
   - ✅ Deadlines
5. **Validation** checks completeness
6. **Storage** saves to `prior_auth_records/`
7. **Next steps** generated automatically

---

## 📊 View Results

**Check the logs:**
```bash
type output.log | findstr "Prior auth"
```

**View saved records:**
```
prior_auth_records/
├── approved/
│   └── 20251028_160200_CA1234567890.json
├── pending/
│   └── 20251028_153000_CA0987654321.json
└── denied/
    └── 20251028_144500_CA1122334455.json
```

**Read the summary:**
```bash
type prior_auth_records\approved\20251028_160200_CA1234567890.txt
```

---

## 🎯 Python Example

```python
import requests

prior_auth = {
    "to_number": "+917013017884",
    "patient_name": "John Doe",
    "patient_dob": "1975-06-15",
    "member_id": "ABC123456789",
    "provider_name": "Dr. Sarah Smith",
    "provider_npi": "1234567890",
    "cpt_code": "72148",
    "procedure_description": "MRI Lumbar Spine",
    "icd_code": "M54.5",
    "diagnosis_description": "Low back pain",
    "insurance_company": "Blue Cross Blue Shield",
    "proposed_date": "2025-11-15"
}

response = requests.post(
    "http://localhost:3000/make-call",
    json=prior_auth
)

print(f"Call initiated: {response.json()['call_sid']}")
```

---

## 🔧 Troubleshooting

### Issue: "Field required" error
**Solution**: Ensure `to_number` is included in your request.

### Issue: No processing happens
**Solution**: Make sure you include at least `patient_name` to trigger prior auth processing.

### Issue: Agent doesn't mention patient details
**Solution**: The agent will use the details you provide in the API call - no JSON config needed!

---

## 💡 Tips

1. **Patient Name Required**: Must include `patient_name` to trigger prior auth processing
2. **Phone Number**: Always provide valid `to_number`
3. **Optional Welcome Message**: System has a default if you don't provide one
4. **All Fields Optional**: Except `to_number` - but more fields = better processing
5. **Dates Format**: Use `YYYY-MM-DD` format for dates

---

## 📋 Common CPT Codes

| Code | Description |
|------|-------------|
| `72148` | MRI Lumbar Spine |
| `29881` | Knee Arthroscopy |
| `93458` | Cardiac Catheterization |
| `95810` | Sleep Study |
| `97110` | Physical Therapy |
| `70553` | MRI Brain |
| `43239` | Upper Endoscopy |
| `45378` | Colonoscopy |

---

## 🏥 Common ICD-10 Codes

| Code | Description |
|------|-------------|
| `M54.5` | Low back pain |
| `M23.2` | Meniscus tear |
| `I25.1` | Coronary artery disease |
| `G47.33` | Obstructive sleep apnea |
| `I10` | Essential hypertension |
| `E11.9` | Type 2 diabetes |
| `J44.0` | COPD |

---

## ✅ Ready to Use!

**No more JSON editing!** Just update your curl command with each patient's details and make the call. 🚀

The system will:
- ✅ Use your provided details during the call
- ✅ Extract information from the conversation
- ✅ Validate completeness
- ✅ Save structured records
- ✅ Generate next steps

**Everything is externalized!** 🎉
