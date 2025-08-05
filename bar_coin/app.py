"""
Main Streamlit application for BAR-COIN.
"""

import streamlit as st
import time
from datetime import datetime
import logging

from bar_coin.config.settings import STREAMLIT_CONFIG, COLORS, UI_CONFIG
from bar_coin.components.auth import render_login_page, check_authentication, render_authentication_status
from bar_coin.components.dashboard import render_dashboard, update_coin_counts
from bar_coin.hardware.coin_counter import coin_counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application function."""
    
    # Page configuration
    st.set_page_config(
        page_title=STREAMLIT_CONFIG["page_title"],
        page_icon=STREAMLIT_CONFIG["page_icon"],
        layout=STREAMLIT_CONFIG["layout"],
        initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(180deg, #f0f2f6 0%, #ffffff 100%);
    }
    .stButton > button {
        background-color: #1E90FF;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #4169E1;
        transform: translateY(-2px);
    }
    .metric-container {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-connected { background-color: #32CD32; }
    .status-disconnected { background-color: #FF6347; }
    .status-connecting { background-color: #FFA500; }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .stButton > button {
            padding: 8px 20px;
            font-size: 14px;
        }
        .metric-container {
            padding: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Check authentication
    user = check_authentication()
    
    if not user:
        # Show login page
        authenticated_user = render_login_page()
        if authenticated_user:
            st.rerun()
        return
    
    # User is authenticated - show dashboard
    render_authentication_status()
    
    # Initialize hardware if not already done
    if 'hardware_initialized' not in st.session_state:
        st.session_state.hardware_initialized = True
        # Initialize hardware in background
        try:
            if coin_counter.mock_mode:
                coin_counter.connect()
        except Exception as e:
            logger.error(f"Hardware initialization error: {e}")
    
    # Auto-refresh for real-time updates
    if st.session_state.get('hardware_connected', False):
        # Update coin counts from hardware
        update_coin_counts()
        
        # Auto-refresh every 100ms for real-time updates
        time.sleep(UI_CONFIG["refresh_rate"] / 1000)
        st.rerun()
    
    # Render main dashboard
    render_dashboard(user)

def render_sidebar():
    """Render sidebar content."""
    with st.sidebar:
        st.title("🪙 BAR-COIN")
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        page = st.selectbox(
            "Select Page",
            ["Dashboard", "Settings", "Help"],
            index=0
        )
        
        # Hardware status
        st.markdown("### Hardware Status")
        status = coin_counter.get_status()
        
        if status['connected']:
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")
        
        if status['mock_mode']:
            st.info("🧪 Mock Mode")
        else:
            st.info("🔧 Hardware Mode")
        
        # Quick stats
        if 'coin_counts' in st.session_state:
            total_coins = sum(st.session_state.coin_counts.values())
            total_value = sum(denom * count for denom, count in st.session_state.coin_counts.items())
            
            st.markdown("### Quick Stats")
            st.metric("Total Coins", f"{total_coins:,}")
            st.metric("Total Value", f"₱{total_value:,.2f}")
        
        # Settings
        st.markdown("### Settings")
        if st.button("⚙️ Settings"):
            st.info("Settings page - coming soon")
        
        if st.button("❓ Help"):
            st.info("Help page - coming soon")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {e}", exc_info=True) 