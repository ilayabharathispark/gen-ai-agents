import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

# Resolve credential files relative to the HITL directory
_HITL_DIR = Path(__file__).parent.parent
_TOKEN_PATH = str(_HITL_DIR / "token.json")
_CREDENTIALS_PATH = str(_HITL_DIR / "credentials.json")


def get_gmail_service():

    creds = None

    # -------------------------------------------------------
    # Check if we already have a token
    # -------------------------------------------------------

    if os.path.exists(_TOKEN_PATH):

        creds = Credentials.from_authorized_user_file(
            _TOKEN_PATH,
            SCOPES
        )

    # -------------------------------------------------------
    # If no valid credentials exist
    # -------------------------------------------------------

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            # First-time OAuth login
            flow = InstalledAppFlow.from_client_secrets_file(
                _CREDENTIALS_PATH,
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        # Save token for future runs
        with open(_TOKEN_PATH, "w") as token:

            token.write(
                creds.to_json()
            )

    # -------------------------------------------------------
    # Create Gmail API service
    # -------------------------------------------------------

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


service = get_gmail_service()

print("✅ Gmail authentication successful!")

print(
    "Gmail service created successfully."
)