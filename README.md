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
