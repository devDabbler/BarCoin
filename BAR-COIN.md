# BAR-COIN UI Development Prompt

## Project Overview
Create a modern, responsive UI for BAR-COIN (Mobile-base Automated Coin Counter and Segregation for Coin Businesses Management) using Streamlit for the frontend and Python for backend hardware integration.

## Core Requirements

### 1. Authentication System
- **Login Page** matching the design:
  - Logo placement (coin icon with $ symbol)
  - "BAR-COIN" branding with tagline
  - Login button (blue, rounded)
  - Register button (blue, rounded)
  - Clean white card on blue gradient background
  - Mobile-responsive design

### 2. Main Dashboard
After login, create a dashboard with:
- **Real-time Coin Counting Display**
  - Live counter showing total coins processed
  - Breakdown by denomination (₱0.01, ₱0.05, ₱0.10, ₱0.25, ₱1, ₱5, ₱10, ₱20)
  - Total value in Philippine Pesos (₱)
  - Processing speed indicator
  
- **Control Panel**
  - Start/Stop/Pause buttons for hardware
  - Reset counter button
  - Emergency stop (red, prominent)
  
- **Statistics Section**
  - Session statistics
  - Daily/Weekly/Monthly summaries
  - Graphical representations (pie charts for coin distribution)
  
- **Hardware Status**
  - Connection status indicator
  - Device health monitoring
  - Error/warning messages

### 3. Architecture Specifications

```python
# Project Structure
bar-coin/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Dependencies
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration settings
├── hardware/
│   ├── __init__.py
│   ├── coin_counter.py      # Hardware interface
│   ├── mock_hardware.py     # Mock for testing
│   └── serial_handler.py    # Serial communication
├── components/
│   ├── __init__.py
│   ├── auth.py             # Authentication component
│   ├── dashboard.py        # Dashboard component
│   └── statistics.py       # Statistics component
├── utils/
│   ├── __init__.py
│   ├── database.py         # SQLite for data storage
│   └── helpers.py          # Utility functions
├── static/
│   └── logo.png            # BAR-COIN logo
└── data/
    └── coins.db            # SQLite database
```

### 4. Technical Implementation Details

#### Frontend (Streamlit)
```python
# Key Streamlit features to implement:
- st.set_page_config() for custom theming
- Session state for user authentication
- Real-time updates using st.empty() containers
- Custom CSS for matching the design aesthetic
- Responsive columns for mobile compatibility
```

#### Hardware Integration
```python
# Serial Communication Protocol
- Baud rate: 9600 (configurable)
- Data format: JSON messages
- Message structure:
  {
    "type": "coin_detected",
    "denomination": 5.00,  # Philippine Peso value
    "timestamp": "2024-01-01T12:00:00",
    "sensor_id": 1
  }
```

#### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMP
);

-- Counting sessions
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    total_value DECIMAL,
    total_coins INTEGER
);

-- Coin counts
CREATE TABLE coin_counts (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    denomination DECIMAL,
    count INTEGER,
    timestamp TIMESTAMP
);
```

### 5. Key Features to Implement

1. **Mock Hardware Mode**
   - Toggle between real hardware and simulation
   - Simulated coin insertion for testing
   - Configurable coin flow rates

2. **Export Functionality**
   - CSV export of session data
   - PDF reports generation
   - Data visualization exports

3. **Real-time Updates**
   - WebSocket-like updates every 100ms
   - Smooth animations for counters
   - Audio feedback for coin detection (optional)

4. **Error Handling**
   - Graceful hardware disconnection handling
   - User-friendly error messages
   - Automatic reconnection attempts

### 6. UI/UX Specifications

```python
# Color Scheme
PRIMARY_BLUE = "#1E90FF"
SECONDARY_BLUE = "#4169E1"
WHITE = "#FFFFFF"
GRAY = "#F0F0F0"
SUCCESS_GREEN = "#32CD32"
ERROR_RED = "#FF6347"

# Font Specifications
HEADER_FONT = "Arial, sans-serif"
BODY_FONT = "Helvetica, sans-serif"

# Component Styling
BUTTON_STYLE = """
    background-color: #1E90FF;
    color: white;
    border-radius: 25px;
    padding: 10px 30px;
    border: none;
    font-size: 16px;
"""
```

### 7. Sample Implementation Starter

```python
# app.py starter code
import streamlit as st
import time
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="BAR-COIN",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(180deg, #1E90FF 0%, #4169E1 100%);
    }
    .stButton>button {
        background-color: #1E90FF;
        color: white;
        border-radius: 25px;
        border: none;
        padding: 10px 30px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'coin_count' not in st.session_state:
    st.session_state.coin_count = {
        0.01: 0,   # 1 sentimo
        0.05: 0,   # 5 sentimo
        0.10: 0,   # 10 sentimo
        0.25: 0,   # 25 sentimo
        1.00: 0,   # ₱1
        5.00: 0,   # ₱5
        10.00: 0,  # ₱10
        20.00: 0   # ₱20
    }

# Main app logic here...
```

### 8. Hardware Communication Protocol

```python
# hardware/coin_counter.py example
import serial
import json
import threading
from queue import Queue

class CoinCounter:
    def __init__(self, port='COM3', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.data_queue = Queue()
        self.is_running = False
        
    def connect(self):
        """Establish serial connection with hardware"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate)
            self.is_running = True
            return True
        except Exception as e:
            return False
    
    def read_data(self):
        """Continuously read data from hardware"""
        while self.is_running:
            if self.serial_conn and self.serial_conn.in_waiting:
                data = self.serial_conn.readline().decode('utf-8').strip()
                try:
                    coin_data = json.loads(data)
                    self.data_queue.put(coin_data)
                except json.JSONDecodeError:
                    pass
```

### 9. Performance Optimizations

1. **Caching Strategy**
   - Use Streamlit's @st.cache_data for expensive operations
   - Cache database queries
   - Implement session-based caching

2. **Efficient Updates**
   - Batch database writes
   - Update UI components selectively
   - Use delta updates for counters

3. **Resource Management**
   - Proper thread management for hardware communication
   - Connection pooling for database
   - Memory-efficient data structures

### 10. Testing Requirements

1. **Unit Tests**
   - Hardware communication mocking
   - Database operations
   - Authentication flow

2. **Integration Tests**
   - Full user flow testing
   - Hardware simulation testing
   - Performance benchmarking

3. **User Acceptance Criteria**
   - < 100ms UI response time
   - 99.9% accuracy in coin counting
   - Graceful degradation without hardware

## Deliverables

1. Fully functional Streamlit application
2. Hardware integration module with mock mode
3. Documentation (README, API docs, user guide)
4. Docker configuration for easy deployment
5. Test suite with >80% coverage

## Additional Considerations

- Implement logging for debugging and audit trails
- Add multi-language support (prepare i18n structure - English/Filipino)
- Consider adding a mobile app API endpoint
- Implement data backup and recovery features
- Add user roles (admin, operator, viewer)
- **Philippine Peso Formatting**:
  - Use proper currency symbol (₱)
  - Format numbers with comma separators (e.g., ₱1,234.56)
  - Handle sentimo (centavo) denominations correctly
  - Consider adding coin images for Philippine coins

### Philippine Coin Specifications

```python
# Philippine coin denominations and properties
PHILIPPINE_COINS = {
    0.01: {"name": "1 sentimo", "diameter": 15.0, "weight": 1.9, "material": "copper-plated steel"},
    0.05: {"name": "5 sentimo", "diameter": 16.7, "weight": 1.9, "material": "copper-plated steel"},
    0.10: {"name": "10 sentimo", "diameter": 17.0, "weight": 2.5, "material": "steel"},
    0.25: {"name": "25 sentimo", "diameter": 20.0, "weight": 3.8, "material": "brass"},
    1.00: {"name": "1 piso", "diameter": 24.0, "weight": 6.1, "material": "nickel-plated steel"},
    5.00: {"name": "5 piso", "diameter": 27.0, "weight": 7.7, "material": "nickel-plated steel"},
    10.00: {"name": "10 piso", "diameter": 26.5, "weight": 8.0, "material": "bi-metallic"},
    20.00: {"name": "20 piso", "diameter": 30.0, "weight": 11.5, "material": "bi-metallic"}
}

# Currency formatting helper
def format_peso(amount):
    return f"₱{amount:,.2f}"
```

## Development Phases

### Phase 1: Core UI (Week 1)
- Login/Register screens
- Basic dashboard layout
- Mock data display

### Phase 2: Hardware Integration (Week 2)
- Serial communication setup
- Real-time data flow
- Error handling

### Phase 3: Features & Polish (Week 3)
- Statistics and reporting
- Export functionality
- Performance optimization

### Phase 4: Testing & Deployment (Week 4)
- Comprehensive testing
- Documentation
- Deployment setup