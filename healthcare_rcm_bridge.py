"""
Healthcare RCM Integration Bridge
Connects healthcare_rcm intelligence layer with ConversationalModel voice framework
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import healthcare_rcm components
try:
    from healthcare_rcm import PriorAuthAnalyzer, PriorAuthRequest
    from healthcare_rcm.utils.config_loader import get_config_loader
    HEALTHCARE_RCM_AVAILABLE = True
except ImportError:
    HEALTHCARE_RCM_AVAILABLE = False
    logging.warning("healthcare_rcm module not available. Install with: pip install -r healthcare_rcm/requirements.txt")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthcareRCMBridge:
    """
    Bridge class to connect healthcare_rcm analysis with voice calling system
    """
    
    def __init__(self):
        """Initialize the bridge"""
        if not HEALTHCARE_RCM_AVAILABLE:
            raise ImportError("healthcare_rcm module is required. Install dependencies first.")
        
        self.config_loader = get_config_loader()
        self.prior_auth_analyzer = PriorAuthAnalyzer()
        logger.info("HealthcareRCMBridge initialized successfully")
    
    def create_prior_auth_config(
        self,
        request_data: Dict[str, Any],
        config_template_path: str = 'example_agent_configs/Prior_Auth_Agent_config.json'
    ) -> Dict[str, Any]:
        """
        Convert prior authorization request data into agent configuration
        
        Args:
            request_data: Dictionary containing prior auth request details
            config_template_path: Path to agent config template
        
        Returns:
            Complete agent configuration ready for voice call
        """
        logger.info("Creating prior auth agent config from request data")
        
        # Step 1: Analyze the request using healthcare_rcm
        analysis = self.prior_auth_analyzer.analyze(request_data)
        
        # Step 2: Load template config
        with open(config_template_path, 'r') as f:
            config = json.load(f)
        
        # Step 3: Populate config with analysis results
        request = analysis.request
        
        config['procedure_code'] = request.procedure_code
        config['procedure_name'] = request.procedure_name
        config['patient_name'] = request.patient_name
        config['patient_dob'] = str(request.patient_dob)
        config['member_id'] = request.member_id
        config['provider_name'] = request.provider_name
        config['provider_npi'] = request.provider_npi
        config['payer_name'] = request.payer_name
        config['diagnosis_code'] = request.diagnosis_code
        config['clinical_notes'] = request.clinical_notes or ""
        config['urgency_level'] = analysis.urgency_level
        
        # Add analysis insights to config
        config['call_strategy_steps'] = analysis.call_strategy_steps
        config['questions_to_ask'] = analysis.questions_to_ask
        config['escalation_needed'] = analysis.escalation_needed
        config['escalation_reason'] = analysis.escalation_reason or ""
        
        logger.info(f"Created config for procedure {request.procedure_code} - {request.procedure_name}")
        
        return config
    
    def create_denial_management_config(
        self,
        claim_data: Dict[str, Any],
        config_template_path: str = 'example_agent_configs/Denial_Management_Agent_config.json'
    ) -> Dict[str, Any]:
        """
        Convert denial management data into agent configuration
        
        Args:
            claim_data: Dictionary containing claim and denial details
            config_template_path: Path to agent config template
        
        Returns:
            Complete agent configuration ready for voice call
        """
        logger.info("Creating denial management agent config from claim data")
        
        # Load template config
        with open(config_template_path, 'r') as f:
            config = json.load(f)
        
        # Populate config with claim data
        config['claim_number'] = claim_data.get('claim_number')
        config['patient_name'] = claim_data.get('patient_name')
        config['service_date'] = claim_data.get('service_date')
        config['procedure_code'] = claim_data.get('procedure_code')
        config['procedure_name'] = claim_data.get('procedure_name')
        config['diagnosis_code'] = claim_data.get('diagnosis_code')
        config['denial_code'] = claim_data.get('denial_code')
        config['denial_reason'] = claim_data.get('denial_reason')
        config['payer_name'] = claim_data.get('payer_name')
        config['provider_name'] = claim_data.get('provider_name')
        config['provider_npi'] = claim_data.get('provider_npi')
        
        logger.info(f"Created denial config for claim {claim_data.get('claim_number')}")
        
        return config
    
    def create_insurance_verification_config(
        self,
        verification_data: Dict[str, Any],
        config_template_path: str = 'example_agent_configs/Insurance_Verification_Agent_config.json'
    ) -> Dict[str, Any]:
        """
        Convert insurance verification data into agent configuration
        
        Args:
            verification_data: Dictionary containing patient and procedure details
            config_template_path: Path to agent config template
        
        Returns:
            Complete agent configuration ready for voice call
        """
        logger.info("Creating insurance verification agent config")
        
        # Load template config
        with open(config_template_path, 'r') as f:
            config = json.load(f)
        
        # Populate config with verification data
        config['patient_name'] = verification_data.get('patient_name')
        config['patient_dob'] = verification_data.get('patient_dob')
        config['member_id'] = verification_data.get('member_id')
        config['procedure_code'] = verification_data.get('procedure_code')
        config['procedure_name'] = verification_data.get('procedure_name')
        config['payer_name'] = verification_data.get('payer_name')
        config['provider_name'] = verification_data.get('provider_name')
        config['provider_npi'] = verification_data.get('provider_npi')
        config['planned_service_date'] = verification_data.get('planned_service_date')
        
        logger.info(f"Created verification config for patient {verification_data.get('patient_name')}")
        
        return config
    
    def save_temp_config(self, config: Dict[str, Any], use_case: str) -> str:
        """
        Save temporary agent configuration to file
        
        Args:
            config: Agent configuration dictionary
            use_case: Type of use case (prior_auth, denial, verification)
        
        Returns:
            Path to saved configuration file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_id = config.get('member_id', 'unknown')
        filename = f"temp_{use_case}_{patient_id}_{timestamp}.json"
        filepath = f"example_agent_configs/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved temporary config to {filepath}")
        return filepath


def initiate_prior_auth_call(
    request_data: Dict[str, Any],
    to_number: str,
    bridge: Optional[HealthcareRCMBridge] = None
) -> tuple[Dict[str, Any], str]:
    """
    End-to-end function: Analyze prior auth request and prepare for voice call
    
    Args:
        request_data: Prior authorization request data
        to_number: Phone number to call
        bridge: HealthcareRCMBridge instance (creates new if None)
    
    Returns:
        Tuple of (agent_config, temp_config_path)
    
    Example:
        request_data = {
            'procedure_code': '72148',
            'patient_name': 'John Doe',
            'patient_dob': '1975-06-15',
            'member_id': 'ABC123456789',
            'provider_name': 'Dr. Sarah Smith',
            'provider_npi': '1234567890',
            'payer_name': 'Blue Cross Blue Shield',
            'diagnosis_code': 'M54.5',
            'clinical_notes': 'Patient presents with chronic lower back pain...'
        }
        
        config, config_path = initiate_prior_auth_call(request_data, '+19550760205')
        
        # Then use config_path with app.py to make the call
    """
    if bridge is None:
        bridge = HealthcareRCMBridge()
    
    # Create agent config from analysis
    config = bridge.create_prior_auth_config(request_data)
    
    # Save temporary config
    config_path = bridge.save_temp_config(config, 'prior_auth')
    
    logger.info(f"Prior auth call ready. Config saved to: {config_path}")
    logger.info(f"To make call, update AGENT_CONFIG_PATH in __config__.py to: {config_path}")
    
    return config, config_path


def initiate_denial_management_call(
    claim_data: Dict[str, Any],
    to_number: str,
    bridge: Optional[HealthcareRCMBridge] = None
) -> tuple[Dict[str, Any], str]:
    """
    End-to-end function: Prepare denial management call
    
    Args:
        claim_data: Claim and denial information
        to_number: Phone number to call
        bridge: HealthcareRCMBridge instance (creates new if None)
    
    Returns:
        Tuple of (agent_config, temp_config_path)
    """
    if bridge is None:
        bridge = HealthcareRCMBridge()
    
    # Create agent config
    config = bridge.create_denial_management_config(claim_data)
    
    # Save temporary config
    config_path = bridge.save_temp_config(config, 'denial')
    
    logger.info(f"Denial management call ready. Config saved to: {config_path}")
    
    return config, config_path


# Example usage
if __name__ == "__main__":
    print("Healthcare RCM Bridge - Integration Layer")
    print("=" * 50)
    
    if not HEALTHCARE_RCM_AVAILABLE:
        print("ERROR: healthcare_rcm module not available")
        print("Install with: pip install -r healthcare_rcm/requirements.txt")
        exit(1)
    
    # Example: Create prior auth config
    example_request = {
        'procedure_code': '72148',
        'patient_name': 'John Doe',
        'patient_dob': '1975-06-15',
        'member_id': 'ABC123456789',
        'provider_name': 'Dr. Sarah Smith',
        'provider_npi': '1234567890',
        'payer_name': 'Blue Cross Blue Shield',
        'diagnosis_code': 'M54.5',
        'clinical_notes': 'Patient presents with chronic lower back pain for 8 weeks. Conservative treatment attempted including physical therapy for 6 weeks (failed to improve), NSAIDs (minimal relief).'
    }
    
    print("\nExample: Creating Prior Authorization Call Config")
    print("-" * 50)
    
    bridge = HealthcareRCMBridge()
    config, config_path = initiate_prior_auth_call(example_request, '+19550760205')
    
    print(f"\n✅ Success!")
    print(f"Config saved to: {config_path}")
    print(f"\nTo make the call:")
    print(f"1. Update AGENT_CONFIG_PATH in __config__.py")
    print(f"2. Run: python app.py")
    print(f"3. POST to /make-call with phone number")
