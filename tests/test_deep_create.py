import logging

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.deep_investigation_page import DeepInvestigationPage


logger = logging.getLogger(__name__)

VALID_TOPIC = "달"
VALID_COMPLEX_TOPIC = "달 탐사! @2025 Moon"
VALID_INSTRUCTIONS = "달 자전주기 아주 간략하게 생성"
BLANK_TOPIC = "   "
MAX_TOPIC_LENGTH = 500
OVER_TOPIC_LENGTH = MAX_TOPIC_LENGTH + 1
MAX_INSTRUCTIONS_LENGTH = 2000
OVER_INSTRUCTIONS_LENGTH = MAX_INSTRUCTIONS_LENGTH + 1
GENERATION_TIMEOUT_SECONDS = 600
TOPIC_LENGTH_ERROR_MESSAGE = "1자 이상 500자 이하로 입력해주세요."
INSTRUCTIONS_LENGTH_ERROR_MESSAGE = "2000자 이하로 입력해주세요."
STOP_MESSAGE_KEYWORDS = {
    "요청에 의해 답변 생성을 중지했습니다.",
    "stopped",
    "중지",
}


def multiline_text(base_text, target_length):
    line = f"{base_text}\n"
    repeat_count = (target_length // len(line)) + 1
    return (line * repeat_count)[:target_length]


class TestDeepInvestigation:
    def show_step(self, page, step_no, message):
        page.show_step(f"Step.{step_no} {message}")

    def assert_error_message_equals(self, actual_message, expected_message, field_name):
        assert actual_message == expected_message, (
            f"{field_name} 에러 메시지가 한국어 기준 문구와 일치하지 않습니다. "
            f"expected={expected_message}, actual={actual_message}"
        )

    def assert_regenerate_enabled(self, page):
        assert page.is_regenerate_enabled(), "다시 생성 버튼이 활성화되지 않았습니다."

    def assert_regenerate_disabled(self, page):
        assert not page.is_regenerate_enabled(), "다시 생성 버튼이 비활성화되지 않았습니다."

    def assert_regenerate_modal_visible(self, page):
        assert page.is_regenerate_modal_visible(), "다시 생성 확인 모달이 표시되지 않았습니다."

    def assert_topic_error_visible(self, page):
        message = page.get_topic_error_text()
        assert message, "주제 에러 메시지가 표시되지 않았습니다."
        return message

    def assert_topic_error_hidden(self, page):
        assert not page.get_topic_error_text(), "주제 에러 메시지가 남아 있습니다."

    def assert_instructions_error_visible(self, page):
        message = page.get_instructions_error_text()
        assert message, "지시사항 에러 메시지가 표시되지 않았습니다."
        return message

    def assert_instructions_error_hidden(self, page):
        assert not page.get_instructions_error_text(), "지시사항 에러 메시지가 남아 있습니다."

    def assert_valid_topic_state(self, page, expected_topic):
        assert page.get_topic_value() == expected_topic, "입력한 주제 값이 유지되지 않았습니다."
        self.assert_topic_error_hidden(page)
        self.assert_regenerate_enabled(page)

    def assert_result_visible(self, page):
        assert page.is_result_panel_visible(), "심층 조사 결과 영역이 표시되지 않았습니다."
        assert page.is_result_success_message_visible(), "심층 조사 결과 생성 완료 메시지가 표시되지 않았습니다."
        assert page.get_result_markdown_text(), "심층 조사 결과 본문이 표시되지 않았습니다."
        assert page.is_result_download_button_visible(), "심층 조사 결과 다운로드 버튼이 표시되지 않았습니다."

    def setup_page(self, logged_in_driver, scenario):
        page = DeepInvestigationPage(logged_in_driver)

        page.navigate()
        self.show_step(
            page,
            1,
            f"로그인 상태로 심층 조사 페이지 진입 - {scenario}",
        )
        logger.info(f"[{scenario}] 심층 조사 페이지 이동 완료")

        page.clear_inputs()
        self.show_step(
            page,
            2,
            f"입력 필드 초기화 - {scenario}",
        )
        logger.info(f"[{scenario}] 입력 필드 초기화 완료")

        return page

    def open_page_only(self, logged_in_driver, scenario):
        page = DeepInvestigationPage(logged_in_driver)

        page.navigate()
        self.show_step(
            page,
            1,
            f"로그인 상태로 심층 조사 페이지 진입 - {scenario}",
        )
        logger.info(f"[{scenario}] 심층 조사 페이지 이동 완료")

        return page

    def enter_generation_inputs(self, page, scenario):
        page.enter_topic(VALID_TOPIC)
        page.enter_instructions(VALID_INSTRUCTIONS)
        self.show_step(page, 3, "주제 / 지시사항 입력")
        logger.info(f"[{scenario}] 주제 / 지시사항 입력 완료")

        self.assert_regenerate_enabled(page)

    def open_regenerate_modal(self, page, scenario):
        page.click_regenerate_button()
        self.assert_regenerate_modal_visible(page)
        self.show_step(page, 4, "다시 생성 버튼 클릭 및 확인 모달 노출 확인")
        logger.info(f"[{scenario}] 다시 생성 버튼 클릭 완료")

    def start_generation(self, page, scenario, long_wait):
        page.click_modal_regenerate_button()
        self.show_step(page, 5, "모달 내부 다시 생성 버튼 클릭")
        logger.info(f"[{scenario}] 모달 내부 다시 생성 버튼 클릭 완료")

        self.show_step(page, 6, "생성 시작 확인 (버튼 비활성화)")
        logger.info(f"[{scenario}] 생성 시작 대기")
        page.wait_until_regenerate_button_disabled(long_wait)

    def wait_for_generation_complete(self, page, scenario, long_wait):
        self.show_step(page, 7, "생성 완료 확인 (버튼 재활성화)")
        logger.info(f"[{scenario}] 생성 완료 대기")
        page.wait_until_regenerate_button_enabled(long_wait)
        logger.info(f"[{scenario}] 생성 완료 확인")

    def download_markdown_result(self, page, scenario, long_wait, download_dir):
        if not hasattr(page, "click_download_button"):
            self.show_step(page, 9, "다운로드 버튼 locator 미정")
            logger.info(f"[{scenario}] 다운로드 버튼 locator 미정")
            pytest.skip("다운로드 버튼의 안정적인 CSS locator가 아직 없습니다.")

        before_files = set(download_dir.iterdir())

        page.click_download_button()
        self.show_step(page, 9, "다운받기 버튼 클릭")
        logger.info(f"[{scenario}] 다운받기 버튼 클릭 완료")

        page.click_markdown_download_option()
        self.show_step(page, 10, "마크다운 다운로드 클릭")
        logger.info(f"[{scenario}] 마크다운 다운로드 클릭 완료")

        def is_download_completed(driver):
            current_files = set(download_dir.iterdir())
            new_files = current_files - before_files
            downloading = any(file.name.endswith(".crdownload") for file in current_files)
            markdown_files = [
                file for file in new_files
                if file.is_file() and file.suffix.lower() in (".md", ".markdown")
            ]
            return markdown_files and not downloading

        long_wait.until(is_download_completed)

        after_files = set(download_dir.iterdir())
        new_files = after_files - before_files
        downloaded_files = [
            file for file in new_files
            if file.is_file() and file.suffix.lower() in (".md", ".markdown")
        ]
        assert downloaded_files, "마크다운 다운로드 파일이 생성되지 않았습니다."
        assert all(file.stat().st_size > 0 for file in downloaded_files), (
            f"다운로드된 마크다운 파일 크기가 0입니다. files={downloaded_files}"
        )

        self.show_step(page, 11, "다운로드 완료 확인")
        logger.info(f"[{scenario}] 다운로드 완료 파일: {[file.name for file in downloaded_files]}")

        for file in downloaded_files:
            file.unlink()
        logger.info(f"[{scenario}] 다운로드 검증 파일 삭제 완료")

    @pytest.mark.ui
    def test_full_generation_result(self, logged_in_driver):
        """
        심층 조사 생성 결과 검증 시나리오

        커버 TC: TC_141, TC_142

        Step 1. 로그인 상태로 심층 조사 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 / 지시사항 입력
        Step 4. 다시 생성 버튼 클릭
        Step 5. 모달 내부 다시 생성 버튼 클릭
        Step 6. 생성 시작 확인 (버튼 비활성화)
        Step 7. 생성 완료 확인 (버튼 재활성화)
        Step 8. 생성 결과 영역 노출 확인
        """

        scenario = "심층 조사 생성 결과"

        driver = logged_in_driver
        long_wait = WebDriverWait(driver, GENERATION_TIMEOUT_SECONDS)
        page = self.setup_page(driver, scenario)

        self.enter_generation_inputs(page, scenario)
        self.open_regenerate_modal(page, scenario)
        self.start_generation(page, scenario, long_wait)
        self.wait_for_generation_complete(page, scenario, long_wait)
        self.assert_result_visible(page)
        self.show_step(page, 8, "생성 결과 영역 노출 확인")
        logger.info(f"[{scenario}] 생성 결과 영역 노출 확인 완료")

    @pytest.mark.ui
    def test_markdown_download_result(self, logged_in_driver, temp_download_dir):
        """
        심층 조사 마크다운 다운로드 검증 보류 시나리오

        커버 TC: TC 미등록 - 다운로드 정책 논의 후 확정 예정

        Step 1. 로그인 상태로 심층 조사 페이지 진입
        Step 2. 생성 완료된 결과 영역 준비
        Step 3. 다운받기 버튼 클릭
        Step 4. 마크다운 다운로드 클릭
        Step 5. 다운로드 파일 생성 및 확장자 / 크기 확인
        """

        scenario = "심층 조사 마크다운 다운로드"
        download_dir = temp_download_dir / "deep_markdown"
        download_dir.mkdir(exist_ok=True)
        logged_in_driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": str(download_dir),
        })

        driver = logged_in_driver
        long_wait = WebDriverWait(driver, GENERATION_TIMEOUT_SECONDS)
        page = self.setup_page(driver, scenario)

        self.enter_generation_inputs(page, scenario)
        self.open_regenerate_modal(page, scenario)
        self.start_generation(page, scenario, long_wait)
        self.wait_for_generation_complete(page, scenario, long_wait)
        self.assert_result_visible(page)
        self.show_step(page, 8, "생성 결과 영역 노출 확인")
        logger.info(f"[{scenario}] 생성 결과 영역 노출 확인 완료")
        self.download_markdown_result(page, scenario, long_wait, download_dir)
    
    @pytest.mark.detail
    def test_topic_validation(self, logged_in_driver):
        """
        심층 조사 주제 입력값 검증 시나리오

        커버 TC: TC_128, TC_129, TC_130, TC_131 일부

        Step 1. 로그인 상태로 심층 조사 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 0자 입력
        Step 4. 주제 0자 에러 메시지 출력 확인
        Step 5. 주제 500자 입력
        Step 6. 주제 500자 입력값 길이 확인
        Step 7. 주제 501자 입력
        Step 8. 주제 501자 에러 메시지 출력 및 버튼 비활성화 확인
        Step 9. 복합 정상 주제 입력값 유지 및 버튼 활성화 확인
        """

        scenario = "주제 입력값 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic("")
        self.show_step(page, 3, "주제 0자 입력")
        logger.info(f"[{scenario}] 주제 0자 입력 완료")

        empty_error_message = self.assert_topic_error_visible(page)
        self.assert_error_message_equals(empty_error_message, TOPIC_LENGTH_ERROR_MESSAGE, "주제 0자")
        self.assert_regenerate_disabled(page)
        self.show_step(page, 4, "주제 0자 에러 메시지 및 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 에러메시지 : {empty_error_message}")

        page.enter_topic(VALID_TOPIC * MAX_TOPIC_LENGTH)
        self.show_step(page, 5, "주제 500자 입력")
        logger.info(f"[{scenario}] 주제 500자 입력 완료")

        actual_length = len(page.get_topic_value())
        assert actual_length == MAX_TOPIC_LENGTH, f"주제 입력값 길이가 다릅니다. expected={MAX_TOPIC_LENGTH}, actual={actual_length}"
        self.assert_topic_error_hidden(page)
        self.assert_regenerate_enabled(page)
        self.show_step(page, 6, "주제 500자 입력값 길이와 버튼 활성화 확인")
        logger.info(f"[{scenario}] 주제 입력값 길이 확인 완료: {actual_length}자")

        page.enter_topic(VALID_TOPIC * OVER_TOPIC_LENGTH)
        self.show_step(page, 7, "주제 501자 입력")
        logger.info(f"[{scenario}] 주제 501자 입력 완료")

        over_limit_error_message = self.assert_topic_error_visible(page)
        self.assert_error_message_equals(over_limit_error_message, TOPIC_LENGTH_ERROR_MESSAGE, "주제 501자")
        self.assert_regenerate_disabled(page)

        self.show_step(page, 8, "주제 501자 에러 메시지 및 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 에러메시지 : {over_limit_error_message}")
        logger.info(f"[{scenario}] 주제 501자 에러 메시지 및 버튼 비활성화 확인 완료")

        page.enter_topic(VALID_COMPLEX_TOPIC)
        self.assert_valid_topic_state(page, VALID_COMPLEX_TOPIC)
        self.show_step(page, 9, "복합 정상 주제 입력값 유지 및 버튼 활성화 확인")
        logger.info(f"[{scenario}] 복합 정상 주제 입력값 검증 완료: {VALID_COMPLEX_TOPIC}")

    @pytest.mark.detail
    @pytest.mark.xfail(
        reason="Known issue: 공백만 있는 주제가 유효값으로 처리되어 다시 생성 버튼이 활성화됨"
    )
    def test_blank_topic_validation(self, logged_in_driver):
        """
        심층 조사 공백 주제 입력값 검증 시나리오

        커버 TC: TC 미등록 - 공백 주제 버그 리포트용

        Step 1. 로그인 상태로 심층 조사 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 공백만 있는 주제 입력
        Step 4. 에러 메시지 및 다시 생성 버튼 비활성화 확인
        """

        scenario = "공백 주제 입력값 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic(BLANK_TOPIC)
        self.show_step(page, 3, "공백만 있는 주제 입력")
        logger.info(f"[{scenario}] 공백 주제 입력 완료")

        error_message = self.assert_topic_error_visible(page)
        self.assert_error_message_equals(error_message, TOPIC_LENGTH_ERROR_MESSAGE, "공백 주제")
        self.assert_regenerate_disabled(page)
        self.show_step(page, 4, "에러 메시지 및 다시 생성 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 에러메시지 : {error_message}")

    @pytest.mark.detail
    def test_instructions_validation(self, logged_in_driver):
        """
        심층 조사 지시사항 입력값 검증 시나리오

        커버 TC: TC_134, TC_135

        Step 1. 로그인 상태로 심층 조사 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 지시사항 2000자 입력
        Step 4. 지시사항 2000자 입력값 길이 확인
        Step 5. 지시사항 2001자 입력
        Step 6. 지시사항 2001자 에러 메시지 출력 확인
        """

        scenario = "지시사항 입력값 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic(VALID_TOPIC)
        page.enter_instructions(multiline_text(VALID_INSTRUCTIONS, MAX_INSTRUCTIONS_LENGTH))
        self.show_step(page, 3, "줄바꿈 포함 지시사항 2000자 입력")
        logger.info(f"[{scenario}] 지시사항 2000자 입력 완료")

        actual_length = len(page.get_instructions_value())
        assert actual_length == MAX_INSTRUCTIONS_LENGTH, f"지시사항 입력값 길이가 다릅니다. expected={MAX_INSTRUCTIONS_LENGTH}, actual={actual_length}"
        self.assert_instructions_error_hidden(page)
        self.assert_regenerate_enabled(page)
        self.show_step(page, 4, "지시사항 2000자 입력값 길이와 버튼 활성화 확인")
        logger.info(f"[{scenario}] 지시사항 입력값 길이 확인 완료: {actual_length}자")

        page.enter_instructions(VALID_TOPIC * OVER_INSTRUCTIONS_LENGTH)
        self.show_step(page, 5, "지시사항 2001자 입력")
        logger.info(f"[{scenario}] 지시사항 2001자 입력 완료")

        error_message = self.assert_instructions_error_visible(page)
        self.assert_error_message_equals(error_message, INSTRUCTIONS_LENGTH_ERROR_MESSAGE, "지시사항 2001자")
        self.assert_regenerate_disabled(page)
        self.show_step(page, 6, "지시사항 2001자 에러 메시지 및 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 에러메시지 : {error_message}")

    @pytest.mark.detail
    def test_regenerate_button_state(self, logged_in_driver):
        """
        심층 조사 다시 생성 버튼 상태 검증 시나리오

        커버 TC: TC_125, TC_136, TC_137, TC_138, TC_139, TC_140

        Step 1. 로그인 상태로 심층 조사 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 미입력 / 지시사항 미입력 상태 버튼 비활성화 확인
        Step 4. 주제 미입력 / 지시사항 입력 상태 버튼 비활성화 확인
        Step 5. 주제 입력 / 지시사항 미입력 상태 버튼 활성화 확인
        Step 6. 주제 입력 / 지시사항 입력 상태 버튼 활성화 확인
        Step 7. 다시 생성 확인 모달 노출 확인
        """

        scenario = "다시 생성 버튼 상태 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic("")
        self.assert_regenerate_disabled(page)
        self.show_step(page, 3, "주제 미입력 / 지시사항 미입력 상태 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 주제 미입력 / 지시사항 미입력 상태 버튼 비활성화 확인 완료")

        page.enter_instructions(VALID_INSTRUCTIONS)
        self.assert_regenerate_disabled(page)
        self.show_step(page, 4, "주제 미입력 / 지시사항 입력 상태 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 주제 미입력 / 지시사항 입력 상태 버튼 비활성화 확인 완료")

        page.enter_topic(VALID_TOPIC)
        page.enter_instructions("")
        self.show_step(page, 5, "주제 입력 / 지시사항 미입력 상태 버튼 활성화 확인")

        assert page.get_topic_value() == VALID_TOPIC, "입력한 주제 값이 유지되지 않았습니다."
        assert page.get_instructions_value() == "", "지시사항 입력값이 비어 있지 않습니다."
        self.assert_regenerate_enabled(page)
        logger.info(f"[{scenario}] 주제 입력 / 지시사항 미입력 상태 버튼 활성화 확인 완료")

        page.enter_instructions(VALID_INSTRUCTIONS)
        self.assert_regenerate_enabled(page)
        self.show_step(page, 6, "주제 입력 / 지시사항 입력 상태 버튼 활성화 확인")
        logger.info(f"[{scenario}] 주제 입력 / 지시사항 입력 상태 버튼 활성화 확인 완료")

        page.click_regenerate_button()
        self.assert_regenerate_modal_visible(page)
        self.show_step(page, 7, "다시 생성 확인 모달 노출 확인")
        logger.info(f"[{scenario}] 다시 생성 확인 모달 노출 확인 완료")

    @pytest.mark.detail
    def test_deep_generation_stop(self, logged_in_driver):
        """
        심층 조사 생성 중지 시나리오

        커버 TC: TC 미등록 - 생성 중지 추가 자동화 시나리오

        Step 1. 로그인 상태로 심층 조사 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 / 지시사항 입력
        Step 4. 다시 생성 버튼 클릭 및 확인 모달 노출 확인
        Step 5. 모달 내 다시 생성 버튼 클릭
        Step 6. 생성 시작 확인
        Step 7. 생성 중지 버튼 클릭
        Step 8. 생성 중지 메시지 출력 확인
        """

        scenario = "심층 조사 생성 중지"
        driver = logged_in_driver
        long_wait = WebDriverWait(driver, GENERATION_TIMEOUT_SECONDS)
        page = self.setup_page(driver, scenario)

        self.enter_generation_inputs(page, scenario)
        self.open_regenerate_modal(page, scenario)
        self.start_generation(page, scenario, long_wait)

        page.click_stop_button()
        self.show_step(page, 7, "생성 중지 버튼 클릭")
        logger.info(f"[{scenario}] 생성 중지 버튼 클릭 완료")

        stop_message = page.get_stop_message_text()
        assert stop_message, "생성 중지 메시지가 표시되지 않았습니다."
        assert any(keyword in stop_message for keyword in STOP_MESSAGE_KEYWORDS), (
            f"생성 중지 메시지가 기대 범위와 다릅니다. actual={stop_message}"
        )
        self.show_step(page, 8, "생성 중지 메시지 확인")
        logger.info(f"[{scenario}] 생성 중지 메시지: {stop_message}")

