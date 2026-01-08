"""
Broker Authentication Helper - Handles runtime authentication

This module provides UI for requesting Client Code, Password, TOTP
and other dynamic credentials during the authentication process.
"""
import streamlit as st
import pandas as pd
from libs.broker_manager import BrokerManager


def request_runtime_auth_and_authenticate(broker: str):
    """
    Request runtime credentials (Client Code, Password, TOTP) and authenticate
    
    Args:
        broker: Broker name (angel, dhan, fyers)
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    broker_mgr = BrokerManager()
    
    # Get stored credentials (only API Key for AngelOne)
    credentials = broker_mgr.get_credentials(broker)
    if not credentials:
        return False, "No API Key found. Please configure broker first."
    
    # Check if broker requires runtime authentication
    broker_info = broker_mgr.SUPPORTED_BROKERS.get(broker, {})
    requires_runtime = broker_info.get('requires_runtime_auth', False)
    
    if requires_runtime and broker == 'angel':
        st.subheader("🔐 AngelOne Authentication")
        st.info("Enter your credentials to authenticate")
        
        with st.form("angel_auth_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                clientcode = st.text_input(
                    "Client Code",
                    placeholder="A12345",
                    help="Your AngelOne User ID/Client Code"
                )
            
            with col2:
                password = st.text_input(
                    "Trading PIN",
                    type="password",
                    max_chars=4,
                    placeholder="••••",
                    help="Your 4-digit Trading PIN"
                )
            
            totp_code = st.text_input(
                "TOTP Code",
                max_chars=6,
                placeholder="000000",
                help="6-digit code from Google Authenticator"
            )
            
            submit = st.form_submit_button("🔓 Authenticate", use_container_width=True)
            
            if submit:
                # Validate inputs
                if not clientcode or len(clientcode) < 3:
                    st.error("Please enter a valid Client Code")
                    return False, "Invalid Client Code"
                
                if not password or len(password) != 4:
                    st.error("Please enter your 4-digit Trading PIN")
                    return False, "Invalid Trading PIN"
                
                if not totp_code or len(totp_code) != 6:
                    st.error("Please enter a valid 6-digit TOTP code")
                    return False, "Invalid TOTP code"
                
                # Add runtime credentials to stored credentials
                credentials['clientcode'] = clientcode
                credentials['password'] = password
                credentials['totp'] = totp_code
                
                with st.spinner("Authenticating with AngelOne..."):
                    success, msg = broker_mgr.validate_credentials(broker, credentials)
                    
                    if success:
                        st.success(f"✅ {msg}")
                        st.balloons()
                        # Store auth token in session state for this session
                        st.session_state['broker_authenticated'] = True
                        st.session_state['broker_auth_time'] = pd.Timestamp.now()
                        return True, msg
                    else:
                        st.error(f"❌ {msg}")
                        return False, msg
    
    return False, "Runtime authentication required but not provided"


def show_broker_login_page():
    """Show broker login page with runtime credential input"""
    st.title("🔐 Broker Authentication")
    
    broker_mgr = BrokerManager()
    active_broker = broker_mgr.get_active_broker()
    
    if not active_broker:
        st.warning("⚠️ No active broker configured")
        st.info("Please go to Broker Configuration page to set up your broker")
        return
    
    broker_info = broker_mgr.SUPPORTED_BROKERS.get(active_broker, {})
    st.write(f"**Active Broker:** {broker_info.get('name', active_broker)}")
    
    # Check if API Key is configured
    credentials = broker_mgr.get_credentials(active_broker)
    if not credentials:
        st.error("❌ No API Key configured for this broker")
        st.info("Please go to Broker Configuration page to add your API Key")
        return
    
    # Show credential status
    st.success(f"✅ API Key configured in .env file")
    
    # Request runtime authentication if needed
    if broker_info.get('requires_runtime_auth'):
        request_runtime_auth_and_authenticate(active_broker)
    else:
        st.info("This broker does not require runtime authentication")


if __name__ == "__main__":
    show_broker_login_page()
