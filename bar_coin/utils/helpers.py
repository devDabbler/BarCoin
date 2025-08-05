"""
Utility helper functions for BAR-COIN application.
"""

import re
import hashlib
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from bar_coin.config.settings import PHILIPPINE_COINS, format_peso, get_coin_name

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def validate_username(username: str) -> bool:
    """Validate username format."""
    if len(username) < 3:
        return False
    
    if len(username) > 20:
        return False
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    
    return True

def validate_password(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        return False
    
    if not re.search(r'[A-Z]', password):
        return False
    
    if not re.search(r'[a-z]', password):
        return False
    
    if not re.search(r'\d', password):
        return False
    
    # Remove special character requirement for now
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     return False
    
    return True

def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:  # Handle empty string
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def calculate_total_value(coin_counts: Dict[float, int]) -> float:
    """Calculate total value from coin counts."""
    total = 0.0
    for denomination, count in coin_counts.items():
        total += denomination * count
    return total

def calculate_total_coins(coin_counts: Dict[float, int]) -> int:
    """Calculate total number of coins."""
    return sum(coin_counts.values())

def format_coin_counts(coin_counts: Dict[float, int]) -> List[Dict[str, Any]]:
    """Format coin counts for display."""
    formatted = []
    for denomination in sorted(PHILIPPINE_COINS.keys()):
        count = coin_counts.get(denomination, 0)
        value = denomination * count
        formatted.append({
            'denomination': denomination,
            'name': get_coin_name(denomination),
            'count': count,
            'value': value,
            'formatted_value': format_peso(value)
        })
    return formatted

def get_coin_statistics(coin_counts: Dict[float, int]) -> Dict[str, Any]:
    """Get comprehensive coin statistics."""
    total_coins = calculate_total_coins(coin_counts)
    total_value = calculate_total_value(coin_counts)
    
    # Find most and least common denominations
    denominations_with_counts = [(d, c) for d, c in coin_counts.items() if c > 0]
    
    if denominations_with_counts:
        most_common = max(denominations_with_counts, key=lambda x: x[1])
        least_common = min(denominations_with_counts, key=lambda x: x[1])
        highest_denomination = max(coin_counts.keys())
        lowest_denomination = min(coin_counts.keys())
    else:
        most_common = least_common = (0.0, 0)
        highest_denomination = lowest_denomination = 0.0
    
    return {
        'total_coins': total_coins,
        'total_value': total_value,
        'formatted_total_value': format_peso(total_value),
        'denominations': len([c for c in coin_counts.values() if c > 0]),
        'unique_denominations': len([c for c in coin_counts.values() if c > 0]),
        'highest_denomination': highest_denomination,
        'lowest_denomination': lowest_denomination,
        'most_common_denomination': most_common[0],
        'most_common_count': most_common[1],
        'least_common_denomination': least_common[0],
        'least_common_count': least_common[1],
        'average_value_per_coin': total_value / total_coins if total_coins > 0 else 0
    }

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if minutes == 1:
            return f"1 minute {remaining_seconds} seconds"
        else:
            return f"{minutes} minutes {remaining_seconds} seconds"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def format_timestamp(timestamp) -> str:
    """Format timestamp for display."""
    if isinstance(timestamp, datetime):
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    try:
        dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)

def generate_session_id() -> str:
    """Generate a unique session identifier."""
    import time
    import random
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_num = random.randint(1000, 9999)
    random_suffix = hashlib.md5(f"{time.time()}{random_num}".encode()).hexdigest()[:8]
    return f"session{timestamp}{random_num}{random_suffix}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    if not filename:
        return "untitled"
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*@#$%]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + '.' + ext if ext else name[:100]
    return filename

def create_export_filename(prefix: str, extension: str) -> str:
    """Create a filename for exports."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return sanitize_filename(f"{prefix}_export_{timestamp}.{extension}")

def parse_serial_data(data: str) -> Optional[Dict[str, Any]]:
    """Parse serial data from hardware."""
    try:
        import json
        parsed = json.loads(data.strip())
        
        # Validate required fields
        required_fields = ['type', 'denomination', 'timestamp']
        if not all(field in parsed for field in required_fields):
            logger.warning(f"Missing required fields in serial data: {data}")
            return None
        
        # Validate denomination
        denomination = float(parsed['denomination'])
        if denomination not in PHILIPPINE_COINS:
            logger.warning(f"Invalid denomination in serial data: {denomination}")
            return None
        
        return parsed
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in serial data: {data}")
        return None
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing serial data: {e}")
        return None

def validate_hardware_message(message: Dict[str, Any]) -> bool:
    """Validate hardware message format."""
    if not isinstance(message, dict):
        return False
    
    if 'type' not in message or message['type'] not in ['coin', 'coin_detected']:
        return False
    
    if 'denomination' not in message:
        return False
    
    try:
        denomination = float(message['denomination'])
        if denomination not in PHILIPPINE_COINS:
            return False
    except (ValueError, TypeError):
        return False
    
    return True

def get_hardware_status_color(status: str) -> str:
    """Get color for hardware status display."""
    status_colors = {
        'connected': 'green',
        'disconnected': 'red',
        'connecting': 'orange',
        'error': 'orange',
        'warning': 'yellow',
        'processing': 'blue'
    }
    return status_colors.get(status.lower(), 'gray')

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    if i == 0:  # Bytes
        return f"{size_bytes:.0f} {size_names[i]}"
    else:  # KB, MB, GB
        return f"{size_bytes:.1f} {size_names[i]}"

def get_mobile_breakpoint() -> int:
    """Get mobile breakpoint for responsive design."""
    return 768

def is_mobile_viewport(width: int = None) -> bool:
    """Check if current viewport is mobile (simplified check)."""
    if width is None:
        return False
    return width <= get_mobile_breakpoint()

def generate_qr_code_data(session_data: Dict[str, Any]) -> str:
    """Generate QR code data for session summary."""
    if isinstance(session_data, dict):
        data = session_data.copy()
    else:
        data = {
            'session_id': str(session_data),
            'total_value': 0,
            'timestamp': datetime.now().isoformat(),
            'app': 'BAR-COIN'
        }
    
    # Ensure timestamp is present
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
    
    # Ensure app identifier is present
    if 'app' not in data:
        data['app'] = 'BAR-COIN'
    
    import json
    return json.dumps(data)

def validate_session_data(session_data: Dict[str, Any]) -> bool:
    """Validate session data before saving."""
    # Check for required top-level sections
    required_sections = ['session_info', 'coin_counts', 'hardware_logs']
    for section in required_sections:
        if section not in session_data:
            return False
    
    # Validate session_info
    session_info = session_data['session_info']
    if not isinstance(session_info, dict):
        return False
    
    # Check for required fields in session_info
    if 'id' not in session_info:
        return False
    
    # Validate coin_counts structure
    coin_counts = session_data['coin_counts']
    if not isinstance(coin_counts, list):
        return False
    
    # Validate hardware_logs structure
    hardware_logs = session_data['hardware_logs']
    if not isinstance(hardware_logs, list):
        return False
    
    # Additional validation for coin_counts items
    for item in coin_counts:
        if not isinstance(item, dict):
            return False
        if 'denomination' not in item or 'count' not in item:
            return False
    
    return True

def calculate_processing_speed(coin_counts: Dict[float, int], duration_seconds: int) -> float:
    """Calculate coins per second processing speed."""
    total_coins = sum(coin_counts.values())
    if total_coins == 0 or duration_seconds == 0:
        return 0.0
    
    return total_coins / duration_seconds 