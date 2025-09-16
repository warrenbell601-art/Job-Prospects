# Send the latest CSV + audit via Gmail API using OAuth2 refresh token
import os, glob, base64, mimetypes
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def _load_creds():
    client_id = os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
    refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError("Missing Gmail secrets (GMAIL_CLIENT_ID/SECRET/REFRESH_TOKEN).")
    return Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token",
                       client_id=client_id, client_secret=client_secret, scopes=SCOPES)

def _attach(msg: EmailMessage, path: str):
    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    with open(path, "rb") as f:
        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))

def send_latest(to_addr=None):
    creds = _load_creds()
    service = build("gmail", "v1", credentials=creds)

    csvs = sorted(glob.glob("data/Job_Search_*.csv"))
    audits = sorted(glob.glob("data/Job_Search_audit_log_*.csv"))
    if not csvs:
        raise RuntimeError("No CSV found in data/. Run run.py first.")
    csv_path = csvs[-1]
    audit_path = audits[-1] if audits else None

    to_addr = to_addr or os.environ.get("EMAIL_TO") or "warrenbell601@gmail.com"
    subject = f"Whangārei Job Search — {os.path.basename(csv_path).replace('Job_Search_','').replace('.csv','')}"
    body = f"Attached: {os.path.basename(csv_path)} and audit log. This is the weekly Whangārei jobs agent run."

    msg = EmailMessage()
    msg["To"] = to_addr
    msg["From"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    _attach(msg, csv_path)
    if audit_path:
        _attach(msg, audit_path)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    print("Email sent to", to_addr)

if __name__ == "__main__":
    send_latest()
