"""
Configuration settings for BAR-COIN application.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Philippine coin denominations and properties
PHILIPPINE_COINS = {
    0.01: {"name": "1 sentimo", "diameter": 15.0, "weight": 1.9, "material": "copper-plated steel"},
    0.05: {"name": "5 sentimo", "diameter": 16.7, "weight": 1.9, "material": "copper-plated steel"},
    0.10: {"name": "10 sentimo", "diameter": 17.0, "weight": 2.5, "material": "steel"},
    0.25: {"name": "25 sentimo", "diameter": 20.0, "weight": 3.8, "material": "brass"},
    1.00: {"name": "1 piso", "diameter": 24.0, "weight": 6.1, "material": "nickel-plated steel"},
    5.00: {"name": "5 piso", "diameter": 27.0, "weight": 7.7, "material": "nickel-plated steel"},
    10.00: {"name": "10 piso", "diameter": 26.5, "weight": 8.0, "material": "bi-metallic"},
    20.00: {"name": "20 piso", "diameter": 30.0, "weight": 11.5, "material": "bi-metallic"}
}

# Color scheme
COLORS = {
    "PRIMARY_BLUE": "#1E90FF",
    "SECONDARY_BLUE": "#4169E1",
    "WHITE": "#FFFFFF",
    "GRAY": "#F0F0F0",
    "SUCCESS_GREEN": "#32CD32",
    "ERROR_RED": "#FF6347",
    "WARNING_ORANGE": "#FFA500"
}

# Font specifications
FONTS = {
    "HEADER_FONT": "Arial, sans-serif",
    "BODY_FONT": "Helvetica, sans-serif"
}

# Database configuration
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/coins.db"),
    "echo": os.getenv("DEBUG", "True").lower() == "true"
}

# Hardware configuration
HARDWARE_CONFIG = {
    "serial_port": os.getenv("SERIAL_PORT", "COM3"),
    "baud_rate": int(os.getenv("BAUD_RATE", "9600")),
    "timeout": 1,
    "mock_mode": os.getenv("MOCK_HARDWARE", "True").lower() == "true"
}

# Application settings
APP_CONFIG = {
    "debug": os.getenv("DEBUG", "True").lower() == "true",
    "secret_key": os.getenv("SECRET_KEY", "bar-coin-secret-key-change-in-production"),
    "session_timeout": 3600,  # 1 hour
    "max_upload_size": 10 * 1024 * 1024,  # 10MB
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    "page_title": "BAR-COIN",
    "page_icon": "🪙",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# UI Configuration
UI_CONFIG = {
    "refresh_rate": 100,  # milliseconds
    "animation_duration": 500,  # milliseconds
    "max_display_coins": 1000,
    "chart_height": 400,
    "mobile_breakpoint": 768
}

# Export configuration
EXPORT_CONFIG = {
    "csv_encoding": "utf-8",
    "pdf_orientation": "portrait",
    "max_rows_per_export": 10000
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "logs" / "bar_coin.log"
}

# Security configuration
SECURITY_CONFIG = {
    "password_min_length": 8,
    "password_require_special": True,
    "max_login_attempts": 5,
    "lockout_duration": 300,  # 5 minutes
    "session_secure": True
}

# Performance configuration
PERFORMANCE_CONFIG = {
    "cache_ttl": 300,  # 5 minutes
    "batch_size": 100,
    "max_connections": 10,
    "connection_timeout": 30
}

def get_config() -> Dict[str, Any]:
    """Get all configuration settings as a dictionary."""
    return {
        "philippine_coins": PHILIPPINE_COINS,
        "colors": COLORS,
        "fonts": FONTS,
        "database": DATABASE_CONFIG,
        "hardware": HARDWARE_CONFIG,
        "app": APP_CONFIG,
        "streamlit": STREAMLIT_CONFIG,
        "ui": UI_CONFIG,
        "export": EXPORT_CONFIG,
        "logging": LOGGING_CONFIG,
        "security": SECURITY_CONFIG,
        "performance": PERFORMANCE_CONFIG
    }

def format_peso(amount: float) -> str:
    """Format amount as Philippine Peso currency."""
    return f"₱{amount:,.2f}"

def get_coin_name(denomination: float) -> str:
    """Get the name of a coin denomination."""
    return PHILIPPINE_COINS.get(denomination, {}).get("name", f"₱{denomination}")

def is_valid_denomination(denomination: float) -> bool:
    """Check if a denomination is valid for Philippine coins."""
    return denomination in PHILIPPINE_COINS 