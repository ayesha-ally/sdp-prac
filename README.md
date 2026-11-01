# Student Assignment Tracker

Web app for tracking university assignments by module: modules, assignments, overdue status, search/filters and a dashboard.

## Setup

Python 3.12+ is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
```

On macOS or Linux, activate with `source .venv/bin/activate`.

## Run

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Test

```powershell
python manage.py test
```

## Database

Local development uses SQLite (`db.sqlite3`). Production uses PostgreSQL via `DATABASE_URL`.

## Deployment (Render)

The app is configured for Render with Gunicorn, WhiteNoise and PostgreSQL.

1. Push this repository to a Git host Render can clone. If you use Gitea, the repo must be publicly cloneable, or use another reachable Git URL.
2. On Render, create a **PostgreSQL** database.
3. Create a **Web Service** from this repo:
   - **Build command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
4. Set environment variables:

| Variable | Value |
|---|---|
| `DEBUG` | `False` |
| `SECRET_KEY` | a long random string |
| `DATABASE_URL` | Internal Database URL from the Render Postgres service |
| `ALLOWED_HOSTS` | optional if Render sets `RENDER_EXTERNAL_HOSTNAME` |
| `CSRF_TRUSTED_ORIGINS` | optional if Render sets `RENDER_EXTERNAL_HOSTNAME` |

After deploy, confirm the CSS loads, create a module, restart the service, and confirm the data is still there.

**Live URL:** _add the public Render URL here after deployment_

## Environment variables

| Variable | Local default | Purpose |
|---|---|---|
| `DEBUG` | `True` | Django debug mode |
| `SECRET_KEY` | insecure dev key | Django secret |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed hostnames |
| `CSRF_TRUSTED_ORIGINS` | empty | HTTPS origins for forms |
| `DATABASE_URL` | SQLite file | Database connection |
