# ALGO DNA

ALGO DNA is a personal algorithm-practice journal that turns problem-solving records into a lightweight learning profile.

## Features
- Account registration and login with hashed passwords
- Log a problem, platform, topic, difficulty, outcome, attempts, and wrong attempts
- Dashboard with solved/attempted totals, success rate, recent activity, and priority topics
- Insights by topic and difficulty
- A generated practice roadmap based on the user's own records
- SQLite database created automatically on first run

## Run locally
```bash
# From inside the algodna folder
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
flask --app app run --debug
```
Open the local URL printed by Flask.

## Notes
- The database file `algodna.db` is generated automatically. Do not create it manually.
- Change `SECRET_KEY` before deploying publicly. For local coursework, the default is sufficient.
- This is a learning project, not a production-grade multi-user service.
