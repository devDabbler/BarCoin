"""
Main coin counter hardware interface for BAR-COIN.
"""

import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from queue import Queue, Empty

from bar_coin.config.settings import HARDWARE_CONFIG, PHILIPPINE_COINS
from bar_coin.utils.helpers import parse_serial_data, validate_hardware_message
from bar_coin.hardware.serial_handler import SerialHandler
from bar_coin.hardware.mock_hardware import MockHardware

logger = logging.getLogger(__name__)

class CoinCounter:
    """Main coin counter hardware interface."""
    
    def __init__(self, mock_mode: Optional[bool] = None):
        """Initialize coin counter."""
        self.mock_mode = mock_mode if mock_mode is not None else HARDWARE_CONFIG["mock_mode"]
        self.is_running = False
        self.is_connected = False
        self.data_queue = Queue()
        self.callbacks = []
        self.current_session_id = None
        
        # Initialize hardware interface
        if self.mock_mode:
            self.hardware = MockHardware()
            logger.info("Initialized in MOCK mode")
        else:
            self.hardware = SerialHandler(
                port=HARDWARE_CONFIG["serial_port"],
                baudrate=HARDWARE_CONFIG["baud_rate"],
                timeout=HARDWARE_CONFIG["timeout"]
            )
            logger.info("Initialized in HARDWARE mode")
        
        # Statistics
        self.stats = {
            'total_coins_processed': 0,
            'session_start_time': None,
            'last_coin_time': None,
            'processing_speed': 0.0,
            'errors': 0,
            'warnings': 0
        }
        
        # Threading
        self._read_thread = None
        self._stats_thread = None
        self._stop_event = threading.Event()
    
    def connect(self) -> bool:
        """Establish connection with hardware."""
        try:
            if self.hardware.connect():
                self.is_connected = True
                self.is_running = True
                self._start_threads()
                logger.info("Successfully connected to hardware")
                return True
            else:
                logger.error("Failed to connect to hardware")
                return False
        except Exception as e:
            logger.error(f"Error connecting to hardware: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from hardware."""
        self.is_running = False
        self.is_connected = False
        self._stop_event.set()
        
        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=5)
        
        if self._stats_thread and self._stats_thread.is_alive():
            self._stats_thread.join(timeout=5)
        
        self.hardware.disconnect()
        logger.info("Disconnected from hardware")
    
    def _start_threads(self):
        """Start background threads."""
        # Data reading thread
        self._read_thread = threading.Thread(target=self._read_data_loop, daemon=True)
        self._read_thread.start()
        
        # Statistics update thread
        self._stats_thread = threading.Thread(target=self._update_stats_loop, daemon=True)
        self._stats_thread.start()
    
    def _read_data_loop(self):
        """Continuously read data from hardware."""
        while self.is_running and not self._stop_event.is_set():
            try:
                data = self.hardware.read_data()
                if data:
                    self._process_data(data)
                time.sleep(0.01)  # 10ms delay
            except Exception as e:
                logger.error(f"Error in data reading loop: {e}")
                self.stats['errors'] += 1
                time.sleep(1)  # Wait before retrying
    
    def _update_stats_loop(self):
        """Update statistics periodically."""
        while self.is_running and not self._stop_event.is_set():
            try:
                self._update_processing_speed()
                time.sleep(1)  # Update every second
            except Exception as e:
                logger.error(f"Error in stats update loop: {e}")
                time.sleep(5)
    
    def _process_data(self, data: str):
        """Process incoming data from hardware."""
        try:
            # Parse the data
            parsed_data = parse_serial_data(data)
            if not parsed_data:
                logger.warning(f"Invalid data received: {data}")
                self.stats['warnings'] += 1
                return
            
            # Validate the message
            if not validate_hardware_message(parsed_data):
                logger.warning(f"Invalid hardware message: {parsed_data}")
                self.stats['warnings'] += 1
                return
            
            # Process coin detection
            if parsed_data['type'] == 'coin_detected':
                self._handle_coin_detection(parsed_data)
            
            # Add to queue for UI updates
            self.data_queue.put(parsed_data)
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            self.stats['errors'] += 1
    
    def _handle_coin_detection(self, data: Dict[str, Any]):
        """Handle coin detection event."""
        denomination = float(data['denomination'])
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Update statistics
        self.stats['total_coins_processed'] += 1
        self.stats['last_coin_time'] = timestamp
        
        # Log the detection
        logger.info(f"Coin detected: ₱{denomination} at {timestamp}")
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback({
                    'type': 'coin_detected',
                    'denomination': denomination,
                    'timestamp': timestamp,
                    'session_id': self.current_session_id
                })
            except Exception as e:
                logger.error(f"Error in callback: {e}")
    
    def _update_processing_speed(self):
        """Update processing speed calculation."""
        if self.stats['session_start_time'] and self.stats['total_coins_processed'] > 0:
            elapsed = datetime.now() - self.stats['session_start_time']
            elapsed_minutes = elapsed.total_seconds() / 60
            
            if elapsed_minutes > 0:
                self.stats['processing_speed'] = self.stats['total_coins_processed'] / elapsed_minutes
    
    def start_session(self, session_id: str) -> bool:
        """Start a new counting session."""
        if not self.is_connected:
            logger.error("Cannot start session: not connected to hardware")
            return False
        
        self.current_session_id = session_id
        self.stats['session_start_time'] = datetime.now()
        self.stats['total_coins_processed'] = 0
        self.stats['processing_speed'] = 0.0
        
        logger.info(f"Started new session: {session_id}")
        return True
    
    def end_session(self) -> Dict[str, Any]:
        """End the current counting session."""
        session_stats = {
            'session_id': self.current_session_id,
            'total_coins': self.stats['total_coins_processed'],
            'duration': None,
            'processing_speed': self.stats['processing_speed'],
            'errors': self.stats['errors'],
            'warnings': self.stats['warnings']
        }
        
        if self.stats['session_start_time']:
            duration = datetime.now() - self.stats['session_start_time']
            session_stats['duration'] = duration.total_seconds()
        
        self.current_session_id = None
        self.stats['session_start_time'] = None
        
        logger.info(f"Ended session: {session_stats}")
        return session_stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get current hardware status."""
        return {
            'connected': self.is_connected,
            'running': self.is_running,
            'mock_mode': self.mock_mode,
            'session_id': self.current_session_id,
            'stats': self.stats.copy(),
            'hardware_status': self.hardware.get_status()
        }
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for coin detection events."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Remove callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_data_queue(self) -> Queue:
        """Get the data queue for UI updates."""
        return self.data_queue
    
    def clear_data_queue(self):
        """Clear the data queue."""
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except Empty:
                break
    
    def reset_counters(self):
        """Reset all counters and statistics."""
        self.stats['total_coins_processed'] = 0
        self.stats['session_start_time'] = None
        self.stats['last_coin_time'] = None
        self.stats['processing_speed'] = 0.0
        self.stats['errors'] = 0
        self.stats['warnings'] = 0
        
        self.clear_data_queue()
        logger.info("Reset all counters")
    
    def emergency_stop(self):
        """Emergency stop all operations."""
        logger.warning("EMERGENCY STOP triggered")
        self.is_running = False
        self.hardware.emergency_stop()
        self.disconnect()
    
    def test_connection(self) -> bool:
        """Test hardware connection."""
        try:
            return self.hardware.test_connection()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information."""
        return {
            'type': 'mock' if self.mock_mode else 'serial',
            'port': HARDWARE_CONFIG["serial_port"] if not self.mock_mode else 'N/A',
            'baud_rate': HARDWARE_CONFIG["baud_rate"] if not self.mock_mode else 'N/A',
            'supported_denominations': list(PHILIPPINE_COINS.keys()),
            'mock_mode': self.mock_mode
        }

# Global coin counter instance
coin_counter = CoinCounter() 