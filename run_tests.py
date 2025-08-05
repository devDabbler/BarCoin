#!/usr/bin/env python3
"""
BAR-COIN Test Runner

This script runs all unit tests for the BAR-COIN application.
"""

import os
import sys
import subprocess
import unittest
from pathlib import Path

def run_tests_with_poetry():
    """Run tests using Poetry."""
    try:
        print("Running tests with Poetry...")
        result = subprocess.run(['poetry', 'run', 'python', '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Failed to run tests: {e}")
        return False

def run_tests_directly():
    """Run tests directly using unittest."""
    try:
        # Add project root to path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = project_root / 'tests'
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    except Exception as e:
        print(f"Failed to run tests: {e}")
        return False

def main():
    """Main test runner."""
    print("=" * 50)
    print("BAR-COIN Test Runner")
    print("=" * 50)
    
    # Try running with Poetry first
    if run_tests_with_poetry():
        print("\n✓ All tests passed!")
        return 0
    
    print("\nFalling back to direct test execution...")
    
    # Fall back to direct execution
    if run_tests_directly():
        print("\n✓ All tests passed!")
        return 0
    
    print("\n✗ Some tests failed!")
    return 1

if __name__ == '__main__':
    sys.exit(main()) 