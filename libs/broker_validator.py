"""
Broker Credential Validator - Validates credential formats and requirements

This module provides utilities to:
- Validate credential format before attempting authentication
- Check API key format patterns
- Validate OAuth token structures
- Provide detailed validation error messages
"""
import re
from typing import Dict, List, Tuple


class BrokerValidator:
    """Validates broker credentials and formats"""
    
    # Credential requirements for each broker
    CREDENTIAL_REQUIREMENTS = {
        'angel': {
            'BROKER_API_KEY': {
                'required': True,
                'min_length': 10,
                'pattern': None,
                'description': 'AngelOne API Key'
            }
            # Client Code, Password, TOTP requested during authentication
        },
        'dhan': {
            'BROKER_API_KEY': {
                'required': True,
                'min_length': 10,
                'pattern': None,
                'description': 'Dhan App ID'
            },
            'BROKER_API_SECRET': {
                'required': True,
                'min_length': 10,
                'pattern': None,
                'description': 'Dhan App Secret'
            },
            'dhan_client_id': {
                'required': True,
                'min_length': 5,
                'pattern': r'^\d+$',
                'description': 'Dhan Client ID (numeric)'
            }
        },
        'fyers': {
            'BROKER_API_KEY': {
                'required': True,
                'min_length': 10,
                'pattern': None,
                'description': 'Fyers App ID'
            },
            'BROKER_API_SECRET': {
                'required': True,
                'min_length': 10,
                'pattern': None,
                'description': 'Fyers App Secret'
            }
        }
    }
    
    @classmethod
    def validate_credential_format(cls, broker: str, credentials: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Validate credential format for a broker
        
        Args:
            broker: Broker name (angel, dhan, fyers)
            credentials: Dictionary of credentials to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list of error messages)
        """
        if broker not in cls.CREDENTIAL_REQUIREMENTS:
            return False, [f"Unsupported broker: {broker}"]
        
        requirements = cls.CREDENTIAL_REQUIREMENTS[broker]
        errors = []
        
        # Check each required credential
        for cred_key, rules in requirements.items():
            if rules['required'] and cred_key not in credentials:
                errors.append(f"Missing required credential: {rules['description']}")
                continue
            
            if cred_key not in credentials:
                continue
            
            value = credentials[cred_key]
            
            # Check if empty
            if not value or not value.strip():
                errors.append(f"{rules['description']} cannot be empty")
                continue
            
            # Check minimum length
            if 'min_length' in rules and len(value) < rules['min_length']:
                errors.append(
                    f"{rules['description']} must be at least {rules['min_length']} characters"
                )
            
            # Check maximum length
            if 'max_length' in rules and len(value) > rules['max_length']:
                errors.append(
                    f"{rules['description']} must be at most {rules['max_length']} characters"
                )
            
            # Check pattern
            if rules.get('pattern') and not re.match(rules['pattern'], value):
                errors.append(
                    f"{rules['description']} has invalid format"
                )
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_api_key_format(cls, api_key: str, broker: str) -> Tuple[bool, str]:
        """
        Validate API key format for a specific broker
        
        Args:
            api_key: API key to validate
            broker: Broker name
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not api_key or not api_key.strip():
            return False, "API key cannot be empty"
        
        if len(api_key) < 10:
            return False, "API key seems too short"
        
        # Broker-specific validation
        if broker == 'angel':
            # AngelOne API keys are typically alphanumeric
            if not re.match(r'^[A-Za-z0-9]+$', api_key):
                return False, "AngelOne API key should be alphanumeric"
        
        elif broker == 'dhan':
            # Dhan app IDs are typically alphanumeric
            if not re.match(r'^[A-Za-z0-9\-_]+$', api_key):
                return False, "Dhan App ID should be alphanumeric"
        
        elif broker == 'fyers':
            # Fyers app IDs have a specific format
            if not re.match(r'^[A-Z0-9\-]+$', api_key):
                return False, "Fyers App ID should be uppercase alphanumeric"
        
        return True, ""
    
    @classmethod
    def validate_oauth_token(cls, token: str) -> Tuple[bool, str]:
        """
        Validate OAuth token format
        
        Args:
            token: OAuth token to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not token or not token.strip():
            return False, "Token cannot be empty"
        
        # Basic JWT format check (header.payload.signature)
        if token.count('.') == 2:
            parts = token.split('.')
            if all(len(part) > 0 for part in parts):
                return True, ""
        
        # Check if it's a simple token (alphanumeric with possible dashes/underscores)
        if re.match(r'^[A-Za-z0-9\-_]+$', token) and len(token) > 20:
            return True, ""
        
        return False, "Invalid token format"
    
    @classmethod
    def get_validation_requirements(cls, broker: str) -> Dict:
        """
        Get validation requirements for a broker
        
        Args:
            broker: Broker name
            
        Returns:
            Dict: Requirements dictionary
        """
        return cls.CREDENTIAL_REQUIREMENTS.get(broker, {})
    
    @classmethod
    def get_missing_credentials(cls, broker: str, credentials: Dict[str, str]) -> List[str]:
        """
        Get list of missing required credentials
        
        Args:
            broker: Broker name
            credentials: Current credentials
            
        Returns:
            List[str]: List of missing credential descriptions
        """
        if broker not in cls.CREDENTIAL_REQUIREMENTS:
            return []
        
        requirements = cls.CREDENTIAL_REQUIREMENTS[broker]
        missing = []
        
        for cred_key, rules in requirements.items():
            if rules['required'] and (cred_key not in credentials or not credentials[cred_key]):
                missing.append(rules['description'])
        
        return missing
    
    @classmethod
    def validate_totp_code(cls, totp: str) -> Tuple[bool, str]:
        """
        Validate TOTP code format
        
        Args:
            totp: TOTP code to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not totp or not totp.strip():
            return False, "TOTP code cannot be empty"
        
        if not re.match(r'^\d{6}$', totp):
            return False, "TOTP code must be exactly 6 digits"
        
        return True, ""
