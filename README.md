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

## ENSO climate intelligence (Milestone B2)

`GET /api/v1/climate/enso` is public and keeps three scientific concepts
structurally separate:

- `observations` contains NOAA CPC weekly OISST.v2.1 Niño 1+2, Niño 3,
  Niño 3.4, and Niño 4 sea-surface temperature anomalies from the official
  [`wksst9120.for`](https://www.cpc.ncep.noaa.gov/data/indices/wksst9120.for)
  product. CPC updates this dataset weekly. Values are °C anomalies relative to
  1991–2020 weekly climatological means; they are not absolute SST values.
- `status` is the latest curated NOAA CPC issued analysis known to this code
  version, preserving CPC's original alert wording and a conservative normalized
  phase.
- `outlook` contains concise, source-attributed NOAA CPC and WMO issued outlooks.
  Only explicitly published probabilities are represented, including qualifiers
  such as `greater_than` or `near`.

Niño 3.4 is the area-averaged SST anomaly for 5°N–5°S and 170°W–120°W. The API
returns its latest weekly observation and a bounded 52-week series for later
visualization. Numeric observations use the existing six-hour TTL and real
last-known-good cache: failed refreshes return cached data as `stale`, or empty
observations as `unavailable` when no real cache exists. Issued bulletins instead
carry issue and verification dates plus `latest_known_issue`; they do not age as
though they were sensor readings.

Bulletin prose is intentionally curated in
`backend/app/services/climate/curated/enso_bulletins.py`. This avoids brittle HTML
scraping and prevents observations, expert analysis, and forecasts from being
collapsed into an EcoPulse-generated prediction. ENSO changes large-scale climate
probabilities, not deterministic daily weather, and event strength alone does not
determine impacts in a particular region. Curated records must be verified and
updated when NOAA CPC or WMO issues a newer bulletin.

## Global climate overview (Milestone B3)

`GET /api/v1/climate/overview` composes the existing CO2, ENSO, and EONET
services with a monthly global surface-temperature analysis and the latest
verified Copernicus Climate Bulletin. It deliberately exposes separate component
freshness and an availability summary rather than inventing an Earth or planet
score. A failed provider therefore makes only its component `stale` or
`unavailable`; other real observations and issued analyses remain usable.

Global temperature uses NOAA NCEI's monthly global merged land–ocean
NOAAGlobalTemp v6.1.0 ASCII series for 90°S–90°N. The product combines land
surface air temperature with ERSST v6 ocean input and reports anomalies relative
to the 1991–2020 monthly climatology. EcoPulse fetches the current versioned
time-series file, returns the latest anomaly plus at most 60 chronological
months, and caches successful responses for 12 hours. The configured filename
contains NOAA's latest-data month and must be advanced when NCEI publishes a new
operational snapshot.

Ocean-temperature and Arctic/Antarctic sea-ice context comes from a versioned,
curated Copernicus monthly record in
`backend/app/services/climate/curated/climate_bulletins.py`. It is labeled as
issued `analysis`, preserves reference/issue/verification dates, and is not
treated as a live feed. The [WMO State of the Global Climate](https://wmo.int/publication-series/state-of-global-climate)
is registered only as longer-term annual context; B3 does not ingest or present
it as current monthly data.

## Global seasonal climate outlook (Milestone B4A)

`GET /api/v1/climate/outlook` exposes the latest verified, curated WMO Global
Seasonal Climate Update as an issued multi-model `forecast`. It keeps the
forecast-period bounds, oceanic drivers, surface-temperature outlook, and
precipitation outlook separate. The endpoint is global seasonal guidance: it is
neither an observation nor a deterministic daily or local weather prediction.

Temperature and precipitation tendencies use tercile categories (`above_normal`,
`near_normal`, and `below_normal`, with `equal_chances` or `unknown` where
needed). Each category is relative to the baseline stored on that particular
issue; the current SON 2026 record uses 1993–2009. Missing probability values
remain null, while source wording such as `exact`, `greater_than`, or `near` is
retained as a qualifier. A favoured category does not imply that every day will
have that condition.

The Indian Ocean Dipole is represented only as a WMO forecast driver, including
its explicitly issued phase and value where available; B4A does not add an IOD
observation feed. Curated issues live in
`backend/app/services/climate/curated/seasonal_outlooks.py`. New verified issues
can be appended with their own period and baseline; date-driven selection marks
them `upcoming`, `current`, or `expired` without season-specific logic.

`GET /api/v1/climate/overview` includes only a compact seasonal-outlook preview
and remains available if no verified outlook record exists. For local decisions,
use outlooks from the relevant WMO Regional Climate Centre or National
Meteorological and Hydrological Service.

## Deploy the FastAPI backend to Vercel

Create a separate Vercel project for the API with these settings:

- **Root Directory:** `backend`
- **Framework Preset:** FastAPI (automatically detected)
- **Build Command:** leave unset
- **Output Directory:** leave unset
- **Install Command:** leave unset; Vercel installs `requirements.txt`
- **Python version:** 3.12, selected by `backend/.python-version`

No `vercel.json` or duplicate `api/index.py` is needed. With `backend` as the
project root, Vercel's FastAPI zero-configuration detection loads the existing
`app` object from `app/main.py` and sends every request to it. FastAPI therefore
keeps the public paths exactly as declared, including `/health`, `/docs`, and
`/api/v1/*`; there is no additional `/api` prefix.

Set the following Vercel environment variables for Production (and for Preview
only if preview deployments should use a database):

```text
DATABASE_URL=postgresql+psycopg://<user>:<password>@<endpoint>-pooler.<region>.aws.neon.tech/<database>?sslmode=require&channel_binding=require
JWT_SECRET=<strong-random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_ORIGIN=https://<frontend-project>.vercel.app
ENVIRONMENT=production
```

Use the pooled Neon connection string for the running serverless application.
EcoPulse uses SQLAlchemy's `NullPool` when `ENVIRONMENT=production`, so individual
Vercel instances do not retain their own connection pools; Neon handles pooling.
Local development retains the existing SQLAlchemy pool and still runs with
`uvicorn app.main:app --reload`.

### Apply production migrations and seed data

Do this once from a trusted local shell or CI job, not from a Vercel request or
FastAPI startup hook. Neon recommends its direct (non-`-pooler`) connection for
schema migrations and other session-dependent operations:

```bash
cd backend
source .venv/bin/activate
DATABASE_URL='postgresql+psycopg://<user>:<password>@<endpoint>.<region>.aws.neon.tech/<database>?sslmode=require&channel_binding=require' alembic upgrade head
DATABASE_URL='postgresql+psycopg://<user>:<password>@<endpoint>.<region>.aws.neon.tech/<database>?sslmode=require&channel_binding=require' python -m app.seed.seed
```

The seed command is idempotent. Neither migrations nor seeding run automatically
inside the Vercel function.

After deployment, verify:

```text
https://<backend-project>.vercel.app/health
https://<backend-project>.vercel.app/docs
https://<backend-project>.vercel.app/api/v1/climate/overview
```

The climate services use process-local TTL caches. A warm function instance can
reuse its cache, but cold starts and separately scaled instances begin with an
empty cache. This is acceptable for the initial deployment and does not change
the existing `current`, `stale`, or `unavailable` behavior. The backend does not
write application data to local files or rely on durable local filesystem state.
