"""FastAPI web application for TimeTracker."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

from time_tracker import TimeTrackerCore
import utils

# Initialize FastAPI app
app = FastAPI(title="TimeTracker", version="1.0.0")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize TimeTrackerCore
tracker = TimeTrackerCore()


# Request/Response Models
class StartSessionRequest(BaseModel):
    task_name: Optional[str] = None
    project: Optional[str] = None


class AddEntryRequest(BaseModel):
    task_name: str
    duration_str: str
    project: Optional[str] = None
    notes: Optional[str] = None
    date: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    task_name: Optional[str] = None
    project: Optional[str] = None
    notes: Optional[str] = None


class UpdateEntryRequest(BaseModel):
    task_name: Optional[str] = None
    duration_str: Optional[str] = None
    project: Optional[str] = None
    notes: Optional[str] = None


# Routes

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, date: Optional[str] = None):
    """Render main dashboard."""
    if date is None:
        date = utils.get_today_date()

    # Get active session
    active_session = tracker.get_current_session()

    # Get today's data
    summary = tracker.get_daily_summary(date)

    # Get sessions and entries for the date
    sessions = tracker.db.get_sessions_by_date(date)
    entries = tracker.db.get_entries_by_date(date)

    # Get all projects for dropdown
    projects = tracker.db.get_all_projects()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "date": date,
        "active_session": active_session,
        "summary": summary,
        "sessions": sessions,
        "entries": entries,
        "projects": projects
    })


# Session API Endpoints

@app.post("/api/sessions/start")
async def start_session(req: StartSessionRequest):
    """Start a new work session."""
    session_id = tracker.start_session(req.task_name, req.project)

    if session_id:
        session = tracker.get_current_session()
        return {
            "success": True,
            "session_id": session_id,
            "start_time": session.start_time
        }
    return {"success": False, "error": "Session already active"}


@app.post("/api/sessions/stop")
async def stop_session():
    """Stop the active work session."""
    if tracker.stop_session():
        # Get today's summary after stopping
        summary = tracker.get_daily_summary()
        return {
            "success": True,
            "total_today": summary.total_formatted
        }
    return {"success": False, "error": "No active session"}


@app.get("/api/sessions/active")
async def get_active_session():
    """Get currently active session."""
    session = tracker.get_current_session()

    if session:
        return {
            "active": True,
            "session_id": session.id,
            "start_time": session.start_time,
            "task_name": session.task_name,
            "project": session.project,
            "duration": session.calculate_current_duration()
        }
    return {"active": False}


@app.put("/api/sessions/{session_id}")
async def update_session(session_id: int, req: UpdateSessionRequest):
    """Update a work session."""
    success = tracker.db.update_work_session(
        session_id,
        task_name=req.task_name,
        project=req.project,
        notes=req.notes
    )

    if success:
        return {"success": True}
    raise HTTPException(status_code=404, detail="Session not found")


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: int):
    """Delete a work session."""
    # If deleting active session, clear current_session_id
    if tracker.current_session_id == session_id:
        tracker.current_session_id = None

    tracker.db.delete_session(session_id)
    return {"success": True}


# Entry API Endpoints

@app.post("/api/entries")
async def add_entry(req: AddEntryRequest):
    """Add a manual time entry."""
    success, message, entry_id = tracker.add_manual_entry(
        task_name=req.task_name,
        duration_str=req.duration_str,
        project=req.project,
        notes=req.notes,
        date=req.date
    )

    if success:
        return {"success": True, "message": message, "entry_id": entry_id}
    return {"success": False, "error": message}


@app.get("/api/entries")
async def get_entries(date: Optional[str] = None):
    """Get manual entries for a date."""
    if date is None:
        date = utils.get_today_date()

    entries = tracker.db.get_entries_by_date(date)
    return {"entries": entries}


@app.put("/api/entries/{entry_id}")
async def update_entry(entry_id: int, req: UpdateEntryRequest):
    """Update a manual entry."""
    # Parse duration if provided
    duration = None
    if req.duration_str:
        duration = utils.parse_duration(req.duration_str)
        if duration is None or duration <= 0:
            return {"success": False, "error": "Invalid duration format"}

    success = tracker.db.update_manual_entry(
        entry_id,
        task_name=req.task_name,
        duration=duration,
        project=req.project,
        notes=req.notes
    )

    if success:
        return {"success": True}
    raise HTTPException(status_code=404, detail="Entry not found")


@app.delete("/api/entries/{entry_id}")
async def delete_entry(entry_id: int):
    """Delete a manual entry."""
    tracker.db.delete_manual_entry(entry_id)
    return {"success": True}


# Summary API Endpoints

@app.get("/api/summary")
async def get_summary(date: Optional[str] = None):
    """Get daily summary."""
    if date is None:
        date = utils.get_today_date()

    summary = tracker.get_daily_summary(date)

    return {
        "date": summary.date,
        "total_duration": summary.total_duration,
        "total_formatted": summary.total_formatted,
        "session_count": summary.session_count,
        "manual_entry_count": summary.manual_entry_count,
        "tasks": summary.tasks
    }


# Project API Endpoints

@app.get("/api/projects")
async def get_projects():
    """Get list of all projects."""
    projects = tracker.db.get_all_projects()
    return {"projects": projects}


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("web_app:app", host="0.0.0.0", port=8000, reload=True)
