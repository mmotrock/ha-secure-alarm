"""Database management for Secure Alarm System."""
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import bcrypt

from .const import (
    TABLE_USERS,
    TABLE_CONFIG,
    TABLE_EVENTS,
    TABLE_FAILED_ATTEMPTS,
    TABLE_ZONES,
    DEFAULT_ENTRY_DELAY,
    DEFAULT_EXIT_DELAY,
    DEFAULT_ALARM_DURATION,
    MAX_FAILED_ATTEMPTS,
    LOCKOUT_DURATION,
)

_LOGGER = logging.getLogger(__name__)

class AlarmDatabase:
    """Database handler for alarm system."""
    
    def __init__(self, db_path: str):
        """Initialize the database."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self) -> None:
        """Initialize database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_USERS} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pin_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                is_duress INTEGER DEFAULT 0,
                enabled INTEGER DEFAULT 1,
                phone TEXT,
                email TEXT,
                has_separate_lock_pin INTEGER DEFAULT 0,
                lock_pin_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                use_count INTEGER DEFAULT 0
            )
        ''')
        
        # Configuration table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_CONFIG} (
                id INTEGER PRIMARY KEY DEFAULT 1,
                entry_delay INTEGER DEFAULT {DEFAULT_ENTRY_DELAY},
                exit_delay INTEGER DEFAULT {DEFAULT_EXIT_DELAY},
                alarm_duration INTEGER DEFAULT {DEFAULT_ALARM_DURATION},
                trigger_doors TEXT,
                notification_mobile INTEGER DEFAULT 1,
                notification_sms INTEGER DEFAULT 0,
                sms_numbers TEXT,
                lock_delay_home INTEGER DEFAULT 0,
                lock_delay_away INTEGER DEFAULT 60,
                close_delay_home INTEGER DEFAULT 0,
                close_delay_away INTEGER DEFAULT 60,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Events/audit log table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_EVENTS} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                user_id INTEGER,
                user_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                state_from TEXT,
                state_to TEXT,
                zone_entity_id TEXT,
                details TEXT,
                is_duress INTEGER DEFAULT 0
            )
        ''')
        
        # Failed attempts table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_FAILED_ATTEMPTS} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_code TEXT,
                attempt_type TEXT
            )
        ''')
        
        # Zones table
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_ZONES} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id TEXT UNIQUE NOT NULL,
                zone_name TEXT NOT NULL,
                zone_type TEXT NOT NULL,
                enabled_away INTEGER DEFAULT 1,
                enabled_home INTEGER DEFAULT 1,
                bypassed INTEGER DEFAULT 0,
                bypass_until TIMESTAMP,
                last_state_change TIMESTAMP
            )
        ''')

        # User lock access table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_lock_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lock_entity_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, lock_entity_id),
                FOREIGN KEY (user_id) REFERENCES alarm_users(id) ON DELETE CASCADE
            )
        ''')
        
        # Insert default config if not exists
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_CONFIG}")
        if cursor.fetchone()[0] == 0:
            cursor.execute(f'''
                INSERT INTO {TABLE_CONFIG} (id) VALUES (1)
            ''')
        
        # Create indexes
        cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_events_timestamp 
            ON {TABLE_EVENTS}(timestamp DESC)
        ''')
        
        cursor.execute(f'''
            CREATE INDEX IF NOT EXISTS idx_failed_attempts_timestamp 
            ON {TABLE_FAILED_ATTEMPTS}(timestamp DESC)
        ''')
        
        conn.commit()
        conn.close()
        
        _LOGGER.info("Database initialized successfully")
    
    def hash_pin(self, pin: str) -> str:
        """Hash a PIN using bcrypt."""
        return bcrypt.hashpw(pin.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_pin(self, pin: str, pin_hash: str) -> bool:
        """Verify a PIN against its hash."""
        try:
            return bcrypt.checkpw(pin.encode('utf-8'), pin_hash.encode('utf-8'))
        except Exception as e:
            _LOGGER.error(f"Error verifying PIN: {e}")
            return False
    
    def add_user(self, name: str, pin: str, is_admin: bool = False, 
                is_duress: bool = False, phone: Optional[str] = None,
                email: Optional[str] = None, has_separate_lock_pin: bool = False,
                lock_pin: Optional[str] = None) -> Optional[int]:
        """Add a new user to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            pin_hash = self.hash_pin(pin)
            lock_pin_hash = self.hash_pin(lock_pin) if lock_pin else None
            
            cursor.execute(f'''
                INSERT INTO {TABLE_USERS} 
                (name, pin_hash, is_admin, is_duress, phone, email, 
                has_separate_lock_pin, lock_pin_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, pin_hash, int(is_admin), int(is_duress), phone, email,
                int(has_separate_lock_pin), lock_pin_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            self.log_event("user_added", user_id=user_id, user_name=name)
            _LOGGER.info(f"User {name} added with ID {user_id}")
            
            return user_id
        except Exception as e:
            _LOGGER.error(f"Error adding user: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, pin: str, code: Optional[str] = None) -> Optional[Dict]:
        """Authenticate a user by PIN."""
        if self.is_locked_out():
            _LOGGER.warning("System is locked out due to failed attempts")
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                SELECT id, name, pin_hash, is_admin, is_duress, enabled
                FROM {TABLE_USERS}
                WHERE enabled = 1
            ''')
            
            users = cursor.fetchall()
            
            for user in users:
                if self.verify_pin(pin, user['pin_hash']):
                    # Update last used
                    cursor.execute(f'''
                        UPDATE {TABLE_USERS}
                        SET last_used = CURRENT_TIMESTAMP,
                            use_count = use_count + 1
                        WHERE id = ?
                    ''', (user['id'],))
                    conn.commit()
                    
                    return {
                        'id': user['id'],
                        'name': user['name'],
                        'is_admin': bool(user['is_admin']),
                        'is_duress': bool(user['is_duress']),
                    }
            
            # Failed authentication
            self.log_failed_attempt(code)
            return None
            
        except Exception as e:
            _LOGGER.error(f"Error authenticating user: {e}")
            return None
        finally:
            conn.close()
    
    def remove_user(self, user_id: int) -> bool:
        """Remove a user from the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                UPDATE {TABLE_USERS}
                SET enabled = 0
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            self.log_event("user_removed", user_id=user_id)
            return True
        except Exception as e:
            _LOGGER.error(f"Error removing user: {e}")
            return False
        finally:
            conn.close()
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM {TABLE_CONFIG} WHERE id = 1")
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return {}
        finally:
            conn.close()
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            
            cursor.execute(f'''
                UPDATE {TABLE_CONFIG}
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            ''', values)
            
            conn.commit()
            self.log_event("config_updated", details=json.dumps(updates))
            return True
        except Exception as e:
            _LOGGER.error(f"Error updating config: {e}")
            return False
        finally:
            conn.close()
    
    def log_event(self, event_type: str, user_id: Optional[int] = None,
                  user_name: Optional[str] = None, state_from: Optional[str] = None,
                  state_to: Optional[str] = None, zone_entity_id: Optional[str] = None,
                  details: Optional[str] = None, is_duress: bool = False) -> None:
        """Log an event to the audit log."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                INSERT INTO {TABLE_EVENTS}
                (event_type, user_id, user_name, state_from, state_to, 
                 zone_entity_id, details, is_duress)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_type, user_id, user_name, state_from, state_to,
                  zone_entity_id, details, int(is_duress)))
            
            conn.commit()
        except Exception as e:
            _LOGGER.error(f"Error logging event: {e}")
        finally:
            conn.close()
    
    def log_failed_attempt(self, user_code: Optional[str] = None) -> None:
        """Log a failed authentication attempt."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                INSERT INTO {TABLE_FAILED_ATTEMPTS}
                (user_code, attempt_type)
                VALUES (?, 'pin_auth')
            ''', (user_code,))
            
            conn.commit()
        except Exception as e:
            _LOGGER.error(f"Error logging failed attempt: {e}")
        finally:
            conn.close()
    
    def is_locked_out(self) -> bool:
        """Check if system is locked out due to failed attempts."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            lockout_time = datetime.now() - timedelta(seconds=LOCKOUT_DURATION)
            
            cursor.execute(f'''
                SELECT COUNT(*) as count
                FROM {TABLE_FAILED_ATTEMPTS}
                WHERE timestamp > ?
            ''', (lockout_time,))
            
            count = cursor.fetchone()['count']
            return count >= MAX_FAILED_ATTEMPTS
        finally:
            conn.close()
    
    def get_failed_attempts_count(self) -> int:
        """Get recent failed attempts count."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            lockout_time = datetime.now() - timedelta(seconds=LOCKOUT_DURATION)
            
            cursor.execute(f'''
                SELECT COUNT(*) as count
                FROM {TABLE_FAILED_ATTEMPTS}
                WHERE timestamp > ?
            ''', (lockout_time,))
            
            return cursor.fetchone()['count']
        finally:
            conn.close()
    
    def clear_failed_attempts(self) -> None:
        """Clear failed attempts (called on successful auth)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"DELETE FROM {TABLE_FAILED_ATTEMPTS}")
            conn.commit()
        finally:
            conn.close()
    
    def add_zone(self, entity_id: str, zone_name: str, zone_type: str,
                 enabled_away: bool = True, enabled_home: bool = True) -> bool:
        """Add or update a zone."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                INSERT OR REPLACE INTO {TABLE_ZONES}
                (entity_id, zone_name, zone_type, enabled_away, enabled_home, last_state_change)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (entity_id, zone_name, zone_type, int(enabled_away), int(enabled_home)))
            
            conn.commit()
            return True
        except Exception as e:
            _LOGGER.error(f"Error adding zone: {e}")
            return False
        finally:
            conn.close()
    
    def update_zone_state_change(self, entity_id: str) -> bool:
        """Update the last state change timestamp for a zone."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                UPDATE {TABLE_ZONES}
                SET last_state_change = CURRENT_TIMESTAMP
                WHERE entity_id = ?
            ''', (entity_id,))
            
            conn.commit()
            return True
        except Exception as e:
            _LOGGER.error(f"Error updating zone state change: {e}")
            return False
        finally:
            conn.close()
    
    def get_zones(self, mode: Optional[str] = None) -> List[Dict]:
        """Get all zones, optionally filtered by mode."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"SELECT * FROM {TABLE_ZONES}"
            
            if mode == "armed_away":
                query += " WHERE enabled_away = 1"
            elif mode == "armed_home":
                query += " WHERE enabled_home = 1"
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def set_zone_bypass(self, entity_id: str, bypassed: bool,
                        bypass_duration: Optional[int] = None) -> bool:
        """Set zone bypass status."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            bypass_until = None
            if bypassed and bypass_duration:
                bypass_until = datetime.now() + timedelta(seconds=bypass_duration)
            
            cursor.execute(f'''
                UPDATE {TABLE_ZONES}
                SET bypassed = ?, bypass_until = ?
                WHERE entity_id = ?
            ''', (int(bypassed), bypass_until, entity_id))
            
            conn.commit()
            self.log_event("zone_bypass", zone_entity_id=entity_id,
                          details=f"Bypassed: {bypassed}")
            return True
        except Exception as e:
            _LOGGER.error(f"Error setting zone bypass: {e}")
            return False
        finally:
            conn.close()
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events from audit log."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                SELECT * FROM {TABLE_EVENTS}
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_users(self) -> List[Dict]:
        """Get all users from database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                SELECT id, name, is_admin, is_duress, enabled, phone, email,
                    has_separate_lock_pin, created_at, last_used, use_count
                FROM {TABLE_USERS}
                ORDER BY name
            ''')
            
            users = [dict(row) for row in cursor.fetchall()]
            
            # Get lock access for each user
            for user in users:
                cursor.execute('''
                    SELECT lock_entity_id FROM user_lock_access
                    WHERE user_id = ?
                ''', (user['id'],))
                user['accessible_locks'] = [row['lock_entity_id'] for row in cursor.fetchall()]
            
            return users
        finally:
            conn.close()

    def update_user(self, user_id: int, name: Optional[str] = None,
                pin: Optional[str] = None, is_admin: Optional[bool] = None,
                phone: Optional[str] = None, email: Optional[str] = None,
                has_separate_lock_pin: Optional[bool] = None,
                lock_pin: Optional[str] = None) -> bool:
        """Update user information."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            values = []
            
            if name is not None:
                updates.append("name = ?")
                values.append(name)
            
            if pin is not None:
                updates.append("pin_hash = ?")
                values.append(self.hash_pin(pin))
            
            if is_admin is not None:
                updates.append("is_admin = ?")
                values.append(int(is_admin))
            
            if phone is not None:
                updates.append("phone = ?")
                values.append(phone)
            
            if email is not None:
                updates.append("email = ?")
                values.append(email)
            
            if has_separate_lock_pin is not None:
                updates.append("has_separate_lock_pin = ?")
                values.append(int(has_separate_lock_pin))
            
            if lock_pin is not None:
                updates.append("lock_pin_hash = ?")
                values.append(self.hash_pin(lock_pin))
            
            if not updates:
                return False
            
            values.append(user_id)
            
            cursor.execute(f'''
                UPDATE {TABLE_USERS}
                SET {", ".join(updates)}
                WHERE id = ?
            ''', values)
            
            conn.commit()
            
            self.log_event("user_updated", user_id=user_id)
            return cursor.rowcount > 0
        except Exception as e:
            _LOGGER.error(f"Error updating user: {e}")
            return False
        finally:
            conn.close()

    def get_user_lock_pin(self, user_id: int) -> Optional[str]:
        """Get user's lock PIN hash if they have a separate one."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                SELECT lock_pin_hash, has_separate_lock_pin
                FROM {TABLE_USERS}
                WHERE id = ? AND enabled = 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            if row and row['has_separate_lock_pin']:
                return row['lock_pin_hash']
            return None
        finally:
            conn.close()

    def authenticate_lock_pin(self, pin: str) -> Optional[Dict]:
        """Authenticate a user by their lock PIN."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                SELECT id, name, lock_pin_hash
                FROM {TABLE_USERS}
                WHERE enabled = 1 AND has_separate_lock_pin = 1
            ''')
            
            users = cursor.fetchall()
            
            for user in users:
                if user['lock_pin_hash'] and self.verify_pin(pin, user['lock_pin_hash']):
                    return {
                        'id': user['id'],
                        'name': user['name'],
                    }
            
            return None
        except Exception as e:
            _LOGGER.error(f"Error authenticating lock PIN: {e}")
            return None
        finally:
            conn.close()

    def set_user_lock_access(self, user_id: int, lock_entity_id: str, can_access: bool) -> bool:
        """Set whether a user can access a specific lock."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if can_access:
                cursor.execute('''
                    INSERT OR IGNORE INTO user_lock_access (user_id, lock_entity_id)
                    VALUES (?, ?)
                ''', (user_id, lock_entity_id))
            else:
                cursor.execute('''
                    DELETE FROM user_lock_access
                    WHERE user_id = ? AND lock_entity_id = ?
                ''', (user_id, lock_entity_id))
            
            conn.commit()
            return True
        except Exception as e:
            _LOGGER.error(f"Error setting user lock access: {e}")
            return False
        finally:
            conn.close()

    def get_user_lock_access(self, user_id: int) -> List[str]:
        """Get list of lock entity IDs the user can access."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT lock_entity_id FROM user_lock_access
                WHERE user_id = ?
            ''', (user_id,))
            
            return [row['lock_entity_id'] for row in cursor.fetchall()]
        except Exception as e:
            _LOGGER.error(f"Error getting user lock access: {e}")
            return []
        finally:
            conn.close()