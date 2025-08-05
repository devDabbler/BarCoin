"""
Serial communication handler for BAR-COIN hardware integration.
"""

import serial
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SerialHandler:
    """Handles serial communication with coin counting hardware."""
    
    def __init__(self, port: str = "COM3", baudrate: int = 9600, timeout: int = 1):
        """Initialize serial handler."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_connected = False
        self.last_error = None
        
        # Connection statistics
        self.stats = {
            'bytes_received': 0,
            'bytes_sent': 0,
            'errors': 0,
            'last_communication': None
        }
    
    def connect(self) -> bool:
        """Establish serial connection."""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            if self.serial_conn.is_open:
                self.is_connected = True
                self.last_error = None
                logger.info(f"Successfully connected to {self.port} at {self.baudrate} baud")
                return True
            else:
                self.last_error = "Serial port failed to open"
                logger.error(f"Failed to open serial port {self.port}")
                return False
                
        except serial.SerialException as e:
            self.last_error = str(e)
            logger.error(f"Serial connection error: {e}")
            return False
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
                logger.info(f"Disconnected from {self.port}")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
        
        self.is_connected = False
        self.serial_conn = None
    
    def read_data(self) -> Optional[str]:
        """Read data from serial port."""
        if not self.is_connected or not self.serial_conn:
            return None
        
        try:
            if self.serial_conn.in_waiting > 0:
                data = self.serial_conn.readline().decode('utf-8').strip()
                if data:
                    self.stats['bytes_received'] += len(data.encode('utf-8'))
                    self.stats['last_communication'] = datetime.now()
                    return data
        except serial.SerialException as e:
            self.stats['errors'] += 1
            self.last_error = str(e)
            logger.error(f"Serial read error: {e}")
        except UnicodeDecodeError as e:
            self.stats['errors'] += 1
            self.last_error = f"Unicode decode error: {e}"
            logger.error(f"Unicode decode error: {e}")
        except Exception as e:
            self.stats['errors'] += 1
            self.last_error = str(e)
            logger.error(f"Unexpected error during read: {e}")
        
        return None
    
    def write_data(self, data: str) -> bool:
        """Write data to serial port."""
        if not self.is_connected or not self.serial_conn:
            return False
        
        try:
            encoded_data = data.encode('utf-8')
            bytes_written = self.serial_conn.write(encoded_data)
            self.serial_conn.flush()
            
            self.stats['bytes_sent'] += bytes_written
            self.stats['last_communication'] = datetime.now()
            
            logger.debug(f"Sent {bytes_written} bytes: {data}")
            return True
            
        except serial.SerialException as e:
            self.stats['errors'] += 1
            self.last_error = str(e)
            logger.error(f"Serial write error: {e}")
            return False
        except Exception as e:
            self.stats['errors'] += 1
            self.last_error = str(e)
            logger.error(f"Unexpected error during write: {e}")
            return False
    
    def send_command(self, command: str) -> bool:
        """Send a command to the hardware."""
        if not command.endswith('\n'):
            command += '\n'
        return self.write_data(command)
    
    def test_connection(self) -> bool:
        """Test if the connection is working."""
        if not self.is_connected:
            return False
        
        try:
            # Send a ping command
            if self.send_command("PING"):
                # Wait for response
                time.sleep(0.1)
                response = self.read_data()
                return response is not None and "PONG" in response
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current serial connection status."""
        status = {
            'connected': self.is_connected,
            'port': self.port,
            'baudrate': self.baudrate,
            'timeout': self.timeout,
            'last_error': self.last_error,
            'stats': self.stats.copy()
        }
        
        if self.serial_conn:
            status.update({
                'port_open': self.serial_conn.is_open,
                'bytes_waiting': self.serial_conn.in_waiting if self.serial_conn.is_open else 0,
                'cts': self.serial_conn.cts if self.serial_conn.is_open else False,
                'dsr': self.serial_conn.dsr if self.serial_conn.is_open else False
            })
        
        return status
    
    def reset_stats(self):
        """Reset connection statistics."""
        self.stats = {
            'bytes_received': 0,
            'bytes_sent': 0,
            'errors': 0,
            'last_communication': None
        }
        self.last_error = None
    
    def emergency_stop(self):
        """Emergency stop - immediately close connection."""
        logger.warning("Emergency stop triggered for serial connection")
        try:
            if self.serial_conn and self.serial_conn.is_open:
                # Send emergency stop command if supported
                self.send_command("EMERGENCY_STOP")
                time.sleep(0.1)
        except:
            pass
        finally:
            self.disconnect()
    
    def get_available_ports(self) -> list:
        """Get list of available serial ports."""
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except Exception as e:
            logger.error(f"Error getting available ports: {e}")
            return []
    
    def change_port(self, new_port: str) -> bool:
        """Change to a different serial port."""
        if self.is_connected:
            self.disconnect()
        
        self.port = new_port
        return self.connect()
    
    def change_baudrate(self, new_baudrate: int) -> bool:
        """Change baudrate."""
        if self.is_connected:
            self.disconnect()
        
        self.baudrate = new_baudrate
        return self.connect()
    
    def flush_buffers(self):
        """Flush input and output buffers."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.reset_input_buffer()
                self.serial_conn.reset_output_buffer()
                logger.debug("Flushed serial buffers")
            except Exception as e:
                logger.error(f"Error flushing buffers: {e}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get detailed connection information."""
        info = {
            'port': self.port,
            'baudrate': self.baudrate,
            'timeout': self.timeout,
            'connected': self.is_connected,
            'available_ports': self.get_available_ports()
        }
        
        if self.serial_conn and self.serial_conn.is_open:
            info.update({
                'device': self.serial_conn.name,
                'settings': self.serial_conn.get_settings(),
                'cts': self.serial_conn.cts,
                'dsr': self.serial_conn.dsr,
                'ri': self.serial_conn.ri,
                'cd': self.serial_conn.cd
            })
        
        return info 