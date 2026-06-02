"""
프로젝트 전역에서 사용되는 Pytest Fixture 설정 파일.
WebDriver 초기화, 공통 환경 변수 관리, Jira/Allure 후처리 담당.
"""

import pytest
import requests
import re
import os
import logging
import time
import sys
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException

from config.config import BASE_API_URL, BASE_UI_URL, DOWNLOAD_DIR, TEST_USER
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from utils.jira_notifier import (
    attach_image_to_jira,
    create_jira_bug_ticket,
    is_jira_configured,
)
from utils.slack_notifier import send_failure_detail, send_test_summary


# 로거 설정
logger = logging.getLogger(__name__)
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# 테스트 전체 실행 시간 측정용
start_time = 0


def pytest_addoption(parser):
    """브라우저 실행 옵션을 등록합니다."""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=("chrome", "edge", "firefox", "all"),
        help="실행할 브라우저를 선택합니다. 현재 지원: chrome, edge, firefox, all",
    )


@pytest.fixture
def browser(request):
    """테스트 실행에 사용할 브라우저명을 제공합니다."""
    return request.param


def pytest_generate_tests(metafunc):
    """--browser all 선택 시 UI 테스트를 브라우저별로 파라미터화합니다."""
    if "browser" not in metafunc.fixturenames:
        return

    selected_browser = metafunc.config.getoption("--browser")
    browsers = (
        ("chrome", "edge", "firefox")
        if selected_browser == "all"
        else (selected_browser,)
    )

    metafunc.parametrize(
        "browser",
        browsers,
        indirect=True,
        ids=browsers,
        scope="function",
    )


# =========================================================
# [1] 로그 파일 초기화
# pytest.ini의 log_file 설정만으로는 logs/ 폴더가 없으면 에러가 납니다.
# 세션 시작 시 폴더와 구분선을 자동으로 생성합니다.
# =========================================================
def pytest_configure(config):
    """pytest 세션 시작 시 logs/ 폴더를 자동으로 생성합니다."""
    os.makedirs("logs", exist_ok=True)


def pytest_sessionstart(session):
    """
    테스트 세션 시작 시:
    - 로그 기록
    - 실행 시간 측정 시작
    """
    global start_time

    # 테스트 실행 시간 측정 시작
    start_time = time.time()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logger.info("=" * 60)
    logger.info(f"테스트 세션 시작: {current_time}")
    logger.info("=" * 60)


def pytest_sessionfinish(session, exitstatus):
    """
    테스트 세션 종료 시:
    - 로그 기록
    - Slack 요약 알림 전송
    """
    try:
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info("=" * 60)
        logger.info(f"테스트 세션 종료: {end_time}")

        # exitstatus 0 = 전체 통과
        status_text = (
            "전체 통과"
            if exitstatus == 0
            else f"실패 있음 (exit code: {exitstatus})"
        )

        logger.info(f"최종 결과: {status_text}")
        logger.info("=" * 60)

        if session.config.option.collectonly:
            return

        # =====================================================
        # Slack 요약 알림 전송
        # =====================================================
        duration = time.time() - start_time

        total = session.testscollected
        failed = getattr(session, "testsfailed", 0)
        passed = total - failed

        send_test_summary(
            total=total,
            passed=passed,
            failed=failed,
            duration=duration
        )

    except Exception as e:
        logger.error(f"[ERROR] pytest_sessionfinish 처리 중 오류 발생: {e}")


# =========================================================
# [2] UI 자동화 관련 Fixture: WebDriver
# =========================================================
@pytest.fixture
def firefox_download_dir(tmp_path):
    """Firefox 전용 임시 다운로드 경로. driver 초기화 시 주입되어 temp_download_dir과 공유."""
    path = tmp_path / "downloads"
    path.mkdir()
    return path


@pytest.fixture(scope="function")
def driver(browser, firefox_download_dir):
    """
    각 테스트 함수마다 Selenium WebDriver를 초기화하고 브라우저 세션을 시작함.
    테스트 종료 후 브라우저를 닫음(Teardown).
    """
    # HEADLESS 환경 변수 읽기
    HEADLESS = os.getenv("HEADLESS", "false").lower()

    if browser == "chrome":
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # CI/CD 환경일 때만 headless 적용
        if HEADLESS == "true":
            options.add_argument("--headless=new")

        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": DOWNLOAD_DIR,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
        )

        driver = webdriver.Chrome(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # CI/CD 환경일 때만 headless 적용
        if HEADLESS == "true":
            options.add_argument("--headless=new")

        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": DOWNLOAD_DIR,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
        )

        driver = webdriver.Edge(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")

        # CI/CD 환경일 때만 headless 적용
        if HEADLESS == "true":
            options.add_argument("-headless")

        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(firefox_download_dir))
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            ",".join([
                "application/pdf",
                "application/octet-stream",
                "application/vnd.ms-powerpoint",
                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "text/plain",
            ])
        )
        options.set_preference("pdfjs.disabled", True)

        driver = webdriver.Firefox(options=options)

    else:
        raise ValueError(f"지원하지 않는 브라우저입니다: {browser}")

    yield driver

    driver.quit()


# =========================================================
# [3] API 자동화 관련 Fixture: 인증 토큰 및 세션
# =========================================================
@pytest.fixture(scope="session")
def auth_token():
    """
    테스트 세션 시작 시 단 한 번 로그인하여
    API 인증용 Bearer 토큰 획득.
    """
    if not TEST_USER["id"] or not TEST_USER["pw"]:
        raise ValueError("TEST_USER_ID / TEST_USER_PW 환경변수 누락")

    login_url = f"{BASE_API_URL}/login"

    payload = {
        "username": TEST_USER["id"],
        "password": TEST_USER["pw"]
    }

    response = requests.post(login_url, data=payload)

    if response.status_code == 200:
        return response.json().get("access_token")

    pytest.fail(
        f"로그인 실패! 상태 코드: {response.status_code}"
    )


@pytest.fixture(scope="function")
def api_session(auth_token):
    """
    인증 헤더가 포함된 requests.Session 객체 제공
    """
    session = requests.Session()

    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "x-elice-org-name-short": "elice"
    })

    yield session

    session.close()


# =========================================================
# [4] 공통 환경 설정 Fixture
# =========================================================
@pytest.fixture
def base_url():
    return BASE_UI_URL


@pytest.fixture
def api_base_url():
    return BASE_API_URL


@pytest.fixture
def test_user():
    return TEST_USER


# =========================================================
# [5] 사전 조건(Pre-condition) 특화 Fixture
# =========================================================
@pytest.fixture(scope="function")
def logged_in_driver(driver, base_url, test_user):
    """
    UI 로그인이 완료된 상태의 WebDriver를 제공
    """
    login_page = LoginPage(driver, base_url)
    signup_page = SignupPage(driver)

    login_page.open()
    login_page.login(
        test_user["id"],
        test_user["pw"]
    )

    try:
        signup_page.agree_and_submit()

    except TimeoutException:
        pass

    assert (
        login_page.is_login_successful() is True
    ), "Fixture 사전 조건 설정 실패: 로그인 불가"

    return driver

# =========================================================
# [6] 다운로드 검증용 임시 디렉토리 Fixture
# =========================================================
@pytest.fixture
def temp_download_dir(tmp_path, logged_in_driver, browser, firefox_download_dir):
    """
    테스트별 격리된 임시 다운로드 경로를 제공.
    Chrome/Edge: CDP로 tmp_path로 경로 변경.
    Firefox: driver 초기화 시 주입한 firefox_download_dir 재사용 (CDP 미지원).
    테스트 종료 시 pytest가 자동 삭제.
    """
    if browser == "firefox":
        yield firefox_download_dir
    else:
        logged_in_driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(tmp_path)
        })
        yield tmp_path


# =========================================================
# [7] Pytest Hook:
# 테스트 실패 감지 및 후처리
#
# - 실패 시 스크린샷 저장
# - 로그 기록
# - Jira 티켓 자동 생성
# =========================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    테스트 실패 시:
    - 로컬 로그 기록
    - 스크린샷 저장
    - Jira 티켓 생성
    """
    outcome = yield
    rep = outcome.get_result()

    # call(테스트 본문) + setup(fixture 오류/ERROR) 모두 처리
    if rep.failed and rep.when in ("call", "setup"):

        driver = (
            item.funcargs.get("driver")
            or item.funcargs.get("logged_in_driver")
        )

        test_name = item.name

        raw_error = (
            str(call.excinfo.value)
            if call.excinfo
            else "알 수 없는 에러"
        )

        # ANSI 터미널 색상 코드 제거
        clean_error = re.sub(
            r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])',
            '',
            raw_error
        )

        # URL 제거 (Selenium 에러 메시지 내 문서 링크 등)
        clean_error = re.sub(r'https?://\S+', '', clean_error).strip()

        # =====================================================
        # Slack 실패 상세 알림 (qa-automation-report 채널)
        # =====================================================
        send_failure_detail(test_name, clean_error)

        # =====================================================
        # 로컬 로그 파일 기록
        # =====================================================
        logger.error("=" * 60)
        logger.error(f"[FAIL] 테스트 실패: {test_name}")
        logger.error(f"   파일 경로 : {item.fspath}")
        logger.error(f"   에러 내용 : {clean_error}")
        logger.error("=" * 60)

        if driver:

            # =====================================================
            # 스크린샷 저장
            # =====================================================
            screenshot_dir = os.path.join(
                "logs",
                "screenshots"
            )

            os.makedirs(
                screenshot_dir,
                exist_ok=True
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            safe_test_name = re.sub(
                r'[\\/:*?"<>|\[\]]',
                "_",
                test_name)

            safe_test_name = safe_test_name[:120]

            screenshot_filename = (
                f"{safe_test_name}_{timestamp}.png"
            )

            screenshot_path = os.path.join(
                screenshot_dir,
                screenshot_filename
            )

            screenshot_bytes = (
                driver.get_screenshot_as_png()
            )

            with open(screenshot_path, "wb") as f:
                f.write(screenshot_bytes)

            logger.error(
                f"   스크린샷  : {screenshot_path}"
            )

            # =====================================================
            # Jira 티켓 자동 생성
            # =====================================================
            if is_jira_configured():

                summary = (
                    f"[자동화 버그] "
                    f"{test_name} 테스트 실패"
                )

                browser_name = (
                    driver.capabilities.get("browserName", "Chrome").title()
                    if driver else "Chrome"
                )

                description = (
                    f"UI 자동화 테스트 실행 중 "
                    f"결함이 발견되었습니다.\n\n"

                    f"*실행 환경:* "
                    f"{browser_name} / Base URL: "
                    f"{item.funcargs.get('base_url', BASE_UI_URL)}\n"

                    f"*테스트 케이스:* "
                    f"{test_name}\n\n"

                    f"*발생한 에러 메시지:*\n"

                    f"{{code:python}}\n"
                    f"{clean_error}\n"
                    f"{{code}}\n\n"

                    f"자세한 화면 캡처는 "
                    f"본 티켓의 첨부파일을 확인해 주세요."
                )

                issue_key = create_jira_bug_ticket(
                    summary,
                    description
                )

                if issue_key:
                    attach_image_to_jira(
                        issue_key,
                        screenshot_bytes
                    )
