"""
Authentication component for BAR-COIN Streamlit application.
"""

import streamlit as st
import bcrypt
from typing import Optional, Dict, Any
from datetime import datetime

from bar_coin.utils.database import db
from bar_coin.utils.helpers import hash_password, verify_password, validate_username, validate_password, validate_email
from bar_coin.config.settings import COLORS, FONTS

def render_login_page() -> Optional[Dict[str, Any]]:
    """Render the login page and return user data if authenticated."""
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #1E90FF 0%, #4169E1 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .login-card {
        background: white;
        border-radius: 15px;
        padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
        max-width: 400px;
        width: 100%;
    }
    .logo {
        font-size: 48px;
        margin-bottom: 10px;
    }
    .brand-name {
        font-size: 32px;
        font-weight: bold;
        color: #1E90FF;
        margin-bottom: 5px;
    }
    .tagline {
        color: #666;
        margin-bottom: 30px;
    }
    .stButton > button {
        background-color: #1E90FF;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #4169E1;
        transform: translateY(-2px);
    }
    .secondary-button {
        background-color: transparent !important;
        color: #1E90FF !important;
        border: 2px solid #1E90FF !important;
    }
    .secondary-button:hover {
        background-color: #1E90FF !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main container
    with st.container():
        st.markdown("""
        <div class="login-container">
            <div class="login-card">
                <div class="logo">🪙</div>
                <div class="brand-name">BAR-COIN</div>
                <div class="tagline">Mobile-base Automated Coin Counter</div>
        """, unsafe_allow_html=True)
        
        # Initialize session state
        if 'show_register' not in st.session_state:
            st.session_state.show_register = False
        
        if st.session_state.show_register:
            return render_register_form()
        else:
            return render_login_form()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

def render_login_form() -> Optional[Dict[str, Any]]:
    """Render the login form."""
    
    st.markdown("### Login")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            login_submitted = st.form_submit_button("Login", use_container_width=True)
        
        with col2:
            if st.form_submit_button("Register", use_container_width=True):
                st.session_state.show_register = True
                st.rerun()
        
        if login_submitted:
            return handle_login(username, password)
    
    return None

def render_register_form() -> Optional[Dict[str, Any]]:
    """Render the registration form."""
    
    st.markdown("### Register")
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Choose a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            register_submitted = st.form_submit_button("Register", use_container_width=True)
        
        with col2:
            if st.form_submit_button("Back to Login", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()
        
        if register_submitted:
            return handle_register(username, email, password, confirm_password)
    
    return None

def handle_login(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Handle login authentication."""
    if not username or not password:
        st.error("Please enter both username and password")
        return None
    
    # Get user from database
    user = db.get_user_by_username(username)
    
    if not user:
        st.error("Invalid username or password")
        return None
    
    # Verify password
    if not verify_password(password, user['password_hash']):
        st.error("Invalid username or password")
        return None
    
    # Update last login
    db.update_last_login(user['id'])
    
    # Store user data in session state
    st.session_state.user = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'login_time': datetime.now()
    }
    
    st.success(f"Welcome back, {user['username']}!")
    return st.session_state.user

def handle_register(username: str, email: str, password: str, confirm_password: str) -> Optional[Dict[str, Any]]:
    """Handle user registration."""
    # Validate inputs
    if not username or not email or not password or not confirm_password:
        st.error("Please fill in all fields")
        return None
    
    # Validate username
    is_valid_username, username_error = validate_username(username)
    if not is_valid_username:
        st.error(username_error)
        return None
    
    # Validate email
    is_valid_email, email_error = validate_email(email)
    if not is_valid_email:
        st.error(email_error)
        return None
    
    # Validate password
    is_valid_password, password_error = validate_password(password)
    if not is_valid_password:
        st.error(password_error)
        return None
    
    # Check password confirmation
    if password != confirm_password:
        st.error("Passwords do not match")
        return None
    
    # Check if username already exists
    existing_user = db.get_user_by_username(username)
    if existing_user:
        st.error("Username already exists")
        return None
    
    try:
        # Hash password and create user
        password_hash = hash_password(password)
        user_id = db.create_user(username, password_hash, email)
        
        st.success("Registration successful! Please login.")
        st.session_state.show_register = False
        st.rerun()
        
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
    
    return None

def check_authentication() -> Optional[Dict[str, Any]]:
    """Check if user is authenticated."""
    if 'user' not in st.session_state:
        return None
    
    user = st.session_state.user
    
    # Check session timeout (1 hour)
    if 'login_time' in user:
        login_time = user['login_time']
        if isinstance(login_time, str):
            login_time = datetime.fromisoformat(login_time)
        
        elapsed = datetime.now() - login_time
        if elapsed.total_seconds() > 3600:  # 1 hour
            logout()
            return None
    
    return user

def logout():
    """Logout the current user."""
    if 'user' in st.session_state:
        del st.session_state.user
    
    # Clear other session state
    keys_to_clear = ['current_session_id', 'coin_counts', 'hardware_connected']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Logged out successfully")
    st.rerun()

def render_user_info(user: Dict[str, Any]):
    """Render user information in sidebar."""
    with st.sidebar:
        st.markdown("### User Info")
        st.write(f"**Username:** {user['username']}")
        if user.get('email'):
            st.write(f"**Email:** {user['email']}")
        
        if st.button("Logout", type="secondary"):
            logout()

def render_authentication_status():
    """Render authentication status in sidebar."""
    user = check_authentication()
    
    if user:
        render_user_info(user)
        return user
    else:
        with st.sidebar:
            st.warning("Please login to continue")
            if st.button("Login"):
                st.rerun()
        return None 