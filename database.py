"""Database operations for TimeTracker with SQLite and PostgreSQL support."""
import sqlite3
import os
from contextlib import contextmanager
import config
import utils


class Database:
    """Handle all database operations for TimeTracker."""

    def __init__(self, db_path=None):
        """Initialize database connection."""
        self.db_path = db_path or config.DATABASE_PATH
        self.database_url = os.getenv("DATABASE_URL")
        self.is_postgres = self.database_url and self.database_url.startswith("postgresql://")
        self.init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections (SQLite or PostgreSQL)."""
        if self.is_postgres:
            try:
                import psycopg2
                import psycopg2.extras
            except ImportError:
                raise ImportError("psycopg2 is required for PostgreSQL support")

            conn = psycopg2.connect(self.database_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
        else:
            # SQLite
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
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

            if self.is_postgres:
                # PostgreSQL syntax
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS work_sessions (
                        id SERIAL PRIMARY KEY,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        duration INTEGER,
                        task_name TEXT,
                        project TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS manual_entries (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        duration INTEGER NOT NULL,
                        task_name TEXT NOT NULL,
                        project TEXT,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            else:
                # SQLite syntax
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS work_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        duration INTEGER,
                        task_name TEXT,
                        project TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS manual_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        duration INTEGER NOT NULL,
                        task_name TEXT NOT NULL,
                        project TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

            # Migrate existing databases (add project column if it doesn't exist)
            self._migrate_add_project_column(cursor)

    def _migrate_add_project_column(self, cursor):
        """Add project column to existing tables if it doesn't exist."""
        try:
            # Check if column exists by trying to select it
            cursor.execute('SELECT project FROM work_sessions LIMIT 1')
        except:
            # Column doesn't exist, add it
            try:
                cursor.execute('ALTER TABLE work_sessions ADD COLUMN project TEXT')
                cursor.execute('ALTER TABLE manual_entries ADD COLUMN project TEXT')
            except:
                pass  # Column already exists or other error

    def create_work_session(self, task_name=None, project=None):
        """
        Create a new work session.

        Args:
            task_name (str, optional): Name/description of the task
            project (str, optional): Project/category name

        Returns:
            int: ID of the created session
        """
        start_time = utils.get_current_datetime()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if self.is_postgres:
                cursor.execute('''
                    INSERT INTO work_sessions (start_time, task_name, project)
                    VALUES (%s, %s, %s) RETURNING id
                ''', (start_time, task_name, project))
                return cursor.fetchone()['id']
            else:
                cursor.execute('''
                    INSERT INTO work_sessions (start_time, task_name, project)
                    VALUES (?, ?, ?)
                ''', (start_time, task_name, project))
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

    def add_manual_entry(self, task_name, duration, date=None, project=None, notes=None):
        """
        Add a manual time entry.

        Args:
            task_name (str): Name/description of the task
            duration (int): Duration in seconds
            date (str, optional): Date of entry (defaults to today)
            project (str, optional): Project/category name
            notes (str, optional): Additional notes

        Returns:
            int: ID of the created entry
        """
        if date is None:
            date = utils.get_today_date()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if self.is_postgres:
                cursor.execute('''
                    INSERT INTO manual_entries (date, duration, task_name, project, notes)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                ''', (date, duration, task_name, project, notes))
                return cursor.fetchone()['id']
            else:
                cursor.execute('''
                    INSERT INTO manual_entries (date, duration, task_name, project, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (date, duration, task_name, project, notes))
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
            param = '%s' if self.is_postgres else '?'
            cursor.execute(f'DELETE FROM manual_entries WHERE id = {param}', (entry_id,))
            return True

    def update_work_session(self, session_id, task_name=None, project=None, notes=None):
        """
        Update a work session's details.

        Args:
            session_id (int): Session ID
            task_name (str, optional): New task name
            project (str, optional): New project name
            notes (str, optional): New notes

        Returns:
            bool: True if successful
        """
        updates = []
        values = []

        if task_name is not None:
            updates.append("task_name = " + ('%s' if self.is_postgres else '?'))
            values.append(task_name)
        if project is not None:
            updates.append("project = " + ('%s' if self.is_postgres else '?'))
            values.append(project)
        if notes is not None:
            updates.append("notes = " + ('%s' if self.is_postgres else '?'))
            values.append(notes)

        if not updates:
            return False

        values.append(session_id)
        param = '%s' if self.is_postgres else '?'

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE work_sessions SET {', '.join(updates)} WHERE id = {param}"
            cursor.execute(query, tuple(values))
            return True

    def update_manual_entry(self, entry_id, task_name=None, duration=None, project=None, notes=None):
        """
        Update a manual entry's details.

        Args:
            entry_id (int): Entry ID
            task_name (str, optional): New task name
            duration (int, optional): New duration in seconds
            project (str, optional): New project name
            notes (str, optional): New notes

        Returns:
            bool: True if successful
        """
        updates = []
        values = []

        if task_name is not None:
            updates.append("task_name = " + ('%s' if self.is_postgres else '?'))
            values.append(task_name)
        if duration is not None:
            updates.append("duration = " + ('%s' if self.is_postgres else '?'))
            values.append(duration)
        if project is not None:
            updates.append("project = " + ('%s' if self.is_postgres else '?'))
            values.append(project)
        if notes is not None:
            updates.append("notes = " + ('%s' if self.is_postgres else '?'))
            values.append(notes)

        if not updates:
            return False

        values.append(entry_id)
        param = '%s' if self.is_postgres else '?'

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE manual_entries SET {', '.join(updates)} WHERE id = {param}"
            cursor.execute(query, tuple(values))
            return True

    def get_sessions_by_date(self, date):
        """
        Get all work sessions for a specific date.

        Args:
            date (str): Date in YYYY-MM-DD format

        Returns:
            list: List of session dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            param = '%s' if self.is_postgres else '?'
            cursor.execute(f'''
                SELECT * FROM work_sessions
                WHERE date(start_time) = {param}
                ORDER BY start_time
            ''', (date,))
            return [dict(row) for row in cursor.fetchall()]

    def get_entries_by_date(self, date):
        """
        Get all manual entries for a specific date.

        Args:
            date (str): Date in YYYY-MM-DD format

        Returns:
            list: List of entry dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            param = '%s' if self.is_postgres else '?'
            cursor.execute(f'''
                SELECT * FROM manual_entries
                WHERE date = {param}
                ORDER BY created_at
            ''', (date,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_projects(self):
        """
        Get a distinct list of all projects from both tables.

        Returns:
            list: List of project names
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT project FROM work_sessions
                WHERE project IS NOT NULL
                UNION
                SELECT DISTINCT project FROM manual_entries
                WHERE project IS NOT NULL
                ORDER BY project
            ''')
            return [row[0] if isinstance(row, tuple) else row['project'] for row in cursor.fetchall()]
