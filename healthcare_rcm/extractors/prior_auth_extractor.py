"""
Prior Authorization Information Extractor
Uses LLM to extract structured information from conversation transcripts
"""

import re
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import json

# Import Bedrock LLM
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from ConversationModel.bedrock_llm import BedrockClaude
from healthcare_rcm.models.prior_auth_models import (
    PriorAuthRecord, PatientInfo, ProviderInfo, ProcedureInfo,
    AuthorizationInfo, RepresentativeInfo, DocumentationRequirements,
    TimelineInfo, AuthorizationStatus, CallOutcome
)

logger = logging.getLogger(__name__)


class PriorAuthExtractor:
    """Extracts structured information from prior authorization conversations"""
    
    def __init__(self, llm: Optional[BedrockClaude] = None):
        """Initialize extractor with LLM"""
        self.llm = llm or BedrockClaude(model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        
    def extract_from_conversation(
        self,
        conversation_history: List[str],
        call_id: str,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> PriorAuthRecord:
        """
        Extract structured prior authorization data from conversation
        
        Args:
            conversation_history: List of conversation turns
            call_id: Unique call identifier
            agent_config: Agent configuration (contains patient, provider, procedure info)
        
        Returns:
            PriorAuthRecord with extracted information
        """
        logger.info(f"Extracting prior auth information from call {call_id}")
        
        # Join conversation for analysis
        full_conversation = "\n".join(conversation_history)
        
        # Extract entities using LLM
        extracted_entities = self._extract_entities_with_llm(full_conversation)
        
        # Build prior auth record
        record = self._build_prior_auth_record(
            call_id=call_id,
            conversation_history=conversation_history,
            extracted_entities=extracted_entities,
            agent_config=agent_config
        )
        
        logger.info(f"Extraction complete. Status: {record.authorization.status.value}")
        return record
    
    def _extract_entities_with_llm(self, conversation: str) -> Dict[str, Any]:
        """Use LLM to extract entities from conversation"""
        
        extraction_prompt = f"""You are a medical billing specialist analyzing a prior authorization phone call transcript. 
Extract the following information in JSON format. If information is not found, use null.

CONVERSATION TRANSCRIPT:
{conversation}

Extract the following information:

1. AUTHORIZATION STATUS: (approved/denied/pending/peer_to_peer_required/additional_info_required/unknown)
2. AUTHORIZATION NUMBER or REFERENCE NUMBER: Any authorization code, reference number, or tracking number
3. REPRESENTATIVE NAME: Name of insurance company representative
4. REPRESENTATIVE ID: Representative's employee ID or badge number
5. TURNAROUND TIME: How many days until decision (extract number)
6. DOCUMENTATION REQUIRED: List all documents mentioned (medical records, test results, etc.)
7. SUBMISSION METHOD: fax, portal, mail, or email
8. FAX NUMBER: Fax number for document submission
9. SUBMISSION DEADLINE: When documents must be submitted
10. EXPEDITED REVIEW: Was expedited review requested? (yes/no)
11. VALID FROM DATE: Authorization start date
12. VALID TO DATE: Authorization end date
13. NEXT STEPS: List any action items mentioned

Return ONLY valid JSON with this structure:
{{
    "authorization_status": "approved",
    "authorization_number": "AUTH-12345",
    "reference_number": "REF-ABC123",
    "representative_name": "Jane Smith",
    "representative_id": "REP-456",
    "turnaround_days": 5,
    "documentation_required": ["medical records", "test results"],
    "submission_method": "fax",
    "fax_number": "1-800-555-1234",
    "submission_deadline": "2025-10-30",
    "expedited_requested": false,
    "valid_from_date": "2025-10-28",
    "valid_to_date": "2025-12-28",
    "next_steps": ["Submit medical records", "Follow up in 5 days"]
}}

IMPORTANT: Return ONLY the JSON object, no additional text."""

        try:
            # Get LLM response
            response = self.llm.invoke(extraction_prompt)
            
            # Handle different response types from Bedrock
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            logger.debug(f"Raw LLM response length: {len(response_text)} chars")
            
            # Check if response is too short (likely failed)
            if len(response_text) < 100:
                logger.warning(f"Response too short ({len(response_text)} chars), using fallback extraction")
                return self._fallback_extraction(conversation)
            
            # Parse JSON from response
            # Try to find JSON in response (handle cases where LLM adds extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    extracted_data = json.loads(json_str)
                    
                    # Validate extraction quality
                    if not extracted_data or len(extracted_data) == 0:
                        logger.warning("LLM returned empty extraction, using fallback")
                        return self._fallback_extraction(conversation)
                    
                    logger.info(f"Successfully extracted entities: {list(extracted_data.keys())}")
                    return extracted_data
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
                    logger.error(f"Attempted to parse (first 500 chars): {json_str[:500]}")
                    # Try to fix common JSON issues
                    try:
                        # Add closing braces if missing
                        brace_count = json_str.count('{') - json_str.count('}')
                        if brace_count > 0:
                            json_str += '}' * brace_count
                            extracted_data = json.loads(json_str)
                            logger.info("Fixed incomplete JSON and successfully parsed")
                            return extracted_data if extracted_data else self._fallback_extraction(conversation)
                    except:
                        pass
                    logger.warning("JSON repair failed, using fallback extraction")
                    return self._fallback_extraction(conversation)
            else:
                logger.warning(f"Could not find JSON in LLM response (length: {len(response_text)})")
                logger.warning(f"Response preview: {response_text[:500]}")
                return self._fallback_extraction(conversation)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return self._fallback_extraction(conversation)
        except Exception as e:
            logger.error(f"Error extracting entities with LLM: {e}", exc_info=True)
            return self._fallback_extraction(conversation)
    
    def _fallback_extraction(self, conversation_text: str) -> Dict[str, Any]:
        """
        Fallback regex-based extraction when LLM fails
        Extracts key information using pattern matching
        """
        logger.info("[FALLBACK] Using regex-based extraction")
        extracted = {}
        
        # Extract representative name
        name_patterns = [
            r"my name is ([A-Z][a-z]+ [A-Z][a-z]+)",
            r"this is ([A-Z][a-z]+ [A-Z][a-z]+)",
            r"([A-Z][a-z]+ [A-Z][a-z]+) speaking",
            r"I'm ([A-Z][a-z]+ [A-Z][a-z]+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, conversation_text, re.IGNORECASE)
            if match:
                extracted['representative_name'] = match.group(1).strip()
                logger.info(f"[FALLBACK] Found representative: {extracted['representative_name']}")
                break
        
        # Extract reference number
        ref_patterns = [
            r"reference (?:number|ID|id) is ([A-Z0-9-]+)",
            r"ref(?:erence)? (?:#|number)?:?\s*([A-Z0-9-]+)",
            r"reference:?\s*([A-Z0-9]+)",
        ]
        for pattern in ref_patterns:
            match = re.search(pattern, conversation_text, re.IGNORECASE)
            if match:
                extracted['reference_number'] = match.group(1).strip()
                logger.info(f"[FALLBACK] Found reference: {extracted['reference_number']}")
                break
        
        # Extract authorization number
        auth_patterns = [
            r"authorization (?:number|code) is ([A-Z0-9-]+)",
            r"auth (?:number|code|#):?\s*([A-Z0-9-]+)",
            r"approved.*?([A-Z]{2,}\d+)",
        ]
        for pattern in auth_patterns:
            match = re.search(pattern, conversation_text, re.IGNORECASE)
            if match:
                extracted['authorization_number'] = match.group(1).strip()
                logger.info(f"[FALLBACK] Found auth number: {extracted['authorization_number']}")
                break
        
        # Determine status from keywords
        text_lower = conversation_text.lower()
        if any(word in text_lower for word in ['approved', 'authorization approved', 'auth approved']):
            extracted['authorization_status'] = 'approved'
            logger.info("[FALLBACK] Status: approved")
        elif any(word in text_lower for word in ['denied', 'not eligible', 'expired', 'inactive', 'denial']):
            extracted['authorization_status'] = 'denied'
            logger.info("[FALLBACK] Status: denied")
        elif any(word in text_lower for word in ['pending', 'under review', 'need more info', 'reviewing']):
            extracted['authorization_status'] = 'pending'
            logger.info("[FALLBACK] Status: pending")
        else:
            extracted['authorization_status'] = 'unknown'
        
        # Extract turnaround time
        turnaround_patterns = [
            r"(\d+)\s*(?:business\s*)?days?",
            r"within\s*(\d+)\s*days?",
        ]
        for pattern in turnaround_patterns:
            match = re.search(pattern, conversation_text, re.IGNORECASE)
            if match:
                try:
                    extracted['turnaround_days'] = int(match.group(1))
                    logger.info(f"[FALLBACK] Found turnaround: {extracted['turnaround_days']} days")
                    break
                except:
                    pass
        
        logger.info(f"[FALLBACK] Extracted {len(extracted)} fields: {list(extracted.keys())}")
        return extracted
    
    def _build_prior_auth_record(
        self,
        call_id: str,
        conversation_history: List[str],
        extracted_entities: Dict[str, Any],
        agent_config: Optional[Dict[str, Any]] = None
    ) -> PriorAuthRecord:
        """Build PriorAuthRecord from extracted entities"""
        
        # Get base info from agent config (if provided)
        patient_info = self._extract_patient_info(extracted_entities, agent_config)
        provider_info = self._extract_provider_info(extracted_entities, agent_config)
        procedure_info = self._extract_procedure_info(extracted_entities, agent_config)
        
        # Extract authorization details
        auth_info = self._extract_authorization_info(extracted_entities)
        rep_info = self._extract_representative_info(extracted_entities)
        doc_info = self._extract_documentation_info(extracted_entities)
        timeline_info = self._extract_timeline_info(extracted_entities)
        
        # Determine call outcome
        call_outcome = self._determine_call_outcome(auth_info, extracted_entities)
        
        # Determine insurance company from conversation or config
        insurance_company = agent_config.get('insurance_company', 'Unknown Insurance') if agent_config else "Unknown Insurance"
        
        # Create record
        record = PriorAuthRecord(
            call_id=call_id,
            call_date=datetime.now(),
            insurance_company=insurance_company,
            patient=patient_info,
            provider=provider_info,
            procedure=procedure_info,
            authorization=auth_info,
            representative=rep_info,
            documentation=doc_info,
            timeline=timeline_info,
            call_outcome=call_outcome,
            conversation_transcript=conversation_history,
            extracted_entities=extracted_entities
        )
        
        return record
    
    def _extract_patient_info(self, entities: Dict[str, Any], config: Optional[Dict] = None) -> PatientInfo:
        """Extract patient information"""
        if config and 'patient_name' in config:
            return PatientInfo(
                name=config.get('patient_name', 'Unknown'),
                date_of_birth=self._parse_date(config.get('patient_dob')),
                member_id=config.get('member_id')
            )
        return PatientInfo(name="Unknown Patient")
    
    def _extract_provider_info(self, entities: Dict[str, Any], config: Optional[Dict] = None) -> ProviderInfo:
        """Extract provider information"""
        if config:
            return ProviderInfo(
                name=config.get('provider_name', 'Unknown Provider'),
                npi=config.get('provider_npi')
            )
        return ProviderInfo(name="Unknown Provider")
    
    def _extract_procedure_info(self, entities: Dict[str, Any], config: Optional[Dict] = None) -> ProcedureInfo:
        """Extract procedure information"""
        if config:
            return ProcedureInfo(
                cpt_code=config.get('cpt_code', 'UNKNOWN'),
                description=config.get('procedure_description'),
                icd_code=config.get('icd_code'),
                icd_description=config.get('diagnosis_description')
            )
        return ProcedureInfo(cpt_code="UNKNOWN")
    
    def _extract_authorization_info(self, entities: Dict[str, Any]) -> AuthorizationInfo:
        """Extract authorization details"""
        # Parse status
        status_str = entities.get('authorization_status', 'unknown').lower()
        status_map = {
            'approved': AuthorizationStatus.APPROVED,
            'denied': AuthorizationStatus.DENIED,
            'pending': AuthorizationStatus.PENDING,
            'peer_to_peer_required': AuthorizationStatus.PEER_TO_PEER_REQUIRED,
            'additional_info_required': AuthorizationStatus.ADDITIONAL_INFO_REQUIRED,
        }
        status = status_map.get(status_str, AuthorizationStatus.UNKNOWN)
        
        return AuthorizationInfo(
            status=status,
            reference_number=entities.get('reference_number'),
            authorization_number=entities.get('authorization_number'),
            valid_from=self._parse_date(entities.get('valid_from_date')),
            valid_to=self._parse_date(entities.get('valid_to_date')),
            notes=entities.get('notes')
        )
    
    def _extract_representative_info(self, entities: Dict[str, Any]) -> RepresentativeInfo:
        """Extract representative information"""
        return RepresentativeInfo(
            name=entities.get('representative_name'),
            id=entities.get('representative_id'),
            department=entities.get('department')
        )
    
    def _extract_documentation_info(self, entities: Dict[str, Any]) -> DocumentationRequirements:
        """Extract documentation requirements"""
        return DocumentationRequirements(
            required_documents=entities.get('documentation_required', []),
            submission_method=entities.get('submission_method'),
            fax_number=entities.get('fax_number'),
            portal_url=entities.get('portal_url'),
            submission_deadline=self._parse_date(entities.get('submission_deadline')),
            special_forms=entities.get('special_forms', [])
        )
    
    def _extract_timeline_info(self, entities: Dict[str, Any]) -> TimelineInfo:
        """Extract timeline information"""
        turnaround_days = entities.get('turnaround_days')
        expedited_requested = entities.get('expedited_requested', False)
        
        # Calculate expected decision date
        expected_date = None
        if turnaround_days:
            try:
                expected_date = date.today() + timedelta(days=int(turnaround_days))
            except (ValueError, TypeError):
                pass
        
        return TimelineInfo(
            standard_turnaround_days=turnaround_days,
            expedited_requested=expedited_requested,
            expected_decision_date=expected_date
        )
    
    def _determine_call_outcome(self, auth_info: AuthorizationInfo, entities: Dict[str, Any]) -> CallOutcome:
        """Determine overall call outcome"""
        if auth_info.status == AuthorizationStatus.APPROVED and auth_info.reference_number:
            return CallOutcome.SUCCESS
        elif auth_info.status != AuthorizationStatus.UNKNOWN and auth_info.reference_number:
            return CallOutcome.PARTIAL
        elif auth_info.reference_number or len(entities) > 3:
            return CallOutcome.PARTIAL
        else:
            return CallOutcome.FAILED
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            return date.fromisoformat(date_str)
        except (ValueError, TypeError):
            pass
        
        # Try common date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%d/%m/%Y',
            '%B %d, %Y',
            '%b %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str), fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None


# Convenience function
def extract_prior_auth_info(
    conversation_history: List[str],
    call_id: str,
    agent_config: Optional[Dict[str, Any]] = None,
    llm: Optional[BedrockClaude] = None
) -> PriorAuthRecord:
    """
    Convenience function to extract prior auth information
    
    Args:
        conversation_history: List of conversation turns
        call_id: Unique call identifier
        agent_config: Agent configuration dict
        llm: Optional LLM instance
    
    Returns:
        PriorAuthRecord with extracted information
    """
    extractor = PriorAuthExtractor(llm=llm)
    return extractor.extract_from_conversation(conversation_history, call_id, agent_config)
