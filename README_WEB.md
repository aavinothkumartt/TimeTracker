# TimeTracker Web Application

Modern, user-friendly web application for tracking your daily work with a beautiful gradient UI, dark mode, and project organization.

## 🎨 Features

- ⏱️ **Real-time Timer**: Start/stop work sessions with live timer display
- ✍️ **Manual Entries**: Quickly log completed work with flexible duration parsing
- 📊 **Daily Summary**: View total time with breakdown by project and task
- 🏷️ **Project Tags**: Organize tasks by projects/categories
- ✏️ **Edit & Delete**: Modify or remove entries after creation
- 🌙 **Dark Mode**: Toggle between light and dark themes
- 📱 **Responsive Design**: Works beautifully on desktop, tablet, and mobile
- 🎨 **Modern UI**: Gradient colors, smooth animations, and vibrant design

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the development server:**
   ```bash
   uvicorn web_app:app --reload
   ```

3. **Open your browser:**
   Navigate to [http://localhost:8000](http://localhost:8000)

## 📱 Usage

### Start a Work Session
1. Enter an optional task name and project
2. Click "Start Session"
3. Watch the timer count up in real-time
4. Click "Stop Session" when done

### Add Manual Entry
1. Enter the task name
2. Enter duration (e.g., "2h 30m", "90m", or "1.5h")
3. Optionally select a project
4. Click "Add Entry"

### View Summary
- See your total work time for the day
- View breakdown by project
- Track number of sessions and manual entries

## 🎨 UI Features

- **Gradient Design**: Purple-to-blue gradient backgrounds and text
- **Animated Cards**: Hover effects and smooth transitions
- **Progress Bars**: Visual representation of time per project
- **Pulsing Timer**: Active sessions have animated borders
- **Project Badges**: Color-coded tags for easy identification

## 🌐 Deployment to Render.com

1. **Push code to GitHub:**
   ```bash
   git add .
   git commit -m "Add web application"
   git push origin main
   ```

2. **Create Render account:**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

3. **Create PostgreSQL database:**
   - Click "New" → "PostgreSQL"
   - Name: `timetracker-db`
   - Click "Create Database"

4. **Create Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Click "Create Web Service"

5. **Access your app:**
   - Your app will be live at: `https://timetracker-[random].onrender.com`

## 🔧 Configuration

### Environment Variables

Create a `.env` file for local development (see `.env.example`):

```
ENVIRONMENT=development
DATABASE_URL=
SECRET_KEY=your-secret-key
```

### Production Settings

On Render.com, these are configured automatically via `render.yaml`.

## 📂 Project Structure

```
TimeTracker/
├── web_app.py              # FastAPI application
├── templates/
│   ├── base.html          # Base template with dark mode
│   └── index.html         # Main dashboard
├── static/
│   ├── css/
│   │   └── styles.css     # Gradient styles & animations
│   └── js/
│       └── timer.js       # Timer management
├── database.py            # Database operations (SQLite/PostgreSQL)
├── models.py              # Data models
├── time_tracker.py        # Core business logic
├── utils.py               # Helper functions
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
└── render.yaml            # Deployment configuration
```

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Jinja2 templates + Alpine.js + Tailwind CSS
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Deployment**: Render.com
- **Styling**: Custom gradients + Tailwind CSS

## 📝 API Endpoints

- `POST /api/sessions/start` - Start new session
- `POST /api/sessions/stop` - Stop active session
- `GET /api/sessions/active` - Get active session
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session
- `POST /api/entries` - Add manual entry
- `GET /api/entries` - Get entries by date
- `PUT /api/entries/{id}` - Update entry
- `DELETE /api/entries/{id}` - Delete entry
- `GET /api/summary` - Get daily summary
- `GET /api/projects` - Get all projects

## 🎯 Future Enhancements

- Calendar view for browsing past dates
- Export data to CSV/PDF
- User authentication for multi-user support
- Weekly/monthly reports with charts
- PWA support (installable web app)
- Recurring tasks/templates
- Time goals and productivity insights

## 📄 License

Open source - feel free to use and modify!

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

---

Made with ❤️ and lots of ☕
