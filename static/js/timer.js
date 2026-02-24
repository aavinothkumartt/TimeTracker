// Timer management for TimeTracker
let timerInterval = null;

function initTimer(sessionId, startTime) {
    // Store in localStorage for persistence
    localStorage.setItem('session_id', sessionId);
    localStorage.setItem('session_start_time', startTime);

    // Start the timer display
    startTimerDisplay(startTime);
}

function startTimerDisplay(startTime) {
    const startDate = new Date(startTime);

    function updateDisplay() {
        const now = new Date();
        const elapsed = Math.floor((now - startDate) / 1000); // seconds

        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;

        const formatted = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        const timerDisplay = document.getElementById('timer-display');
        if (timerDisplay) {
            timerDisplay.textContent = formatted;
        }
    }

    // Update immediately
    updateDisplay();

    // Update every second
    timerInterval = setInterval(updateDisplay, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }

    localStorage.removeItem('session_id');
    localStorage.removeItem('session_start_time');
}

// Auto-resume timer if page is refreshed during active session
window.addEventListener('load', () => {
    const sessionId = localStorage.getItem('session_id');
    const startTime = localStorage.getItem('session_start_time');

    if (sessionId && startTime && document.getElementById('timer-display')) {
        // Timer is already initialized by template, just ensure it's running
        console.log('Timer resumed from localStorage');
    }
});

// Clear timer on stop
window.addEventListener('beforeunload', () => {
    // Keep session info in localStorage for resume
});
