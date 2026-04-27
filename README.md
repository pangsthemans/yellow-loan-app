# Yellow Loan Application

A mobile-first phone financing application built with FastAPI, PostgreSQL, and Vue 3 + Quasar.

## Tech Stack

| Layer     | Technology                         |
|-----------|------------------------------------|
| Backend   | FastAPI + SQLAlchemy + PostgreSQL  |
| Frontend  | Vue 3 + Quasar + Pinia + Vite      |
| Dev Setup | Docker Compose                     |

## Live Demo

| | URL |
|---|---|
| **Frontend** | https://visionary-cocada-3231e1.netlify.app |
| **Backend API** | https://yellow-loan-backend.fly.dev |
| **API Docs** | https://yellow-loan-backend.fly.dev/docs |

---

## Architecture

### Local Development (Docker Compose)

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Compose                       │
│                                                          │
│  ┌──────────────────┐       ┌──────────────────────┐    │
│  │  frontend:9000   │       │    backend:8000       │    │
│  │                  │       │                       │    │
│  │  Vite dev server │       │  FastAPI + Uvicorn    │    │
│  │  Vue 3 + Quasar  │       │  SQLAlchemy ORM       │    │
│  │                  │       │                       │    │
│  │  /api/* ─────────┼──────▶│  (CORS not needed —  │    │
│  │  proxy rewrite   │       │   same Docker network)│    │
│  └──────────────────┘       └──────────┬────────────┘    │
│          ▲                             │                  │
│          │                             │ postgresql://    │
│          │                        ┌────▼─────────────┐   │
│          │                        │    db:5432        │   │
│          │                        │                   │   │
│          │                        │  PostgreSQL 15    │   │
│          │                        │  (volume-backed)  │   │
│          │                        └───────────────────┘   │
└──────────┼──────────────────────────────────────────────┘
           │
    Browser (localhost:9000)
```

**Key detail:** Vite's dev server proxies all `/api/*` requests to `http://backend:8000` and strips the `/api` prefix. The browser only ever talks to port 9000, so no CORS headers are needed locally.

---

### Production (Netlify + Fly.io)

```
                        Browser
                           │
           ┌───────────────┴────────────────┐
           │                                │
           ▼                                ▼
  ┌─────────────────┐             ┌──────────────────────┐
  │    Netlify CDN   │             │  yellow-loan-backend  │
  │                  │             │     .fly.dev          │
  │  Static SPA      │  HTTPS +    │                       │
  │  (Vite build)    │  CORS ─────▶│  FastAPI + Uvicorn    │
  │                  │             │  SQLAlchemy ORM       │
  │  VITE_API_BASE_URL             │                       │
  │  points to Fly.io│             │  ALLOWED_ORIGINS env  │
  │  at build time   │             │  permits Netlify host │
  └─────────────────┘             └──────────┬────────────┘
                                             │
                                   Fly.io private network
                                   (flycast — never public)
                                             │
                                  ┌──────────▼────────────┐
                                  │   yellow-loan-db       │
                                  │   .flycast:5432        │
                                  │                        │
                                  │  Fly.io Postgres       │
                                  │  (single node, jnb)    │
                                  └────────────────────────┘
```

**Key details:**
- `VITE_API_BASE_URL` is baked into the JS bundle at Netlify build time — there is no runtime config file
- The Postgres cluster is only reachable via Fly.io's internal `flycast` DNS — it is not exposed to the public internet
- `ALLOWED_ORIGINS` on the backend is set as a Fly.io secret; adding a new frontend domain requires only `fly secrets set` and no redeploy
- Both Fly.io machines scale to zero when idle and cold-start on the first request (~2s)

---

## Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Run Locally

```bash
git clone https://github.com/pangsthemans/yellow-loan-app.git
cd yellow-loan-app
docker compose up --build
```

Then open:
- **Frontend**: http://localhost:9000
- **API Docs**: http://localhost:8000/docs

That's it. The database is automatically created and phones are seeded on first startup.

---

## Features

### Core
- **Multi-step form** (4 steps): Personal → Income → Phone Selection → Review
- **SA ID validation**: 13-digit format check + Luhn checksum + age derivation
- **Age restriction**: Only applicants aged 18–65 (inclusive) may apply
- **ID uniqueness**: Prevents duplicate applications from the same ID number
- **Loan calculations**:
  - `loanPrincipal = cashPrice × (1 - depositPercent)`
  - `loanAmount = loanPrincipal × (1 + interestRate)`
  - `dailyPayment = loanAmount / 360`
- **Document upload**: Proof of income stored as base64 in PostgreSQL

### Extras Implemented

#### Risk Scoring
Age is used to assign a risk group that determines the interest rate:
- Group 1 (18–30): lowest interest rate (15%)
- Group 2 (31–50): medium interest rate (20%)
- Group 3 (51–65): highest interest rate (28%)

Once the ID number is submitted and age is confirmed, the user cannot go back to change it.

#### Affordability Filter
Phones are automatically hidden from the selection screen if:
```
monthly_income < 10 × monthly_payment
```
A notice informs the user how many phones were hidden.

#### Yellow UI Styling
The UI uses Yellow's brand colours (#F5C400) with a clean, mobile-first design.

---

## Project Structure

```
yellow-loan-app/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # Settings (DATABASE_URL etc.)
│   │   │   ├── database.py       # SQLAlchemy engine + session
│   │   │   └── sa_id.py          # SA ID parsing + Luhn check
│   │   ├── models/
│   │   │   └── models.py         # Phone + Application SQLAlchemy models
│   │   ├── routers/
│   │   │   ├── phones.py         # GET /phones, POST /phones/seed
│   │   │   └── applications.py   # POST /applications, POST /validate-id
│   │   ├── schemas/
│   │   │   └── schemas.py        # Pydantic request/response schemas
│   │   └── main.py               # FastAPI app + CORS + auto-seed
│   ├── tests/
│   │   ├── test_sa_id.py
│   │   └── test_applications.py
│   ├── conftest.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ApplicationForm.vue   # Main 4-step form
│   │   │   └── SuccessPage.vue       # Confirmation screen
│   │   ├── stores/
│   │   │   └── application.js        # Pinia store (all state + API calls)
│   │   ├── tests/
│   │   │   ├── setup.js
│   │   │   ├── ApplicationForm.test.js
│   │   │   └── SuccessPage.test.js
│   │   ├── router/index.js
│   │   ├── styles/global.css
│   │   ├── App.vue
│   │   └── main.js
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── vitest.config.js
└── docker-compose.yml
```

---

## API Endpoints

| Method | Endpoint                        | Description                              |
|--------|---------------------------------|------------------------------------------|
| GET    | `/phones/`                      | List phones with pricing by risk group   |
| GET    | `/phones/{id}`                  | Get single phone with pricing            |
| POST   | `/phones/seed`                  | Seed phone database (auto-runs on start) |
| POST   | `/applications/validate-id`     | Validate SA ID + check eligibility       |
| POST   | `/applications/`                | Submit complete loan application         |
| GET    | `/applications/{id}`            | Retrieve submitted application           |
| GET    | `/health`                       | Health check                             |

Full interactive docs: http://localhost:8000/docs

---

## Running Tests

### Frontend (Vitest)

```bash
docker compose exec frontend npm run test
```

### Backend (pytest)

```bash
docker compose exec backend pytest
```

---

## SA ID Validation

South African ID numbers follow the format `YYMMDDSSSSCA Z` (13 digits):
- `YYMMDD` — date of birth
- `SSSS` — sequence number (0000–4999 = female, 5000–9999 = male)
- `C` — citizenship (0 = SA citizen, 1 = permanent resident)
- `A` — usually 8 or 9
- `Z` — Luhn checksum digit

The backend validates:
1. Exactly 13 digits
2. Valid date of birth embedded in digits 1–6
3. Luhn checksum passes
4. Age between 18 and 65

---

## Phones Database

8 phones are pre-seeded covering a range of price points:

| Phone              | Cash Price | Deposit |
|--------------------|------------|---------|
| TECNO Spark 20     | R 2,999    | 10%     |
| Redmi Note 13      | R 4,999    | 10%     |
| Huawei P50 Lite    | R 5,999    | 10%     |
| Samsung Galaxy A55 | R 8,999    | 10%     |
| Google Pixel 8a    | R 13,999   | 12%     |
| iPhone 15          | R 19,999   | 15%     |
| Samsung Galaxy S24 | R 24,999   | 20%     |
| iPhone 15 Pro      | R 29,999   | 20%     |

Interest rates vary by risk group (15% / 20% / 28%).
