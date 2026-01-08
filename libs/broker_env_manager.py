"""
Broker Environment Manager - Handles .env file operations for broker credentials

This module provides utilities to:
- Read/write .env file safely
- Update specific broker credentials without affecting others
- Validate .env file format
- Set active broker in .env
- Backup/restore .env file
"""
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import shutil
from datetime import datetime


class BrokerEnvManager:
    """Manages .env file operations for broker credentials"""
    
    # Broker credential key mappings
    BROKER_KEYS = {
        'angel': {
            'BROKER_API_KEY': 'ANGEL_API_KEY'
            # Client Code, Password, TOTP requested during authentication
        },
        'dhan': {
            'BROKER_API_KEY': 'DHAN_API_KEY',
            'BROKER_API_SECRET': 'DHAN_API_SECRET',
            'dhan_client_id': 'DHAN_CLIENT_ID'
        },
        'fyers': {
            'BROKER_API_KEY': 'FYERS_API_KEY',
            'BROKER_API_SECRET': 'FYERS_API_SECRET'
        }
    }
    
    def __init__(self, env_path: Optional[Path] = None):
        """Initialize with optional custom .env path"""
        self.env_path = env_path or Path(__file__).parent.parent / ".env"
        self.backup_dir = Path(__file__).parent.parent / "data" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def read_env_file(self) -> Dict[str, str]:
        """
        Read .env file and return as dictionary
        
        Returns:
            Dict[str, str]: Environment variables from .env file
        """
        env_vars = {}
        
        if not self.env_path.exists():
            return env_vars
        
        try:
            with open(self.env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error reading .env file: {e}")
        
        return env_vars
    
    def write_env_file(self, env_vars: Dict[str, str]) -> bool:
        """
        Write environment variables to .env file
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Backup existing file first
            if self.env_path.exists():
                self.backup_env_file()
            
            with open(self.env_path, 'w') as f:
                f.write("# ============================================\n")
                f.write("# Broker Configuration\n")
                f.write("# ============================================\n")
                f.write(f"# Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write active broker first
                if 'ACTIVE_BROKER' in env_vars:
                    f.write(f"ACTIVE_BROKER={env_vars['ACTIVE_BROKER']}\n\n")
                
                # Write AngelOne credentials
                f.write("# ============================================\n")
                f.write("# AngelOne (SmartAPI) Credentials\n")
                f.write("# ============================================\n")
                for key in ['ANGEL_API_KEY', 'ANGEL_CLIENT_CODE', 'ANGEL_PASSWORD', 'ANGEL_TOTP_SECRET']:
                    f.write(f"{key}={env_vars.get(key, '')}\n")
                f.write("\n")
                
                # Write Dhan credentials
                f.write("# ============================================\n")
                f.write("# Dhan Securities Credentials\n")
                f.write("# ============================================\n")
                for key in ['DHAN_API_KEY', 'DHAN_API_SECRET', 'DHAN_CLIENT_ID']:
                    f.write(f"{key}={env_vars.get(key, '')}\n")
                f.write("\n")
                
                # Write Fyers credentials
                f.write("# ============================================\n")
                f.write("# Fyers Securities Credentials\n")
                f.write("# ============================================\n")
                for key in ['FYERS_API_KEY', 'FYERS_API_SECRET']:
                    f.write(f"{key}={env_vars.get(key, '')}\n")
                f.write("\n")
                
                # Write legacy environment variables
                f.write("# ============================================\n")
                f.write("# Legacy Environment Variables (auto-set)\n")
                f.write("# ============================================\n")
                if 'BROKER_API_KEY' in env_vars:
                    f.write(f"BROKER_API_KEY={env_vars['BROKER_API_KEY']}\n")
                if 'BROKER_API_SECRET' in env_vars:
                    f.write(f"BROKER_API_SECRET={env_vars['BROKER_API_SECRET']}\n")
            
            return True
        except Exception as e:
            print(f"Error writing .env file: {e}")
            return False
    
    def update_broker_credentials(self, broker: str, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """
        Update credentials for a specific broker
        
        Args:
            broker: Broker name (angel, dhan, fyers)
            credentials: Dictionary of credentials
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if broker not in self.BROKER_KEYS:
            return False, f"Unsupported broker: {broker}"
        
        try:
            # Read existing env vars
            env_vars = self.read_env_file()
            
            # Update broker-specific credentials
            key_mapping = self.BROKER_KEYS[broker]
            for cred_key, env_key in key_mapping.items():
                if cred_key in credentials:
                    env_vars[env_key] = credentials[cred_key]
            
            # Auto-set legacy BROKER_API_KEY and BROKER_API_SECRET for backward compatibility
            if 'BROKER_API_KEY' in credentials and credentials['BROKER_API_KEY']:
                env_vars['BROKER_API_KEY'] = credentials['BROKER_API_KEY']
            
            # For brokers with API_SECRET, also set legacy BROKER_API_SECRET
            if broker in ['dhan', 'fyers']:
                if 'BROKER_API_SECRET' in credentials and credentials['BROKER_API_SECRET']:
                    env_vars['BROKER_API_SECRET'] = credentials['BROKER_API_SECRET']
            
            # Write back to file
            if self.write_env_file(env_vars):
                return True, f"Credentials updated for {broker}"
            else:
                return False, "Failed to write .env file"
        except Exception as e:
            return False, f"Error updating credentials: {str(e)}"
    
    def set_active_broker(self, broker: str) -> Tuple[bool, str]:
        """
        Set the active broker and update legacy environment variables
        
        Args:
            broker: Broker name (angel, dhan, fyers)
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        if broker not in self.BROKER_KEYS:
            return False, f"Unsupported broker: {broker}"
        
        try:
            # Read existing env vars
            env_vars = self.read_env_file()
            
            # Set active broker
            env_vars['ACTIVE_BROKER'] = broker
            
            # Update legacy BROKER_API_KEY and BROKER_API_SECRET
            key_mapping = self.BROKER_KEYS[broker]
            
            # Map to legacy keys
            if 'BROKER_API_KEY' in key_mapping:
                legacy_key = key_mapping['BROKER_API_KEY']
                env_vars['BROKER_API_KEY'] = env_vars.get(legacy_key, '')
            
            if 'BROKER_API_SECRET' in key_mapping:
                legacy_key = key_mapping['BROKER_API_SECRET']
                env_vars['BROKER_API_SECRET'] = env_vars.get(legacy_key, '')
            
            # Write back to file
            if self.write_env_file(env_vars):
                # Reload environment variables
                self._reload_env()
                return True, f"Active broker set to {broker}"
            else:
                return False, "Failed to write .env file"
        except Exception as e:
            return False, f"Error setting active broker: {str(e)}"
    
    def get_active_broker(self) -> Optional[str]:
        """
        Get the currently active broker from .env
        
        Returns:
            Optional[str]: Active broker name or None
        """
        env_vars = self.read_env_file()
        return env_vars.get('ACTIVE_BROKER')
    
    def get_broker_credentials(self, broker: str) -> Optional[Dict[str, str]]:
        """
        Get credentials for a specific broker
        
        Args:
            broker: Broker name (angel, dhan, fyers)
            
        Returns:
            Optional[Dict[str, str]]: Credentials dictionary or None
        """
        if broker not in self.BROKER_KEYS:
            return None
        
        env_vars = self.read_env_file()
        key_mapping = self.BROKER_KEYS[broker]
        
        credentials = {}
        for cred_key, env_key in key_mapping.items():
            value = env_vars.get(env_key, '')
            if value:
                credentials[cred_key] = value
        
        return credentials if credentials else None
    
    def backup_env_file(self) -> Optional[Path]:
        """
        Create a backup of the .env file
        
        Returns:
            Optional[Path]: Path to backup file or None if failed
        """
        if not self.env_path.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / f".env.backup.{timestamp}"
            shutil.copy2(self.env_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Error backing up .env file: {e}")
            return None
    
    def restore_env_file(self, backup_path: Path) -> bool:
        """
        Restore .env file from a backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not backup_path.exists():
            return False
        
        try:
            shutil.copy2(backup_path, self.env_path)
            self._reload_env()
            return True
        except Exception as e:
            print(f"Error restoring .env file: {e}")
            return False
    
    def _reload_env(self):
        """Reload environment variables from .env file"""
        try:
            from dotenv import load_dotenv
            load_dotenv(self.env_path, override=True)
        except ImportError:
            # If python-dotenv not available, manually set env vars
            env_vars = self.read_env_file()
            for key, value in env_vars.items():
                os.environ[key] = value
    
    def has_broker_credentials(self, broker: str) -> bool:
        """
        Check if broker has credentials configured
        
        Args:
            broker: Broker name (angel, dhan, fyers)
            
        Returns:
            bool: True if credentials exist, False otherwise
        """
        credentials = self.get_broker_credentials(broker)
        return credentials is not None and len(credentials) > 0
