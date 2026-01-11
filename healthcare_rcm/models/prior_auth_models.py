"""
Prior Authorization Data Models
Defines structured data models for capturing and validating prior authorization information
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class AuthorizationStatus(Enum):
    """Authorization status enumeration"""
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"
    PEER_TO_PEER_REQUIRED = "peer_to_peer_required"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    UNKNOWN = "unknown"


class CallOutcome(Enum):
    """Overall call outcome"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    DISCONNECTED = "disconnected"


@dataclass
class PatientInfo:
    """Patient demographic information"""
    name: str
    date_of_birth: Optional[date] = None
    member_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.date_of_birth:
            data['date_of_birth'] = self.date_of_birth.isoformat()
        return data


@dataclass
class ProviderInfo:
    """Healthcare provider information"""
    name: str
    npi: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProcedureInfo:
    """Medical procedure information"""
    cpt_code: str
    description: Optional[str] = None
    icd_code: Optional[str] = None
    icd_description: Optional[str] = None
    proposed_date: Optional[date] = None
    urgency: Optional[str] = None  # "routine", "urgent", "stat"
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.proposed_date:
            data['proposed_date'] = self.proposed_date.isoformat()
        return data


@dataclass
class AuthorizationInfo:
    """Authorization details from insurance"""
    status: AuthorizationStatus = AuthorizationStatus.UNKNOWN
    reference_number: Optional[str] = None
    authorization_number: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    approved_units: Optional[int] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            'status': self.status.value,
            'reference_number': self.reference_number,
            'authorization_number': self.authorization_number,
            'approved_units': self.approved_units,
            'notes': self.notes
        }
        if self.valid_from:
            data['valid_from'] = self.valid_from.isoformat()
        if self.valid_to:
            data['valid_to'] = self.valid_to.isoformat()
        return data


@dataclass
class RepresentativeInfo:
    """Insurance representative information"""
    name: Optional[str] = None
    id: Optional[str] = None
    phone: Optional[str] = None
    extension: Optional[str] = None
    department: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DocumentationRequirements:
    """Required documentation for authorization"""
    required_documents: List[str] = field(default_factory=list)
    submission_method: Optional[str] = None  # "fax", "portal", "mail", "email"
    fax_number: Optional[str] = None
    portal_url: Optional[str] = None
    submission_deadline: Optional[date] = None
    special_forms: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.submission_deadline:
            data['submission_deadline'] = self.submission_deadline.isoformat()
        return data


@dataclass
class TimelineInfo:
    """Timeline and turnaround information"""
    standard_turnaround_days: Optional[int] = None
    expedited_requested: bool = False
    expedited_approved: bool = False
    expected_decision_date: Optional[date] = None
    follow_up_date: Optional[date] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.expected_decision_date:
            data['expected_decision_date'] = self.expected_decision_date.isoformat()
        if self.follow_up_date:
            data['follow_up_date'] = self.follow_up_date.isoformat()
        return data


@dataclass
class PriorAuthRecord:
    """Complete prior authorization record"""
    call_id: str
    call_date: datetime
    insurance_company: str
    
    # Core information
    patient: PatientInfo
    provider: ProviderInfo
    procedure: ProcedureInfo
    
    # Authorization details
    authorization: AuthorizationInfo = field(default_factory=AuthorizationInfo)
    representative: RepresentativeInfo = field(default_factory=RepresentativeInfo)
    documentation: DocumentationRequirements = field(default_factory=DocumentationRequirements)
    timeline: TimelineInfo = field(default_factory=TimelineInfo)
    
    # Call metadata
    call_outcome: CallOutcome = CallOutcome.FAILED
    conversation_transcript: List[str] = field(default_factory=list)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    
    # Validation and tracking
    missing_fields: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    
    # System metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'call_id': self.call_id,
            'call_date': self.call_date.isoformat(),
            'insurance_company': self.insurance_company,
            'patient': self.patient.to_dict(),
            'provider': self.provider.to_dict(),
            'procedure': self.procedure.to_dict(),
            'authorization': self.authorization.to_dict(),
            'representative': self.representative.to_dict(),
            'documentation': self.documentation.to_dict(),
            'timeline': self.timeline.to_dict(),
            'call_outcome': self.call_outcome.value,
            'conversation_transcript': self.conversation_transcript,
            'extracted_entities': self.extracted_entities,
            'missing_fields': self.missing_fields,
            'validation_errors': self.validation_errors,
            'validation_warnings': self.validation_warnings,
            'next_steps': self.next_steps,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save_to_file(self, filepath: str):
        """Save record to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriorAuthRecord':
        """Create instance from dictionary"""
        # Convert nested dictionaries to dataclass objects
        if 'patient' in data and isinstance(data['patient'], dict):
            patient_data = data['patient'].copy()
            if 'date_of_birth' in patient_data and patient_data['date_of_birth']:
                patient_data['date_of_birth'] = date.fromisoformat(patient_data['date_of_birth'])
            data['patient'] = PatientInfo(**patient_data)
        
        if 'provider' in data and isinstance(data['provider'], dict):
            data['provider'] = ProviderInfo(**data['provider'])
        
        if 'procedure' in data and isinstance(data['procedure'], dict):
            procedure_data = data['procedure'].copy()
            if 'proposed_date' in procedure_data and procedure_data['proposed_date']:
                procedure_data['proposed_date'] = date.fromisoformat(procedure_data['proposed_date'])
            data['procedure'] = ProcedureInfo(**procedure_data)
        
        if 'authorization' in data and isinstance(data['authorization'], dict):
            auth_data = data['authorization'].copy()
            if 'status' in auth_data:
                auth_data['status'] = AuthorizationStatus(auth_data['status'])
            if 'valid_from' in auth_data and auth_data['valid_from']:
                auth_data['valid_from'] = date.fromisoformat(auth_data['valid_from'])
            if 'valid_to' in auth_data and auth_data['valid_to']:
                auth_data['valid_to'] = date.fromisoformat(auth_data['valid_to'])
            data['authorization'] = AuthorizationInfo(**auth_data)
        
        if 'representative' in data and isinstance(data['representative'], dict):
            data['representative'] = RepresentativeInfo(**data['representative'])
        
        if 'documentation' in data and isinstance(data['documentation'], dict):
            doc_data = data['documentation'].copy()
            if 'submission_deadline' in doc_data and doc_data['submission_deadline']:
                doc_data['submission_deadline'] = date.fromisoformat(doc_data['submission_deadline'])
            data['documentation'] = DocumentationRequirements(**doc_data)
        
        if 'timeline' in data and isinstance(data['timeline'], dict):
            timeline_data = data['timeline'].copy()
            if 'expected_decision_date' in timeline_data and timeline_data['expected_decision_date']:
                timeline_data['expected_decision_date'] = date.fromisoformat(timeline_data['expected_decision_date'])
            if 'follow_up_date' in timeline_data and timeline_data['follow_up_date']:
                timeline_data['follow_up_date'] = date.fromisoformat(timeline_data['follow_up_date'])
            data['timeline'] = TimelineInfo(**timeline_data)
        
        # Convert enums
        if 'call_outcome' in data:
            data['call_outcome'] = CallOutcome(data['call_outcome'])
        
        # Convert datetime strings
        if 'call_date' in data:
            data['call_date'] = datetime.fromisoformat(data['call_date'])
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)
    
    @classmethod
    def from_json_file(cls, filepath: str) -> 'PriorAuthRecord':
        """Load record from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def is_complete(self) -> bool:
        """Check if all critical fields are populated"""
        return (
            self.authorization.reference_number is not None and
            self.authorization.status != AuthorizationStatus.UNKNOWN and
            len(self.missing_fields) == 0 and
            len(self.validation_errors) == 0
        )
    
    def is_approved(self) -> bool:
        """Check if authorization was approved"""
        return self.authorization.status == AuthorizationStatus.APPROVED
    
    def requires_followup(self) -> bool:
        """Check if follow-up action is required"""
        return self.authorization.status in [
            AuthorizationStatus.PENDING,
            AuthorizationStatus.PEER_TO_PEER_REQUIRED,
            AuthorizationStatus.ADDITIONAL_INFO_REQUIRED
        ]
