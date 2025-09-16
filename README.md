[README.md](https://github.com/user-attachments/files/22357867/README.md)
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
