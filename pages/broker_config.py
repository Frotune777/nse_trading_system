"""
Broker Configuration Page for Dashboard
Allows users to select broker, configure credentials, and validate authentication
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from libs.broker_manager import BrokerManager

def page_broker_config():
    """Broker Configuration Page"""
    st.title("🔌 Broker Configuration")
    st.markdown("Configure your broker credentials for live trading integration.")
    
    broker_mgr = BrokerManager()
    
    # Display configured brokers
    st.subheader("Configured Brokers")
    configured = broker_mgr.list_configured_brokers()
    
    # Also check for brokers with credentials in .env but not in database
    all_brokers = set(broker_mgr.SUPPORTED_BROKERS.keys())
    configured_broker_names = {b['broker'] for b in configured}
    
    # Add brokers from .env that aren't in database
    for broker in all_brokers:
        if broker not in configured_broker_names:
            if broker_mgr.env_manager.has_broker_credentials(broker):
                configured.append({
                    'broker': broker,
                    'name': broker_mgr.SUPPORTED_BROKERS[broker]['name'],
                    'is_active': False,
                    'validation_status': 'pending',
                    'last_validated': None,
                    'updated_at': None,
                    'has_credentials': True
                })
    
    if configured:
        for broker_info in configured:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                # Status icon based on validation
                if broker_info['is_active']:
                    if broker_info.get('validation_status') == 'valid':
                        status_icon = "🟢"
                        status_text = "Active & Valid"
                    elif broker_info.get('validation_status') == 'invalid':
                        status_icon = "🔴"
                        status_text = "Active but Invalid"
                    else:
                        status_icon = "🟡"
                        status_text = "Active (Not Validated)"
                else:
                    if broker_info.get('has_credentials'):
                        status_icon = "⚪"
                        status_text = "Configured"
                    else:
                        status_icon = "⚫"
                        status_text = "No Credentials"
                
                st.write(f"{status_icon} **{broker_info['name']}** ({broker_info['broker']})")
                st.caption(status_text)
            
            with col2:
                if broker_info.get('has_credentials'):
                    st.success("✓ In .env")
                else:
                    st.error("✗ Missing")
            
            with col3:
                if broker_info['last_validated']:
                    st.caption(f"Validated: {broker_info['last_validated'][:10]}")
                else:
                    st.caption("Not validated")
            
            with col4:
                if not broker_info['is_active'] and broker_info.get('has_credentials'):
                    if st.button(f"Activate", key=f"activate_{broker_info['broker']}"):
                        success, msg = broker_mgr.set_active_broker(broker_info['broker'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
    else:
        st.info("No brokers configured yet. Add one below.")
    
    st.divider()
    
    # Add/Update Broker Credentials
    st.subheader("Add/Update Broker")
    
    broker_choice = st.selectbox(
        "Select Broker",
        options=list(broker_mgr.SUPPORTED_BROKERS.keys()),
        format_func=lambda x: broker_mgr.SUPPORTED_BROKERS[x]['name']
    )
    
    broker_info = broker_mgr.SUPPORTED_BROKERS[broker_choice]
    st.info(f"**{broker_info['name']}** - {broker_info['description']}")
    
    # Load existing credentials from .env
    existing_creds = broker_mgr.get_credentials(broker_choice) or {}
    
    # Show current status
    status = broker_mgr.get_broker_status(broker_choice)
    if status.get('has_credentials'):
        if status.get('validation_status') == 'valid':
            st.success(f"✅ Credentials configured and validated")
        elif status.get('validation_status') == 'invalid':
            st.error(f"❌ Credentials configured but invalid: {status.get('error_message')}")
        else:
            st.warning(f"⚠️ Credentials configured but not validated")
    else:
        st.info("ℹ️ No credentials configured for this broker")
    
    # Credential input form
    with st.form(f"broker_form_{broker_choice}"):
        st.markdown("### Enter Credentials")
        
        credentials = {}
        
        for cred_name in broker_info['credentials']:
            # Determine input type - API Keys should also be masked
            is_secret = any(keyword in cred_name.lower() for keyword in ['secret', 'password', 'totp', 'pin', 'key'])
            input_type = "password" if is_secret else "default"
            
            # Get existing value (show masked for secrets)
            default_value = existing_creds.get(cred_name, "")
            if is_secret and default_value:
                # Show that credential exists but don't reveal it
                placeholder = "••••••••" if default_value else ""
            else:
                placeholder = default_value
            
            # Create input field
            credentials[cred_name] = st.text_input(
                cred_name,
                value="" if is_secret else default_value,
                type=input_type,
                placeholder=placeholder if is_secret else f"Enter your {cred_name}",
                help=f"Enter your {cred_name}"
            )
            
            # If secret field is empty, use existing value
            if is_secret and not credentials[cred_name] and default_value:
                credentials[cred_name] = default_value
        
        col1, col2, col3 = st.columns(3)
        with col1:
            save_btn = st.form_submit_button("💾 Save Credentials", use_container_width=True)
        with col2:
            validate_btn = st.form_submit_button("✓ Save & Validate", use_container_width=True)
        with col3:
            activate_btn = st.form_submit_button("🚀 Save, Validate & Activate", use_container_width=True)
    
    # Handle form submission
    if save_btn or validate_btn or activate_btn:
        # Save credentials
        success, msg = broker_mgr.save_credentials(broker_choice, credentials)
        
        if success:
            st.success(msg)
            
            # Validate if requested (and if broker supports it)
            if validate_btn or activate_btn:
                # For AngelOne, skip validation if only API Key provided
                # (full validation requires Client Code, Password, TOTP at runtime)
                if broker_choice == 'angel':
                    st.info("ℹ️ AngelOne validation requires Client Code, Password, and TOTP")
                    st.info("These will be requested when you authenticate for trading")
                    
                    # Mark as pending validation
                    try:
                        import sqlite3
                        with sqlite3.connect(broker_mgr.db_path) as conn:
                            conn.execute("""
                                INSERT OR REPLACE INTO broker_config 
                                (broker_name, validation_status, updated_at)
                                VALUES (?, 'pending', datetime('now'))
                            """, (broker_choice,))
                    except Exception:
                        pass
                    
                    # Activate if requested
                    if activate_btn:
                        success, activate_msg = broker_mgr.set_active_broker(broker_choice)
                        if success:
                            st.success(f"🚀 {activate_msg}")
                            st.info("💡 Use 'Broker Authentication' page to login when needed")
                            st.balloons()
                        else:
                            st.error(f"Failed to activate: {activate_msg}")
                else:
                    # For other brokers, validate normally
                    with st.spinner("Validating credentials..."):
                        valid, validation_msg = broker_mgr.validate_credentials(broker_choice, credentials)
                        
                        if valid:
                            st.success(f"✅ {validation_msg}")
                            
                            # Activate if requested
                            if activate_btn:
                                success, activate_msg = broker_mgr.set_active_broker(broker_choice)
                                if success:
                                    st.success(f"🚀 {activate_msg}")
                                    st.balloons()
                                else:
                                    st.error(f"Failed to activate: {activate_msg}")
                        else:
                            st.error(f"❌ Validation failed: {validation_msg}")
        else:
            st.error(f"Failed to save: {msg}")
    
    # Authentication Flow Instructions
    with st.expander("📖 Authentication Guide"):
        st.markdown(f"""
        ### {broker_info['name']} Authentication
        
        **Required Credentials:**
        {chr(10).join([f'- `{cred}`' for cred in broker_info['credentials']])}
        
        **Steps:**
        1. Obtain API credentials from your broker's developer portal
        2. Enter all required fields above
        3. Click "Save & Validate" to test the connection
        4. Once validated, click "Activate" to use this broker for live trading
        
        **Security Note:** Credentials are stored encrypted in the local database.
        """)

if __name__ == "__main__":
    page_broker_config()
