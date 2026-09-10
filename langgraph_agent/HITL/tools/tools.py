import os
import base64
from pathlib import Path

from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from tavily import TavilyClient


# ============================================================
# GMAIL CONFIGURATION
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

# Resolve credential files relative to THIS file, not the CWD
_TOOLS_DIR = Path(__file__).parent
_TOKEN_PATH = str(_TOOLS_DIR.parent / "token.json")
_CREDENTIALS_PATH = str(_TOOLS_DIR.parent / "credentials.json")


# ============================================================
# CREATE GMAIL SERVICE
# ============================================================

def get_gmail_service():

    creds = None

    # --------------------------------------------------------
    # Check whether we already authenticated
    # --------------------------------------------------------

    if os.path.exists(_TOKEN_PATH):

        creds = Credentials.from_authorized_user_file(
            _TOKEN_PATH,
            SCOPES
        )

    # --------------------------------------------------------
    # If credentials are missing or expired
    # --------------------------------------------------------

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            # First-time authentication
            flow = InstalledAppFlow.from_client_secrets_file(
                _CREDENTIALS_PATH,
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        # Save token for future use
        with open(_TOKEN_PATH, "w") as token:

            token.write(
                creds.to_json()
            )

    # --------------------------------------------------------
    # Build Gmail API service
    # --------------------------------------------------------

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    return service


# ============================================================
# SEND EMAIL
# ============================================================

def send_email(
    recipient: str,
    subject: str,
    body: str
):

    service = get_gmail_service()

    # --------------------------------------------------------
    # Create email
    # --------------------------------------------------------

    message = EmailMessage()

    message["To"] = recipient

    message["Subject"] = subject

    message.set_content(body)

    # --------------------------------------------------------
    # Gmail requires Base64 URL encoding
    # --------------------------------------------------------

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    # --------------------------------------------------------
    # Gmail API call
    # --------------------------------------------------------

    result = (
        service.users()
        .messages()
        .send(
            userId="me",
            body={
                "raw": encoded_message
            }
        )
        .execute()
    )

    return result["id"]

def tavily_search_engine(query: str) -> str:
    """Search the latest information from web."""
    client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    response = client.search(
        query=query,
        search_depth="advanced"
    )
    return response