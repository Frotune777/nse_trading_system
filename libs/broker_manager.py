"""
Broker Manager - Handles broker selection, credential validation, and authentication
"""
import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Tuple
import json
from datetime import datetime

from libs.broker_env_manager import BrokerEnvManager
from libs.broker_validator import BrokerValidator

PROJECT_ROOT = Path(__file__).parent.parent

class BrokerManager:
    """Manages broker credentials and authentication"""
    
    SUPPORTED_BROKERS = {
        'angel': {
            'name': 'AngelOne',
            'credentials': ['BROKER_API_KEY'],  # Only API Key stored
            'description': 'AngelOne (SmartAPI)',
            'requires_runtime_auth': True,  # Client Code, Password, TOTP requested during auth
            'runtime_credentials': ['clientcode', 'password', 'totp']
        },
        'dhan': {
            'name': 'Dhan',
            'credentials': ['BROKER_API_KEY', 'BROKER_API_SECRET', 'dhan_client_id'],
            'description': 'Dhan Securities'
        },
        'fyers': {
            'name': 'Fyers',
            'credentials': ['BROKER_API_KEY', 'BROKER_API_SECRET'],
            'description': 'Fyers Securities'
        }
    }
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or PROJECT_ROOT / "data" / "trading.db"
        self.env_manager = BrokerEnvManager()
        self.validator = BrokerValidator()
        self._init_db()
    
    def _init_db(self):
        """Initialize broker_config table (metadata only, credentials in .env)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS broker_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    broker_name TEXT UNIQUE NOT NULL,
                    is_active INTEGER DEFAULT 0,
                    validation_status TEXT DEFAULT 'pending',
                    last_validated TEXT,
                    last_connection_test TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_credentials(self, broker: str, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """Save broker credentials to .env file"""
        if broker not in self.SUPPORTED_BROKERS:
            return False, f"Unsupported broker: {broker}"
        
        # Validate credential format
        is_valid, errors = self.validator.validate_credential_format(broker, credentials)
        if not is_valid:
            return False, "\n".join(errors)
        
        # Save to .env file
        success, msg = self.env_manager.update_broker_credentials(broker, credentials)
        if not success:
            return False, msg
        
        # Update database metadata
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO broker_config 
                    (broker_name, validation_status, updated_at)
                    VALUES (?, 'pending', datetime('now'))
                """, (broker,))
            return True, "Credentials saved successfully to .env file"
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def get_credentials(self, broker: str) -> Optional[Dict[str, str]]:
        """Retrieve broker credentials from .env file"""
        return self.env_manager.get_broker_credentials(broker)
    
    def get_active_broker(self) -> Optional[str]:
        """Get the currently active broker from .env and database"""
        # First check .env file
        active_broker = self.env_manager.get_active_broker()
        if active_broker:
            return active_broker
        
        # Fallback to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT broker_name FROM broker_config WHERE is_active = 1"
                )
                row = cursor.fetchone()
                if row:
                    return row[0]
        except Exception:
            pass
        return None
    
    def set_active_broker(self, broker: str) -> Tuple[bool, str]:
        """Set a broker as active in both .env and database"""
        if broker not in self.SUPPORTED_BROKERS:
            return False, f"Unsupported broker: {broker}"
        
        # Update .env file
        success, msg = self.env_manager.set_active_broker(broker)
        if not success:
            return False, msg
        
        # Update database
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Deactivate all
                conn.execute("UPDATE broker_config SET is_active = 0")
                # Activate selected
                conn.execute(
                    "UPDATE broker_config SET is_active = 1 WHERE broker_name = ?",
                    (broker,)
                )
            return True, f"{self.SUPPORTED_BROKERS[broker]['name']} activated"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def validate_credentials(self, broker: str, credentials: Dict[str, str]) -> Tuple[bool, str]:
        """Validate broker credentials by attempting authentication"""
        if broker not in self.SUPPORTED_BROKERS:
            return False, "Unsupported broker"
        
        try:
            # Set environment variables temporarily
            for key, value in credentials.items():
                os.environ[key] = value
            
            validation_result = False
            validation_msg = ""
            
            # Import broker-specific auth module
            if broker == 'angel':
                from broker.angel.api.auth_api import authenticate_broker
                auth_token, feed_token, error = authenticate_broker(
                    credentials.get('clientcode'),
                    credentials.get('password'),
                    credentials.get('totp')
                )
                if auth_token:
                    validation_result = True
                    validation_msg = "Authentication successful"
                else:
                    validation_msg = error or "Authentication failed"
            
            elif broker == 'dhan':
                from broker.dhan.api.auth_api import generate_consent
                consent_id, error = generate_consent(credentials.get('dhan_client_id'))
                if consent_id:
                    validation_result = True
                    validation_msg = f"Consent generated. Complete OAuth flow with: {consent_id}"
                else:
                    validation_msg = error or "Failed to generate consent"
            
            elif broker == 'fyers':
                # Fyers requires OAuth flow, can't validate without request_token
                # Just check if credentials are set
                if credentials.get('BROKER_API_KEY') and credentials.get('BROKER_API_SECRET'):
                    validation_result = True
                    validation_msg = "Credentials format valid (OAuth flow required for full auth)"
                else:
                    validation_msg = "Missing API key or secret"
            
            # Update database with validation status
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE broker_config 
                        SET validation_status = ?,
                            last_validated = datetime('now'),
                            error_message = ?,
                            updated_at = datetime('now')
                        WHERE broker_name = ?
                    """, ('valid' if validation_result else 'invalid', 
                          None if validation_result else validation_msg,
                          broker))
            except Exception as db_error:
                print(f"Database update error: {db_error}")
            
            return validation_result, validation_msg
            
        except ImportError as e:
            return False, f"Broker module not found: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"
        finally:
            # Clean up environment
            for key in credentials.keys():
                os.environ.pop(key, None)
    
    def list_configured_brokers(self) -> list:
        """List all configured brokers with status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT broker_name, is_active, validation_status, last_validated, updated_at 
                    FROM broker_config
                """)
                return [
                    {
                        'broker': row[0],
                        'name': self.SUPPORTED_BROKERS.get(row[0], {}).get('name', row[0]),
                        'is_active': bool(row[1]),
                        'validation_status': row[2],
                        'last_validated': row[3],
                        'updated_at': row[4],
                        'has_credentials': self.env_manager.has_broker_credentials(row[0])
                    }
                    for row in cursor.fetchall()
                ]
        except Exception:
            return []
    
    def check_active_broker_credentials(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Check if active broker has valid credentials in .env
        
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (has_credentials, broker_name, error_message)
        """
        active_broker = self.get_active_broker()
        
        if not active_broker:
            return False, None, "No active broker configured"
        
        # Check if credentials exist in .env
        if not self.env_manager.has_broker_credentials(active_broker):
            return False, active_broker, f"No credentials found for {active_broker} in .env file"
        
        # Check validation status in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT validation_status, error_message 
                    FROM broker_config 
                    WHERE broker_name = ?
                """, (active_broker,))
                row = cursor.fetchone()
                
                if row:
                    status, error = row
                    if status == 'invalid':
                        return False, active_broker, error or "Credentials validation failed"
                    elif status == 'pending':
                        return True, active_broker, "Credentials not yet validated"
        except Exception as e:
            print(f"Database error: {e}")
        
        return True, active_broker, None
    
    def get_broker_status(self, broker: str) -> Dict:
        """Get comprehensive broker status
        
        Returns:
            Dict with status information
        """
        if broker not in self.SUPPORTED_BROKERS:
            return {'error': 'Unsupported broker'}
        
        has_credentials = self.env_manager.has_broker_credentials(broker)
        is_active = self.get_active_broker() == broker
        
        status = {
            'broker': broker,
            'name': self.SUPPORTED_BROKERS[broker]['name'],
            'configured': has_credentials,
            'has_credentials': has_credentials,
            'is_active': is_active,
            'validation_status': 'unknown',
            'last_validated': None,
            'error_message': None
        }
        
        # Get database info
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT validation_status, last_validated, error_message 
                    FROM broker_config 
                    WHERE broker_name = ?
                """, (broker,))
                row = cursor.fetchone()
                
                if row:
                    status['validation_status'] = row[0]
                    status['last_validated'] = row[1]
                    status['error_message'] = row[2]
        except Exception as e:
            status['error'] = str(e)
        
        return status
