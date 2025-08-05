"""
Unit tests for database operations in BAR-COIN application.
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bar_coin.utils.database import DatabaseManager
from bar_coin.utils.helpers import hash_password


class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_coins.db')
        self.db_manager = DatabaseManager(self.db_path)
        self.db_manager._init_database()
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_init_database(self):
        """Test database initialization."""
        # Check if tables exist
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check users table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='users'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # Check sessions table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sessions'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # Check coin_counts table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='coin_counts'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # Check hardware_logs table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='hardware_logs'
            """)
            self.assertIsNotNone(cursor.fetchone())
    
    def test_create_user(self):
        """Test user creation."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user
        user_id = self.db_manager.create_user(username, password, email)
        self.assertIsNotNone(user_id)
        
        # Verify user was created
        user = self.db_manager.get_user_by_username(username)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], username)
        self.assertEqual(user['email'], email)
        self.assertTrue(user['password_hash'].startswith('$2b$'))
    
    def test_duplicate_username(self):
        """Test creating user with duplicate username."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create first user
        self.db_manager.create_user(username, password, email)
        
        # Try to create duplicate
        with self.assertRaises(sqlite3.IntegrityError):
            self.db_manager.create_user(username, "differentpass", "different@example.com")
    
    def test_get_user_by_username(self):
        """Test retrieving user by username."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user
        self.db_manager.create_user(username, password, email)
        
        # Get user
        user = self.db_manager.get_user_by_username(username)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], username)
        self.assertEqual(user['email'], email)
        
        # Test non-existent user
        user = self.db_manager.get_user_by_username("nonexistent")
        self.assertIsNone(user)
    
    def test_update_last_login(self):
        """Test updating last login timestamp."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user
        user_id = self.db_manager.create_user(username, password, email)
        
        # Update last login
        self.db_manager.update_last_login(user_id)
        
        # Verify update
        user = self.db_manager.get_user_by_username(username)
        self.assertIsNotNone(user['last_login'])
    
    def test_session_management(self):
        """Test session creation and ending."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user
        user_id = self.db_manager.create_user(username, password, email)
        
        # Create session
        session_id = self.db_manager.create_session(user_id, "test_session")
        self.assertIsNotNone(session_id)
        
        # End session
        self.db_manager.end_session(session_id)
        
        # Verify session was ended
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT end_time FROM sessions WHERE id = ?", (session_id,))
            result = cursor.fetchone()
            self.assertIsNotNone(result[0])
    
    def test_coin_counting(self):
        """Test coin count operations."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user and session
        user_id = self.db_manager.create_user(username, password, email)
        session_id = self.db_manager.create_session(user_id, "test_session")
        
        # Add coin counts
        self.db_manager.add_coin_count(session_id, 1, 10)  # 10 x 1 peso
        self.db_manager.add_coin_count(session_id, 5, 5)   # 5 x 5 peso
        self.db_manager.add_coin_count(session_id, 10, 3)  # 3 x 10 peso
        
        # Get session counts
        counts = self.db_manager.get_session_counts(session_id)
        self.assertEqual(len(counts), 3)
        
        # Verify counts
        self.assertEqual(counts[1], 10)
        self.assertEqual(counts[5], 5)
        self.assertEqual(counts[10], 3)
    
    def test_session_summary(self):
        """Test session summary calculation."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user and session
        user_id = self.db_manager.create_user(username, password, email)
        session_id = self.db_manager.create_session(user_id, "test_session")
        
        # Add coin counts
        self.db_manager.add_coin_count(session_id, 1, 10)  # 10 peso
        self.db_manager.add_coin_count(session_id, 5, 5)   # 25 peso
        self.db_manager.add_coin_count(session_id, 10, 3)  # 30 peso
        
        # Get summary
        summary = self.db_manager.get_session_summary(session_id)
        self.assertIsNotNone(summary)
        self.assertEqual(summary['total_value'], 65)  # 10 + 25 + 30
        self.assertEqual(summary['total_coins'], 18)  # 10 + 5 + 3
    
    def test_hardware_logging(self):
        """Test hardware log operations."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user and session
        user_id = self.db_manager.create_user(username, password, email)
        session_id = self.db_manager.create_session(user_id, "test_session")
        
        # Add hardware log
        log_id = self.db_manager.add_hardware_log(
            session_id, "INFO", "Test hardware message"
        )
        self.assertIsNotNone(log_id)
        
        # Get hardware logs
        logs = self.db_manager.get_hardware_logs(session_id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]['message'], "Test hardware message")
        self.assertEqual(logs[0]['event_type'], "INFO")
    
    def test_export_session_data(self):
        """Test session data export."""
        username = "testuser"
        password = "testpass123"
        email = "test@example.com"
        
        # Create user and session
        user_id = self.db_manager.create_user(username, password, email)
        session_id = self.db_manager.create_session(user_id, "test_session")
        
        # Add some data
        self.db_manager.add_coin_count(session_id, 1, 10)
        self.db_manager.add_hardware_log(session_id, "INFO", "Test log")
        
        # Export data
        data = self.db_manager.export_session_data(session_id)
        self.assertIsNotNone(data)
        self.assertIn('session_info', data)
        self.assertIn('coin_counts', data)
        self.assertIn('hardware_logs', data)
        
        # Verify session info
        self.assertEqual(data['session_info']['user_id'], user_id)
        self.assertEqual(data['session_info']['name'], f"Session {session_id}")
        
        # Verify coin counts
        self.assertEqual(len(data['coin_counts']), 1)
        self.assertEqual(data['coin_counts'][0]['denomination'], 1)
        self.assertEqual(data['coin_counts'][0]['count'], 10)
        
        # Verify hardware logs
        self.assertEqual(len(data['hardware_logs']), 1)
        self.assertEqual(data['hardware_logs'][0]['message'], "Test log")


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection handling."""
    
    def test_connection_context_manager(self):
        """Test database connection context manager."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, 'test_coins.db')

        try:
            db_manager = DatabaseManager(db_path)
            db_manager._init_database()

            # Test context manager
            with db_manager._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)

            # Connection should be closed (check by trying to use it)
            try:
                conn.execute("SELECT 1")
                self.fail("Connection should be closed")
            except (sqlite3.ProgrammingError, sqlite3.OperationalError):
                pass  # Expected - connection is closed

        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.remove(db_path)
            os.rmdir(temp_dir)


if __name__ == '__main__':
    unittest.main() 