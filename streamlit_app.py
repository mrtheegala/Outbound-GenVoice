import streamlit as st
import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

# Page config
st.set_page_config(
    page_title="Healthcare AI Voice Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:3000"

# Example scenarios for quick demo
EXAMPLE_SCENARIOS = {
    "Prior Authorization - MRI": {
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
    },
    "Prior Authorization - CT Scan": {
        "to_number": "+917013017884",
        "welcome_message": "Hello, this is Michael from Premier Medical Services regarding a prior authorization.",
        "patient_name": "Jane Smith",
        "patient_dob": "1982-03-22",
        "member_id": "DEF456789012",
        "provider_name": "Dr. Robert Johnson",
        "provider_npi": "9876543210",
        "cpt_code": "70450",
        "procedure_description": "CT scan of head without contrast",
        "icd_code": "R51",
        "diagnosis_description": "Headache",
        "insurance_company": "United Healthcare",
        "proposed_date": "2025-11-10",
        "urgency_level": "urgent",
        "clinical_notes": "Patient experiencing severe persistent headaches for 3 weeks, unresponsive to medication. Neurological examination shows concerns requiring imaging."
    },
    "Prior Authorization - Knee Surgery": {
        "to_number": "+917013017884",
        "welcome_message": "Good morning, this is Lisa from Orthopedic Care calling about a surgical authorization.",
        "patient_name": "Robert Williams",
        "patient_dob": "1968-09-10",
        "member_id": "GHI789012345",
        "provider_name": "Dr. Emily Chen",
        "provider_npi": "5555555555",
        "cpt_code": "29881",
        "procedure_description": "Arthroscopy, knee, surgical with meniscectomy",
        "icd_code": "M23.205",
        "diagnosis_description": "Derangement of meniscus due to old tear, left knee",
        "insurance_company": "Aetna",
        "proposed_date": "2025-11-20",
        "urgency_level": "routine",
        "clinical_notes": "Patient with documented meniscus tear on MRI. Failed 12 weeks of physical therapy and conservative management. Persistent pain and locking symptoms affecting mobility."
    }
}

def load_call_records():
    """Load call records from prior_auth_records directory"""
    records = []
    records_dir = Path("prior_auth_records")
    
    if not records_dir.exists():
        return []
    
    for status_dir in ["approved", "denied", "pending", "failed"]:
        status_path = records_dir / status_dir
        if status_path.exists():
            for file in status_path.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        record = json.load(f)
                        record['status'] = status_dir
                        record['file'] = file.name
                        records.append(record)
                except Exception as e:
                    st.error(f"Error loading {file.name}: {e}")
    
    # Sort by timestamp (newest first)
    records.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return records

def make_call(call_data):
    """Make API call to initiate voice call"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/make-call",
            json=call_data,
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to server. Make sure the server is running on port 3000."}, 500
    except Exception as e:
        return {"error": str(e)}, 500

def check_call_status(call_sid):
    """Check status of ongoing call"""
    try:
        response = requests.get(f"{API_BASE_URL}/call-status/{call_sid}")
        return response.json()
    except:
        return None

# Header
st.markdown('<div class="main-header">🏥 Healthcare AI Voice Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automating Prior Authorization, Denial Management & Insurance Verification</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Healthcare+AI", width='stretch')
    
    st.markdown("### 📊 System Status")
    
    # Check server status
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Server Online")
        else:
            st.error("❌ Server Error")
    except:
        st.error("❌ Server Offline")
    
    st.markdown("---")
    
    st.markdown("### 📈 Quick Stats")
    records = load_call_records()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Calls", len(records))
    with col2:
        approved = len([r for r in records if r.get('status') == 'approved'])
        st.metric("Approved", approved)
    
    col3, col4 = st.columns(2)
    with col3:
        denied = len([r for r in records if r.get('status') == 'denied'])
        st.metric("Denied", denied)
    with col4:
        pending = len([r for r in records if r.get('status') == 'pending'])
        st.metric("Pending", pending)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ About")
    st.info("""
    **AI Voice Agent** automates routine insurance calls:
    
    - 🎯 Prior Authorization
    - 📋 Denial Management
    - ✅ Insurance Verification
    
    **Cost:** $0.03/call  
    **Response Time:** 1.5-2s  
    **Autonomous Rate:** 87%
    """)

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Make Call", "📊 Call History", "📋 Recent Logs", "💡 API Examples"])

with tab1:
    st.markdown("## 🚀 Initiate Voice Call")
    
    # Initialize session state for form data
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {key: "" for key in EXAMPLE_SCENARIOS["Prior Authorization - MRI"].keys()}
    
    # Example scenario selector
    st.markdown("### Quick Start with Example Scenarios")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 MRI Authorization", width='stretch'):
            st.session_state.form_data = EXAMPLE_SCENARIOS["Prior Authorization - MRI"]
            st.success("✅ Loaded: Prior Authorization - MRI")
    with col2:
        if st.button("🧠 CT Scan", width='stretch'):
            st.session_state.form_data = EXAMPLE_SCENARIOS["Prior Authorization - CT Scan"]
            st.success("✅ Loaded: CT Scan Authorization")
    with col3:
        if st.button("🦵 Knee Surgery", width='stretch'):
            st.session_state.form_data = EXAMPLE_SCENARIOS["Prior Authorization - Knee Surgery"]
            st.success("✅ Loaded: Knee Surgery Authorization")
    with col4:
        if st.button("🗑️ Clear Form", width='stretch'):
            st.session_state.form_data = {key: "" for key in EXAMPLE_SCENARIOS["Prior Authorization - MRI"].keys()}
            st.info("🔄 Form cleared")
    
    st.markdown("---")
    
    # Use session state data
    default_data = st.session_state.form_data
    
    # Call configuration form
    with st.form("call_form"):
        st.markdown("### 📞 Call Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            to_number = st.text_input("Phone Number *", value=default_data.get("to_number", ""), help="Recipient phone number")
            welcome_message = st.text_area("Welcome Message *", value=default_data.get("welcome_message", ""), height=100)
        
        with col2:
            urgency_level = st.selectbox("Urgency Level", ["routine", "urgent", "stat"], index=["routine", "urgent", "stat"].index(default_data.get("urgency_level", "routine") or "routine"))
            insurance_company = st.text_input("Insurance Company *", value=default_data.get("insurance_company", ""))
        
        st.markdown("### 👤 Patient Information")
        col3, col4, col5 = st.columns(3)
        
        with col3:
            patient_name = st.text_input("Patient Name *", value=default_data.get("patient_name", ""))
        with col4:
            patient_dob = st.text_input("Date of Birth *", value=default_data.get("patient_dob", ""), help="Format: YYYY-MM-DD")
        with col5:
            member_id = st.text_input("Member ID *", value=default_data.get("member_id", ""))
        
        st.markdown("### 👨‍⚕️ Provider Information")
        col6, col7 = st.columns(2)
        
        with col6:
            provider_name = st.text_input("Provider Name *", value=default_data.get("provider_name", ""))
        with col7:
            provider_npi = st.text_input("Provider NPI *", value=default_data.get("provider_npi", ""))
        
        st.markdown("### 🏥 Procedure Information")
        col8, col9 = st.columns(2)
        
        with col8:
            cpt_code = st.text_input("CPT Code *", value=default_data.get("cpt_code", ""))
            procedure_description = st.text_input("Procedure Description *", value=default_data.get("procedure_description", ""))
        with col9:
            icd_code = st.text_input("ICD-10 Code *", value=default_data.get("icd_code", ""))
            diagnosis_description = st.text_input("Diagnosis Description *", value=default_data.get("diagnosis_description", ""))
        
        proposed_date = st.text_input("Proposed Date *", value=default_data.get("proposed_date", ""), help="Format: YYYY-MM-DD")
        clinical_notes = st.text_area("Clinical Notes *", value=default_data.get("clinical_notes", ""), height=100)
        
        submit_button = st.form_submit_button("📞 Initiate Call", width='stretch')
        
        if submit_button:
            # Validate required fields
            if not all([to_number, patient_name, patient_dob, member_id, provider_name, provider_npi, 
                       cpt_code, procedure_description, icd_code, diagnosis_description, insurance_company, 
                       proposed_date, clinical_notes, welcome_message]):
                st.error("❌ Please fill in all required fields marked with *")
            else:
                # Prepare call data
                call_data = {
                    "to_number": to_number,
                    "welcome_message": welcome_message,
                    "patient_name": patient_name,
                    "patient_dob": patient_dob,
                    "member_id": member_id,
                    "provider_name": provider_name,
                    "provider_npi": provider_npi,
                    "cpt_code": cpt_code,
                    "procedure_description": procedure_description,
                    "icd_code": icd_code,
                    "diagnosis_description": diagnosis_description,
                    "insurance_company": insurance_company,
                    "proposed_date": proposed_date,
                    "urgency_level": urgency_level,
                    "clinical_notes": clinical_notes
                }
                
                # Show loading spinner
                with st.spinner("🔄 Initiating call..."):
                    response, status_code = make_call(call_data)
                
                # Display result
                if status_code == 200:
                    st.success("✅ Call initiated successfully!")
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.json(response)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Store call SID for tracking
                    if 'call_sid' in response:
                        st.session_state['active_call_sid'] = response['call_sid']
                else:
                    st.error(f"❌ Error initiating call (Status: {status_code})")
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.json(response)
                    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("## 📊 Call History")
    
    # Refresh button
    if st.button("🔄 Refresh", width='content'):
        st.rerun()
    
    records = load_call_records()
    
    if not records:
        st.info("📭 No call records found. Make your first call to see history here!")
    else:
        # Filter options
        col1, col2 = st.columns([1, 3])
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                ["approved", "denied", "pending", "failed"],
                default=["approved", "denied", "pending", "failed"]
            )
        
        # Filter records
        filtered_records = [r for r in records if r.get('status') in status_filter]
        
        st.markdown(f"### Showing {len(filtered_records)} of {len(records)} records")
        
        # Display records
        for idx, record in enumerate(filtered_records):
            status = record.get('status', 'unknown')
            status_emoji = {
                'approved': '✅',
                'denied': '❌',
                'pending': '⏳',
                'failed': '⚠️'
            }.get(status, '❓')
            
            with st.expander(f"{status_emoji} {record.get('patient', {}).get('name', 'Unknown Patient')} - {record.get('timestamp', 'No timestamp')} ({status.upper()})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Patient Information**")
                    patient = record.get('patient', {})
                    st.write(f"- **Name:** {patient.get('name', 'N/A')}")
                    st.write(f"- **DOB:** {patient.get('dob', 'N/A')}")
                    st.write(f"- **Member ID:** {patient.get('member_id', 'N/A')}")
                    
                    st.markdown("**Procedure Information**")
                    procedure = record.get('procedure', {})
                    st.write(f"- **CPT:** {procedure.get('cpt_code', 'N/A')}")
                    st.write(f"- **Description:** {procedure.get('description', 'N/A')}")
                    st.write(f"- **Date:** {procedure.get('proposed_date', 'N/A')}")
                
                with col2:
                    st.markdown("**Authorization Information**")
                    auth = record.get('authorization', {})
                    st.write(f"- **Status:** {auth.get('status', 'N/A')}")
                    st.write(f"- **Reference #:** {auth.get('reference_number', 'N/A')}")
                    st.write(f"- **Effective Date:** {auth.get('effective_date', 'N/A')}")
                    
                    if record.get('representative'):
                        st.markdown("**Representative**")
                        rep = record.get('representative', {})
                        st.write(f"- **Name:** {rep.get('name', 'N/A')}")
                
                if record.get('next_steps'):
                    st.markdown("**Next Steps**")
                    for step in record.get('next_steps', []):
                        st.write(f"- {step}")
                
                if record.get('validation_errors'):
                    st.markdown("**Validation Errors**")
                    for error in record.get('validation_errors', []):
                        st.error(error)
                
                # Full JSON view
                with st.expander("📄 View Full JSON"):
                    st.json(record)

with tab3:
    st.markdown("## 📋 Recent Server Logs")
    
    if st.button("🔄 Refresh Logs", width='content'):
        st.rerun()
    
    # Try to read output.log if it exists
    log_file = Path("output.log")
    
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                logs = f.readlines()
            
            # Show last 100 lines
            recent_logs = logs[-100:]
            
            st.text_area("Server Logs (Last 100 lines)", 
                        value=''.join(recent_logs), 
                        height=400,
                        disabled=True)
        except Exception as e:
            st.error(f"Error reading logs: {e}")
    else:
        st.info("📭 No log file found. Logs will appear here once the server starts running.")

with tab4:
    st.markdown("## 💡 API Examples")
    
    st.markdown("""
    ### REST API Endpoints
    
    The Healthcare AI Voice Agent exposes the following endpoints:
    """)
    
    # Make Call endpoint
    st.markdown("#### 📞 POST `/make-call`")
    st.markdown("Initiates an outbound voice call for prior authorization.")
    
    st.code("""
curl -X POST "http://localhost:3000/make-call" \\
  -H "Content-Type: application/json" \\
  -d '{
    "to_number": "+1234567890",
    "welcome_message": "Hi, this is Sarah from HealthCare calling about prior auth.",
    "patient_name": "John Doe",
    "patient_dob": "1975-06-15",
    "member_id": "ABC123456789",
    "provider_name": "Dr. Smith",
    "provider_npi": "1234567890",
    "cpt_code": "72148",
    "procedure_description": "MRI Lumbar Spine",
    "icd_code": "M54.5",
    "diagnosis_description": "Low back pain",
    "insurance_company": "Blue Cross",
    "proposed_date": "2025-11-15",
    "urgency_level": "routine",
    "clinical_notes": "Patient with chronic pain..."
  }'
""", language="bash")
    
    st.markdown("**Response:**")
    st.code("""
{
  "status": "success",
  "call_sid": "CAxxxxxxxxxxxx",
  "message": "Call initiated successfully"
}
""", language="json")
    
    st.markdown("---")
    
    # Python example
    st.markdown("#### 🐍 Python Example")
    st.code("""
import requests

url = "http://localhost:3000/make-call"
data = {
    "to_number": "+1234567890",
    "patient_name": "John Doe",
    "patient_dob": "1975-06-15",
    "member_id": "ABC123456789",
    "provider_name": "Dr. Smith",
    "provider_npi": "1234567890",
    "cpt_code": "72148",
    "procedure_description": "MRI Lumbar Spine",
    "icd_code": "M54.5",
    "diagnosis_description": "Low back pain",
    "insurance_company": "Blue Cross",
    "proposed_date": "2025-11-15",
    "urgency_level": "routine",
    "clinical_notes": "Patient with chronic pain..."
}

response = requests.post(url, json=data)
print(response.json())
""", language="python")
    
    st.markdown("---")
    
    # JavaScript example
    st.markdown("#### 🌐 JavaScript Example")
    st.code("""
const response = await fetch('http://localhost:3000/make-call', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    to_number: '+1234567890',
    patient_name: 'John Doe',
    patient_dob: '1975-06-15',
    member_id: 'ABC123456789',
    provider_name: 'Dr. Smith',
    provider_npi: '1234567890',
    cpt_code: '72148',
    procedure_description: 'MRI Lumbar Spine',
    icd_code: 'M54.5',
    diagnosis_description: 'Low back pain',
    insurance_company: 'Blue Cross',
    proposed_date: '2025-11-15',
    urgency_level: 'routine',
    clinical_notes: 'Patient with chronic pain...'
  })
});

const data = await response.json();
console.log(data);
""", language="javascript")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Healthcare AI Voice Agent</strong> | Powered by AWS Bedrock Claude 3.5 Sonnet</p>
    <p>🎯 Prior Authorization • 📋 Denial Management • ✅ Insurance Verification</p>
</div>
""", unsafe_allow_html=True)
