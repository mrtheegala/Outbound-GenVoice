"""
Prior Authorization Validator
Validates completeness, formats, and business rules for prior authorization records
"""

import re
import logging
from datetime import date, timedelta
from typing import List, Dict, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from healthcare_rcm.models.prior_auth_models import (
    PriorAuthRecord, AuthorizationStatus, CallOutcome
)

logger = logging.getLogger(__name__)


class PriorAuthValidator:
    """Validates prior authorization records for completeness and correctness"""
    
    # Required fields by authorization status
    REQUIRED_FIELDS_BY_STATUS = {
        AuthorizationStatus.APPROVED: [
            'authorization.reference_number',
            'authorization.authorization_number',
            'representative.name',
            'timeline.expected_decision_date'
        ],
        AuthorizationStatus.PENDING: [
            'authorization.reference_number',
            'documentation.required_documents',
            'documentation.submission_deadline',
            'representative.name'
        ],
        AuthorizationStatus.DENIED: [
            'authorization.reference_number',
            'representative.name'
        ],
        AuthorizationStatus.PEER_TO_PEER_REQUIRED: [
            'authorization.reference_number',
            'representative.name',
            'representative.phone'
        ]
    }
    
    def validate(self, record: PriorAuthRecord) -> PriorAuthRecord:
        """
        Validate prior auth record and populate missing_fields, validation_errors, validation_warnings
        
        Args:
            record: PriorAuthRecord to validate
        
        Returns:
            Updated record with validation results
        """
        logger.info(f"Validating prior auth record for call {record.call_id}")
        
        # Clear existing validation results
        record.missing_fields = []
        record.validation_errors = []
        record.validation_warnings = []
        record.next_steps = []
        
        # Run validation checks
        self._validate_completeness(record)
        self._validate_formats(record)
        self._validate_business_rules(record)
        self._generate_next_steps(record)
        
        # Update call outcome based on validation
        self._update_call_outcome(record)
        
        logger.info(f"Validation complete. Errors: {len(record.validation_errors)}, "
                   f"Warnings: {len(record.validation_warnings)}, "
                   f"Missing: {len(record.missing_fields)}")
        
        return record
    
    def _validate_completeness(self, record: PriorAuthRecord):
        """Check if all required fields are present"""
        
        # Always check for reference number
        if not record.authorization.reference_number and not record.authorization.authorization_number:
            record.missing_fields.append('authorization_reference_number')
            record.validation_errors.append("No authorization or reference number obtained from call")
        
        # Check status-specific required fields
        required_fields = self.REQUIRED_FIELDS_BY_STATUS.get(record.authorization.status, [])
        
        for field_path in required_fields:
            if not self._get_nested_field(record, field_path):
                field_name = field_path.split('.')[-1]
                record.missing_fields.append(field_name)
                record.validation_warnings.append(f"Missing required field: {field_name}")
        
        # Check representative info
        if not record.representative.name:
            record.missing_fields.append('representative_name')
            record.validation_warnings.append("Insurance representative name not captured")
        
        # Check documentation for pending/additional info required
        if record.authorization.status in [AuthorizationStatus.PENDING, AuthorizationStatus.ADDITIONAL_INFO_REQUIRED]:
            if not record.documentation.required_documents:
                record.missing_fields.append('required_documents')
                record.validation_errors.append("Authorization pending but no documentation requirements captured")
            
            if not record.documentation.submission_deadline:
                record.missing_fields.append('submission_deadline')
                record.validation_errors.append("No documentation submission deadline captured")
    
    def _validate_formats(self, record: PriorAuthRecord):
        """Validate data formats"""
        
        # Validate CPT code format (5 digits)
        if record.procedure.cpt_code and not re.match(r'^\d{5}$', record.procedure.cpt_code):
            record.validation_warnings.append(f"Invalid CPT code format: {record.procedure.cpt_code}")
        
        # Validate ICD code format (standard ICD-10 format)
        if record.procedure.icd_code and not re.match(r'^[A-Z]\d{2}\.?\d{0,2}$', record.procedure.icd_code):
            record.validation_warnings.append(f"Invalid ICD-10 code format: {record.procedure.icd_code}")
        
        # Validate NPI format (10 digits)
        if record.provider.npi and not re.match(r'^\d{10}$', record.provider.npi):
            record.validation_warnings.append(f"Invalid NPI format: {record.provider.npi}")
        
        # Validate phone/fax numbers
        if record.documentation.fax_number and not self._is_valid_phone(record.documentation.fax_number):
            record.validation_warnings.append(f"Invalid fax number format: {record.documentation.fax_number}")
        
        # Validate authorization number format (should be alphanumeric)
        if record.authorization.authorization_number:
            if not re.match(r'^[A-Z0-9\-]+$', record.authorization.authorization_number, re.IGNORECASE):
                record.validation_warnings.append(f"Unusual authorization number format: {record.authorization.authorization_number}")
    
    def _validate_business_rules(self, record: PriorAuthRecord):
        """Validate business logic and rules"""
        
        # Check authorization validity period
        if record.authorization.valid_from and record.authorization.valid_to:
            validity_days = (record.authorization.valid_to - record.authorization.valid_from).days
            
            if validity_days < 0:
                record.validation_errors.append("Authorization end date is before start date")
            elif validity_days < 30:
                record.validation_warnings.append(f"Short authorization validity period: {validity_days} days")
            elif validity_days > 365:
                record.validation_warnings.append(f"Unusually long authorization validity period: {validity_days} days")
        
        # Check submission deadline vs procedure date
        if record.documentation.submission_deadline and record.procedure.proposed_date:
            if record.documentation.submission_deadline >= record.procedure.proposed_date:
                record.validation_errors.append(
                    "Documentation deadline is on or after procedure date - may cause delays"
                )
        
        # Check if deadline is in the past
        if record.documentation.submission_deadline:
            if record.documentation.submission_deadline < date.today():
                record.validation_errors.append(
                    f"Documentation deadline has already passed: {record.documentation.submission_deadline}"
                )
            elif (record.documentation.submission_deadline - date.today()).days <= 1:
                record.validation_warnings.append(
                    "Documentation deadline is very soon (within 1 day)"
                )
        
        # Check turnaround time reasonableness
        if record.timeline.standard_turnaround_days:
            if record.timeline.standard_turnaround_days < 1:
                record.validation_warnings.append("Unusually fast turnaround time")
            elif record.timeline.standard_turnaround_days > 30:
                record.validation_warnings.append("Very long turnaround time - consider expedited review")
        
        # Check if approved but no authorization number
        if record.authorization.status == AuthorizationStatus.APPROVED:
            if not record.authorization.authorization_number:
                record.validation_errors.append(
                    "Authorization approved but no authorization number provided"
                )
        
        # Check if denied but no appeal information
        if record.authorization.status == AuthorizationStatus.DENIED:
            if not record.authorization.notes:
                record.validation_warnings.append(
                    "Authorization denied but no denial reason captured"
                )
        
        # Validate peer-to-peer requirements
        if record.authorization.status == AuthorizationStatus.PEER_TO_PEER_REQUIRED:
            if not record.representative.phone:
                record.validation_errors.append(
                    "Peer-to-peer required but no callback number captured"
                )
    
    def _generate_next_steps(self, record: PriorAuthRecord):
        """Generate actionable next steps based on validation"""
        
        if record.authorization.status == AuthorizationStatus.APPROVED:
            if record.authorization.authorization_number:
                record.next_steps.append(
                    f"✅ Authorization approved! Reference: {record.authorization.authorization_number}"
                )
            if record.authorization.valid_to:
                record.next_steps.append(
                    f"Authorization valid until {record.authorization.valid_to}"
                )
            record.next_steps.append("Proceed with scheduling procedure")
            record.next_steps.append("Update EHR/billing system with authorization number")
            
        elif record.authorization.status == AuthorizationStatus.PENDING:
            record.next_steps.append("⏳ Authorization pending - action required")
            if record.documentation.required_documents:
                record.next_steps.append(
                    f"Submit required documents: {', '.join(record.documentation.required_documents)}"
                )
            if record.documentation.submission_deadline:
                record.next_steps.append(
                    f"⚠️ Deadline: {record.documentation.submission_deadline}"
                )
            if record.documentation.fax_number:
                record.next_steps.append(
                    f"Fax documents to: {record.documentation.fax_number}"
                )
            if record.timeline.expected_decision_date:
                record.next_steps.append(
                    f"Expected decision by: {record.timeline.expected_decision_date}"
                )
            record.next_steps.append("Follow up if no decision received by expected date")
            
        elif record.authorization.status == AuthorizationStatus.DENIED:
            record.next_steps.append("❌ Authorization denied - appeal required")
            record.next_steps.append("Review denial reason with provider")
            record.next_steps.append("Gather additional documentation for appeal")
            record.next_steps.append("Submit formal appeal within insurance timeline")
            if record.representative.name:
                record.next_steps.append(
                    f"Contact representative {record.representative.name} for appeal process"
                )
            
        elif record.authorization.status == AuthorizationStatus.PEER_TO_PEER_REQUIRED:
            record.next_steps.append("👨‍⚕️ Peer-to-peer review required")
            record.next_steps.append("Schedule peer-to-peer call between provider and insurance medical director")
            if record.representative.phone:
                record.next_steps.append(
                    f"Call {record.representative.phone} to schedule"
                )
            record.next_steps.append("Prepare clinical documentation for review")
        
        # Add general follow-up items
        if record.missing_fields:
            record.next_steps.append(
                f"⚠️ Incomplete information - missing: {', '.join(record.missing_fields[:3])}"
            )
            record.next_steps.append("Call back to obtain missing information")
        
        if record.validation_errors:
            record.next_steps.append(
                f"⚠️ {len(record.validation_errors)} validation errors need attention"
            )
    
    def _update_call_outcome(self, record: PriorAuthRecord):
        """Update call outcome based on validation results"""
        
        # Override outcome if we have critical errors
        if len(record.validation_errors) > 0:
            if record.call_outcome == CallOutcome.SUCCESS:
                record.call_outcome = CallOutcome.PARTIAL
        
        # Success criteria
        if (record.authorization.status == AuthorizationStatus.APPROVED and
            record.authorization.authorization_number and
            len(record.validation_errors) == 0):
            record.call_outcome = CallOutcome.SUCCESS
        
        # Partial success criteria
        elif (record.authorization.reference_number and
              record.authorization.status != AuthorizationStatus.UNKNOWN):
            record.call_outcome = CallOutcome.PARTIAL
        
        # Failed criteria
        elif not record.authorization.reference_number:
            record.call_outcome = CallOutcome.FAILED
    
    def _get_nested_field(self, record: PriorAuthRecord, field_path: str) -> any:
        """Get nested field value from record"""
        parts = field_path.split('.')
        value = record
        for part in parts:
            value = getattr(value, part, None)
            if value is None:
                return None
        return value
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone/fax number format"""
        # Remove common formatting characters
        clean = re.sub(r'[\s\-\(\)\.]+', '', phone)
        # Check if it's 10-11 digits (US format)
        return bool(re.match(r'^1?\d{10}$', clean))


# Convenience function
def validate_prior_auth(record: PriorAuthRecord) -> PriorAuthRecord:
    """
    Convenience function to validate a prior auth record
    
    Args:
        record: PriorAuthRecord to validate
    
    Returns:
        Validated record with errors/warnings populated
    """
    validator = PriorAuthValidator()
    return validator.validate(record)
