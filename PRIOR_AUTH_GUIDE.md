# 🏥 Prior Authorization System - Complete Guide

## Overview

This system automatically processes prior authorization phone calls, extracting and validating critical information to streamline the revenue cycle management process.

## ✨ Features

### 1. **Intelligent Information Extraction** 🤖
- Uses AWS Bedrock Claude to extract structured data from conversations
- Captures authorization numbers, reference numbers, representative info
- Extracts documentation requirements and deadlines
- Determines authorization status (approved/denied/pending)

### 2. **Comprehensive Validation** ✅
- Validates completeness of captured information
- Checks data formats (CPT codes, ICD codes, NPI, phone numbers)
- Enforces business rules (deadline logic, validity periods)
- Generates actionable next steps

### 3. **Structured Storage** 💾
- Saves records in JSON format
- Organizes by status (approved/pending/denied/failed)
- Creates human-readable text summaries
- Supports export to CSV for analytics

### 4. **Automated Workflows** 🔄
- Triggers post-call processing automatically on call completion
- Generates task lists based on authorization status
- Logs workflow actions for team coordination

### 5. **Notification System** 📧
- Sends email notifications to providers
- Includes full call summary and next steps
- HTML and plain text email formats
- Highlights urgent items and missing information

---

## 🚀 Quick Start

### Installation

The system is automatically integrated with your Outbound Phone GPT installation. No additional setup required!

### Basic Usage

The system works automatically! When a prior authorization call completes:

1. **Call Completion Detected**: System detects `<END_OF_CALL>` marker
2. **Information Extracted**: LLM extracts structured data from conversation
3. **Validation Performed**: Data validated for completeness and accuracy
4. **Record Saved**: JSON and text files saved to `prior_auth_records/`
5. **Workflows Triggered**: Next steps logged and tasks generated

---

## 📊 What Gets Captured

### Patient Information
- Name
- Date of Birth
- Member ID

### Provider Information
- Provider Name
- NPI Number

### Procedure Details
- CPT Code & Description
- ICD-10 Diagnosis Code
- Proposed Service Date

### Authorization Details
- ✅ **Authorization Number** (if approved)
- 📋 **Reference Number**
- 📅 **Valid Dates** (from/to)
- 👤 **Representative Name & ID**

### Documentation Requirements
- Required documents list
- Submission method (fax/portal)
- Fax number
- ⏰ **Submission deadline**

### Timeline Information
- Standard turnaround time
- Expected decision date
- Expedited review status

---

## 📂 File Organization

```
prior_auth_records/
├── approved/
│   ├── 20251028_160200_CA1234567890.json
│   └── 20251028_160200_CA1234567890.txt
├── pending/
│   ├── 20251028_153000_CA0987654321.json
│   └── 20251028_153000_CA0987654321.txt
├── denied/
│   └── ...
└── failed/
    └── ...
```

---

## 🔍 Example Output

### JSON Record
```json
{
  "call_id": "CA1234567890",
  "call_date": "2025-10-28T16:02:00",
  "insurance_company": "Blue Cross Blue Shield",
  "patient": {
    "name": "John Doe",
    "date_of_birth": "1975-06-15",
    "member_id": "ABC123456789"
  },
  "authorization": {
    "status": "approved",
    "authorization_number": "AUTH-2025-12345",
    "reference_number": "REF-XYZ789",
    "valid_from": "2025-10-28",
    "valid_to": "2026-01-28"
  },
  "call_outcome": "success",
  "next_steps": [
    "✅ Authorization approved! Reference: AUTH-2025-12345",
    "Proceed with scheduling procedure",
    "Update EHR/billing system with authorization number"
  ]
}
```

### Text Summary
```
================================================================================
PRIOR AUTHORIZATION CALL SUMMARY
================================================================================

Call ID: CA1234567890
Date: 2025-10-28 16:02:00
Insurance: Blue Cross Blue Shield
Status: APPROVED
Outcome: SUCCESS

--------------------------------------------------------------------------------
PATIENT INFORMATION
--------------------------------------------------------------------------------
Name: John Doe
DOB: 1975-06-15
Member ID: ABC123456789

--------------------------------------------------------------------------------
AUTHORIZATION DETAILS
--------------------------------------------------------------------------------
✅ Authorization Number: AUTH-2025-12345
Reference Number: REF-XYZ789
Valid: 2025-10-28 to 2026-01-28

--------------------------------------------------------------------------------
NEXT STEPS
--------------------------------------------------------------------------------
1. ✅ Authorization approved! Reference: AUTH-2025-12345
2. Proceed with scheduling procedure
3. Update EHR/billing system with authorization number

================================================================================
```

---

## 🎯 Status-Based Workflows

### ✅ APPROVED
- Update EHR with authorization number
- Contact patient to schedule procedure
- Update billing system
- Proceed with service delivery

### ⏳ PENDING
- Submit required documentation
- Fax to specified number by deadline
- Follow up on expected decision date
- Monitor for approval

### ❌ DENIED
- Review denial reason with provider
- Gather additional documentation
- Prepare and submit formal appeal
- Consider peer-to-peer review

### 👨‍⚕️ PEER-TO-PEER REQUIRED
- Schedule call with insurance medical director
- Prepare clinical documentation
- Provider discusses medical necessity
- Follow up after review

---

## 📧 Email Notifications

To enable email notifications, set environment variables:

```bash
SMTP_SERVER=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=prior-auth@yourcompany.com
```

Or configure in code:
```python
from healthcare_rcm.notifications.notifier import PriorAuthNotifier

notifier = PriorAuthNotifier(
    smtp_server='smtp.gmail.com',
    smtp_port=587,
    smtp_username='your-email@gmail.com',
    smtp_password='your-app-password',
    from_email='prior-auth@yourcompany.com'
)

notifier.process_record(record, provider_email='dr.smith@clinic.com')
```

---

## 🔧 Manual Processing

To manually process a call:

```python
from healthcare_rcm.processors.post_call_processor import process_completed_call

conversation_history = [
    "Sarah Mitchell: Hi, this is Sarah Mitchell...",
    "User: Hello?",
    # ... full conversation
]

agent_config = {
    'agent_role': 'prior_authorization',
    'patient_name': 'John Doe',
    'patient_dob': '1975-06-15',
    'member_id': 'ABC123456789',
    'provider_name': 'Dr. Sarah Smith',
    'provider_npi': '1234567890',
    'cpt_code': '72148',
    'procedure_description': 'MRI Lumbar Spine',
    'icd_code': 'M54.5',
    'insurance_company': 'Blue Cross Blue Shield'
}

record = process_completed_call(
    conversation_history=conversation_history,
    call_id='CA1234567890',
    agent_config=agent_config
)

print(f"Status: {record.authorization.status.value}")
print(f"Auth Number: {record.authorization.authorization_number}")
```

---

## 📊 Analytics & Reporting

### View Summary Statistics
```python
from healthcare_rcm.storage.prior_auth_storage import get_storage

storage = get_storage()
stats = storage.get_summary_statistics()

print(f"Total Calls: {stats['total_records']}")
print(f"Approved: {stats['by_status']['approved']}")
print(f"Pending: {stats['by_status']['pending']}")
print(f"Denied: {stats['by_status']['denied']}")
```

### Export to CSV
```python
storage.export_to_csv('prior_auth_report.csv')
```

### Query Records
```python
from healthcare_rcm.models.prior_auth_models import AuthorizationStatus
from datetime import date, timedelta

# Get all approved authorizations from last 7 days
approved_records = storage.list_records(
    status=AuthorizationStatus.APPROVED,
    start_date=date.today() - timedelta(days=7)
)

for filepath in approved_records:
    record = storage.load_record(filepath)
    print(f"{record.patient.name}: {record.authorization.authorization_number}")
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Phone Call Completed                     │
│                  (END_OF_CALL detected)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              1. INFORMATION EXTRACTION                       │
│  • LLM analyzes conversation transcript                      │
│  • Extracts authorization numbers, status, requirements      │
│  • Captures representative info and timelines               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              2. VALIDATION                                   │
│  • Check completeness (required fields present)              │
│  • Validate formats (CPT, ICD, NPI, phone numbers)          │
│  • Verify business rules (deadlines, validity periods)      │
│  • Generate next steps based on status                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              3. STORAGE                                      │
│  • Save JSON record (structured data)                       │
│  • Save text summary (human-readable)                       │
│  • Organize by status (approved/pending/denied)             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              4. NOTIFICATIONS & WORKFLOWS                    │
│  • Send email to provider                                   │
│  • Generate task list                                       │
│  • Log workflow actions                                     │
│  • Trigger automated follow-ups                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Configuration

### Agent Config Fields

Add these fields to your agent configuration JSON to enable proper extraction:

```json
{
  "agent_role": "prior_authorization",
  "patient_name": "John Doe",
  "patient_dob": "1975-06-15",
  "member_id": "ABC123456789",
  "provider_name": "Dr. Sarah Smith",
  "provider_npi": "1234567890",
  "cpt_code": "72148",
  "procedure_description": "MRI Lumbar Spine without contrast",
  "icd_code": "M54.5",
  "diagnosis_description": "Low back pain",
  "insurance_company": "Blue Cross Blue Shield"
}
```

---

## 🐛 Troubleshooting

### Issue: No records being created
**Solution**: Check that `<END_OF_CALL>` is in the agent's final response, or that completion phrases like "goodbye" are detected.

### Issue: Missing fields in extracted data
**Solution**: Review conversation transcript - ensure representative provided the information. Check `missing_fields` list in record.

### Issue: Email notifications not sending
**Solution**: Verify SMTP credentials are set. Check logs for specific error messages. Test with basic SMTP connection.

### Issue: Wrong authorization status
**Solution**: Check LLM extraction prompt. Review conversation for ambiguous responses from insurance rep.

---

## 📚 API Reference

### Core Classes

- **`PriorAuthRecord`**: Complete authorization record data model
- **`PriorAuthExtractor`**: Extracts information from conversations
- **`PriorAuthValidator`**: Validates records for completeness
- **`PriorAuthStorage`**: Manages file storage and retrieval
- **`PriorAuthNotifier`**: Handles notifications and workflows

### Key Functions

- **`process_completed_call()`**: Main entry point for processing
- **`extract_prior_auth_info()`**: Extract data from conversation
- **`validate_prior_auth()`**: Validate a record
- **`notify_and_automate()`**: Trigger notifications

---

## 🎓 Best Practices

1. **Always capture reference numbers** - Even if authorization is pending/denied
2. **Document deadlines** - Critical for avoiding delays
3. **Verify representative info** - Needed for follow-up calls
4. **Review validation errors** - Fix missing information promptly
5. **Follow next steps** - System-generated tasks ensure nothing is missed

---

## 🆘 Support

For questions or issues:
1. Check logs in `output.log`
2. Review validation errors in record
3. Examine conversation transcript for extraction issues
4. Verify agent configuration is complete

---

## 📈 Future Enhancements

- [ ] EHR integration (Epic, Cerner)
- [ ] CRM integration (Salesforce)
- [ ] Real-time analytics dashboard
- [ ] Machine learning for improved extraction
- [ ] Multi-language support
- [ ] Voice recording storage
- [ ] Automated appeal generation

---

## 🏆 Success Metrics

Track these KPIs:
- **Approval Rate**: % of calls approved
- **Average Processing Time**: Time from call to documentation submission
- **Missing Information Rate**: % of records with missing fields
- **Follow-up Completion Rate**: % of next steps completed on time
- **Appeal Success Rate**: % of denied auths successfully appealed

---

**Built with ❤️ for Healthcare RCM Teams**
