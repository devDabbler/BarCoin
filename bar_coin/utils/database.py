"""
Database operations for BAR-COIN application.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager

from bar_coin.config.settings import DATABASE_CONFIG, BASE_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations for BAR-COIN."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager."""
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Extract path from DATABASE_URL
            db_url = DATABASE_CONFIG["url"]
            if db_url.startswith("sqlite:///"):
                db_path = db_url.replace("sqlite:///", "")
                self.db_path = Path(db_path)
            else:
                self.db_path = BASE_DIR / "data" / "coins.db"
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    total_value DECIMAL(10,2) DEFAULT 0.00,
                    total_coins INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create coin_counts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coin_counts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    denomination DECIMAL(4,2) NOT NULL,
                    count INTEGER DEFAULT 0,
                    value DECIMAL(10,2) DEFAULT 0.00,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            # Create hardware_logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hardware_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    event_type TEXT NOT NULL,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> int:
        """Create a new user."""
        from bar_coin.utils.helpers import hash_password
        password_hash = hash_password(password)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            """, (username, password_hash, email))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE username = ? AND is_active = 1
            """, (username,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_id,))
            conn.commit()
    
    def create_session(self, user_id: int, session_name: str = None) -> int:
        """Create a new counting session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (user_id, start_time, status)
                VALUES (?, CURRENT_TIMESTAMP, 'active')
            """, (user_id,))
            conn.commit()
            return cursor.lastrowid
    
    def end_session(self, session_id: int, total_value: float = None, total_coins: int = None):
        """End a counting session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # If values not provided, calculate from coin counts
            if total_value is None or total_coins is None:
                counts = self.get_session_counts(session_id)
                if total_coins is None:
                    total_coins = sum(counts.values())
                if total_value is None:
                    total_value = sum(denomination * count for denomination, count in counts.items())
            
            cursor.execute("""
                UPDATE sessions 
                SET end_time = CURRENT_TIMESTAMP,
                    total_value = ?,
                    total_coins = ?,
                    status = 'completed'
                WHERE id = ?
            """, (total_value, total_coins, session_id))
            conn.commit()
    
    def add_coin_count(self, session_id: int, denomination: float, count: int = 1):
        """Add coin count to session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if denomination already exists for this session
            cursor.execute("""
                SELECT id, count FROM coin_counts 
                WHERE session_id = ? AND denomination = ?
            """, (session_id, denomination))
            
            existing = cursor.fetchone()
            if existing:
                # Update existing count
                new_count = existing['count'] + count
                value = denomination * new_count
                cursor.execute("""
                    UPDATE coin_counts 
                    SET count = ?, value = ?, timestamp = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_count, value, existing['id']))
            else:
                # Insert new denomination
                value = denomination * count
                cursor.execute("""
                    INSERT INTO coin_counts (session_id, denomination, count, value)
                    VALUES (?, ?, ?, ?)
                """, (session_id, denomination, count, value))
            
            conn.commit()
    
    def get_session_counts(self, session_id: int) -> Dict[float, int]:
        """Get coin counts for a session."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT denomination, count FROM coin_counts
                WHERE session_id = ?
                ORDER BY denomination
            """, (session_id,))
            
            counts = {}
            for row in cursor.fetchall():
                counts[row['denomination']] = row['count']
            return counts
    
    def get_session_summary(self, session_id: int) -> Dict[str, Any]:
        """Get session summary."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, u.username,
                       (SELECT SUM(value) FROM coin_counts WHERE session_id = s.id) as calculated_value,
                       (SELECT SUM(count) FROM coin_counts WHERE session_id = s.id) as calculated_coins
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                summary = dict(row)
                # Use calculated values if available, otherwise use stored values
                summary['total_value'] = summary.get('calculated_value', 0) or summary.get('total_value', 0)
                summary['total_coins'] = summary.get('calculated_coins', 0) or summary.get('total_coins', 0)
                return summary
            return {}
    
    def get_user_sessions(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user's recent sessions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, 
                       (SELECT SUM(value) FROM coin_counts WHERE session_id = s.id) as calculated_value,
                       (SELECT SUM(count) FROM coin_counts WHERE session_id = s.id) as calculated_coins
                FROM sessions s
                WHERE s.user_id = ?
                ORDER BY s.start_time DESC
                LIMIT ?
            """, (user_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_daily_stats(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily statistics for user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    DATE(s.start_time) as date,
                    COUNT(s.id) as sessions,
                    SUM(s.total_value) as total_value,
                    SUM(s.total_coins) as total_coins
                FROM sessions s
                WHERE s.user_id = ? 
                AND s.start_time >= DATE('now', '-{} days')
                GROUP BY DATE(s.start_time)
                ORDER BY date DESC
            """.format(days), (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_hardware_log(self, session_id: Optional[int], event_type: str, message: str) -> int:
        """Add hardware log entry."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO hardware_logs (session_id, event_type, message, timestamp)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (session_id, event_type, message))
            conn.commit()
            return cursor.lastrowid
    
    def get_hardware_logs(self, session_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get hardware logs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute("""
                    SELECT * FROM hardware_logs
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM hardware_logs
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def export_session_data(self, session_id: int) -> Dict[str, Any]:
        """Export session data for CSV/PDF generation."""
        session_summary = self.get_session_summary(session_id)
        coin_counts = self.get_session_counts(session_id)
        hardware_logs = self.get_hardware_logs(session_id)
        
        # Convert coin_counts dict to list format for export
        coin_counts_list = []
        for denomination, count in coin_counts.items():
            coin_counts_list.append({
                'denomination': denomination,
                'count': count,
                'value': denomination * count
            })
        
        return {
            "session_info": {
                "id": session_id,
                "user_id": session_summary.get('user_id'),
                "name": f"Session {session_id}",
                "start_time": session_summary.get('start_time'),
                "end_time": session_summary.get('end_time'),
                "total_value": session_summary.get('total_value', 0),
                "total_coins": session_summary.get('total_coins', 0)
            },
            "coin_counts": coin_counts_list,
            "hardware_logs": hardware_logs
        }

# Global database instance
db = DatabaseManager() 