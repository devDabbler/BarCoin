"""
Tests for hardware functionality.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch

from bar_coin.hardware.mock_hardware import MockHardware
from bar_coin.hardware.serial_handler import SerialHandler
from bar_coin.utils.helpers import parse_serial_data, validate_hardware_message

class TestMockHardware:
    """Test mock hardware functionality."""
    
    def test_mock_hardware_initialization(self):
        """Test mock hardware initialization."""
        hardware = MockHardware()
        assert hardware.is_connected == False
        assert hardware.is_running == False
        assert len(hardware.denominations) > 0
    
    def test_mock_hardware_connection(self):
        """Test mock hardware connection."""
        hardware = MockHardware()
        assert hardware.connect() == True
        assert hardware.is_connected == True
        assert hardware.is_running == True
    
    def test_mock_hardware_disconnection(self):
        """Test mock hardware disconnection."""
        hardware = MockHardware()
        hardware.connect()
        hardware.disconnect()
        assert hardware.is_connected == False
        assert hardware.is_running == False
    
    def test_mock_coin_detection(self):
        """Test mock coin detection."""
        hardware = MockHardware()
        hardware.connect()
        
        # Simulate coin detection
        hardware._simulate_coin_detection()
        
        # Check if data was added to queue
        data = hardware.read_data()
        assert data is not None
        
        # Parse the data
        parsed = json.loads(data)
        assert parsed['type'] == 'coin_detected'
        assert 'denomination' in parsed
        assert 'timestamp' in parsed
    
    def test_mock_error_simulation(self):
        """Test mock error simulation."""
        hardware = MockHardware()
        hardware.connect()
        
        # Simulate error
        hardware._simulate_error()
        
        # Check if error was added to queue
        data = hardware.read_data()
        assert data is not None
        
        # Parse the data
        parsed = json.loads(data)
        assert parsed['type'] == 'error'
        assert 'error_type' in parsed

class TestSerialHandler:
    """Test serial handler functionality."""
    
    @patch('serial.Serial')
    def test_serial_connection(self, mock_serial):
        """Test serial connection."""
        mock_serial.return_value.is_open = True
        
        handler = SerialHandler(port="COM3", baudrate=9600)
        assert handler.connect() == True
        assert handler.is_connected == True
    
    @patch('serial.Serial')
    def test_serial_disconnection(self, mock_serial):
        """Test serial disconnection."""
        mock_serial.return_value.is_open = True
        
        handler = SerialHandler(port="COM3", baudrate=9600)
        handler.connect()
        handler.disconnect()
        assert handler.is_connected == False

class TestDataParsing:
    """Test data parsing functionality."""
    
    def test_valid_serial_data_parsing(self):
        """Test parsing valid serial data."""
        valid_data = '{"type": "coin_detected", "denomination": 5.00, "timestamp": "2024-01-01T12:00:00"}'
        parsed = parse_serial_data(valid_data)
        assert parsed is not None
        assert parsed['type'] == 'coin_detected'
        assert parsed['denomination'] == 5.00
    
    def test_invalid_serial_data_parsing(self):
        """Test parsing invalid serial data."""
        invalid_data = 'invalid json data'
        parsed = parse_serial_data(invalid_data)
        assert parsed is None
    
    def test_hardware_message_validation(self):
        """Test hardware message validation."""
        valid_message = {
            'type': 'coin_detected',
            'denomination': 5.00,
            'timestamp': '2024-01-01T12:00:00'
        }
        assert validate_hardware_message(valid_message) == True
        
        invalid_message = {
            'type': 'invalid_type',
            'denomination': 5.00
        }
        assert validate_hardware_message(invalid_message) == False

if __name__ == "__main__":
    pytest.main([__file__]) 