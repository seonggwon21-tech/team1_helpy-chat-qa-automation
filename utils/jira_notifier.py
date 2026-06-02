"""Jira integration helpers for pytest failure handling."""

import json
import logging

import requests
from requests.auth import HTTPBasicAuth

from config.config import JIRA_API_TOKEN, JIRA_EMAIL, JIRA_PROJECT_KEY, JIRA_URL


logger = logging.getLogger(__name__)


def is_jira_configured() -> bool:
    """Return True when all Jira environment variables are available."""
    return bool(JIRA_URL and JIRA_EMAIL and JIRA_API_TOKEN and JIRA_PROJECT_KEY)


def create_jira_bug_ticket(summary, description):
    """Create a Jira bug issue and return the created issue key."""
    url = f"{JIRA_URL}/rest/api/2/issue"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = json.dumps({
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Bug"},
            "labels": ["Automation", "UI-Test"],
        }
    })

    try:
        response = requests.post(url, data=payload, headers=headers, auth=auth)

        if response.status_code == 201:
            issue_key = response.json().get("key")
            logger.info(f"[JIRA 연동 성공] 티켓 자동 생성 완료: {JIRA_URL}/browse/{issue_key}")
            return issue_key

        logger.error(
            f"[JIRA 연동 실패] 응답 코드: {response.status_code}, 상세: {response.text}"
        )
        return None

    except Exception as e:
        logger.error(f"[JIRA 통신 에러] API 호출 중 문제가 발생했습니다: {e}")
        return None


def attach_image_to_jira(issue_key, image_bytes):
    """Attach screenshot bytes to an existing Jira issue."""
    url = f"{JIRA_URL}/rest/api/2/issue/{issue_key}/attachments"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"X-Atlassian-Token": "no-check"}
    files = {"file": ("error_screenshot.png", image_bytes, "image/png")}

    try:
        response = requests.post(url, headers=headers, auth=auth, files=files)

        if response.status_code == 200:
            logger.info("[JIRA 첨부 성공] 스크린샷 이미지가 티켓에 정상 업로드되었습니다.")
            return

        logger.error(
            f"[JIRA 첨부 실패] 상태 코드: {response.status_code}, 상세: {response.text}"
        )

    except Exception as e:
        logger.error(f"[JIRA 첨부 에러] {e}")
