# Job Tracker Pro — Quick Start

## 🚀 How to Run

### Step 1: Install Backend Dependencies
```powershell
cd d:\job-apply-mcp
.venv\Scripts\pip install fastapi "uvicorn[standard]" sqlalchemy apscheduler websockets python-multipart jinja2 pydantic-settings
```

### Step 2: Start the Backend
```powershell
cd d:\job-apply-mcp
.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
```

### Step 3: Install & Start Frontend (requires Node.js)
```powershell
cd d:\job-apply-mcp\frontend
npm install
npm run dev
```

### Step 4: Open the App
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs

---

## 🔑 Gemini API Key
Set in `.env`:
```
GEMINI_API_KEY=AIzaSyC3sGOqp7_P33hOYSm6X4mN11Pqn73iKmA
```

---

## 📁 Project Structure
```
job-apply-mcp/
├── backend/          ← FastAPI backend
│   ├── main.py       ← Entry point
│   ├── api/routes/   ← All REST routes
│   ├── core/         ← Config, DB, Scheduler, Seeder
│   ├── db/           ← ORM models, schemas, CRUD
│   └── services/     ← Job, notification, analytics services
├── frontend/         ← React + Vite + Tailwind
│   └── src/
│       ├── pages/    ← Dashboard, JobFeed, Applications, etc.
│       ├── components/layout/
│       ├── store/    ← Zustand stores
│       ├── hooks/    ← useWebSocket
│       └── api/      ← Axios client + API helpers
└── src/              ← EXISTING scrapers + AI matcher (unchanged)
```

---

## ✨ Features
- 🎯 AI match scoring (Gemini 2.0 Flash)
- 📊 Dashboard with funnel chart & stats  
- 🔍 Job feed with filters, search, match rings
- 📝 Kanban application tracker (drag & drop)
- ✉️ AI cover letter generation
- 🔔 Real-time WebSocket notifications
- 🏢 Company tracking
- 👤 Editable profile
- 🌙 Dark theme
- 🗄️ SQLite database (auto-seeded with 20 mock jobs)
- ⏰ APScheduler for daily scans
