"""
Prior Authorization Data Models
Pydantic models for type safety and validation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class UrgencyLevel(str, Enum):
    """Urgency levels for prior authorization requests"""
    ROUTINE = "routine"
    URGENT = "urgent"
    STAT = "stat"


class AuthorizationStatus(str, Enum):
    """Status of authorization request"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    PENDED = "pended"  # Additional information needed
    CANCELLED = "cancelled"


class PriorAuthRequest(BaseModel):
    """
    Prior Authorization Request Model
    Represents a complete prior authorization request
    """
    # Procedure Information
    procedure_code: str = Field(..., description="CPT procedure code")
    procedure_name: Optional[str] = Field(None, description="Procedure name (auto-populated)")
    diagnosis_code: str = Field(..., description="ICD-10 diagnosis code")
    diagnosis_description: Optional[str] = Field(None, description="Diagnosis description")
    
    # Patient Information
    patient_name: str = Field(..., description="Patient full name")
    patient_dob: date = Field(..., description="Patient date of birth")
    member_id: str = Field(..., description="Insurance member ID")
    
    # Provider Information
    provider_name: str = Field(..., description="Requesting provider name")
    provider_npi: str = Field(..., description="Provider NPI number")
    provider_tax_id: Optional[str] = Field(None, description="Provider tax ID")
    
    # Clinical Information
    clinical_notes: str = Field(..., description="Clinical summary and medical necessity")
    service_date: Optional[date] = Field(None, description="Proposed service date")
    
    # Request Details
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.ROUTINE, description="Urgency level")
    is_retroactive: bool = Field(default=False, description="Is this a retroactive auth request?")
    original_claim_number: Optional[str] = Field(None, description="Original claim if retroactive")
    
    # Payer Information
    payer_name: Optional[str] = Field(None, description="Insurance payer name")
    payer_phone: Optional[str] = Field(None, description="Payer contact phone")
    
    # Metadata
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Request creation timestamp")
    
    @validator('procedure_code')
    def validate_procedure_code(cls, v):
        """Validate procedure code format"""
        if not v or len(v) < 4:
            raise ValueError("Procedure code must be at least 4 characters")
        return v.strip()
    
    @validator('diagnosis_code')
    def validate_diagnosis_code(cls, v):
        """Validate diagnosis code format"""
        if not v or len(v) < 3:
            raise ValueError("Diagnosis code must be at least 3 characters")
        return v.strip()
    
    @validator('provider_npi')
    def validate_npi(cls, v):
        """Validate NPI format (10 digits)"""
        if v and not v.isdigit():
            raise ValueError("NPI must contain only digits")
        if v and len(v) != 10:
            raise ValueError("NPI must be exactly 10 digits")
        return v
    
    class Config:
        use_enum_values = True
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class PriorAuthAnalysis(BaseModel):
    """
    Prior Authorization Analysis Result
    Contains analyzed information and call strategy
    """
    # Request Information
    request: PriorAuthRequest
    
    # Procedure Analysis
    procedure_category: str = Field(..., description="Procedure category")
    requires_prior_auth: bool = Field(..., description="Whether prior auth is required")
    typical_cost: Optional[float] = Field(None, description="Typical procedure cost")
    
    # Documentation Analysis
    required_documentation: List[str] = Field(default_factory=list, description="Required documentation")
    missing_documentation: List[str] = Field(default_factory=list, description="Missing documentation")
    documentation_complete: bool = Field(..., description="Whether all documentation is present")
    
    # Approval Criteria
    approval_criteria: Dict[str, Any] = Field(default_factory=dict, description="Approval criteria")
    criteria_met: bool = Field(..., description="Whether criteria are met")
    
    # Call Strategy
    questions_to_ask: List[str] = Field(default_factory=list, description="Questions for payer")
    call_strategy_steps: List[str] = Field(default_factory=list, description="Step-by-step call strategy")
    payer_contact_department: str = Field(..., description="Which department to contact")
    
    # Timeline
    expected_turnaround_time: str = Field(..., description="Expected decision timeline")
    
    # Escalation
    needs_escalation: bool = Field(default=False, description="Whether escalation is needed")
    escalation_reason: Optional[str] = Field(None, description="Reason for escalation")
    escalation_type: Optional[str] = Field(None, description="Type of escalation needed")
    
    # Success Prediction
    success_probability: float = Field(..., ge=0.0, le=1.0, description="Estimated success probability")
    
    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PriorAuthCallResult(BaseModel):
    """
    Prior Authorization Call Result
    Captures outcome of authorization call
    """
    # Request Reference
    request_id: str = Field(..., description="Request identifier")
    
    # Call Information
    call_sid: Optional[str] = Field(None, description="Twilio call SID")
    call_duration_seconds: Optional[int] = Field(None, description="Call duration")
    call_timestamp: datetime = Field(default_factory=datetime.now, description="Call timestamp")
    
    # Representative Information
    representative_name: Optional[str] = Field(None, description="Payer representative name")
    representative_id: Optional[str] = Field(None, description="Representative ID")
    department: Optional[str] = Field(None, description="Department contacted")
    
    # Authorization Result
    authorization_status: AuthorizationStatus = Field(..., description="Authorization status")
    authorization_number: Optional[str] = Field(None, description="Authorization reference number")
    approval_date: Optional[date] = Field(None, description="Date of approval")
    valid_through_date: Optional[date] = Field(None, description="Authorization expiration date")
    
    # Additional Information
    additional_documentation_required: List[str] = Field(default_factory=list, description="Additional docs needed")
    payer_notes: Optional[str] = Field(None, description="Notes from payer")
    denial_reason: Optional[str] = Field(None, description="Reason for denial if applicable")
    
    # Next Steps
    next_steps: List[str] = Field(default_factory=list, description="Required next steps")
    follow_up_required: bool = Field(default=False, description="Whether follow-up is needed")
    follow_up_date: Optional[date] = Field(None, description="When to follow up")
    
    # Escalation
    was_escalated: bool = Field(default=False, description="Whether call was escalated")
    escalation_type: Optional[str] = Field(None, description="Type of escalation")
    peer_to_peer_scheduled: bool = Field(default=False, description="Whether P2P was scheduled")
    peer_to_peer_date: Optional[datetime] = Field(None, description="P2P scheduled date/time")
    
    # Call Quality
    call_successful: bool = Field(..., description="Whether call achieved objective")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in captured data")
    
    # Transcript
    call_transcript: Optional[str] = Field(None, description="Full call transcript")
    key_conversation_points: List[str] = Field(default_factory=list, description="Key points from conversation")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


class DocumentationRequirement(BaseModel):
    """
    Documentation Requirement Model
    Represents a single documentation requirement
    """
    requirement_type: str = Field(..., description="Type of documentation")
    description: str = Field(..., description="Description of requirement")
    is_mandatory: bool = Field(default=True, description="Whether this is mandatory")
    keywords: List[str] = Field(default_factory=list, description="Keywords to search for")
    is_met: bool = Field(default=False, description="Whether requirement is met")
    
    class Config:
        schema_extra = {
            "example": {
                "requirement_type": "clinical_notes",
                "description": "History and physical examination",
                "is_mandatory": True,
                "keywords": ["history", "exam", "assessment"],
                "is_met": True
            }
        }


if __name__ == "__main__":
    # Test the models
    from datetime import date
    
    print("="*60)
    print("Testing Prior Authorization Models")
    print("="*60)
    
    # Create a sample request
    request = PriorAuthRequest(
        procedure_code="72148",
        procedure_name="MRI Lumbar Spine",
        diagnosis_code="M54.5",
        diagnosis_description="Low back pain",
        patient_name="John Doe",
        patient_dob=date(1975, 6, 15),
        member_id="ABC123456789",
        provider_name="Dr. Smith",
        provider_npi="1234567890",
        clinical_notes="Patient has chronic lower back pain for 8 weeks. Failed conservative treatment including PT and NSAIDs.",
        urgency_level=UrgencyLevel.ROUTINE
    )
    
    print("\nPrior Auth Request Created:")
    print(f"  Procedure: {request.procedure_name} ({request.procedure_code})")
    print(f"  Patient: {request.patient_name}")
    print(f"  Urgency: {request.urgency_level}")
    print(f"  Valid: {request}")
    
    # Test JSON serialization
    print("\nJSON Serialization:")
    print(request.json(indent=2))
