"""
Base Analyzer Abstract Class
Defines interface for all RCM analyzers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BaseAnalyzer(ABC):
    """
    Abstract base class for all RCM analyzers
    Enforces consistent interface across different use cases
    """
    
    def __init__(self, config_loader):
        """
        Initialize base analyzer
        
        Args:
            config_loader: ConfigLoader instance for accessing configurations
        """
        self.config_loader = config_loader
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze input data and generate strategy
        
        Args:
            data: Input data dictionary
            
        Returns:
            Analysis result dictionary
        """
        pass
    
    @abstractmethod
    def create_call_strategy(self, analysis: Dict[str, Any]) -> List[str]:
        """
        Create step-by-step call strategy
        
        Args:
            analysis: Analysis result
            
        Returns:
            List of strategy steps
        """
        pass
    
    @abstractmethod
    def check_escalation_needed(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Determine if escalation is needed
        
        Args:
            data: Input data
            
        Returns:
            Tuple of (needs_escalation, escalation_reason)
        """
        pass
    
    def extract_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """
        Extract matching keywords from text
        
        Args:
            text: Text to search
            keywords: List of keywords to find
            
        Returns:
            List of found keywords
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in text_lower]
        
        return found_keywords
    
    def check_keywords_present(self, text: str, keywords: List[str]) -> bool:
        """
        Check if any keywords are present in text
        
        Args:
            text: Text to search
            keywords: List of keywords
            
        Returns:
            True if any keyword found
        """
        return len(self.extract_keywords(text, keywords)) > 0
    
    def calculate_confidence_score(self, required_fields: List[str], provided_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on data completeness
        
        Args:
            required_fields: List of required field names
            provided_data: Dictionary of provided data
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not required_fields:
            return 1.0
        
        present_fields = sum(1 for field in required_fields if provided_data.get(field))
        return present_fields / len(required_fields)
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
        """
        Validate input data has required fields
        
        Args:
            data: Input data dictionary
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, missing_fields)
        """
        missing_fields = [field for field in required_fields if not data.get(field)]
        is_valid = len(missing_fields) == 0
        
        if not is_valid:
            self.logger.warning(f"Missing required fields: {missing_fields}")
        
        return is_valid, missing_fields
    
    def log_analysis(self, analysis_type: str, input_data: Dict[str, Any], result: Dict[str, Any]):
        """
        Log analysis for debugging and auditing
        
        Args:
            analysis_type: Type of analysis performed
            input_data: Input data
            result: Analysis result
        """
        self.logger.info(f"Analysis Type: {analysis_type}")
        self.logger.debug(f"Input: {input_data}")
        self.logger.debug(f"Result: {result}")
