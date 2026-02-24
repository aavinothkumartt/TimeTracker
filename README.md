# TimeTracker

A simple macOS menu bar application for tracking your work time with manual entry and automatic timer features.

## Features

- **Menu Bar Integration**: Lives in your macOS menu bar for easy access
- **Start/Stop Timer**: Track work sessions with automatic timing
- **Manual Time Entry**: Add past work sessions manually
- **Daily Summary**: View your total work time and breakdown by task
- **Persistent Storage**: All data saved locally in SQLite database
- **Simple Interface**: Clean, distraction-free interface

## Installation

### Prerequisites

- macOS (tested on macOS 10.15+)
- Python 3.9 or higher

### Setup

1. Navigate to the TimeTracker directory:
   ```bash
   cd /Users/aavinothkumar/Desktop/Practice/TimeTracker
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Usage

### Starting the App

Once started, you'll see a ⏱ icon in your menu bar. Click it to access the menu.

### Menu Options

#### Start/Stop Work Session
- Click "Start Work Session"
- Enter a task name (optional)
- The timer starts and the menu bar shows elapsed time (▶ HH:MM:SS)
- Click "Stop Work Session" when done
- Your session is automatically saved

#### Add Manual Entry
- Click "Add Manual Entry"
- Enter task name
- Enter duration using formats like:
  - "2h 30m" (2 hours 30 minutes)
  - "90m" (90 minutes)
  - "1.5h" (1.5 hours)
  - "2.5" (2.5 hours)
- Entry is immediately saved

#### Today's Summary
- Click "Today's Summary"
- See total work time for today
- View breakdown by task
- See number of sessions and manual entries

#### Quit
- Click "Quit" to exit the app
- If a session is running, you'll be asked to save or discard it

## Data Storage

All your work data is stored in:
```
~/.timetracker/timetracker.db
```

This SQLite database contains:
- `work_sessions`: Timed work sessions
- `manual_entries`: Manually entered time

## Testing

Run the basic functionality test:
```bash
source venv/bin/activate
python test_basic.py
```

## Project Structure

```
TimeTracker/
├── app.py              # Main menu bar application
├── time_tracker.py     # Core tracking logic
├── database.py         # SQLite database operations
├── models.py           # Data models
├── utils.py            # Time formatting utilities
├── config.py           # Configuration
├── requirements.txt    # Python dependencies
├── test_basic.py       # Basic functionality test
└── README.md           # This file
```

## Building Standalone App (Optional)

To create a standalone `.app` bundle:

1. Create `setup.py`:
   ```python
   from setuptools import setup

   APP = ['app.py']
   OPTIONS = {
       'argv_emulation': False,
       'plist': {
           'CFBundleName': 'TimeTracker',
           'LSUIElement': True,  # Hide from Dock
       },
       'packages': ['rumps', 'sqlite3'],
   }

   setup(
       app=APP,
       name='TimeTracker',
       options={'py2app': OPTIONS},
       setup_requires=['py2app'],
   )
   ```

2. Build the app:
   ```bash
   python setup.py py2app
   ```

3. Find your app in `dist/TimeTracker.app`

4. Copy to Applications:
   ```bash
   cp -r dist/TimeTracker.app /Applications/
   ```

## Tips

- The app runs in the menu bar, not the Dock
- Data persists between app restarts
- You can run only one work session at a time
- Manual entries can be added anytime, even while a session is running
- All times are stored in your local timezone

## Troubleshooting

### App won't start
- Ensure Python 3.9+ is installed
- Verify virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Database errors
- Check that `~/.timetracker/` directory is writable
- Delete `~/.timetracker/timetracker.db` to reset (you'll lose data)

### Menu bar icon not showing
- Make sure no other instance is running
- Try restarting with `python app.py`

## License

Free to use and modify for personal use.

## Version

1.0.0 - Initial release
