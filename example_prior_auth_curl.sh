#!/bin/bash
# Example: Prior Authorization Call for MRI

curl -X POST "http://localhost:3000/make-call" \
  -H "Content-Type: application/json" \
  -d '{
    "to_number": "+917013017884",
    "welcome_message": "Hi, this is Sarah Mitchell from HealthCare RCM Solutions calling about a prior authorization request.",
    
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
    "urgency_level": "routine",
    
    "clinical_notes": "Patient presents with chronic lower back pain for 8 weeks. Conservative treatment including physical therapy (6 weeks, failed), NSAIDs (minimal relief), muscle relaxants (no improvement). Positive straight leg raise test, radicular symptoms in left leg."
  }'
