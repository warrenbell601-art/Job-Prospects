# One-time local bootstrap to obtain a Gmail OAuth refresh token
import json, os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    if not os.path.exists("client_secret.json"):
        raise SystemExit("Place your OAuth client JSON as client_secret.json")
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)
    data = {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": getattr(creds, 'refresh_token', None) or getattr(creds, '_refresh_token', None),
        "token_uri": creds.token_uri
    }
    with open("token_bootstrap.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Wrote token_bootstrap.json. Copy values into GitHub Secrets.")

if __name__ == "__main__":
    main()
