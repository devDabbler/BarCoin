# BAR-COIN

**Mobile-base Automated Coin Counter and Segregation for Coin Businesses Management**

A modern, responsive web application for automated coin counting and segregation using Streamlit and Python hardware integration.

## Features

- 🔐 **Secure Authentication System** - User login and registration
- 🪙 **Real-time Coin Counting** - Live counter with Philippine Peso denominations
- 📊 **Interactive Dashboard** - Real-time statistics and visualizations
- 🔧 **Hardware Integration** - Serial communication with coin counting hardware
- 📈 **Comprehensive Reporting** - Session statistics and data export
- 📱 **Mobile Responsive** - Optimized for mobile and desktop use

## Philippine Coin Support

Supports all Philippine Peso denominations:
- ₱0.01 (1 sentimo)
- ₱0.05 (5 sentimo)
- ₱0.10 (10 sentimo)
- ₱0.25 (25 sentimo)
- ₱1.00 (1 piso)
- ₱5.00 (5 piso)
- ₱10.00 (10 piso)
- ₱20.00 (20 piso)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)
- Serial port access (for hardware integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bar-coin
   ```

2. **Install Poetry (if not already installed)**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Quick setup (recommended)**
   ```bash
   python setup.py
   ```
   
   This will:
   - Check Python version
   - Install Poetry if needed
   - Install all dependencies
   - Create `.env` file from template
   - Test the setup

4. **Run the application**
   ```bash
   python run.py
   ```
   
   This will:
   - Check Poetry installation
   - Install dependencies if needed
   - Create `.env` file from template
   - Initialize the database
   - Start the Streamlit application

5. **Alternative manual setup**
   ```bash
   # Install dependencies
   poetry install
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run the application
   poetry run streamlit run bar_coin/app.py
   ```

The application will be available at `http://localhost:8501`

## Project Structure

```
bar-coin/
├── bar_coin/
│   ├── app.py                    # Main Streamlit application
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py          # Configuration settings
│   ├── hardware/
│   │   ├── __init__.py
│   │   ├── coin_counter.py      # Hardware interface
│   │   ├── mock_hardware.py     # Mock for testing
│   │   └── serial_handler.py    # Serial communication
│   ├── components/
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication component
│   │   ├── dashboard.py        # Dashboard component
│   │   └── statistics.py       # Statistics component
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLite for data storage
│   │   └── helpers.py          # Utility functions
│   └── static/
│       └── logo.png            # BAR-COIN logo
├── data/
│   └── coins.db                # SQLite database
├── tests/                      # Test suite
├── pyproject.toml             # Poetry configuration
└── README.md                  # This file
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///data/coins.db

# Hardware Configuration
SERIAL_PORT=COM3
BAUD_RATE=9600

# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Mock Mode (for testing without hardware)
MOCK_HARDWARE=True
```

### Hardware Setup

1. **Serial Connection**
   - Connect coin counting hardware via USB
   - Configure port and baud rate in settings
   - Test connection using the hardware status panel

2. **Mock Mode**
   - Enable mock mode for testing without hardware
   - Simulates coin insertion for development

## Usage

### Authentication

1. Register a new account or login with existing credentials
2. Secure password hashing with bcrypt
3. Session-based authentication

### Dashboard

1. **Real-time Counter**
   - Live display of total coins processed
   - Breakdown by denomination
   - Total value in Philippine Pesos

2. **Control Panel**
   - Start/Stop/Pause hardware operations
   - Reset counter
   - Emergency stop functionality

3. **Statistics**
   - Session summaries
   - Historical data visualization
   - Export capabilities

### Hardware Integration

- **Serial Communication**: JSON-based protocol
- **Real-time Updates**: 100ms refresh rate
- **Error Handling**: Graceful disconnection handling
- **Auto-reconnection**: Automatic retry on connection loss

## Development

### Running Tests

```bash
# Run all tests (recommended)
python run_tests.py

# Alternative: Run with Poetry
poetry run pytest

# Run with coverage
poetry run pytest --cov=bar_coin

# Run specific test file
poetry run pytest tests/test_hardware.py
```

### Code Quality

```bash
# Format code
poetry run black bar_coin/

# Lint code
poetry run flake8 bar_coin/

# Type checking
poetry run mypy bar_coin/
```

### Adding New Features

1. Follow the existing project structure
2. Add tests for new functionality
3. Update documentation
4. Ensure mobile responsiveness

## API Documentation

### Hardware Communication Protocol

```json
{
  "type": "coin_detected",
  "denomination": 5.00,
  "timestamp": "2024-01-01T12:00:00",
  "sensor_id": 1
}
```

### Database Schema

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

## Deployment

### Production Setup

1. Set `DEBUG=False` in environment
2. Configure production database
3. Set up reverse proxy (nginx)
4. Enable SSL/TLS
5. Configure logging

### Running in Production

```bash
# Install dependencies
poetry install --no-dev

# Set production environment
export DEBUG=False
export SECRET_KEY=your-production-secret-key

# Run the application
poetry run streamlit run bar_coin/app.py --server.port 8501 --server.address 0.0.0.0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

## Changelog

### v0.1.0 (Current)
- Initial release
- Basic coin counting functionality
- Authentication system
- Real-time dashboard
- Hardware integration
- Mock mode for testing 