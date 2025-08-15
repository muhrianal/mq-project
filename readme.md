# MathQuest – Local Dev Guide

Duolingo-style math learning app with a Django REST API and a React frontend.

* Backend: `mathquest/` (Django + DRF + PostgreSQL)
* Frontend: `mathquest-frontend/` (React + Tailwind v3)
* Idempotent `/submit` (via `attempt_id`)
* XP awarded **once per problem** (upgrades when a previously-wrong answer becomes correct)
* Streaks tracked by UTC day

---

## Prerequisites

* **Python** 3.9+ (3.10 recommended)
* **Node.js** 18+ (or 20+).
* **Docker** + **Docker Compose** (for PostgreSQL)

---

## 1) Backend (Django) — `mathquest/`

### 1.1 Create and activate venv

```bash
cd mathquest
python3.9 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 1.2 Install deps

```bash
python3.9 -m pip install -r requirements.txt
```

### 1.3 Environment (.env)

Create `mathquest/.env` (no need, if it's already there):

```env
DJANGO_SECRET_KEY=dev-secret-key
DEBUG=1

POSTGRES_DB=mathquest
POSTGRES_USER=mathquest_user
POSTGRES_PASSWORD=mathquest_pass
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

> `settings.py` loads `.env` from the project root.
> `ALLOWED_HOSTS` should include `127.0.0.1` and `localhost` for local dev.

### 1.4 Start PostgreSQL (Docker)

inside `mathquest/` (where `docker-compose.yml` lives), run:

```bash
docker compose up -d
```

**Reset DB** (if you want fresh start):

```bash
docker compose down -v
docker compose up -d
```

### 1.5 Migrate & seed

```bash
# from mathquest/
python3.9 manage.py migrate
python3.9 manage.py seed_data
```

### 1.6 Run backend

```bash
python3.9 manage.py runserver
# API base: http://127.0.0.1:8000/api
```

### 1.7 API quick test (curl)

```bash
curl -i http://127.0.0.1:8000/api/lessons/
```

### 1.8 Tests (idempotency + streak)

```bash
python3.9 manage.py test
```

---

## 2) Frontend (React) — `mathquest-frontend/`

### 2.1 Install deps

```bash
npm install
```

### 2.2 Run frontend

```bash
npm start
# App: http://localhost:3000
```

---

## 3) Endpoints (contract)

* `GET /api/lessons` → list lessons (problems included, correct answers **not** leaked)
* `GET /api/lessons/:id` → lesson detail
* `POST /api/lessons/:id/submit`

  * Body:

    ```json
    {
      "attempt_id": "uuid",
      "answers": [
        {"problem_id": 101, "option_id": 3},
        {"problem_id": 102, "value": 12}
      ]
    }
    ```
  * Response:

    ```json
    {
      "correct_count": 2,
      "earned_xp": 20,
      "new_total_xp": 120,
      "streak": {"current": 3, "best": 5},
      "lesson_progress": 0.6,
      "duplicate": false
    }
    ```
* `GET /api/profile` → user stats

**Rules implemented**

* **Idempotency**: same `attempt_id` returns the same saved result; no double XP/streak.
* **XP Upgrade**: XP granted **once per problem** when it becomes correct for the first time (e.g., 2/3 → later 3/3 adds +10, total 30; no farming).
* **Streak** (UTC): increments if activity is on a new UTC day; resets on missed day; same-day submissions don’t increment.

---


## 4) What’s included vs future improvements

**Included**

* Clean layered backend (views → services → models)
* Postgres migrations + seed
* Idempotent `/submit` with transaction safety
* XP upgrade logic (per-problem)
* Streak logic (UTC)
* React UI (mobile-first) with Tailwind v3
* Tests for idempotency + streak

**Future**

* Auth (multi-user)
* Rich progress visuals and animations
* Swagger / OpenAPI docs
* CI workflow
* More granular per-lesson analytics

---

## 5) Contact / Notes

* Demo user is `id=1` (created by `seed_data`).
* If you reset DB volumes, run **migrate** + **seed** again.

Happy testing! 🎯
