# Job Tracker Pro — Full App Build Plan

## 🎯 Project Goal

Build a full-stack **Job Tracker Pro** application that:
1. **Daily scans** job portals (LinkedIn, Indeed, Glassdoor, Naukri, Internshala) for openings matching my resume/profile
2. **Displays a feed** of matched companies/jobs ranked by relevance
3. **Lets me "Like" or "Apply"** — clicking Apply guides me through the application flow
4. **Sends notifications** (in-app + email/push) about new openings, application status updates, and tracked company activity
5. Uses **Gemini AI** to score match quality, generate cover letters, and suggest resume improvements

---

## 👤 User Profile

The user profile is already defined in `data/profile.json`. Key info:
- **Name:** Al Mahaboob Phyas A
- **Degree:** B.Tech AI & Data Science @ KCT (2022–2026, CGPA 7.68)
- **Target Roles:** AI/ML Engineer, Data Scientist, Python Developer, Software Engineer
- **Target Locations:** Remote, Chennai, Bangalore, Hyderabad
- **Experience Level:** Fresher (with internship experience at Stats Perform, Forge Innovation, Codsoft)
- **Key Skills:** Python, PyTorch, TensorFlow, Hugging Face, LangChain, Flask, React.js, Playwright

---

## 🏗️ Existing Code (Reuse This)

The following backend modules are **already built** in `src/`. Reuse and extend them:

| File | Purpose |
|------|---------|
| `src/scrapers/base.py` | Base scraper class with httpx, rate limiting, anti-detection |
| `src/scrapers/linkedin.py` | LinkedIn job scraper |
| `src/scrapers/indeed.py` | Indeed job scraper |
| `src/scrapers/glassdoor.py` | Glassdoor job scraper |
| `src/scrapers/naukri.py` | Naukri job scraper |
| `src/scrapers/internshala.py` | Internshala job scraper |
| `src/ai_matcher.py` | Gemini AI integration — job matching, cover letters, resume tips |
| `src/engine.py` | Central orchestrator — search, dedup, ranking, caching |
| `src/models.py` | Pydantic models — JobListing, ApplicationRecord, SearchQuery, MatchAnalysis |
| `src/config.py` | Config from .env file |
| `src/server.py` | MCP server (can be converted to REST API) |
| `data/profile.json` | Complete user profile |
| `.env` | API keys and preferences |

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Dashboard │ │ Job Feed │ │ Apply    │ │ Notif.     │ │
│  │  (Home)   │ │ (Browse) │ │ Tracker  │ │ Center     │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │ Profile  │ │ Cover    │ │ Settings │                │
│  │ Page     │ │ Letters  │ │ Page     │                │
│  └──────────┘ └──────────┘ └──────────┘                │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (HTTP)
┌────────────────────┴────────────────────────────────────┐
│                BACKEND (FastAPI + Python)                 │
│  ┌────────────┐ ┌────────────┐ ┌──────────────────────┐ │
│  │ API Routes │ │ Scheduler  │ │ Notification Engine  │ │
│  │ (FastAPI)  │ │ (APScheduler│ │ (Email/Push/In-App)  │ │
│  └────────────┘ │  or Celery)│ └──────────────────────┘ │
│  ┌────────────┐ └────────────┘ ┌──────────────────────┐ │
│  │ Auth       │                │ WebSocket Server     │ │
│  │ (JWT)      │                │ (Real-time notifs)   │ │
│  └────────────┘                └──────────────────────┘ │
│                                                          │
│  ┌─── Existing Modules (reuse from src/) ──────────────┐ │
│  │ engine.py │ ai_matcher.py │ scrapers/* │ models.py  │ │
│  └─────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                    DATABASE (SQLite)                      │
│  jobs │ applications │ notifications │ companies │ user  │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Frontend** | React 18 + Vite + Tailwind CSS | Fast, modern, user already knows React.js |
| **UI Components** | shadcn/ui or Headless UI | Clean, accessible components |
| **State Management** | Zustand or React Context | Lightweight, no boilerplate |
| **Backend** | FastAPI (Python) | Async, auto-docs, pairs with existing Python code |
| **Database** | SQLite + SQLAlchemy | Zero setup, portable, good for single-user app |
| **Scheduler** | APScheduler | Daily/hourly job scans without external infra |
| **AI** | Google Gemini 2.0 Flash | Already integrated in ai_matcher.py |
| **Notifications** | WebSocket (in-app) + SMTP (email) | Real-time + email alerts |
| **Auth** | Simple JWT or session-based | Single user, keep it simple |

---

## 📁 Target Project Structure

```
job-apply-mcp/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py          # GET /jobs, POST /jobs/search, GET /jobs/{id}
│   │   │   ├── applications.py  # POST /apply, GET /applications, PATCH /applications/{id}
│   │   │   ├── notifications.py # GET /notifications, PATCH /notifications/{id}/read
│   │   │   ├── companies.py     # GET /companies, POST /companies/{id}/track
│   │   │   ├── profile.py       # GET /profile, PUT /profile
│   │   │   ├── cover_letters.py # POST /cover-letter/generate
│   │   │   └── analytics.py     # GET /analytics/dashboard
│   │   ├── deps.py              # Dependency injection
│   │   └── websocket.py         # WebSocket for real-time notifications
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # App configuration (extend existing)
│   │   ├── database.py          # SQLAlchemy engine, session
│   │   └── scheduler.py         # APScheduler setup for daily scans
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── schemas.py           # Pydantic schemas for API
│   │   └── crud.py              # Database CRUD operations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── job_service.py       # Job search orchestration (uses engine.py)
│   │   ├── notification_service.py  # Notification creation & delivery
│   │   ├── application_service.py   # Application tracking logic
│   │   └── analytics_service.py     # Dashboard stats & charts
│   ├── notifications/
│   │   ├── __init__.py
│   │   ├── email_notifier.py    # SMTP email notifications
│   │   ├── push_notifier.py     # Browser push notifications
│   │   └── in_app.py            # In-app notification storage
│   └── requirements.txt         # Backend dependencies
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── public/
│   │   ├── favicon.ico
│   │   └── notification-sound.mp3
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── api/
│   │   │   ├── client.js        # Axios/fetch wrapper
│   │   │   ├── jobs.js          # Job API calls
│   │   │   ├── applications.js  # Application API calls
│   │   │   └── notifications.js # Notification API calls
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── NotificationBell.jsx
│   │   │   │   └── Layout.jsx
│   │   │   ├── jobs/
│   │   │   │   ├── JobCard.jsx
│   │   │   │   ├── JobList.jsx
│   │   │   │   ├── JobDetail.jsx
│   │   │   │   ├── JobFilters.jsx
│   │   │   │   └── MatchBadge.jsx
│   │   │   ├── applications/
│   │   │   │   ├── ApplicationCard.jsx
│   │   │   │   ├── ApplicationPipeline.jsx
│   │   │   │   └── StatusTimeline.jsx
│   │   │   ├── notifications/
│   │   │   │   ├── NotificationItem.jsx
│   │   │   │   ├── NotificationList.jsx
│   │   │   │   └── NotificationToast.jsx
│   │   │   ├── dashboard/
│   │   │   │   ├── StatsCards.jsx
│   │   │   │   ├── MatchChart.jsx
│   │   │   │   ├── RecentJobs.jsx
│   │   │   │   └── ApplicationFunnel.jsx
│   │   │   └── common/
│   │   │       ├── Button.jsx
│   │   │       ├── Badge.jsx
│   │   │       ├── Modal.jsx
│   │   │       ├── Spinner.jsx
│   │   │       └── EmptyState.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── JobFeed.jsx
│   │   │   ├── JobDetailPage.jsx
│   │   │   ├── Applications.jsx
│   │   │   ├── Notifications.jsx
│   │   │   ├── CoverLetters.jsx
│   │   │   ├── Profile.jsx
│   │   │   └── Settings.jsx
│   │   ├── hooks/
│   │   │   ├── useJobs.js
│   │   │   ├── useNotifications.js
│   │   │   ├── useWebSocket.js
│   │   │   └── useApplications.js
│   │   ├── store/
│   │   │   ├── jobStore.js
│   │   │   ├── notificationStore.js
│   │   │   └── appStore.js
│   │   └── utils/
│   │       ├── formatters.js
│   │       └── constants.js
│   └── .env
│
├── src/                         # ← EXISTING (keep as-is, import into backend)
│   ├── scrapers/
│   ├── ai_matcher.py
│   ├── engine.py
│   ├── models.py
│   └── config.py
│
├── data/
│   ├── profile.json             # ← EXISTING
│   └── job_tracker.db           # SQLite database (auto-created)
│
├── .env                         # ← EXISTING (add new vars)
└── README.md
```

---

## 📋 Feature Specifications

### Feature 1: Dashboard (Home Page)
**Priority: HIGH**

The landing page showing a summary of everything:

- **Stats Cards Row:**
  - Total jobs found today
  - Average match score
  - Applications sent (this week)
  - Pending responses
  - Interviews scheduled

- **Today's Top Matches:** Top 5 jobs with highest AI match score, each showing:
  - Company logo (fetch from clearbit API: `https://logo.clearbit.com/{domain}`)
  - Job title, company name, location
  - Match score badge (color-coded: green >80, yellow 60-80, red <60)
  - Quick "Save" or "Apply" button

- **Application Funnel Chart:** Visual funnel showing:
  - Jobs Found → Saved → Applied → Interview → Offer

- **Recent Activity Timeline:** Last 10 actions (new jobs found, applications sent, status updates)

---

### Feature 2: Job Feed (Browse Jobs)
**Priority: HIGH**

A scrollable feed of all scraped jobs, like a social media feed:

- **Filter Bar (top):**
  - Platform filter: All / LinkedIn / Indeed / Glassdoor / Naukri / Internshala
  - Location filter: Remote / Chennai / Bangalore / Hyderabad / All
  - Role filter: AI/ML Engineer / Data Scientist / Python Developer / Software Engineer
  - Match score range slider (0-100)
  - Sort by: Match Score / Date Posted / Company Name
  - Search text box

- **Job Cards:** Each card shows:
  - Company name + logo
  - Job title
  - Location + work type (Remote/Hybrid/On-site)
  - Posted date (relative: "2 hours ago", "Yesterday")
  - Match score with circular progress indicator
  - Key matching skills (highlighted tags)
  - Missing skills (greyed-out tags)
  - Platform badge (which portal it was found on)
  - Action buttons: ❤️ Save | 📝 Apply | 📄 Cover Letter | 🔔 Track Company

- **Infinite scroll** or pagination (20 jobs per page)

- **Job Detail View** (click to expand or go to detail page):
  - Full job description
  - AI Match Analysis: why it matches, what's missing
  - Auto-generated cover letter (via Gemini)
  - Resume improvement suggestions
  - Direct link to apply on the platform
  - Company info panel

---

### Feature 3: Application Tracker
**Priority: HIGH**

Kanban-style board to track application status:

- **Columns (drag & drop):**
  1. **Saved** — Jobs I've bookmarked
  2. **Applied** — Submitted application
  3. **In Review** — Company acknowledged
  4. **Interview** — Got interview call
  5. **Offer** — Received offer
  6. **Rejected** — Not selected

- **Application Card** shows:
  - Company + role
  - Date applied
  - Current status
  - Next action / follow-up date
  - Notes field (editable)
  - Link to original listing
  - Generated cover letter (if any)

- **Timeline view** for each application showing all status changes with dates

---

### Feature 4: Notification System
**Priority: HIGH**

Multi-channel notification system:

- **In-App Notifications:**
  - Bell icon in header with unread count badge
  - Dropdown showing recent notifications
  - Full notifications page with mark-as-read, delete
  - Toast notifications for real-time events

- **Notification Types:**
  - 🆕 "5 new jobs matching your profile found on LinkedIn"
  - 🎯 "High match alert! 95% match: ML Engineer at Google (Remote)"
  - 📊 "Daily digest: 12 new jobs found, 3 with 80%+ match"
  - 🔔 "Company you're tracking (TCS) posted a new AI role"
  - ⏰ "Follow up reminder: You applied to Infosys 7 days ago"
  - 📈 "Weekly report: 23 jobs found, 5 applications sent"

- **Email Notifications (optional, configurable):**
  - Daily digest email at configured time (default 9 AM)
  - Instant email for 90%+ match jobs
  - Weekly summary report

- **WebSocket** for real-time in-app push without page refresh

- **Notification Settings** (configurable per type):
  - Enable/disable each notification type
  - Set quiet hours
  - Choose channels (in-app only, email, both)
  - Set minimum match score threshold for alerts

---

### Feature 5: Company Tracking
**Priority: MEDIUM**

Track specific companies for job updates:

- **Track a company** from any job card
- **Tracked Companies page:** list of tracked companies with:
  - Company name + logo
  - Number of open positions matching profile
  - Last checked timestamp
  - Toggle notifications on/off per company

- Scheduler checks tracked companies daily for new postings

---

### Feature 6: Cover Letter Generator
**Priority: MEDIUM**

- Select a job → click "Generate Cover Letter"
- Uses Gemini AI (existing `ai_matcher.py`) to generate a tailored cover letter
- Shows in a rich text editor for editing
- Save / Copy / Download as PDF
- History of generated cover letters

---

### Feature 7: Profile & Settings
**Priority: MEDIUM**

- **Profile Page:**
  - View/edit profile loaded from `data/profile.json`
  - Upload resume (PDF/HTML)
  - Skills management (add/remove skills)
  - Job preferences (roles, locations, salary expectations)

- **Settings Page:**
  - Gemini API key configuration
  - Notification preferences
  - Scan schedule (how often to scan: hourly, every 6 hrs, daily)
  - Platform toggle (enable/disable specific job portals)
  - Email configuration for notifications
  - Theme (light/dark mode)

---

## 🗄️ Database Schema

```sql
-- Jobs found by scrapers
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,                -- UUID
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    url TEXT NOT NULL,
    platform TEXT NOT NULL,             -- linkedin/indeed/glassdoor/naukri/internshala
    job_type TEXT,                      -- full-time/internship/contract
    experience_level TEXT,
    salary_range TEXT,
    skills_required TEXT,               -- JSON array
    posted_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    match_score REAL,                   -- 0-100 from Gemini
    match_analysis TEXT,                -- JSON from Gemini
    is_saved BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    company_logo_url TEXT
);

-- Application tracking
CREATE TABLE applications (
    id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id),
    status TEXT DEFAULT 'saved',        -- saved/applied/in_review/interview/offer/rejected
    applied_date TIMESTAMP,
    cover_letter TEXT,
    notes TEXT,
    follow_up_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Application status history
CREATE TABLE application_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id TEXT REFERENCES applications(id),
    old_status TEXT,
    new_status TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT
);

-- Tracked companies
CREATE TABLE tracked_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    domain TEXT,                        -- for logo URL
    notify BOOLEAN DEFAULT TRUE,
    last_checked TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                 -- new_jobs/high_match/daily_digest/company_update/follow_up/weekly_report
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    data TEXT,                          -- JSON payload (job_id, company, etc.)
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cover letters
CREATE TABLE cover_letters (
    id TEXT PRIMARY KEY,
    job_id TEXT REFERENCES jobs(id),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scan history
CREATE TABLE scan_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT,
    jobs_found INTEGER,
    new_jobs INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT                          -- success/failed/partial
);
```

---

## 🔌 API Endpoints

### Jobs
```
GET    /api/jobs                    — List jobs (with filters, pagination)
GET    /api/jobs/{id}               — Get job details + match analysis
POST   /api/jobs/search             — Trigger a new job search
POST   /api/jobs/{id}/save          — Save/bookmark a job
DELETE /api/jobs/{id}/save          — Unsave a job
GET    /api/jobs/daily-digest       — Get today's job summary
```

### Applications
```
GET    /api/applications            — List all applications (with filters)
POST   /api/applications            — Create application (from a saved job)
PATCH  /api/applications/{id}       — Update status, notes, follow-up date
DELETE /api/applications/{id}       — Remove application
GET    /api/applications/{id}/timeline — Get status change history
GET    /api/applications/stats      — Get application funnel stats
```

### Notifications
```
GET    /api/notifications           — List notifications (paginated)
PATCH  /api/notifications/{id}/read — Mark as read
POST   /api/notifications/read-all  — Mark all as read
DELETE /api/notifications/{id}      — Delete notification
GET    /api/notifications/unread-count — Get unread count
WS     /ws/notifications            — WebSocket for real-time notifications
```

### Companies
```
GET    /api/companies               — List tracked companies
POST   /api/companies/track         — Track a new company
DELETE /api/companies/{id}/track    — Stop tracking
PATCH  /api/companies/{id}          — Update tracking preferences
```

### Cover Letters
```
POST   /api/cover-letters/generate  — Generate cover letter for a job
GET    /api/cover-letters           — List saved cover letters
GET    /api/cover-letters/{id}      — Get specific cover letter
PUT    /api/cover-letters/{id}      — Update cover letter
DELETE /api/cover-letters/{id}      — Delete cover letter
```

### Profile & Settings
```
GET    /api/profile                 — Get user profile
PUT    /api/profile                 — Update profile
GET    /api/settings                — Get app settings
PUT    /api/settings                — Update settings
POST   /api/profile/resume-tips     — Get AI resume improvement tips
```

### Analytics
```
GET    /api/analytics/dashboard     — Dashboard stats
GET    /api/analytics/weekly        — Weekly report data
GET    /api/analytics/trends        — Job market trends
```

---

## ⏰ Scheduler Jobs

Configure these in `backend/core/scheduler.py`:

| Job | Schedule | Description |
|-----|----------|-------------|
| `daily_full_scan` | Every day at 6:00 AM | Full scan of all platforms for all target roles |
| `tracked_company_check` | Every 12 hours | Check tracked companies for new postings |
| `daily_digest_notification` | Every day at 9:00 AM | Create daily digest notification + email |
| `weekly_report` | Every Monday at 9:00 AM | Generate weekly summary |
| `follow_up_reminder` | Every day at 10:00 AM | Check for applications needing follow-up |
| `cleanup_old_jobs` | Every Sunday at midnight | Remove jobs older than 30 days |

---

## 🚀 Build Steps (Sequential Order)

### Phase 1: Backend Foundation
1. Set up FastAPI project in `backend/`
2. Set up SQLAlchemy + SQLite database with all tables
3. Create CRUD operations for all models
4. Create Pydantic schemas for API request/response
5. Import and wire existing `src/` modules (engine, scrapers, ai_matcher)
6. Build all REST API endpoints
7. Add CORS middleware for frontend

### Phase 2: Scheduler & Notifications
8. Set up APScheduler with daily scan job
9. Build notification service (create, store, retrieve)
10. Add WebSocket endpoint for real-time notifications
11. Add email notification support via SMTP
12. Wire scheduler to create notifications on new job finds

### Phase 3: Frontend Setup
13. Create React + Vite project in `frontend/`
14. Install and configure Tailwind CSS
15. Set up React Router for page navigation
16. Create Layout component (Sidebar + Header + NotificationBell)
17. Set up API client (axios/fetch wrapper with base URL)
18. Set up Zustand stores

### Phase 4: Core Pages
19. Build Dashboard page with stats cards, top matches, activity timeline
20. Build Job Feed page with filters, job cards, infinite scroll
21. Build Job Detail page with full description, match analysis, cover letter
22. Build Application Tracker with Kanban board (drag & drop)
23. Build Notifications page and toast system

### Phase 5: Additional Pages
24. Build Company Tracking page
25. Build Cover Letter generator/editor page
26. Build Profile page (view/edit)
27. Build Settings page

### Phase 6: Polish & Integration
28. Add WebSocket client for real-time notifications
29. Add dark/light theme toggle
30. Add loading states, error handling, empty states
31. Mobile responsive design
32. Add sound for notifications

---

## 🎨 UI Design Guidelines

- **Color Scheme:**
  - Primary: `#6366f1` (Indigo 500) — main actions, nav highlights
  - Success/High Match: `#22c55e` (Green 500)
  - Warning/Medium Match: `#f59e0b` (Amber 500)
  - Danger/Low Match: `#ef4444` (Red 500)
  - Background: `#f8fafc` (light) / `#0f172a` (dark)
  - Card: `#ffffff` (light) / `#1e293b` (dark)

- **Typography:** Inter or system font stack
- **Border radius:** `rounded-xl` (12px) for cards, `rounded-lg` (8px) for buttons
- **Shadows:** Subtle `shadow-sm` for cards, `shadow-lg` for modals
- **Spacing:** Consistent 4px grid (p-2, p-4, p-6, gap-4, gap-6)

- **Match Score Visual:**
  ```
  90-100: 🟢 Excellent Match (green badge with star)
  70-89:  🟡 Good Match (yellow badge)
  50-69:  🟠 Fair Match (orange badge)
  0-49:   🔴 Low Match (red badge)
  ```

---

## 🔐 Environment Variables (add to .env)

```env
# Existing
GEMINI_API_KEY=your_gemini_api_key_here

# New — Backend
BACKEND_PORT=8000
DATABASE_URL=sqlite:///data/job_tracker.db
SECRET_KEY=your_random_secret_key_here
CORS_ORIGINS=http://localhost:5173

# New — Scheduler
DAILY_SCAN_TIME=06:00
DIGEST_TIME=09:00
SCAN_INTERVAL_HOURS=24

# New — Email Notifications (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=mahaboobphyas.22ad@kct.ac.in

# New — Frontend
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

## 📦 Dependencies

### Backend (`backend/requirements.txt`)
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
alembic==1.13.0
apscheduler==3.10.4
websockets==12.0
python-multipart==0.0.9
aiosmtplib==3.0.1
jinja2==3.1.4
# Plus existing: mcp[cli], google-generativeai, httpx, beautifulsoup4, pydantic, python-dotenv, aiohttp, fake-useragent, lxml, pandas, rich
```

### Frontend (`frontend/package.json`)
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "axios": "^1.7.0",
    "zustand": "^4.5.0",
    "@hello-pangea/dnd": "^16.6.0",
    "recharts": "^2.12.0",
    "lucide-react": "^0.400.0",
    "date-fns": "^3.6.0",
    "react-hot-toast": "^2.4.1",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.4.0"
  },
  "devDependencies": {
    "vite": "^5.4.0",
    "@vitejs/plugin-react": "^4.3.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

---

## 🧪 How to Run (After Building)

```bash
# Terminal 1 — Backend
cd job-apply-mcp
python -m uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd job-apply-mcp/frontend
npm install
npm run dev
```

Then open `http://localhost:5173` in browser.

---

## 🎯 Key Implementation Notes

1. **Reuse existing scrapers:** Import from `src.scrapers` and `src.engine` — don't rewrite them. The `JobEngine` class already handles concurrent multi-platform search with deduplication.

2. **Reuse AI matcher:** Import from `src.ai_matcher` — it already has `analyze_match()`, `generate_cover_letter()`, and `suggest_resume_improvements()` methods using Gemini.

3. **Single-user app:** No complex auth needed. Use a simple API key or skip auth entirely since it runs locally.

4. **SQLite is enough:** This is a personal tool, not multi-tenant. SQLite handles it perfectly with zero setup.

5. **Gemini API key required:** The user needs to add their Gemini API key in `.env`. The app should show a setup screen if the key is missing.

6. **Scraper reliability:** Web scrapers may break due to site changes. Always wrap in try/except, show "scrape failed" gracefully, never crash the app.

7. **Rate limiting:** The existing scrapers have built-in rate limiting. Don't bypass it — respect the job portals.

8. **Job deduplication:** The existing `engine.py` deduplicates by URL. Make sure the database also enforces unique URLs.

9. **Profile as source of truth:** Always load profile from `data/profile.json`. The profile page should edit this file.

10. **Start with mock data:** If scrapers fail or API key isn't set, have a seed/mock data mode so the UI can be tested immediately.

---

## 🏁 Start Building!

Open this folder (`job-apply-mcp`) in your code editor and begin with **Phase 1** (Backend Foundation). The existing `src/` modules give you a huge head start — you mainly need to:
1. Wrap them in a FastAPI server
2. Add a database layer
3. Add a scheduler
4. Build the React frontend

The existing code in `src/` handles the hard parts (scraping, AI matching, deduplication). Your job is to build the web app around it.

**Good luck! 🚀**
