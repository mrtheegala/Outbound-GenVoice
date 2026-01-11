"""
Denial Management Call Extractor
Extracts key information from denial management phone calls
"""

import re
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)


class DenialStatus(Enum):
    """Possible denial statuses"""
    OVERTURNED = "overturned"
    UPHELD = "upheld"
    PENDING_REVIEW = "pending_review"
    PENDING_DOCUMENTATION = "pending_documentation"
    RESUBMIT_REQUIRED = "resubmit_required"
    APPEAL_REQUIRED = "appeal_required"
    PEER_TO_PEER_REQUIRED = "peer_to_peer_required"
    UNKNOWN = "unknown"


class DenialMgmtExtractor:
    """Extracts denial management information from conversation transcripts"""
    
    def __init__(self, bedrock_client=None):
        """
        Initialize the extractor
        
        Args:
            bedrock_client: AWS Bedrock client for LLM extraction
        """
        self.bedrock_client = bedrock_client
    
    def extract_from_conversation(self, conversation_history: List[str], call_id: str,
                                  agent_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Extract denial management information from conversation
        
        Args:
            conversation_history: List of conversation turns
            call_id: Unique identifier for the call
            agent_config: Agent configuration with claim details
        
        Returns:
            Dictionary with extracted denial management information
        """
        # Convert conversation history to single text
        full_conversation = "\n".join(conversation_history)
        
        logger.info(f"Extracting denial mgmt info from call {call_id}")
        logger.info(f"Conversation length: {len(full_conversation)} characters")
        
        # Extract entities using LLM
        extracted_entities = self._extract_entities_with_llm(full_conversation)
        
        # Build denial management record
        record = {
            "call_id": call_id,
            "timestamp": datetime.now().isoformat(),
            "conversation_turns": len(conversation_history),
            
            "claim": {
                "claim_number": agent_config.get('claim_number') if agent_config else None,
                "patient_name": agent_config.get('patient_name') if agent_config else None,
                "service_date": agent_config.get('service_date') if agent_config else None,
                "procedure_code": agent_config.get('procedure_code') if agent_config else None,
                "procedure_name": agent_config.get('procedure_name') if agent_config else None
            },
            
            "denial_info": {
                "denial_code": agent_config.get('denial_code') if agent_config else None,
                "denial_reason": agent_config.get('denial_reason') if agent_config else None,
                "resolution_status": extracted_entities.get('resolution_status', 'unknown'),
                "resolution_path": extracted_entities.get('resolution_path'),  # resubmit, appeal, peer-to-peer
                "detailed_reason": extracted_entities.get('detailed_reason')
            },
            
            "representative": {
                "name": extracted_entities.get('representative_name'),
                "id": extracted_entities.get('representative_id'),
                "department": extracted_entities.get('department')
            },
            
            "resolution": {
                "required_documents": extracted_entities.get('required_documents', []),
                "submission_method": extracted_entities.get('submission_method'),
                "fax_number": extracted_entities.get('fax_number'),
                "portal_url": extracted_entities.get('portal_url'),
                "submission_deadline": extracted_entities.get('submission_deadline'),
                "special_requirements": extracted_entities.get('special_requirements', [])
            },
            
            "timeline": {
                "reprocessing_time": extracted_entities.get('reprocessing_time'),
                "appeal_deadline": extracted_entities.get('appeal_deadline'),
                "expected_decision_date": extracted_entities.get('expected_decision_date')
            },
            
            "next_steps": extracted_entities.get('next_steps', []),
            "reference_number": extracted_entities.get('reference_number'),
            "notes": extracted_entities.get('notes')
        }
        
        return record
    
    def _extract_entities_with_llm(self, conversation: str) -> Dict[str, Any]:
        """Use LLM to extract entities from conversation"""
        
        extraction_prompt = f"""You are a medical billing specialist analyzing a denial management phone call transcript.
Extract the following information in JSON format. If information is not found, use null.

CONVERSATION TRANSCRIPT:
{conversation}

Extract the following information:

1. RESOLUTION STATUS: (overturned/upheld/pending_review/pending_documentation/resubmit_required/appeal_required/peer_to_peer_required/unknown)
2. RESOLUTION PATH: What action is needed (resubmit, appeal, peer-to-peer review, etc.)
3. DETAILED REASON: Specific explanation for the denial beyond the denial code
4. REPRESENTATIVE NAME: Name of insurance company representative
5. REPRESENTATIVE ID: Representative's employee ID or badge number
6. DEPARTMENT: Which department handled the call
7. REQUIRED DOCUMENTS: List all documents needed for resolution
8. SUBMISSION METHOD: fax, portal, mail, or email
9. FAX NUMBER: Fax number for document submission
10. PORTAL URL: URL for online submission
11. SUBMISSION DEADLINE: When documents must be submitted
12. SPECIAL REQUIREMENTS: Any special forms, attestations, or additional requirements
13. REPROCESSING TIME: How long reprocessing will take
14. APPEAL DEADLINE: Deadline for filing an appeal
15. EXPECTED DECISION DATE: When a decision is expected
16. NEXT STEPS: List of action items mentioned
17. REFERENCE NUMBER: Reference number for this inquiry
18. NOTES: Any additional important information

Return ONLY valid JSON with this structure:
{{
    "resolution_status": "pending_review",
    "resolution_path": "resubmit with additional documentation",
    "detailed_reason": "Medical necessity not established",
    "representative_name": "John Smith",
    "representative_id": "REP12345",
    "department": "Claims Resolution",
    "required_documents": ["Medical records", "Physician notes"],
    "submission_method": "fax",
    "fax_number": "555-1234",
    "portal_url": null,
    "submission_deadline": "2024-12-31",
    "special_requirements": [],
    "reprocessing_time": "10-14 business days",
    "appeal_deadline": "2024-12-15",
    "expected_decision_date": "2024-12-20",
    "next_steps": ["Gather medical records", "Submit via fax", "Follow up in 2 weeks"],
    "reference_number": "INQ-2024-67890",
    "notes": "Representative was helpful and provided clear instructions"
}}
"""
        
        try:
            # Use Bedrock if available
            if self.bedrock_client:
                response = self.bedrock_client.invoke_model(
                    modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 2000,
                        "messages": [{
                            "role": "user",
                            "content": extraction_prompt
                        }]
                    })
                )
                
                response_body = json.loads(response['body'].read())
                response_text = response_body['content'][0]['text']
            else:
                response_text = "{}"
            
            logger.debug(f"Raw LLM response length: {len(response_text)} chars")
            
            # Check if response is too short (likely failed)
            if len(response_text) < 100:
                logger.warning(f"Response too short ({len(response_text)} chars), using fallback extraction")
                return self._fallback_extraction(conversation)
            
            # Parse JSON from response
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
                    return self._fallback_extraction(conversation)
            else:
                logger.warning(f"Could not find JSON in LLM response")
                return self._fallback_extraction(conversation)
                
        except Exception as e:
            logger.error(f"Error extracting entities with LLM: {e}", exc_info=True)
            return self._fallback_extraction(conversation)
    
    def _fallback_extraction(self, conversation_text: str) -> Dict[str, Any]:
        """
        Fallback regex-based extraction when LLM fails
        """
        logger.info("[FALLBACK] Using regex-based extraction for denial management")
        extracted = {}
        
        # Extract representative name
        rep_patterns = [
            r"(?:my name is|I'm|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"(?:speaking with|talking to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]
        for pattern in rep_patterns:
            match = re.search(pattern, conversation_text, re.IGNORECASE)
            if match:
                extracted['representative_name'] = match.group(1)
                break
        
        # Extract reference number
        ref_patterns = [
            r"(?:reference|inquiry|tracking)\s*(?:number|#|num)?\s*:?\s*([A-Z0-9-]+)",
            r"(?:INQ|REF|TRK)[- ]?\d{4}[- ]?\d{4,}",
        ]
        for pattern in ref_patterns:
            match = re.search(pattern, conversation_text, re.IGNORECASE)
            if match:
                extracted['reference_number'] = match.group(0) if match.lastindex is None else match.group(1)
                break
        
        # Extract resolution status keywords
        if re.search(r'\b(overturned|approved|accepted)\b', conversation_text, re.IGNORECASE):
            extracted['resolution_status'] = 'overturned'
        elif re.search(r'\b(upheld|maintained|denied again)\b', conversation_text, re.IGNORECASE):
            extracted['resolution_status'] = 'upheld'
        elif re.search(r'\b(appeal|file an appeal)\b', conversation_text, re.IGNORECASE):
            extracted['resolution_status'] = 'appeal_required'
        elif re.search(r'\b(resubmit|re-submit|resubmission)\b', conversation_text, re.IGNORECASE):
            extracted['resolution_status'] = 'resubmit_required'
        elif re.search(r'\b(peer.?to.?peer|medical review)\b', conversation_text, re.IGNORECASE):
            extracted['resolution_status'] = 'peer_to_peer_required'
        else:
            extracted['resolution_status'] = 'unknown'
        
        # Extract fax number
        fax_match = re.search(r'(?:fax|submit to)\s*:?\s*(\d{3}[-.]?\d{3}[-.]?\d{4})', conversation_text, re.IGNORECASE)
        if fax_match:
            extracted['fax_number'] = fax_match.group(1)
        
        # Extract timeline
        timeline_match = re.search(r'(\d+)(?:-(\d+))?\s+(?:business\s+)?days', conversation_text, re.IGNORECASE)
        if timeline_match:
            if timeline_match.group(2):
                extracted['reprocessing_time'] = f"{timeline_match.group(1)}-{timeline_match.group(2)} days"
            else:
                extracted['reprocessing_time'] = f"{timeline_match.group(1)} days"
        
        logger.info(f"[FALLBACK] Extracted {len(extracted)} fields: {list(extracted.keys())}")
        return extracted
