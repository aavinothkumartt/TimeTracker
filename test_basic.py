#!/usr/bin/env python3
"""Basic test to verify TimeTracker components work."""
import sys
import time
from time_tracker import TimeTrackerCore
import utils


def test_basic_functionality():
    """Test basic time tracking functionality."""
    print("TimeTracker - Basic Functionality Test")
    print("=" * 50)

    # Initialize tracker
    print("\n1. Initializing tracker...")
    tracker = TimeTrackerCore()
    print("   ✓ Tracker initialized")

    # Test manual entry
    print("\n2. Testing manual entry...")
    success, message, entry_id = tracker.add_manual_entry(
        task_name="Testing",
        duration_str="1h 30m"
    )
    if success:
        print(f"   ✓ {message}")
    else:
        print(f"   ✗ {message}")
        return False

    # Test session start
    print("\n3. Testing session start...")
    session_id = tracker.start_session("Test Session")
    if session_id:
        print(f"   ✓ Session started (ID: {session_id})")
    else:
        print("   ✗ Failed to start session")
        return False

    # Wait a bit
    print("\n4. Running session for 3 seconds...")
    for i in range(3):
        time.sleep(1)
        duration = tracker.get_current_session_duration()
        print(f"   {i+1}s - Elapsed: {utils.format_duration(duration)}")

    # Test session stop
    print("\n5. Testing session stop...")
    success = tracker.stop_session()
    if success:
        print("   ✓ Session stopped")
    else:
        print("   ✗ Failed to stop session")
        return False

    # Test daily summary
    print("\n6. Testing daily summary...")
    summary = tracker.get_daily_summary()
    print(f"   Total duration: {summary.total_formatted}")
    print(f"   Sessions: {summary.session_count}")
    print(f"   Manual entries: {summary.manual_entry_count}")
    print(f"   Total items: {summary.total_items}")

    if summary.total_items > 0:
        print("   ✓ Summary generated successfully")
    else:
        print("   ✗ Summary is empty")
        return False

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
    print("\nFull summary:")
    print(summary.get_summary_text())

    return True


if __name__ == '__main__':
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
