"""Data models for TimeTracker."""
from dataclasses import dataclass
from typing import Optional
import utils


@dataclass
class WorkSession:
    """Represents a timed work session."""

    id: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    task_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None

    @property
    def is_active(self):
        """Check if session is currently running."""
        return self.end_time is None

    @property
    def duration_formatted(self):
        """Get formatted duration string."""
        if self.duration:
            return utils.format_duration(self.duration)
        return "0s"

    def calculate_current_duration(self):
        """
        Calculate current duration if session is active.

        Returns:
            int: Duration in seconds
        """
        if not self.start_time:
            return 0

        if self.end_time:
            # Session is completed
            return self.duration or 0

        # Session is active, calculate from start_time to now
        return utils.calculate_duration_seconds(
            self.start_time,
            utils.get_current_datetime()
        ) or 0


@dataclass
class ManualEntry:
    """Represents a manually entered time entry."""

    id: Optional[int] = None
    date: Optional[str] = None
    duration: int = 0  # in seconds
    task_name: str = ""
    notes: Optional[str] = None
    created_at: Optional[str] = None

    @property
    def duration_formatted(self):
        """Get formatted duration string."""
        return utils.format_duration(self.duration)


@dataclass
class DailySummary:
    """Represents aggregated daily work data."""

    date: str
    total_duration: int = 0  # in seconds
    session_count: int = 0
    manual_entry_count: int = 0
    tasks: list = None

    def __post_init__(self):
        """Initialize tasks list if not provided."""
        if self.tasks is None:
            self.tasks = []

    @property
    def total_formatted(self):
        """Get formatted total duration string."""
        return utils.format_duration(self.total_duration)

    @property
    def total_items(self):
        """Get total number of items (sessions + manual entries)."""
        return self.session_count + self.manual_entry_count

    def add_session(self, session: WorkSession):
        """
        Add a work session to the summary.

        Args:
            session (WorkSession): Session to add
        """
        if session.duration:
            self.total_duration += session.duration
            self.session_count += 1

            if session.task_name:
                self._add_task(session.task_name, session.duration)

    def add_manual_entry(self, entry: ManualEntry):
        """
        Add a manual entry to the summary.

        Args:
            entry (ManualEntry): Entry to add
        """
        self.total_duration += entry.duration
        self.manual_entry_count += 1

        if entry.task_name:
            self._add_task(entry.task_name, entry.duration)

    def _add_task(self, task_name, duration):
        """
        Add or update task in the breakdown.

        Args:
            task_name (str): Name of the task
            duration (int): Duration in seconds
        """
        # Find existing task
        for task in self.tasks:
            if task['name'] == task_name:
                task['duration'] += duration
                task['duration_formatted'] = utils.format_duration(task['duration'])
                return

        # Add new task
        self.tasks.append({
            'name': task_name,
            'duration': duration,
            'duration_formatted': utils.format_duration(duration)
        })

    def get_summary_text(self):
        """
        Get formatted summary text for display.

        Returns:
            str: Formatted summary
        """
        lines = []
        lines.append(f"Total Work Time: {self.total_formatted}")
        lines.append(f"Items: {self.total_items} ({self.session_count} sessions, {self.manual_entry_count} manual)")

        if self.tasks:
            lines.append("\nBreakdown by Task:")
            for task in sorted(self.tasks, key=lambda x: x['duration'], reverse=True):
                lines.append(f"  • {task['name']}: {task['duration_formatted']}")

        return "\n".join(lines)
