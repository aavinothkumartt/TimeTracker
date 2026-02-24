"""Core time tracking logic for TimeTracker."""
from database import Database
from models import WorkSession, ManualEntry, DailySummary
import utils


class TimeTrackerCore:
    """Core business logic for time tracking."""

    def __init__(self):
        """Initialize time tracker with database."""
        self.db = Database()
        self.current_session_id = None
        self._load_active_session()

    def _load_active_session(self):
        """Load any active session from database."""
        active = self.db.get_active_session()
        if active:
            self.current_session_id = active['id']

    def is_session_active(self):
        """
        Check if a work session is currently running.

        Returns:
            bool: True if session is active
        """
        return self.current_session_id is not None

    def start_session(self, task_name=None):
        """
        Start a new work session.

        Args:
            task_name (str, optional): Name/description of the task

        Returns:
            int: Session ID, or None if a session is already active
        """
        if self.is_session_active():
            return None

        session_id = self.db.create_work_session(task_name)
        self.current_session_id = session_id
        return session_id

    def stop_session(self):
        """
        Stop the currently active work session.

        Returns:
            bool: True if successful, False if no active session
        """
        if not self.is_session_active():
            return False

        success = self.db.end_work_session(self.current_session_id)
        if success:
            self.current_session_id = None
        return success

    def get_current_session(self):
        """
        Get the current active session data.

        Returns:
            WorkSession: Current session, or None if no active session
        """
        if not self.is_session_active():
            return None

        session_data = self.db.get_session(self.current_session_id)
        if session_data:
            return WorkSession(**session_data)
        return None

    def get_current_session_duration(self):
        """
        Get the elapsed time of the current session.

        Returns:
            int: Duration in seconds, or 0 if no active session
        """
        session = self.get_current_session()
        if session:
            return session.calculate_current_duration()
        return 0

    def add_manual_entry(self, task_name, duration_str, notes=None):
        """
        Add a manual time entry.

        Args:
            task_name (str): Name/description of the task
            duration_str (str): Duration string (e.g., "2h 30m")
            notes (str, optional): Additional notes

        Returns:
            tuple: (success: bool, message: str, entry_id: int or None)
        """
        # Parse duration
        duration = utils.parse_duration(duration_str)

        if duration is None or duration <= 0:
            return (False, "Invalid duration format. Use formats like '2h 30m', '90m', or '1.5h'.", None)

        if not task_name or not task_name.strip():
            return (False, "Task name cannot be empty.", None)

        # Add to database
        entry_id = self.db.add_manual_entry(
            task_name=task_name.strip(),
            duration=duration,
            notes=notes
        )

        return (True, f"Added {utils.format_duration(duration)} for '{task_name}'", entry_id)

    def get_daily_summary(self, date=None):
        """
        Get summary of work for a specific date.

        Args:
            date (str, optional): Date in YYYY-MM-DD format (defaults to today)

        Returns:
            DailySummary: Summary object with aggregated data
        """
        if date is None:
            date = utils.get_today_date()

        summary = DailySummary(date=date)

        # Get completed sessions for the date
        sessions = self.db.get_today_sessions()
        for session_data in sessions:
            if session_data.get('duration'):  # Only count completed sessions
                session = WorkSession(**session_data)
                summary.add_session(session)

        # Get manual entries for the date
        entries = self.db.get_today_manual_entries()
        for entry_data in entries:
            entry = ManualEntry(**entry_data)
            summary.add_manual_entry(entry)

        return summary

    def get_session_task_name(self):
        """
        Get the task name of the current session.

        Returns:
            str: Task name, or None if no active session
        """
        session = self.get_current_session()
        if session:
            return session.task_name
        return None

    def cancel_current_session(self):
        """
        Cancel the current session without saving.

        Returns:
            bool: True if successful
        """
        if not self.is_session_active():
            return False

        self.db.delete_session(self.current_session_id)
        self.current_session_id = None
        return True
