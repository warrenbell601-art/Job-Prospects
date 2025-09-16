# Whangārei Jobs Agent

A turnkey weekly job-search agent for the **greater Whangārei area** (NZ), outputting a CSV each Saturday at **06:00 NZT** and emailing the results + audit log to **warrenbell601@gmail.com**.

- **Region:** Greater Whangārei (configurable)
- **Industry filter:** _None_ (removed)
- **Keywords (title or description must contain any):** production, technical, compliance, health and safety
- **Output format:** CSV (`Job_Search_YYYY-MM-DD.csv`), <= 25 rows, sorted by **nearest Deadline first** (nulls last)
- **Audit log:** `Job_Search_audit_log_YYYY-MM-DD.csv`
- **Delivery:** Gmail API email with attachments
- **Schedule:** Weekly, Saturdays at 06:00 NZT (dual UTC crons to handle NZST/NZDT)

> ⚠️ **Scraping terms:** Respect each site's robots.txt and Terms. Prefer official search feeds/alerts. This repo includes basic scrapers for SEEK and Trade Me using Playwright; selectors can change and may require tweaks.

---

## Quick start

### 1) Fork or download
- Fork this repo, or download the ZIP and push to your GitHub account as a new repository.

### 2) Enable Gmail API and capture credentials
We use OAuth2 with a persistent **refresh token** stored as a GitHub secret.

1. Go to **https://console.cloud.google.com/apis/credentials** (use the Google account that owns `warrenbell601@gmail.com`).
2. Create a **Desktop** OAuth client (type: _Desktop app_). Download the JSON and save it as `client_secret.json` locally.
3. Run the bootstrap once on your machine to obtain a **refresh token**:
   ```bash
   python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   python auth_bootstrap.py
   ```
   This opens a browser; sign in and approve Gmail send scope. It will print `refresh_token`.
4. Copy the **client_id**, **client_secret**, and **refresh_token** from the generated `token_bootstrap.json`.

### 3) Add GitHub Secrets
In your repo → **Settings → Secrets and variables → Actions → New repository secret**, add:

- `GMAIL_CLIENT_ID` — from your OAuth client
- `GMAIL_CLIENT_SECRET` — from your OAuth client
- `GMAIL_REFRESH_TOKEN` — from the bootstrap step
- *(optional)* `EMAIL_TO` — defaults to `warrenbell601@gmail.com`

### 4) Configure filters (optional)
Edit `config.yaml` to adjust suburbs (greater Whangārei) or keywords.

### 5) Run it
- The GitHub Actions workflow is already scheduled to run **weekly** at Saturday 06:00 NZT (handled by two UTC crons).
- You can also trigger manually via the **Actions → Run workflow** button.

### Local manual run (for testing)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
python email_gmail.py  # sends the latest CSV + audit to your email
```

---

## What the agent does

1. Queries SEEK and Trade Me with a Whangārei focus.
2. Renders with **Playwright** to capture dynamic content.
3. Extracts: Role, Company, Location, Date Listed, Deadline (if found).
4. Filters:
   - Location ∈ Greater Whangārei (regex in `config.yaml`)
   - Keywords present in title or description (production | technical | compliance | health and safety)
5. Normalises dates (NZT), dedupes, sorts by **Deadline asc** (nulls last), limits to **25**.
6. Writes CSV + audit log to `/data` folder.
7. Emails the CSV + audit log via Gmail API.

---

## Notes & maintenance

- Job boards change HTML often. If selectors break, update `sources/seek.py` and `sources/trademe.py`.
- Use saved HTML snapshots for quick parser unit tests.
- Consider adding more sources or company career pages later.
