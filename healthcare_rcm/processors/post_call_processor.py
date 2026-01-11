"""
Post-Call Processor for Prior Authorization Calls
Handles extraction, validation, and storage after call completion
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from healthcare_rcm.extractors.prior_auth_extractor import PriorAuthExtractor, extract_prior_auth_info
from healthcare_rcm.validators.prior_auth_validator import PriorAuthValidator, validate_prior_auth
from healthcare_rcm.storage.prior_auth_storage import PriorAuthStorage, get_storage
from healthcare_rcm.models.prior_auth_models import PriorAuthRecord, AuthorizationStatus

logger = logging.getLogger(__name__)


class PostCallProcessor:
    """Processes prior authorization calls after completion"""
    
    def __init__(self, storage_dir: str = "prior_auth_records"):
        """
        Initialize post-call processor
        
        Args:
            storage_dir: Directory to store prior auth records
        """
        self.extractor = PriorAuthExtractor()
        self.validator = PriorAuthValidator()
        self.storage = get_storage(storage_dir)
        
        logger.info("PostCallProcessor initialized")
    
    def process_prior_auth_call(
        self,
        conversation_history: list,
        call_id: str,
        agent_config: Optional[Dict[str, Any]] = None
    ) -> PriorAuthRecord:
        """
        Process a completed prior authorization call
        
        Args:
            conversation_history: List of conversation turns
            call_id: Unique call identifier
            agent_config: Agent configuration with patient/provider/procedure info
        
        Returns:
            Validated PriorAuthRecord
        """
        logger.info(f"Processing prior auth call: {call_id}")
        logger.info(f"Conversation turns: {len(conversation_history)}")
        
        try:
            # Step 1: Extract structured information from conversation
            logger.info("Step 1: Extracting information from conversation...")
            record = self.extractor.extract_from_conversation(
                conversation_history=conversation_history,
                call_id=call_id,
                agent_config=agent_config
            )
            
            # Step 2: Validate extracted information
            logger.info("Step 2: Validating extracted information...")
            record = self.validator.validate(record)
            
            # Step 3: Save to storage
            logger.info("Step 3: Saving record to storage...")
            filepath = self.storage.save_record(record)
            
            # Step 4: Log results
            self._log_results(record, filepath)
            
            return record
            
        except Exception as e:
            logger.error(f"Error processing prior auth call {call_id}: {e}", exc_info=True)
            raise
    
    def _log_results(self, record: PriorAuthRecord, filepath: str):
        """Log processing results"""
        logger.info("=" * 80)
        logger.info(f"PRIOR AUTH CALL COMPLETED: {record.call_id}")
        logger.info("=" * 80)
        logger.info(f"Status: {record.authorization.status.value.upper()}")
        logger.info(f"Outcome: {record.call_outcome.value.upper()}")
        
        if record.authorization.authorization_number:
            logger.info(f"[OK] Auth Number: {record.authorization.authorization_number}")
        
        if record.authorization.reference_number:
            logger.info(f"[OK] Reference: {record.authorization.reference_number}")
        
        if record.missing_fields:
            logger.warning(f"[MISSING] Fields ({len(record.missing_fields)}): {', '.join(record.missing_fields[:5])}")
        
        if record.validation_errors:
            logger.error(f"[ERROR] Validation Errors ({len(record.validation_errors)})")
            for error in record.validation_errors[:3]:
                logger.error(f"  - {error}")
        
        if record.validation_warnings:
            logger.warning(f"[WARN] Warnings ({len(record.validation_warnings)})")
            for warning in record.validation_warnings[:3]:
                logger.warning(f"  - {warning}")
        
        logger.info(f"[SAVED] File: {filepath}")
        
        if record.next_steps:
            logger.info("\n[NEXT STEPS]:")
            for i, step in enumerate(record.next_steps[:5], 1):
                logger.info(f"  {i}. {step}")
        
        logger.info("=" * 80)
    
    def should_process_call(self, conversation_history: list, agent_config: Optional[Dict] = None) -> bool:
        """
        Determine if call should be processed as prior authorization
        
        Args:
            conversation_history: List of conversation turns
            agent_config: Agent configuration
        
        Returns:
            True if this appears to be a prior auth call
        """
        # Check agent config for prior auth indicators
        if agent_config:
            agent_role = agent_config.get('agent_role', '').lower()
            if 'prior' in agent_role or 'authorization' in agent_role:
                return True
        
        # Check conversation content for prior auth keywords
        conversation_text = ' '.join(conversation_history).lower()
        prior_auth_keywords = [
            'prior authorization',
            'prior auth',
            'authorization request',
            'cpt code',
            'medical necessity',
            'authorization number',
            'reference number'
        ]
        
        # If we find multiple prior auth keywords, likely a prior auth call
        keyword_matches = sum(1 for keyword in prior_auth_keywords if keyword in conversation_text)
        
        return keyword_matches >= 3


# Convenience function for integration
def process_completed_call(
    conversation_history: list,
    call_id: str,
    agent_config: Optional[Dict[str, Any]] = None,
    storage_dir: str = "prior_auth_records"
) -> Optional[PriorAuthRecord]:
    """
    Convenience function to process a completed call
    
    Args:
        conversation_history: List of conversation turns
        call_id: Unique call identifier  
        agent_config: Agent configuration
        storage_dir: Directory to store records
    
    Returns:
        PriorAuthRecord if processed, None if not a prior auth call
    """
    processor = PostCallProcessor(storage_dir=storage_dir)
    
    # Check if this is a prior auth call
    if not processor.should_process_call(conversation_history, agent_config):
        logger.info(f"Call {call_id} does not appear to be a prior authorization call - skipping processing")
        return None
    
    # Process the call
    return processor.process_prior_auth_call(conversation_history, call_id, agent_config)
