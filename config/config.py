"""Project-wide configuration values.

Keep environment-specific values here so pytest fixtures, notifiers, and page
objects do not need to read `.env` directly.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_UI_URL = os.getenv("BASE_UI_URL", "https://qaproject-temp.app.elice.io/ai-helpy-chat")
BASE_API_URL = os.getenv("BASE_API_URL", "https://dev-v2-community-api.dev.elicer.io")

TEST_USER = {
    "id": os.getenv("TEST_USER_ID"),
    "pw": os.getenv("TEST_USER_PW"),
}

DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", str(Path.home() / "Downloads"))
DEFAULT_API_TIMEOUT = int(os.getenv("DEFAULT_API_TIMEOUT", "10"))

JIRA_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_WEBHOOK_FAILURES_URL = os.getenv("SLACK_WEBHOOK_FAILURES_URL")
