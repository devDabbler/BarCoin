#!/usr/bin/env python3
"""
Create default admin user for BAR-COIN application.
This script creates a test admin user for development and testing purposes.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from bar_coin.utils.database import db
from bar_coin.utils.helpers import hash_password

def create_admin_user():
    """Create a default admin user."""
    try:
        # Check if admin user already exists
        existing_user = db.get_user_by_username("admin")
        if existing_user:
            print("✓ Admin user already exists")
            print("Username: admin")
            print("Password: admin123")
            return
        
        # Create admin user
        username = "admin"
        password = "admin123"
        email = "admin@barcoin.local"
        
        user_id = db.create_user(username, password, email)
        
        print("✓ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Email: admin@barcoin.local")
        print(f"User ID: {user_id}")
        
    except Exception as e:
        print(f"✗ Failed to create admin user: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("BAR-COIN Admin User Creator")
    print("=" * 50)
    
    success = create_admin_user()
    
    if success:
        print("\n" + "=" * 50)
        print("You can now login to BAR-COIN with:")
        print("Username: admin")
        print("Password: admin123")
        print("=" * 50)
    else:
        print("\n✗ Failed to create admin user")
        sys.exit(1) 