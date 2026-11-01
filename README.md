# Student Assignment Tracker

Web app for tracking university assignments by module. This is the project skeleton only.

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

Open http://127.0.0.1:8000/ — you should see the skeleton home page.

## Test

```powershell
python manage.py test
```

No feature tests are included yet. The command should complete with `NO TESTS RAN`.

## Database

Local development uses SQLite (`db.sqlite3`). For production, set `DATABASE_URL` to a PostgreSQL connection string. Optional environment variables: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` (comma-separated).

## Deployment

Not configured yet. The live application will be deployed after features are implemented.
