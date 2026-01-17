# Squire - Hackathon Project
# SOLACE + SENTRY + SURVEYMONKEY

A clean scaffolding for the Squire hackathon project with FastAPI backend and React + TypeScript frontend.

## Quick Start

### Option 1: Using the dev script

```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

### Option 2: Using npm (if root package.json is configured)

```bash
npm run dev
```

This will start:
- **Backend**: FastAPI server on `http://localhost:8000`
- **Frontend**: React + Vite dev server on `http://localhost:5173`

## Project Structure

```
squire/
├── backend/          # FastAPI backend with SQLite
├── frontend/         # React + TypeScript + Vite + Tailwind
├── scripts/          # Development scripts
└── README.md         # This file
```

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Setup

1. Copy `backend/.env.example` to `backend/.env`
2. Update environment variables as needed

The SQLite database will be automatically created at `backend/data/squire.db` on first run.

## Features (Scaffolding)

- ✅ FastAPI backend with SQLite
- ✅ React + TypeScript frontend with Vite
- ✅ Tailwind CSS for styling
- ✅ Single command dev run
- ✅ Placeholder structure for future expansion

## Next Steps

This is a scaffolding project. Future development should include:
- SAM agent implementations (sentiment, risk, recommendation)
- Solace messaging integration
- SurveyMonkey webhook handling
- Dashboard UI implementation
- Business logic and data models

