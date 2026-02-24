#!/usr/bin/env python3
"""TimeTracker - macOS menu bar time tracking application."""
import rumps
from time_tracker import TimeTrackerCore
import utils
import config


class TimeTrackerApp(rumps.App):
    """macOS menu bar application for time tracking."""

    def __init__(self):
        """Initialize the TimeTracker app."""
        super(TimeTrackerApp, self).__init__(
            name="TimeTracker",
            title=config.ICON_IDLE,
            quit_button=None
        )

        # Initialize core tracker
        self.tracker = TimeTrackerCore()

        # Build menu
        self.menu = [
            rumps.MenuItem("Start Work Session", callback=self.toggle_session),
            rumps.separator,
            rumps.MenuItem("Add Manual Entry", callback=self.add_manual_entry),
            rumps.MenuItem("Today's Summary", callback=self.show_summary),
            rumps.separator,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        # Update UI based on current state
        self._update_ui_state()

    def _update_ui_state(self):
        """Update menu items based on current session state."""
        if self.tracker.is_session_active():
            self.menu["Start Work Session"].title = "Stop Work Session"
            self.title = config.ICON_ACTIVE + " 0:00:00"
        else:
            self.menu["Start Work Session"].title = "Start Work Session"
            self.title = config.ICON_IDLE

    @rumps.clicked("Start Work Session")
    def toggle_session(self, sender):
        """Toggle work session start/stop."""
        if self.tracker.is_session_active():
            # Stop the session
            success = self.tracker.stop_session()
            if success:
                self.menu["Start Work Session"].title = "Start Work Session"
                self.title = config.ICON_IDLE

                # Get session info for notification
                summary = self.tracker.get_daily_summary()
                rumps.notification(
                    title="Work Session Stopped",
                    subtitle="Session saved successfully",
                    message=f"Today's total: {summary.total_formatted}"
                )
        else:
            # Get task name from user
            response = rumps.Window(
                title='Start Work Session',
                message='Enter task name (optional):',
                default_text='',
                ok='Start',
                cancel='Cancel',
                dimensions=(320, 100)
            ).run()

            if response.clicked:
                task_name = response.text.strip() if response.text.strip() else None

                # Start the session
                session_id = self.tracker.start_session(task_name)
                if session_id:
                    self.menu["Start Work Session"].title = "Stop Work Session"
                    self.title = config.ICON_ACTIVE + " 0:00:00"

                    # Show notification
                    task_msg = f"Task: {task_name}" if task_name else "Timer started"
                    rumps.notification(
                        title="Work Session Started",
                        subtitle=task_msg,
                        message="Click 'Stop Work Session' when done"
                    )

    @rumps.clicked("Add Manual Entry")
    def add_manual_entry(self, sender):
        """Add a manual time entry via dialog."""
        # Get task name
        task_response = rumps.Window(
            title='Add Time Entry',
            message='Enter task name:',
            default_text='',
            ok='Next',
            cancel='Cancel',
            dimensions=(320, 100)
        ).run()

        if not task_response.clicked or not task_response.text.strip():
            return

        task_name = task_response.text.strip()

        # Get duration
        duration_response = rumps.Window(
            title='Duration',
            message='Enter duration (e.g., "2h 30m", "90m", or "1.5h"):',
            default_text='',
            ok='Add',
            cancel='Cancel',
            dimensions=(320, 100)
        ).run()

        if not duration_response.clicked or not duration_response.text.strip():
            return

        duration_str = duration_response.text.strip()

        # Add the entry
        success, message, entry_id = self.tracker.add_manual_entry(
            task_name=task_name,
            duration_str=duration_str
        )

        if success:
            # Show success notification
            rumps.notification(
                title="Time Entry Added",
                subtitle=task_name,
                message=message
            )
        else:
            # Show error alert
            rumps.alert(
                title="Error",
                message=message,
                ok="OK"
            )

    @rumps.clicked("Today's Summary")
    def show_summary(self, sender):
        """Show today's work summary."""
        summary = self.tracker.get_daily_summary()

        # Build message
        if summary.total_items == 0:
            message = "No work logged today yet.\n\nStart a work session or add a manual entry to begin tracking!"
        else:
            message = summary.get_summary_text()

        # Show alert with summary
        rumps.alert(
            title="Today's Work Summary",
            message=message,
            ok="Close"
        )

    @rumps.clicked("Quit")
    def quit_app(self, sender):
        """Quit the application."""
        # Check if there's an active session
        if self.tracker.is_session_active():
            response = rumps.alert(
                title="Active Session",
                message="You have an active work session. What would you like to do?",
                ok="Stop & Quit",
                cancel="Cancel",
                other="Quit Without Saving"
            )

            if response == 1:  # OK - Stop & Quit
                self.tracker.stop_session()
                rumps.quit_application()
            elif response == 0:  # Other - Quit Without Saving
                self.tracker.cancel_current_session()
                rumps.quit_application()
            # else: Cancel - do nothing
        else:
            rumps.quit_application()

    @rumps.timer(1)
    def update_timer(self, sender):
        """Update the menu bar timer display every second."""
        if self.tracker.is_session_active():
            elapsed = self.tracker.get_current_session_duration()
            time_str = utils.format_duration_detailed(elapsed)
            self.title = f"{config.ICON_ACTIVE} {time_str}"
        else:
            self.title = config.ICON_IDLE


def main():
    """Main entry point for the application."""
    try:
        app = TimeTrackerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nTimeTracker stopped.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
