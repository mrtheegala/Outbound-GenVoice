"""
Configuration Loader Utility
Loads YAML/JSON configurations with caching and validation
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Production-ready configuration loader with caching and validation
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader
        
        Args:
            config_dir: Path to configuration directory. If None, uses default.
        """
        if config_dir is None:
            # Default to config directory relative to this file
            self.config_dir = Path(__file__).parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Configuration directory not found: {self.config_dir}")
        
        logger.info(f"ConfigLoader initialized with directory: {self.config_dir}")
    
    @lru_cache(maxsize=32)
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """
        Load YAML configuration file with caching
        
        Args:
            filename: Name of YAML file (with or without .yaml extension)
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        # Ensure .yaml extension
        if not filename.endswith('.yaml') and not filename.endswith('.yml'):
            filename = f"{filename}.yaml"
        
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded configuration from: {filename}")
            return config or {}
        
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration file {filename}: {e}")
            raise
    
    @lru_cache(maxsize=32)
    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file with caching
        
        Args:
            filename: Name of JSON file (with or without .json extension)
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Loaded configuration from: {filename}")
            return config
        
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file {filename}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration file {filename}: {e}")
            raise
    
    def get_procedure_config(self, procedure_code: str) -> Dict[str, Any]:
        """
        Get configuration for specific procedure code
        
        Args:
            procedure_code: CPT procedure code
            
        Returns:
            Procedure configuration dictionary
        """
        procedures = self.load_yaml("procedures")
        
        # Try to find specific procedure
        procedure_config = procedures.get("procedures", {}).get(procedure_code)
        
        if procedure_config:
            logger.info(f"Found configuration for procedure: {procedure_code}")
            return procedure_config
        
        # Return default if not found
        logger.warning(f"Procedure {procedure_code} not found, using default configuration")
        return procedures.get("default_procedure", {})
    
    def get_denial_config(self, denial_code: str) -> Dict[str, Any]:
        """
        Get configuration for specific denial code
        
        Args:
            denial_code: Denial code (e.g., CO-16, PR-1)
            
        Returns:
            Denial configuration dictionary
        """
        denials = self.load_yaml("denial_codes")
        
        # Try to find specific denial code
        denial_config = denials.get("denial_codes", {}).get(denial_code)
        
        if denial_config:
            logger.info(f"Found configuration for denial code: {denial_code}")
            return denial_config
        
        # Return default if not found
        logger.warning(f"Denial code {denial_code} not found, using default configuration")
        return denials.get("default_denial", {})
    
    def get_conversation_stages(self, use_case: str) -> Dict[str, Any]:
        """
        Get conversation stages for specific use case
        
        Args:
            use_case: Use case name (e.g., 'prior_authorization', 'denial_management')
            
        Returns:
            Dictionary of conversation stages
        """
        templates = self.load_yaml("conversation_templates")
        
        stages = templates.get("conversation_stages", {}).get(use_case)
        
        if not stages:
            raise ValueError(f"No conversation stages found for use case: {use_case}")
        
        logger.info(f"Loaded {len(stages)} conversation stages for: {use_case}")
        return stages
    
    def get_escalation_protocol(self, protocol_type: str) -> Dict[str, Any]:
        """
        Get escalation protocol configuration
        
        Args:
            protocol_type: Type of escalation (e.g., 'clinical_review', 'appeal_process')
            
        Returns:
            Escalation protocol configuration
        """
        templates = self.load_yaml("conversation_templates")
        
        protocol = templates.get("escalation_protocols", {}).get(protocol_type)
        
        if not protocol:
            raise ValueError(f"No escalation protocol found for: {protocol_type}")
        
        logger.info(f"Loaded escalation protocol: {protocol_type}")
        return protocol
    
    def get_success_indicators(self, use_case: str) -> Dict[str, Any]:
        """
        Get success indicators for specific use case
        
        Args:
            use_case: Use case name
            
        Returns:
            Dictionary of success indicators
        """
        templates = self.load_yaml("conversation_templates")
        
        indicators = templates.get("success_indicators", {}).get(use_case)
        
        if not indicators:
            logger.warning(f"No success indicators found for: {use_case}")
            return {}
        
        return indicators
    
    def clear_cache(self):
        """Clear the configuration cache"""
        self.load_yaml.cache_clear()
        self.load_json.cache_clear()
        logger.info("Configuration cache cleared")
    
    def reload_config(self, filename: str) -> Dict[str, Any]:
        """
        Force reload of configuration file (bypasses cache)
        
        Args:
            filename: Name of configuration file
            
        Returns:
            Reloaded configuration dictionary
        """
        self.clear_cache()
        
        if filename.endswith('.json'):
            return self.load_json(filename)
        else:
            return self.load_yaml(filename)


# Singleton instance for global use
_config_loader_instance: Optional[ConfigLoader] = None


def get_config_loader(config_dir: Optional[Path] = None) -> ConfigLoader:
    """
    Get singleton ConfigLoader instance
    
    Args:
        config_dir: Optional configuration directory path
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader_instance
    
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader(config_dir)
    
    return _config_loader_instance


# Convenience functions
def load_procedure_config(procedure_code: str) -> Dict[str, Any]:
    """Convenience function to load procedure configuration"""
    return get_config_loader().get_procedure_config(procedure_code)


def load_denial_config(denial_code: str) -> Dict[str, Any]:
    """Convenience function to load denial configuration"""
    return get_config_loader().get_denial_config(denial_code)


def load_conversation_stages(use_case: str) -> Dict[str, Any]:
    """Convenience function to load conversation stages"""
    return get_config_loader().get_conversation_stages(use_case)


if __name__ == "__main__":
    # Test the configuration loader
    logging.basicConfig(level=logging.INFO)
    
    loader = get_config_loader()
    
    # Test procedure loading
    print("\n" + "="*60)
    print("Testing Procedure Configuration")
    print("="*60)
    mri_config = loader.get_procedure_config("72148")
    print(f"Procedure: {mri_config.get('name')}")
    print(f"Requires Prior Auth: {mri_config.get('requires_prior_auth')}")
    print(f"Questions: {len(mri_config.get('standard_questions', []))}")
    
    # Test denial loading
    print("\n" + "="*60)
    print("Testing Denial Configuration")
    print("="*60)
    denial_config = loader.get_denial_config("CO-197")
    print(f"Description: {denial_config.get('description')}")
    print(f"Success Probability: {denial_config.get('success_probability')}")
    print(f"Requires Escalation: {denial_config.get('requires_escalation')}")
    
    # Test conversation stages
    print("\n" + "="*60)
    print("Testing Conversation Stages")
    print("="*60)
    stages = loader.get_conversation_stages("prior_authorization")
    print(f"Total Stages: {len(stages)}")
    for stage_id, stage_info in stages.items():
        print(f"  Stage {stage_id}: {stage_info.get('name')}")
