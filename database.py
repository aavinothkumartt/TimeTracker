"""Database operations for TimeTracker using SQLite."""
import sqlite3
from contextlib import contextmanager
import config
import utils


class Database:
    """Handle all database operations for TimeTracker."""

    def __init__(self, db_path=None):
        """Initialize database connection."""
        self.db_path = db_path or config.DATABASE_PATH
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_db(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Work sessions table (for timer-based tracking)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS work_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration INTEGER,
                    task_name TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Manual entries table (for manually entered time)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS manual_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    task_name TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def create_work_session(self, task_name=None):
        """
        Create a new work session.

        Args:
            task_name (str, optional): Name/description of the task

        Returns:
            int: ID of the created session
        """
        start_time = utils.get_current_datetime()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO work_sessions (start_time, task_name)
                VALUES (?, ?)
            ''', (start_time, task_name))
            return cursor.lastrowid

    def end_work_session(self, session_id):
        """
        End a work session by setting end_time and calculating duration.

        Args:
            session_id (int): ID of the session to end

        Returns:
            bool: True if successful, False otherwise
        """
        end_time = utils.get_current_datetime()

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get the start time
            cursor.execute('SELECT start_time FROM work_sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()

            if not row:
                return False

            start_time = row['start_time']
            duration = utils.calculate_duration_seconds(start_time, end_time)

            # Update the session
            cursor.execute('''
                UPDATE work_sessions
                SET end_time = ?, duration = ?
                WHERE id = ?
            ''', (end_time, duration, session_id))

            return True

    def add_manual_entry(self, task_name, duration, date=None, notes=None):
        """
        Add a manual time entry.

        Args:
            task_name (str): Name/description of the task
            duration (int): Duration in seconds
            date (str, optional): Date of entry (defaults to today)
            notes (str, optional): Additional notes

        Returns:
            int: ID of the created entry
        """
        if date is None:
            date = utils.get_today_date()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO manual_entries (date, duration, task_name, notes)
                VALUES (?, ?, ?, ?)
            ''', (date, duration, task_name, notes))
            return cursor.lastrowid

    def get_active_session(self):
        """
        Get the currently active work session (if any).

        Returns:
            dict: Session data, or None if no active session
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM work_sessions
                WHERE end_time IS NULL
                ORDER BY start_time DESC
                LIMIT 1
            ''')
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def get_today_sessions(self):
        """
        Get all work sessions for today.

        Returns:
            list: List of session dictionaries
        """
        today = utils.get_today_date()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM work_sessions
                WHERE date(start_time) = ?
                ORDER BY start_time
            ''', (today,))
            return [dict(row) for row in cursor.fetchall()]

    def get_today_manual_entries(self):
        """
        Get all manual entries for today.

        Returns:
            list: List of entry dictionaries
        """
        today = utils.get_today_date()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM manual_entries
                WHERE date = ?
                ORDER BY created_at
            ''', (today,))
            return [dict(row) for row in cursor.fetchall()]

    def get_session(self, session_id):
        """
        Get a specific work session by ID.

        Args:
            session_id (int): Session ID

        Returns:
            dict: Session data, or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM work_sessions WHERE id = ?', (session_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

    def delete_session(self, session_id):
        """
        Delete a work session.

        Args:
            session_id (int): Session ID

        Returns:
            bool: True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM work_sessions WHERE id = ?', (session_id,))
            return True

    def delete_manual_entry(self, entry_id):
        """
        Delete a manual entry.

        Args:
            entry_id (int): Entry ID

        Returns:
            bool: True if successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM manual_entries WHERE id = ?', (entry_id,))
            return True
