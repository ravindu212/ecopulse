# EcoPulse

EcoPulse is an SDG 13 climate action platform built with Next.js, FastAPI, and PostgreSQL.

## Phase 0 local setup

### Prerequisites

- Node.js and npm
- Python 3.12+
- Docker Desktop or Docker Engine with Docker Compose

### Database

From the repository root, start PostgreSQL:

```bash
docker compose up -d postgres
```

PostgreSQL is available locally at `127.0.0.1:5434`. Inside the Docker network,
the PostgreSQL container listens on port `5432`.

### Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Confirm it with
`http://localhost:8000/health`.

Apply the database migrations before using authentication endpoints:

```bash
alembic upgrade head
```

The migrations create the `users` table used by registration and login, followed by
the `assessments` table used by the authenticated Climate Action Score flow.

### Frontend

In a second terminal:

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

## Environment files

- Copy `backend/.env.example` to `backend/.env` for local API configuration.
- Copy `frontend/.env.local.example` to `frontend/.env.local` for the frontend API URL.
- Local environment files are ignored by Git. Do not commit secrets.

## Climate data (Milestone B1)

The public endpoints `GET /api/v1/climate/co2` and
`GET /api/v1/climate/events` use, respectively, NOAA GML's machine-readable
[Estimated Global Trend daily CO2 CSV](https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_trend_gl.csv)
and the official [NASA EONET v3 events API](https://eonet.gsfc.nasa.gov/api/v3/events).
No provider credentials are required.

Successful NOAA responses are cached in-process for six hours; EONET responses
are cached for 15 minutes per filter set. If a refresh fails after expiry, only
the process's real last-known-good response is returned and it is explicitly
marked `stale`. Without a valid cached response, the endpoint reports
`unavailable` and returns no substitute measurements or events. Every response
retains publisher, source URL, fetch time, freshness, and methodology metadata.

EONET reports natural events; feed inclusion does not establish that climate
change caused an event. Climate attribution requires separate scientific
analysis, and clients must retain that distinction and the supplied source
attribution.
