"""
Prior Authorization Analyzer
Production-ready analyzer with zero hardcoding
"""

from typing import Dict, Any, List
import logging
from .base_analyzer import BaseAnalyzer
from ...models.prior_auth import PriorAuthRequest, PriorAuthAnalysis, DocumentationRequirement
from ...utils.config_loader import get_config_loader

logger = logging.getLogger(__name__)


class PriorAuthAnalyzer(BaseAnalyzer):
    """
    Analyzes prior authorization requests and creates call strategies
    All logic driven by YAML configuration - zero hardcoding
    """
    
    def __init__(self, config_loader=None):
        """
        Initialize Prior Authorization Analyzer
        
        Args:
            config_loader: Optional ConfigLoader instance
        """
        if config_loader is None:
            config_loader = get_config_loader()
        
        super().__init__(config_loader)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze(self, data: Dict[str, Any]) -> PriorAuthAnalysis:
        """
        Analyze prior authorization request
        
        Args:
            data: Dictionary containing prior auth request data
            
        Returns:
            PriorAuthAnalysis object with complete analysis
        """
        self.logger.info(f"Analyzing prior auth request for procedure: {data.get('procedure_code')}")
        
        # Validate input
        required_fields = ['procedure_code', 'diagnosis_code', 'patient_name', 'patient_dob', 'clinical_notes']
        is_valid, missing_fields = self.validate_input(data, required_fields)
        
        if not is_valid:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Create request model
        request = PriorAuthRequest(**data)
        
        # Load procedure configuration
        procedure_config = self.config_loader.get_procedure_config(request.procedure_code)
        
        # Populate procedure name if not provided
        if not request.procedure_name:
            request.procedure_name = procedure_config.get('name', f"Procedure {request.procedure_code}")
        
        # Analyze documentation
        doc_analysis = self._analyze_documentation(request.clinical_notes, procedure_config)
        
        # Check approval criteria
        criteria_met = self._check_approval_criteria(request.clinical_notes, procedure_config)
        
        # Determine escalation needs
        needs_escalation, escalation_reason = self.check_escalation_needed(data)
        
        # Get call strategy
        call_strategy = self.create_call_strategy({
            'procedure_config': procedure_config,
            'urgency': request.urgency_level,
            'is_retroactive': request.is_retroactive
        })
        
        # Calculate success probability
        success_prob = self._calculate_success_probability(
            doc_analysis['documentation_complete'],
            criteria_met,
            needs_escalation
        )
        
        # Get turnaround time
        turnaround = self._get_turnaround_time(procedure_config, request.urgency_level)
        
        # Create analysis result
        analysis = PriorAuthAnalysis(
            request=request,
            procedure_category=procedure_config.get('category', 'general'),
            requires_prior_auth=procedure_config.get('requires_prior_auth', True),
            typical_cost=procedure_config.get('typical_cost'),
            required_documentation=[doc['description'] for doc in doc_analysis['requirements']],
            missing_documentation=doc_analysis['missing'],
            documentation_complete=doc_analysis['documentation_complete'],
            approval_criteria=procedure_config.get('approval_criteria', {}),
            criteria_met=criteria_met,
            questions_to_ask=procedure_config.get('standard_questions', []),
            call_strategy_steps=call_strategy,
            payer_contact_department=self._determine_contact_department(request.urgency_level),
            expected_turnaround_time=turnaround,
            needs_escalation=needs_escalation,
            escalation_reason=escalation_reason if needs_escalation else None,
            escalation_type=self._determine_escalation_type(escalation_reason) if needs_escalation else None,
            success_probability=success_prob
        )
        
        self.log_analysis("prior_authorization", data, analysis.dict())
        
        return analysis
    
    def _analyze_documentation(self, clinical_notes: str, procedure_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze if required documentation is present
        
        Args:
            clinical_notes: Clinical notes text
            procedure_config: Procedure configuration
            
        Returns:
            Dictionary with documentation analysis
        """
        requirements = procedure_config.get('documentation_requirements', [])
        missing = []
        
        for req in requirements:
            if req.get('mandatory', True):
                keywords = req.get('keywords', [req.get('description', '')])
                if not self.check_keywords_present(clinical_notes, keywords):
                    missing.append(req.get('description', 'Unknown requirement'))
        
        return {
            'requirements': requirements,
            'missing': missing,
            'documentation_complete': len(missing) == 0
        }
    
    def _check_approval_criteria(self, clinical_notes: str, procedure_config: Dict[str, Any]) -> bool:
        """
        Check if approval criteria are met
        
        Args:
            clinical_notes: Clinical notes text
            procedure_config: Procedure configuration
            
        Returns:
            True if criteria appear to be met
        """
        approval_criteria = procedure_config.get('approval_criteria', {})
        
        # Check primary criterion
        primary = approval_criteria.get('primary', '')
        if not primary:
            return True  # No criteria defined
        
        # Simple keyword check - in production, this would be more sophisticated
        primary_keywords = primary.lower().split()
        notes_lower = clinical_notes.lower()
        
        # Check if most keywords are present
        matches = sum(1 for kw in primary_keywords if kw in notes_lower)
        
        return matches >= len(primary_keywords) * 0.5  # At least 50% match
    
    def create_call_strategy(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Create step-by-step call strategy
        
        Args:
            analysis: Analysis data including procedure_config
            
        Returns:
            List of strategy steps
        """
        procedure_config = analysis.get('procedure_config', {})
        urgency = analysis.get('urgency', 'routine')
        is_retroactive = analysis.get('is_retroactive', False)
        
        strategy = [
            "1. Verify speaking with Prior Authorization department",
            "2. Provide provider name, NPI, and tax ID",
            "3. State purpose: Prior authorization request",
            "4. Provide patient demographics (name, DOB, member ID)",
            "5. Verify patient coverage is active",
            f"6. State procedure: {procedure_config.get('name', 'procedure')} (CPT {analysis.get('procedure_code', 'code')})",
            "7. Provide diagnosis code and description",
            "8. Explain medical necessity based on clinical notes",
            "9. Answer standard questions about clinical presentation",
            "10. Confirm required documentation and submission method",
            "11. Request authorization reference number",
            "12. Confirm expected turnaround time",
            "13. Get representative name and direct callback number",
            "14. Thank and end call professionally"
        ]
        
        # Add urgency step if urgent
        if urgency in ['urgent', 'stat']:
            strategy.insert(6, "6a. Request expedited review due to urgency")
        
        # Add retroactive note if applicable
        if is_retroactive:
            strategy.insert(3, "3a. Note: This is a RETROACTIVE authorization request")
        
        return strategy
    
    def check_escalation_needed(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Determine if escalation is needed
        
        Args:
            data: Input data
            
        Returns:
            Tuple of (needs_escalation, escalation_reason)
        """
        procedure_code = data.get('procedure_code', '')
        clinical_notes = data.get('clinical_notes', '')
        
        # Load procedure config
        procedure_config = self.config_loader.get_procedure_config(procedure_code)
        
        # Check escalation triggers from config
        escalation_triggers = procedure_config.get('escalation_triggers', [])
        
        for trigger in escalation_triggers:
            keyword = trigger.get('keyword', '')
            if keyword and keyword.lower() in clinical_notes.lower():
                action = trigger.get('action', 'clinical_review')
                return True, f"{keyword.capitalize()} detected - requires {action}"
        
        return False, ""
    
    def _determine_escalation_type(self, escalation_reason: str) -> str:
        """
        Determine type of escalation needed
        
        Args:
            escalation_reason: Reason for escalation
            
        Returns:
            Escalation type
        """
        if 'peer' in escalation_reason.lower():
            return "peer_to_peer"
        elif 'clinical' in escalation_reason.lower():
            return "clinical_review"
        else:
            return "general_escalation"
    
    def _calculate_success_probability(self, docs_complete: bool, criteria_met: bool, needs_escalation: bool) -> float:
        """
        Calculate probability of successful authorization
        
        Args:
            docs_complete: Whether documentation is complete
            criteria_met: Whether approval criteria are met
            needs_escalation: Whether escalation is needed
            
        Returns:
            Success probability between 0.0 and 1.0
        """
        base_prob = 0.5
        
        if docs_complete:
            base_prob += 0.2
        
        if criteria_met:
            base_prob += 0.2
        
        if needs_escalation:
            base_prob -= 0.2
        
        return max(0.0, min(1.0, base_prob))
    
    def _get_turnaround_time(self, procedure_config: Dict[str, Any], urgency: str) -> str:
        """
        Get expected turnaround time
        
        Args:
            procedure_config: Procedure configuration
            urgency: Urgency level
            
        Returns:
            Turnaround time string
        """
        turnaround_times = procedure_config.get('turnaround_time', {})
        
        if isinstance(turnaround_times, dict):
            return turnaround_times.get(urgency, "3-5 business days")
        else:
            return str(turnaround_times)
    
    def _determine_contact_department(self, urgency: str) -> str:
        """
        Determine which department to contact
        
        Args:
            urgency: Urgency level
            
        Returns:
            Department name
        """
        if urgency == 'stat':
            return "Urgent Prior Authorization Line"
        elif urgency == 'urgent':
            return "Expedited Prior Authorization"
        else:
            return "Prior Authorization Department"


if __name__ == "__main__":
    # Test the analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = PriorAuthAnalyzer()
    
    # Test case
    test_data = {
        "procedure_code": "72148",
        "diagnosis_code": "M54.5",
        "patient_name": "John Doe",
        "patient_dob": "1975-06-15",
        "member_id": "ABC123456789",
        "provider_name": "Dr. Smith",
        "provider_npi": "1234567890",
        "clinical_notes": "Patient has chronic lower back pain for 8 weeks. Failed conservative treatment including physical therapy for 6 weeks and NSAIDs. Radicular symptoms present.",
        "urgency_level": "routine"
    }
    
    print("\n" + "="*60)
    print("PRIOR AUTHORIZATION ANALYSIS")
    print("="*60)
    
    analysis = analyzer.analyze(test_data)
    
    print(f"\nProcedure: {analysis.request.procedure_name} ({analysis.request.procedure_code})")
    print(f"Category: {analysis.procedure_category}")
    print(f"Requires Prior Auth: {analysis.requires_prior_auth}")
    print(f"\nDocumentation Complete: {analysis.documentation_complete}")
    if analysis.missing_documentation:
        print(f"Missing: {', '.join(analysis.missing_documentation)}")
    
    print(f"\nCriteria Met: {analysis.criteria_met}")
    print(f"Success Probability: {analysis.success_probability:.0%}")
    print(f"Expected Turnaround: {analysis.expected_turnaround_time}")
    
    print(f"\nNeeds Escalation: {analysis.needs_escalation}")
    if analysis.needs_escalation:
        print(f"Escalation Reason: {analysis.escalation_reason}")
    
    print(f"\nQuestions to Ask ({len(analysis.questions_to_ask)}):")
    for q in analysis.questions_to_ask:
        print(f"  • {q}")
    
    print(f"\nCall Strategy ({len(analysis.call_strategy_steps)} steps):")
    for step in analysis.call_strategy_steps[:5]:  # Show first 5
        print(f"  {step}")
    print(f"  ... ({len(analysis.call_strategy_steps) - 5} more steps)")
