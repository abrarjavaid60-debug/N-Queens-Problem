# Smart Campus — Student Complaint and Issue Management System

A beginner-friendly university mini-project built with Python, Streamlit, SQLite, Pandas and Matplotlib.

## Features
- Submit complaints with title, description, category, location and priority
- Unique complaint ID generated automatically
- Student complaint tracking by ID
- Admin authentication and status management (Pending, In Progress, Resolved)
- Search/filter by complaint ID, category, location and status
- Dashboard metrics and charts
- SQLite persistence and CSV export
- Optional sample data

## Requirements
- Python 3.10 or newer
- Internet connection for the first-time package installation

## Install and run
Open a terminal in the `Smart-Campus` folder.

### Windows
```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`. Open it in your browser. The `data/` folder and SQLite database are created automatically when the app starts.

## Admin login
For a local classroom demo only, the default password is `admin123!`. Change it before sharing or deployment.

macOS/Linux:
```bash
export SMART_CAMPUS_ADMIN_PASSWORD='choose-a-long-unique-password'
streamlit run app.py
```

Windows PowerShell:
```powershell
$env:SMART_CAMPUS_ADMIN_PASSWORD = 'choose-a-long-unique-password'
streamlit run app.py
```

This is a mini-project authentication example, not a production identity system. For real deployment, use managed secrets, HTTPS, rate limiting, audit logs, and individual staff accounts.

## Optional sample data
Stop the Streamlit app, then run:
```bash
python seed_data.py
```
Sample data is only added when the database has no complaints. Restart the app afterwards. Do not run this if you want to demonstrate a clean database.

## Test checklist
1. Open **Submit Complaint** and try submitting empty fields; validation should block it.
2. Submit a valid Wi-Fi complaint. A unique ID beginning `SC-` should appear.
3. Open **Track Complaint**, enter that ID, and confirm the initial status is **Pending**.
4. Open **Admin Dashboard**, sign in, select the complaint and change it to **In Progress**.
5. Track the complaint again; its status should now show **In Progress**.
6. Change the status to **Resolved** and check the dashboard metrics/charts.
7. Try filtering the admin list by category, location, status and complaint ID.
8. Download the CSV and open it in a spreadsheet application.
9. Stop and restart the app; existing complaints should remain in the SQLite database.

## Project algorithm
1. Start the app and create the database table if it does not exist.
2. Let a student enter complaint details.
3. Validate required fields and allowed category/priority values.
4. Generate a unique complaint ID and save the complaint with status `Pending`.
5. When tracking is requested, look up the exact complaint ID and show its details.
6. When an administrator logs in, display complaints, filters, metrics and charts.
7. Validate and save any status update, including the update timestamp.
8. Refresh the dashboard using current database records.

## Pseudocode
```text
START
  initialise database
  show navigation
  IF student submits complaint THEN
    validate input
    IF valid THEN generate ID, save record, show ID
    ELSE show validation message
  ELSE IF student tracks complaint THEN
    search by complaint ID and display result
  ELSE IF administrator opens dashboard THEN
    authenticate administrator
    load complaints and display metrics/charts
    allow filtering and status updates
  END IF
END
```

## Flowchart
```text
[Start]
   |
[Initialise SQLite]
   |
[Choose page] ----------------------------
   |                 |                    |
[Submit]          [Track]              [Admin]
   |                 |                    |
[Validate]      [Find ID]          [Authenticate]
   |                 |                    |
[Save + ID]     [Show status]      [Filter / Update]
   |                 |                    |
   ---------------[End / Return]----------
```

## Limitations and future scope
- Student tracking uses a complaint ID; student accounts and email/SMS notifications are not included.
- Admin access uses one shared password in this demonstration.
- For production, add individual accounts, role-based access, password rotation, audit history, backups and privacy review.
