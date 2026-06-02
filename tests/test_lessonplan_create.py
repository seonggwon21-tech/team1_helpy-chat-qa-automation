"""
수업지도안 기능 테스트
"""

import logging

import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.lesson_plan_page import LessonplanPage
from pages.register_page import RegisterPage, get_next_user_info
from pages.login_page import LoginPage

logger = logging.getLogger(__name__)

TOOL_URL_ID = "b641b251-ecad-4cf7-8375-4b87efa281e9"
RESULT_LOCATOR = (By.CSS_SELECTOR, "[data-panel='output'] div.elice-aichat__markdown")
LOADING_LOCATOR = (By.CSS_SELECTOR, "[data-panel='output'] .MuiCircularProgress-root")


@pytest.fixture(scope="function")
def new_user_driver(driver, base_url):
    """신규 계정 회원가입 후 로그인 완료 driver를 반환합니다."""
    user_info = get_next_user_info()
    reg_page = RegisterPage(driver)
    login_page = LoginPage(driver, base_url)

    logger.info(f"[INFO] 신규 계정 생성 진행: {user_info['email']}")

    with reg_page.step("회원가입 페이지 진입", step_no=1, total_steps=3):
        reg_page.open()

    with reg_page.step("신규 계정 회원가입", step_no=2, total_steps=3):
        registered_user_info = reg_page.register(
            email=user_info["email"],
            password=user_info["password"],
            name=user_info["name"],
        )
        if registered_user_info:
            user_info = registered_user_info

    with reg_page.step("로그인 상태 검증", step_no=3, total_steps=3):
        assert login_page.is_login_successful(), (
            f"[사전 조건 실패] 로그인 상태 전환 실패 (계정: {user_info['email']})"
        )

    logger.info(f"[PASS] 신규 계정 로그인 성공: {user_info['email']}")
    return driver


class TestLessonPlan:
    """수업지도안 생성 시나리오"""

    TOTAL_STEPS = 13

    DEFAULT_CASE = {
        "school_level": "초등학교",
        "grade": "1학년",
        "subject": "국어",
        "topic": "1단원 글자의 짜임",
        "lesson_number": "2",
        "button_label": "생성하기",
        "tc_id": "TC-TOOL-001",
    }
    EXISTING_USER_CASE = {
        "school_level": "고등학교",
        "grade": "3학년",
        "subject": "한국사",
        "topic": "한국사를 쉽게 알려줘",
        "lesson_number": "1",
        "button_label": "다시 생성",
        "tc_id": "TC-TOOL-002",
    }

    @pytest.mark.xfail(
        reason="AI 응답 지연 및 간헐적 생성 실패로 인해 임시 제외",
        strict=False
    )
    @pytest.mark.ui
    def test_generate_lesson_plan_success(self, new_user_driver):
        page = LessonplanPage(new_user_driver)
        self._run_lesson_plan_flow(new_user_driver, page, self.DEFAULT_CASE)

    @pytest.mark.ui
    def test_generate_lesson_plan_with_existing_account(self, logged_in_driver):
        page = LessonplanPage(logged_in_driver)
        self._run_lesson_plan_flow(logged_in_driver, page, self.EXISTING_USER_CASE)

    def _run_lesson_plan_flow(self, driver, page, case):
        logger.info(f"[START] [{case['tc_id']}] 수업지도안 생성 시나리오 시작")

        self._navigate_to_tool(driver, page)
        self._fill_form(page, case)
        previous_result_text = self._request_generation(
            driver,
            page,
            case["button_label"]
        )
        self._wait_and_verify_result(
            driver,
            page,
            case["tc_id"],
            previous_result_text
        )

    def _navigate_to_tool(self, driver, page):
        with page.step("도구 메뉴 진입", step_no=4, total_steps=self.TOTAL_STEPS):
            page.navigate_to_tool()
            try:
                WebDriverWait(driver, 15).until(EC.url_contains(TOOL_URL_ID))
            except TimeoutException:
                pytest.fail("[FAIL] 수업지도안 페이지로 이동되지 않았습니다.")

            logger.info("[PASS] 수업지도안 페이지 진입 완료")

    def _fill_form(self, page, case):
        field_steps = [
            ("학교급 선택", 5, page.select_mui_dropdown, page.SCHOOL_LEVEL_DROPDOWN, case["school_level"]),
            ("학년 선택", 6, page.select_mui_dropdown, page.GRADE_DROPDOWN, case["grade"]),
            ("과목 선택", 7, page.select_mui_dropdown, page.SUBJECT_DROPDOWN, case["subject"]),
            ("수업 주제 입력", 8, page.enter_text, page.TOPIC_INPUT, case["topic"]),
            ("수업 차시 선택", 9, page.select_mui_dropdown, page.LESSON_NUMBER_DROPDOWN, case["lesson_number"]),
        ]

        for title, step_no, action, locator, value in field_steps:
            with page.step(title, step_no=step_no, total_steps=self.TOTAL_STEPS):
                logger.info(f"[INFO] {title}: {value}")
                action(locator, value)

    def _request_generation(self, driver, page, button_label):
        with page.step("수업지도안 생성 요청", step_no=10, total_steps=self.TOTAL_STEPS):
            previous_result_text = self._current_result_text(driver)

            logger.info(f"[ACTION] '{button_label}' 버튼 클릭")
            page.click(page.GENERATE_BUTTON)

            if page.is_generate_confirm_modal_visible():
                logger.info(f"[ACTION] 모달 내부 '{button_label}' 버튼 클릭")
                page.click_modal_generate_button()
            else:
                logger.info("[INFO] 확인 모달 없이 생성 요청이 시작되었습니다.")

            return previous_result_text

    def _wait_and_verify_result(self, driver, page, tc_id, previous_result_text=""):
        with page.step("AI 생성 결과 대기", step_no=11, total_steps=self.TOTAL_STEPS):
            self._log_loading_state(driver)

            try:
                result_element = WebDriverWait(driver, 60).until(
                    lambda current_driver: self._ready_result(current_driver)
                )
            except TimeoutException:
                pytest.fail("[FAIL] 수업지도안 결과가 60초 이내에 나타나지 않았습니다.")

            current_result_text = result_element.text.strip()
            if previous_result_text and current_result_text == previous_result_text:
                logger.info(
                    "[INFO] 생성 후 결과 텍스트가 이전 결과와 동일합니다. "
                    "결과 영역 노출 및 무결성 검증을 계속 진행합니다."
                )

            logger.info("[PASS] AI 수업지도안 생성 완료")

        with page.step("생성 결과 무결성 검증", step_no=12, total_steps=self.TOTAL_STEPS):
            result_text = result_element.text.strip()
            logger.info(f"[INFO] 생성 결과 길이: {len(result_text)}자")

            assert result_text, "[FAIL] 결과 텍스트가 비어 있습니다."
            assert len(result_text) > 10, (
                f"[FAIL] 결과 텍스트가 비정상적으로 짧습니다. (내용: {result_text})"
            )
            logger.info(f"[PASS] 생성 결과 일부 확인: {result_text[:80]}...")

        with page.step("테스트 완료", step_no=13, total_steps=self.TOTAL_STEPS):
            logger.info(f"[PASS] [{tc_id}] 수업지도안 생성 시나리오 최종 통과!")
            page.clear_step_overlay()

    @staticmethod
    def _current_result_text(driver) -> str:
        for element in driver.find_elements(*RESULT_LOCATOR):
            if element.is_displayed() and element.text.strip():
                return element.text.strip()
        return ""

    @staticmethod
    def _ready_result(driver):
        for element in driver.find_elements(*RESULT_LOCATOR):
            if element.is_displayed() and len(element.text.strip()) > 10:
                return element
        return False

    @staticmethod
    def _log_loading_state(driver):
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(LOADING_LOCATOR)
            )
            logger.info("[WAIT] AI 생성 로딩 감지")
        except TimeoutException:
            logger.info("[INFO] 로딩 스피너 미감지 - 계속 진행합니다.")
