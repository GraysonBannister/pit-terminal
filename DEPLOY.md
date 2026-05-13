# PIT Terminal — Deployment Guide

## Architecture

- **Frontend**: Next.js 16 (React 19, Tailwind, shadcn/ui) — runs on Vercel/Netlify
- **Backend**: FastAPI (Python) — runs on Railway/Render/Fly.io
- **Database**: PostgreSQL 15 — Supabase or managed Postgres
- **Cache/Scheduler**: Redis 7 — Upstash or managed Redis
- **Data Sources**: Polymarket Gamma API, NewsAPI.org, OpenAI GPT-4o-mini

## Environment Variables

Create a `.env` file in `backend/`:

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/pit_terminal
REDIS_URL=redis://host:port/0

# Optional but strongly recommended
OPENAI_API_KEY=sk-...        # Enables AI summaries & sentiment analysis
NEWSAPI_KEY=...               # Enables live news ingestion
```

## Local Development

### 1. Start Database & Cache (Docker)

```bash
docker-compose up -d
```

This starts PostgreSQL on `:5432` and Redis on `:6379`.

### 2. Install Python Dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run Backend

```bash
cd backend
source .venv/bin/activate
python main.py
```

API available at `http://localhost:8000`.

### 4. Run Frontend

```bash
npm run dev
```

Frontend available at `http://localhost:3000` (falls back to `:3001` if occupied).

### 5. Verify Pipeline

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/markets
curl http://localhost:8000/api/opportunities
```

## Production Deployment

### Backend — Railway (Recommended)

1. Push code to GitHub
2. Create new Railway project, connect repo
3. Add PostgreSQL plugin (or connect external Supabase)
4. Add Redis plugin (or connect Upstash)
5. Set environment variables in Railway dashboard
6. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Deploy

### Backend — Render

1. Create new Web Service
2. Connect GitHub repo
3. Set:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add PostgreSQL managed database
5. Set environment variables
6. Deploy

### Database — Supabase

1. Create Supabase project
2. Copy connection string from Settings > Database
3. Set `DATABASE_URL` with `postgresql+asyncpg://` prefix

### Redis — Upstash

1. Create Upstash Redis database
2. Copy Redis URL
3. Set `REDIS_URL`

### Frontend — Vercel

1. Import GitHub repo
2. Framework preset: Next.js
3. Set environment variable: `NEXT_PUBLIC_API_URL=https://your-backend-url.com/api`
4. Deploy

## Scheduler Configuration

The APScheduler runs three jobs automatically on backend startup:

| Job | Interval | Description |
|-----|----------|-------------|
| Polymarket ingestion | Every 3 min | Fetches live markets, prices, volume |
| News ingestion | Every 10 min | Fetches news via NewsAPI |
| Opportunity engine | Every 5 min | Scores markets, generates opportunities |

No additional cron configuration needed.

## API Keys & Rate Limits

### Polymarket Gamma API
- No API key required
- Be respectful: 3-minute polling is conservative
- Add backoff if you see 429 responses

### NewsAPI
- Free tier: 100 requests/day
- Paid tier: $449/mo for 1M requests
- Alternative: RSS feeds (Reuters, AP) with feedparser

### OpenAI
- GPT-4o-mini: ~$0.15/m input, $0.60/m output tokens
- Typical cost: $0.01–0.05 per market analysis
- Enable only for markets with sufficient volume

## Monitoring

- Health check: `GET /health`
- Backend logs: `docker logs pit_backend` or Railway/Render dashboard
- Database: Check `markets`, `opportunities`, `price_points` tables

## First-Time Setup Checklist

- [ ] Set `DATABASE_URL` and run backend (tables auto-create)
- [ ] Set `OPENAI_API_KEY` for AI features
- [ ] Set `NEWSAPI_KEY` for news ingestion
- [ ] Verify Polymarket data appears in `/api/markets`
- [ ] Verify opportunities appear in `/api/opportunities` after 5–10 minutes
- [ ] Connect frontend to backend API URL
- [ ] Verify dashboard loads with live data
