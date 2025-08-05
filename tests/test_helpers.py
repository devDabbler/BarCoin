"""
Unit tests for helper functions in BAR-COIN application.
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bar_coin.utils.helpers import (
    hash_password, verify_password, validate_username, validate_password,
    validate_email, calculate_total_value, calculate_total_coins,
    format_coin_counts, get_coin_statistics, format_duration,
    format_timestamp, generate_session_id, sanitize_filename,
    create_export_filename, parse_serial_data, validate_hardware_message,
    get_hardware_status_color, format_file_size, get_mobile_breakpoint,
    is_mobile_viewport, generate_qr_code_data, validate_session_data,
    calculate_processing_speed
)


class TestPasswordHelpers(unittest.TestCase):
    """Test password-related helper functions."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Check that hash is different from original
        self.assertNotEqual(password, hashed)
        
        # Check that hash starts with bcrypt identifier
        self.assertTrue(hashed.startswith('$2b$'))
        
        # Check that same password produces different hash (due to salt)
        hashed2 = hash_password(password)
        self.assertNotEqual(hashed, hashed2)
    
    def test_verify_password(self):
        """Test password verification."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Test correct password
        self.assertTrue(verify_password(password, hashed))
        
        # Test incorrect password
        self.assertFalse(verify_password("wrongpassword", hashed))
        
        # Test empty password
        self.assertFalse(verify_password("", hashed))
    
    def test_validate_password(self):
        """Test password validation."""
        # Test valid password
        self.assertTrue(validate_password("ValidPass123"))
        
        # Test too short password
        self.assertFalse(validate_password("short"))
        
        # Test password without uppercase
        self.assertFalse(validate_password("nouppercase123"))
        
        # Test password without lowercase
        self.assertFalse(validate_password("NOLOWERCASE123"))
        
        # Test password without number
        self.assertFalse(validate_password("NoNumbers"))
        
        # Test empty password
        self.assertFalse(validate_password(""))


class TestValidationHelpers(unittest.TestCase):
    """Test validation helper functions."""
    
    def test_validate_username(self):
        """Test username validation."""
        # Test valid username
        self.assertTrue(validate_username("validuser"))
        self.assertTrue(validate_username("user123"))
        self.assertTrue(validate_username("user_name"))
        
        # Test invalid username
        self.assertFalse(validate_username(""))  # Empty
        self.assertFalse(validate_username("a" * 21))  # Too long
        self.assertFalse(validate_username("user@name"))  # Invalid character
        self.assertFalse(validate_username("user name"))  # Space
    
    def test_validate_email(self):
        """Test email validation."""
        # Test valid emails
        self.assertTrue(validate_email("test@example.com"))
        self.assertTrue(validate_email("user.name@domain.co.uk"))
        self.assertTrue(validate_email("user+tag@example.org"))
        
        # Test invalid emails
        self.assertFalse(validate_email(""))  # Empty
        self.assertFalse(validate_email("invalid-email"))  # No @
        self.assertFalse(validate_email("@example.com"))  # No local part
        self.assertFalse(validate_email("user@"))  # No domain
        self.assertFalse(validate_email("user@.com"))  # No domain name


class TestCoinCalculationHelpers(unittest.TestCase):
    """Test coin calculation helper functions."""
    
    def test_calculate_total_value(self):
        """Test total value calculation."""
        coin_counts = {1: 10, 5: 5, 10: 3, 20: 2}
        total = calculate_total_value(coin_counts)
        expected = (1 * 10) + (5 * 5) + (10 * 3) + (20 * 2)  # 10 + 25 + 30 + 40 = 105
        self.assertEqual(total, expected)
        
        # Test empty counts
        self.assertEqual(calculate_total_value({}), 0)
        
        # Test single denomination
        self.assertEqual(calculate_total_value({5: 10}), 50)
    
    def test_calculate_total_coins(self):
        """Test total coin count calculation."""
        coin_counts = {1: 10, 5: 5, 10: 3, 20: 2}
        total = calculate_total_coins(coin_counts)
        expected = 10 + 5 + 3 + 2  # 20
        self.assertEqual(total, expected)
        
        # Test empty counts
        self.assertEqual(calculate_total_coins({}), 0)
        
        # Test single denomination
        self.assertEqual(calculate_total_coins({5: 10}), 10)
    
    def test_format_coin_counts(self):
        """Test coin count formatting."""
        coin_counts = {1: 10, 5: 5, 10: 3, 20: 2}
        formatted = format_coin_counts(coin_counts)
        
        # Check that all denominations are present in the list
        denominations = [item['denomination'] for item in formatted]
        self.assertIn(1.0, denominations)
        self.assertIn(5.0, denominations)
        self.assertIn(10.0, denominations)
        self.assertIn(20.0, denominations)
        
        # Check counts
        for item in formatted:
            if item['denomination'] == 1.0:
                self.assertEqual(item['count'], 10)
            elif item['denomination'] == 5.0:
                self.assertEqual(item['count'], 5)
            elif item['denomination'] == 10.0:
                self.assertEqual(item['count'], 3)
            elif item['denomination'] == 20.0:
                self.assertEqual(item['count'], 2)
    
    def test_get_coin_statistics(self):
        """Test coin statistics calculation."""
        coin_counts = {1: 10, 5: 5, 10: 3, 20: 2}
        stats = get_coin_statistics(coin_counts)
        
        self.assertEqual(stats['total_value'], 105)
        self.assertEqual(stats['total_coins'], 20)
        self.assertEqual(stats['denominations'], 4)
        self.assertEqual(stats['highest_denomination'], 20)
        self.assertEqual(stats['lowest_denomination'], 1)
        
        # Test empty counts
        empty_stats = get_coin_statistics({})
        self.assertEqual(empty_stats['total_value'], 0)
        self.assertEqual(empty_stats['total_coins'], 0)
        self.assertEqual(empty_stats['denominations'], 0)


class TestFormattingHelpers(unittest.TestCase):
    """Test formatting helper functions."""
    
    def test_format_duration(self):
        """Test duration formatting."""
        # Test seconds
        self.assertEqual(format_duration(30), "30 seconds")
        
        # Test minutes
        self.assertEqual(format_duration(90), "1 minute 30 seconds")
        self.assertEqual(format_duration(120), "2 minutes 0 seconds")
        
        # Test hours
        self.assertEqual(format_duration(3661), "1h 1m")
        self.assertEqual(format_duration(7200), "2h 0m")
        
        # Test zero
        self.assertEqual(format_duration(0), "0 seconds")
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        # Test current time
        now = datetime.now()
        formatted = format_timestamp(now)
        self.assertIsInstance(formatted, str)
        self.assertIn(str(now.year), formatted)
        
        # Test specific time
        test_time = datetime(2023, 12, 25, 14, 30, 45)
        formatted = format_timestamp(test_time)
        self.assertIn("2023", formatted)
        self.assertIn("14:30", formatted)
    
    def test_format_file_size(self):
        """Test file size formatting."""
        # Test bytes
        self.assertEqual(format_file_size(512), "512 B")
        
        # Test kilobytes
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1536), "1.5 KB")
        
        # Test megabytes
        self.assertEqual(format_file_size(1024 * 1024), "1.0 MB")
        self.assertEqual(format_file_size(1024 * 1024 * 2.5), "2.5 MB")
        
        # Test gigabytes
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.0 GB")


class TestUtilityHelpers(unittest.TestCase):
    """Test utility helper functions."""
    
    def test_generate_session_id(self):
        """Test session ID generation."""
        session_id = generate_session_id()
        
        # Check format (should be alphanumeric)
        self.assertIsInstance(session_id, str)
        self.assertTrue(session_id.isalnum())
        
        # Check it starts with 'session'
        self.assertTrue(session_id.startswith('session'))
        
        # Check uniqueness
        session_id2 = generate_session_id()
        self.assertNotEqual(session_id, session_id2)
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test valid filename
        self.assertEqual(sanitize_filename("valid_file.txt"), "valid_file.txt")
        
        # Test filename with spaces
        self.assertEqual(sanitize_filename("file with spaces.txt"), "file_with_spaces.txt")
        
        # Test filename with special characters
        self.assertEqual(sanitize_filename("file@#$%.txt"), "file.txt")
        
        # Test filename with path separators
        self.assertEqual(sanitize_filename("path/to/file.txt"), "pathtofile.txt")
        
        # Test empty filename
        self.assertEqual(sanitize_filename(""), "untitled")
    
    def test_create_export_filename(self):
        """Test export filename creation."""
        filename = create_export_filename("test_session", "csv")
        
        # Check format
        self.assertIn("test_session", filename)
        self.assertIn(".csv", filename)
        self.assertIn("export", filename.lower())
        
        # Check timestamp is included
        current_year = str(datetime.now().year)
        self.assertIn(current_year, filename)
    
    def test_get_hardware_status_color(self):
        """Test hardware status color mapping."""
        # Test valid statuses
        self.assertEqual(get_hardware_status_color("connected"), "green")
        self.assertEqual(get_hardware_status_color("disconnected"), "red")
        self.assertEqual(get_hardware_status_color("error"), "orange")
        self.assertEqual(get_hardware_status_color("processing"), "blue")
        
        # Test unknown status
        self.assertEqual(get_hardware_status_color("unknown"), "gray")
    
    def test_get_mobile_breakpoint(self):
        """Test mobile breakpoint calculation."""
        breakpoint = get_mobile_breakpoint()
        self.assertIsInstance(breakpoint, int)
        self.assertGreater(breakpoint, 0)
        self.assertLess(breakpoint, 2000)  # Reasonable mobile breakpoint
    
    def test_is_mobile_viewport(self):
        """Test mobile viewport detection."""
        # Test mobile width
        self.assertTrue(is_mobile_viewport(375))
        self.assertTrue(is_mobile_viewport(768))
        
        # Test desktop width
        self.assertFalse(is_mobile_viewport(1024))
        self.assertFalse(is_mobile_viewport(1920))


class TestHardwareHelpers(unittest.TestCase):
    """Test hardware-related helper functions."""
    
    def test_parse_serial_data(self):
        """Test serial data parsing."""
        # Test valid JSON data
        valid_data = '{"type": "coin", "denomination": 5, "timestamp": "2023-12-25T14:30:00"}'
        parsed = parse_serial_data(valid_data)
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed['type'], 'coin')
        self.assertEqual(parsed['denomination'], 5)
        
        # Test invalid JSON
        invalid_data = '{"invalid": json}'
        parsed = parse_serial_data(invalid_data)
        self.assertIsNone(parsed)
        
        # Test empty data
        self.assertIsNone(parse_serial_data(""))
    
    def test_validate_hardware_message(self):
        """Test hardware message validation."""
        # Test valid message
        valid_msg = {
            "type": "coin",
            "denomination": 5,
            "timestamp": "2023-12-25T14:30:00"
        }
        self.assertTrue(validate_hardware_message(valid_msg))
        
        # Test missing required fields
        invalid_msg = {"type": "coin"}
        self.assertFalse(validate_hardware_message(invalid_msg))
        
        # Test invalid denomination
        invalid_msg2 = {
            "type": "coin",
            "denomination": 999,
            "timestamp": "2023-12-25T14:30:00"
        }
        self.assertFalse(validate_hardware_message(invalid_msg2))
    
    def test_calculate_processing_speed(self):
        """Test processing speed calculation."""
        # Test with some coin counts over time
        coin_counts = {1: 10, 5: 5, 10: 3}
        duration_seconds = 60  # 1 minute

        speed = calculate_processing_speed(coin_counts, duration_seconds)
        expected = (10 + 5 + 3) / 60  # 18 coins / 60 seconds = 0.3 coins/second
        self.assertEqual(speed, expected)
        
        # Test with zero coins
        speed_zero = calculate_processing_speed({}, 60)
        self.assertEqual(speed_zero, 0.0)
        
        # Test with zero duration
        speed_zero_duration = calculate_processing_speed(coin_counts, 0)
        self.assertEqual(speed_zero_duration, 0.0)


class TestDataValidationHelpers(unittest.TestCase):
    """Test data validation helper functions."""
    
    def test_validate_session_data(self):
        """Test session data validation."""
        # Test valid session data
        valid_data = {
            "session_info": {"id": 1, "name": "test"},
            "coin_counts": [{"denomination": 1, "count": 10}],
            "hardware_logs": [{"level": "INFO", "message": "test"}]
        }
        self.assertTrue(validate_session_data(valid_data))
        
        # Test missing required sections
        invalid_data = {"session_info": {"id": 1}}
        self.assertFalse(validate_session_data(invalid_data))
        
        # Test invalid coin counts
        invalid_data2 = {
            "session_info": {"id": 1, "name": "test"},
            "coin_counts": [{"invalid": "data"}],
            "hardware_logs": []
        }
        self.assertFalse(validate_session_data(invalid_data2))
    
    def test_generate_qr_code_data(self):
        """Test QR code data generation."""
        data = {"session_id": "123", "total_value": 100}
        qr_data = generate_qr_code_data(data)
        
        # Check that data is JSON string
        self.assertIsInstance(qr_data, str)
        
        # Check that original data is included
        self.assertIn("123", qr_data)
        self.assertIn("100", qr_data)


if __name__ == '__main__':
    unittest.main() 