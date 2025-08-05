#!/usr/bin/env python3
"""
BAR-COIN Setup Script

This script helps users set up the BAR-COIN application quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print the BAR-COIN banner."""
    print("=" * 60)
    print("🚀 BAR-COIN Setup")
    print("Mobile-base Automated Coin Counter and Segregation")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_poetry():
    """Install Poetry if not present."""
    try:
        result = subprocess.run(['poetry', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Poetry found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing Poetry...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'poetry'
            ], check=True)
            print("✅ Poetry installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install Poetry")
            print("   Please install manually: https://python-poetry.org/docs/#installation")
            return False

def setup_project():
    """Set up the project structure and dependencies."""
    print("\n🔧 Setting up project...")
    
    # Install dependencies
    try:
        subprocess.run(['poetry', 'install'], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ .env file created from template")
            print("   Please edit .env with your configuration")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    return True

def test_setup():
    """Test the setup by running basic checks."""
    print("\n🧪 Testing setup...")
    
    try:
        # Test database initialization
        subprocess.run([
            'poetry', 'run', 'python', '-c',
            'from bar_coin.utils.database import db; print("Database OK")'
        ], check=True, capture_output=True)
        print("✅ Database initialization test passed")
        
        # Test imports
        subprocess.run([
            'poetry', 'run', 'python', '-c',
            'import bar_coin; print("Imports OK")'
        ], check=True, capture_output=True)
        print("✅ Import test passed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run the application: python run.py")
    print("3. Or run tests: python run_tests.py")
    print("\nFor more information, see README.md")

def main():
    """Main setup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install Poetry
    if not install_poetry():
        return 1
    
    # Setup project
    if not setup_project():
        return 1
    
    # Test setup
    if not test_setup():
        return 1
    
    # Print next steps
    print_next_steps()
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 