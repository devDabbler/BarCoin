"""
Mock hardware implementation for BAR-COIN testing and development.
"""

import json
import random
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from queue import Queue

from bar_coin.config.settings import PHILIPPINE_COINS

class MockHardware:
    """Mock hardware implementation for testing."""
    
    def __init__(self):
        """Initialize mock hardware."""
        self.is_connected = False
        self.is_running = False
        self.data_queue = Queue()
        self.simulation_thread = None
        self.stop_event = threading.Event()
        
        # Simulation settings
        self.simulation_config = {
            'coin_rate': 2.0,  # coins per second
            'error_rate': 0.01,  # 1% error rate
            'jamming_rate': 0.005,  # 0.5% jamming rate
            'max_coins_per_batch': 5,
            'min_delay': 0.1,  # minimum delay between coins
            'max_delay': 2.0   # maximum delay between coins
        }
        
        # Statistics
        self.stats = {
            'coins_simulated': 0,
            'errors_simulated': 0,
            'jams_simulated': 0,
            'last_coin_time': None,
            'session_start': None
        }
        
        # Supported denominations
        self.denominations = list(PHILIPPINE_COINS.keys())
    
    def connect(self) -> bool:
        """Simulate hardware connection."""
        self.is_connected = True
        self.is_running = True
        self.stats['session_start'] = datetime.now()
        print("Mock hardware connected successfully")
        return True
    
    def disconnect(self):
        """Simulate hardware disconnection."""
        self.is_connected = False
        self.is_running = False
        self.stop_event.set()
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5)
        
        print("Mock hardware disconnected")
    
    def start_simulation(self):
        """Start coin simulation."""
        if not self.is_connected:
            return False
        
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        print("Mock hardware simulation started")
        return True
    
    def stop_simulation(self):
        """Stop coin simulation."""
        self.stop_event.set()
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=5)
        print("Mock hardware simulation stopped")
    
    def _simulation_loop(self):
        """Main simulation loop."""
        while self.is_running and not self.stop_event.is_set():
            try:
                # Simulate coin detection
                if random.random() < self.simulation_config['error_rate']:
                    self._simulate_error()
                elif random.random() < self.simulation_config['jamming_rate']:
                    self._simulate_jam()
                else:
                    self._simulate_coin_detection()
                
                # Random delay between events
                delay = random.uniform(
                    self.simulation_config['min_delay'],
                    self.simulation_config['max_delay']
                )
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error in simulation loop: {e}")
                time.sleep(1)
    
    def _simulate_coin_detection(self):
        """Simulate a coin detection event."""
        # Randomly select denomination
        denomination = random.choice(self.denominations)
        
        # Create coin detection message
        coin_data = {
            "type": "coin_detected",
            "denomination": denomination,
            "timestamp": datetime.now().isoformat(),
            "sensor_id": random.randint(1, 4),
            "confidence": random.uniform(0.85, 0.99)
        }
        
        # Add to data queue
        self.data_queue.put(json.dumps(coin_data))
        
        # Update statistics
        self.stats['coins_simulated'] += 1
        self.stats['last_coin_time'] = datetime.now()
        
        print(f"Mock coin detected: ₱{denomination}")
    
    def _simulate_error(self):
        """Simulate a hardware error."""
        error_types = [
            "sensor_error",
            "communication_error",
            "power_fluctuation",
            "mechanical_error"
        ]
        
        error_data = {
            "type": "error",
            "error_type": random.choice(error_types),
            "timestamp": datetime.now().isoformat(),
            "message": f"Simulated {random.choice(error_types)}",
            "severity": random.choice(["low", "medium", "high"])
        }
        
        self.data_queue.put(json.dumps(error_data))
        self.stats['errors_simulated'] += 1
        
        print(f"Mock error: {error_data['error_type']}")
    
    def _simulate_jam(self):
        """Simulate a coin jam."""
        jam_data = {
            "type": "jam_detected",
            "timestamp": datetime.now().isoformat(),
            "location": random.choice(["input", "sorting", "output"]),
            "severity": random.choice(["minor", "major", "critical"])
        }
        
        self.data_queue.put(json.dumps(jam_data))
        self.stats['jams_simulated'] += 1
        
        print(f"Mock jam detected: {jam_data['location']}")
    
    def read_data(self) -> Optional[str]:
        """Read simulated data."""
        if not self.is_connected:
            return None
        
        try:
            return self.data_queue.get_nowait()
        except:
            return None
    
    def write_data(self, data: str) -> bool:
        """Simulate writing data to hardware."""
        if not self.is_connected:
            return False
        
        print(f"Mock hardware received: {data}")
        return True
    
    def send_command(self, command: str) -> bool:
        """Send command to mock hardware."""
        if not self.is_connected:
            return False
        
        print(f"Mock hardware command: {command}")
        
        # Handle specific commands
        if command.strip().upper() == "START":
            self.start_simulation()
            return True
        elif command.strip().upper() == "STOP":
            self.stop_simulation()
            return True
        elif command.strip().upper() == "RESET":
            self.reset_stats()
            return True
        elif command.strip().upper() == "STATUS":
            # Return status as JSON
            status_data = {
                "type": "status_response",
                "timestamp": datetime.now().isoformat(),
                "connected": self.is_connected,
                "running": self.is_running,
                "stats": self.stats
            }
            self.data_queue.put(json.dumps(status_data))
            return True
        
        return True
    
    def test_connection(self) -> bool:
        """Test mock connection."""
        return self.is_connected
    
    def get_status(self) -> Dict[str, Any]:
        """Get mock hardware status."""
        return {
            'connected': self.is_connected,
            'running': self.is_running,
            'simulation_active': self.simulation_thread and self.simulation_thread.is_alive(),
            'config': self.simulation_config,
            'stats': self.stats.copy(),
            'denominations': self.denominations
        }
    
    def reset_stats(self):
        """Reset simulation statistics."""
        self.stats = {
            'coins_simulated': 0,
            'errors_simulated': 0,
            'jams_simulated': 0,
            'last_coin_time': None,
            'session_start': datetime.now()
        }
        print("Mock hardware stats reset")
    
    def emergency_stop(self):
        """Simulate emergency stop."""
        print("Mock hardware emergency stop triggered")
        self.stop_simulation()
        self.disconnect()
    
    def configure_simulation(self, **kwargs):
        """Configure simulation parameters."""
        for key, value in kwargs.items():
            if key in self.simulation_config:
                self.simulation_config[key] = value
        
        print(f"Mock hardware configuration updated: {kwargs}")
    
    def simulate_batch(self, denominations: List[float], count: int = 1):
        """Simulate a batch of specific coins."""
        for _ in range(count):
            for denomination in denominations:
                if denomination in self.denominations:
                    coin_data = {
                        "type": "coin_detected",
                        "denomination": denomination,
                        "timestamp": datetime.now().isoformat(),
                        "sensor_id": 1,
                        "confidence": 0.95
                    }
                    self.data_queue.put(json.dumps(coin_data))
                    self.stats['coins_simulated'] += 1
                    time.sleep(0.1)  # Small delay between coins
    
    def get_simulation_info(self) -> Dict[str, Any]:
        """Get detailed simulation information."""
        return {
            'type': 'mock',
            'connected': self.is_connected,
            'running': self.is_running,
            'config': self.simulation_config.copy(),
            'stats': self.stats.copy(),
            'supported_denominations': self.denominations,
            'session_duration': (datetime.now() - self.stats['session_start']).total_seconds() if self.stats['session_start'] else 0
        } 