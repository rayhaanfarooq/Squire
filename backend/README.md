# Backend - FastAPI + SQLite

FastAPI backend for the Squire hackathon project.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

3. Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Structure

- `app/main.py` - FastAPI application entry point
- `app/core/` - Configuration and logging
- `app/api/` - HTTP routes (webhooks, health check)
- `app/services/` - Business logic services
- `app/agents/` - SAM agent stubs (sentiment, risk, recommendation)
- `app/messaging/` - Solace client stubs, topic definitions
- `app/models/` - Domain models
- `app/schemas/` - Pydantic request/response schemas
- `app/db/` - SQLite connection, session helper, ORM base

## Database

SQLite database is stored at `data/squire.db` (created automatically on first run).

