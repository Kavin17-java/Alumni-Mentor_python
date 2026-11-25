# AlumniConnect

A three-person student project for career mentoring. Python, Flask, SQLite and HTML/CSS.

## Local setup (Windows)

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe app.py
```

Open http://127.0.0.1:5000. After the database branch is merged, run `.venv\Scripts\python.exe seed.py` to add fictional demo accounts. The initial starter is a preview only; all three feature PRs are needed for the final demo.

## Team contributions
- Member 1: templates, CSS, frontend tests.
- Member 2: Flask routes, permissions, backend tests.
- Member 3: SQLite schema, database operations, seed and database tests.

Replace member labels with real names and add real PR links, screenshots, verified test results and deployment URL before submission. Record AI-assisted development and checks in each member's docs file.

## Limitations
Demo only: simple keyword matching, no email verification, chat, notifications or password reset. Use fictional users. Render default storage may reset; persistent SQLite requires a suitable persistent disk. Set SECRET_KEY on deployment, use HTTPS and do not enable debug. Start command: `gunicorn app:app`.
