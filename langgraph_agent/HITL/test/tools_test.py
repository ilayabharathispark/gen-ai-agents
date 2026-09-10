import sys
from pathlib import Path

# Add the HITL directory to sys.path so `tools.tools` can be found
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.tools import send_email

email_id = send_email(
    recipient="ilayabharathi334@gmail.com",
    subject="Test from LangGraph",
    body="Hello! This email was sent using Gmail API."
)

print("Email sent!")
print("Message ID:", email_id)