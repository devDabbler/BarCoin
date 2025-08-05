#!/usr/bin/env python3
"""
BAR-COIN Application Runner

This script initializes and runs the BAR-COIN Streamlit application.
It handles environment setup, database initialization, and error handling.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_poetry_installation():
    """Check if Poetry is installed."""
    try:
        result = subprocess.run(['poetry', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✓ Poetry found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Poetry not found. Please install Poetry first:")
        print("  curl -sSL https://install.python-poetry.org | python3 -")
        return False

def check_dependencies():
    """Check if all dependencies are installed."""
    try:
        result = subprocess.run(['poetry', 'check'], 
                              capture_output=True, text=True, check=True)
        print("✓ Dependencies check passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Dependencies check failed: {e.stderr}")
        return False

def install_dependencies():
    """Install project dependencies using Poetry."""
    print("Installing dependencies...")
    try:
        subprocess.run(['poetry', 'install'], check=True)
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up environment variables and configuration."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from template...")
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✓ .env file created. Please edit it with your configuration.")
            return False  # User should edit the file
        except Exception as e:
            print(f"✗ Failed to create .env file: {e}")
            return False
    
    elif not env_file.exists():
        print("✗ No .env file found and no template available.")
        return False
    
    return True

def initialize_database():
    """Initialize the database."""
    try:
        # Import and initialize database
        sys.path.insert(0, str(Path(__file__).parent))
        from bar_coin.utils.database import db
        
        print("✓ Database initialized")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        return False

def run_application():
    """Run the Streamlit application."""
    print("Starting BAR-COIN application...")
    try:
        # Set PYTHONPATH to include the project root
        env = os.environ.copy()
        project_root = str(Path(__file__).parent)
        env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
        
        # Run with Poetry
        subprocess.run(['poetry', 'run', 'streamlit', 'run', 'bar_coin/app.py'], 
                      check=True, env=env)
    except KeyboardInterrupt:
        print("\n✓ Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start application: {e}")
        return False
    
    return True

def main():
    """Main application runner."""
    print("=" * 50)
    print("BAR-COIN Application Runner")
    print("=" * 50)
    
    # Check Poetry installation
    if not check_poetry_installation():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        print("Installing dependencies...")
        if not install_dependencies():
            return 1
    
    # Setup environment
    if not setup_environment():
        print("\nPlease configure your .env file and run again.")
        return 1
    
    # Initialize database
    if not initialize_database():
        return 1
    
    # Run application
    print("\n" + "=" * 50)
    print("Starting BAR-COIN...")
    print("=" * 50)
    
    success = run_application()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 