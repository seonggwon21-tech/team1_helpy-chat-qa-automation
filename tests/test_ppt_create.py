import logging

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from pages.ppt_page import PptPage


logger = logging.getLogger(__name__)

VALID_TOPIC = "초등학교 수학 문제"
VALID_INSTRUCTIONS = "더하기 빼기 위주로 주어진 값이 5를 넘지 않는 문제 2개만 내줘"
COMPLEX_TEXT = '가것 ABab01! @2026 테스트'
BLANK_TOPIC = "   "
VALID_SLIDES_COUNT = "6"
VALID_SECTION_COUNT = "2"
MIN_SLIDES_COUNT = "3"
MAX_SLIDES_COUNT = "50"
MIN_SECTION_COUNT = "1"
MAX_SECTION_COUNT = "8"
INVALID_NUMERIC_TEXT = '가것ABab01!"'
NUMERIC_TEXT_EXTRACTED_VALUE = "1"
MAX_TOPIC_LENGTH = 500
OVER_TOPIC_LENGTH = MAX_TOPIC_LENGTH + 1
MAX_INSTRUCTIONS_LENGTH = 2000
OVER_INSTRUCTIONS_LENGTH = MAX_INSTRUCTIONS_LENGTH + 1
GENERATION_TIMEOUT_SECONDS = 600
DOWNLOAD_TIMEOUT_SECONDS = 60
LONG_SLIDES_COUNT = "111111111111111111111111"
LONG_SECTION_COUNT = "1000000000000000000000"
LONG_NUMERIC_FIELD_CASES = (
    ("enter_slides_count", "get_slides_count_value", LONG_SLIDES_COUNT, "슬라이드 수", "TC_066, TC_067, TC_073"),
    ("enter_section_count", "get_section_count_value", LONG_SECTION_COUNT, "섹션 수", "TC_079, TC_080"),
)

TOPIC_LENGTH_ERROR_MESSAGE = "1자 이상 500자 이하로 입력해주세요."
INSTRUCTIONS_LENGTH_ERROR_MESSAGE = "2000자 이하로 입력해주세요."
SLIDES_COUNT_RANGE_ERROR_MESSAGE = "3 이상 50 이하로 입력해주세요."
SECTION_COUNT_RANGE_ERROR_MESSAGE = "1 이상 8 이하로 입력해주세요."
STOP_MESSAGE_KEYWORDS = {
    "요청에 의해 답변 생성을 중지했습니다.",
    "stopped",
    "停止",
}


def multiline_text(base_text, target_length):
    line = f"{base_text}\n"
    repeat_count = (target_length // len(line)) + 1
    return (line * repeat_count)[:target_length]


class TestPptCreate:
    def setup_ppt_page(self, logged_in_driver):
        self.driver = logged_in_driver
        self.wait = WebDriverWait(self.driver, 10)
        self.long_wait = WebDriverWait(self.driver, GENERATION_TIMEOUT_SECONDS)
        self.download_wait = WebDriverWait(self.driver, DOWNLOAD_TIMEOUT_SECONDS)
        self.ppt_page = PptPage(self.driver)

    def show_step(self, page, step_no, message):
        page.show_step(f"Step.{step_no} {message}")

    def assert_error_message_equals(self, actual_message, expected_message, field_name):
        assert actual_message == expected_message, (
            f"{field_name} 에러 메시지가 한국어 기준 문구와 일치하지 않습니다. "
            f"expected={expected_message}, actual={actual_message}"
        )

    def assert_range_error_message(self, actual_message, field_name):
        self.assert_error_message_equals(
            actual_message,
            SLIDES_COUNT_RANGE_ERROR_MESSAGE,
            field_name,
        )

    def assert_section_range_error_message(self, actual_message, field_name):
        self.assert_error_message_equals(
            actual_message,
            SECTION_COUNT_RANGE_ERROR_MESSAGE,
            field_name,
        )

    def assert_count_error_hidden(self, actual_message, field_name):
        assert not actual_message, f"{field_name} 정상 경계값 입력 후 에러 메시지가 남아 있습니다."

    def assert_generate_enabled(self, page):
        assert page.is_generate_enabled(), "PPT 생성 버튼이 활성화되지 않았습니다."

    def assert_generate_disabled(self, page):
        assert page.is_generate_button_disabled(), "PPT 생성 버튼이 비활성화되지 않았습니다."

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

    def setup_page(self, logged_in_driver, scenario):
        self.setup_ppt_page(logged_in_driver)
        page = self.ppt_page

        page.navigate()
        page.verify_ppt_page_url()
        self.show_step(page, 1, f"PPT 생성 페이지 진입 - {scenario}")
        logger.info(f"[{scenario}] PPT 생성 페이지 이동 완료")

        page.clear_inputs()
        self.show_step(page, 2, f"입력 필드 초기화 - {scenario}")
        logger.info(f"[{scenario}] 입력 필드 초기화 완료")

        return page

    def enter_valid_inputs(self, page):
        page.enter_topic(VALID_TOPIC)
        page.enter_instructions(VALID_INSTRUCTIONS)
        page.enter_slides_count(VALID_SLIDES_COUNT)
        page.enter_section_count(VALID_SECTION_COUNT)

        assert page.get_topic_value() == VALID_TOPIC, "주제 입력값이 유지되지 않았습니다."
        assert page.get_instructions_value() == VALID_INSTRUCTIONS, (
            "지시사항 입력값이 유지되지 않았습니다."
        )
        assert page.get_slides_count_value() == VALID_SLIDES_COUNT, (
            "슬라이드 수 입력값이 유지되지 않았습니다."
        )
        assert page.get_section_count_value() == VALID_SECTION_COUNT, (
            "섹션 수 입력값이 유지되지 않았습니다."
        )
        self.assert_generate_enabled(page)

    def start_generation(self, page, scenario):
        self.assert_generate_enabled(page)

        page.click_generate_button()
        self.show_step(page, 4, "생성 버튼 클릭")
        logger.info(f"[{scenario}] 생성 버튼 클릭 완료")

        try:
            page.click_modal_generate_button()
            self.show_step(page, 5, "모달 내부 생성 버튼 클릭")
            logger.info(f"[{scenario}] 모달 내부 생성 버튼 클릭 완료")
        except TimeoutException:
            logger.info(f"[{scenario}] 확인 모달 없이 생성이 시작되었습니다.")

        self.show_step(page, 6, "생성 시작 확인")
        page.wait_until_generation_starts(self.long_wait)
        logger.info(f"[{scenario}] 생성 시작 확인 완료")

    def wait_generation_complete(self, page, scenario):
        self.show_step(page, 7, "생성 완료 확인")
        page.wait_until_generation_completes(self.long_wait)
        assert page.is_result_download_button_visible(), (
            "PPT 생성 결과 다운로드 버튼이 표시되지 않았습니다."
        )
        logger.info(f"[{scenario}] 생성 완료 확인")

    def download_result(self, page, scenario, download_dir):
        before_files = set(download_dir.iterdir())

        page.click_download_button()
        self.show_step(page, 8, "생성 결과 다운로드 버튼 클릭")
        logger.info(f"[{scenario}] 생성 결과 다운로드 버튼 클릭 완료")

        def is_download_completed(driver):
            current_files = set(download_dir.iterdir())
            new_files = current_files - before_files
            downloading = any(file.name.endswith(".crdownload") for file in current_files)
            pptx_files = [
                file for file in new_files
                if file.is_file() and file.suffix.lower() == ".pptx"
            ]
            return pptx_files and not downloading

        self.download_wait.until(is_download_completed)
        after_files = set(download_dir.iterdir())
        new_files = after_files - before_files
        downloaded_files = [
            file for file in new_files
            if file.is_file() and file.suffix.lower() == ".pptx"
        ]
        assert downloaded_files, "PPTX 다운로드 파일이 생성되지 않았습니다."
        assert all(file.stat().st_size > 0 for file in downloaded_files), (
            f"다운로드된 PPTX 파일 크기가 0입니다. files={downloaded_files}"
        )
        self.show_step(page, 9, "다운로드 완료 확인")
        logger.info(f"[{scenario}] 다운로드 완료 파일: {[file.name for file in downloaded_files]}")

        for file in downloaded_files:
            file.unlink()
        logger.info(f"[{scenario}] 다운로드 검증 파일 삭제 완료")

    @pytest.mark.ui
    def test_ppt_create_full_option(self, logged_in_driver):
        """
        PPT 전체 입력값 생성 시나리오

        커버 TC: TC_051, TC_098, TC_099, TC_102

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 / 지시사항 / 슬라이드 수 / 섹션 수 입력
        Step 4. 생성 버튼 클릭
        Step 5. 모달 내부 생성 버튼 클릭
        Step 6. 생성 시작 확인
        Step 7. 생성 완료 및 생성 결과 다운로드 버튼 노출 확인
        """
        scenario = "전체 입력값 생성"
        page = self.setup_page(logged_in_driver, scenario)

        self.enter_valid_inputs(page)
        self.show_step(page, 3, "주제 / 지시사항 / 슬라이드 수 / 섹션 수 입력")
        logger.info(f"[{scenario}] 필수 입력값 입력 완료")

        self.start_generation(page, scenario)
        self.wait_generation_complete(page, scenario)

    @pytest.mark.ui
    def test_ppt_download_file_contract(self, logged_in_driver, temp_download_dir):
        """
        PPT 다운로드 파일 품질 검증 보류 시나리오

        커버 TC: TC_100 확장

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 생성 완료된 결과 영역 준비
        Step 3. 생성 결과 다운로드 버튼 클릭
        Step 4. 다운로드 파일 확장자 / 크기 / 파일명 / 내용 형식 검증
        """

        scenario = "다운로드 파일 품질 검증"
        page = self.setup_page(logged_in_driver, scenario)
        self.enter_valid_inputs(page)
        self.start_generation(page, scenario)
        self.wait_generation_complete(page, scenario)
        self.download_result(page, scenario, temp_download_dir)

    @pytest.mark.detail
    def test_ppt_topic_validation(self, logged_in_driver):
        """
        PPT 주제 입력값 검증 시나리오

        커버 TC: TC_055, TC_056, TC_057

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 0자 입력
        Step 4. 주제 0자 에러 메시지 출력 확인
        Step 5. 주제 500자 입력값 길이 확인
        Step 6. 주제 501자 에러 메시지 출력 확인
        Step 7. 한글 / 영문 대소문자 / 숫자 / 특수문자 / 띄어쓰기 주제 입력 확인
        """
        scenario = "주제 입력값 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic("")
        page.blur_active_element()
        self.show_step(page, 3, "주제 0자 입력")
        empty_error = self.assert_topic_error_visible(page)
        self.assert_error_message_equals(empty_error, TOPIC_LENGTH_ERROR_MESSAGE, "주제 0자")
        self.show_step(page, 4, "주제 0자 에러 메시지 확인")
        logger.info(f"[{scenario}] 주제 0자 에러 메시지: {empty_error}")

        page.enter_topic("달" * MAX_TOPIC_LENGTH)
        actual_length = len(page.get_topic_value())
        assert actual_length == MAX_TOPIC_LENGTH, (
            f"주제 입력값 길이가 다릅니다. expected={MAX_TOPIC_LENGTH}, actual={actual_length}"
        )
        self.assert_topic_error_hidden(page)
        self.show_step(page, 5, "주제 500자 입력값 길이 확인")

        page.enter_topic("달" * OVER_TOPIC_LENGTH)
        page.blur_active_element()
        over_limit_error = self.assert_topic_error_visible(page)
        self.assert_error_message_equals(
            over_limit_error,
            TOPIC_LENGTH_ERROR_MESSAGE,
            "주제 501자",
        )
        self.show_step(page, 6, "주제 501자 에러 메시지 확인")
        logger.info(f"[{scenario}] 주제 501자 에러 메시지: {over_limit_error}")

        page.enter_topic(COMPLEX_TEXT)
        assert page.get_topic_value() == COMPLEX_TEXT, "복합 주제 입력값이 유지되지 않았습니다."
        self.assert_topic_error_hidden(page)
        self.show_step(page, 7, "한글 / 영문 대소문자 / 숫자 / 특수문자 / 띄어쓰기 주제 입력 확인")

    @pytest.mark.detail
    def test_ppt_instructions_validation(self, logged_in_driver):
        """
        PPT 지시사항 입력값 검증 시나리오

        커버 TC: TC_059, TC_060, TC_061

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 한글 / 영문 대소문자 / 숫자 / 특수문자 / 띄어쓰기 지시사항 입력 확인
        Step 4. 줄바꿈 포함 지시사항 2000자 입력값 확인
        Step 5. 지시사항 2001자 에러 메시지 출력 확인
        """
        scenario = "지시사항 입력값 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic(VALID_TOPIC)
        page.enter_instructions(COMPLEX_TEXT)
        assert page.get_instructions_value() == COMPLEX_TEXT, (
            "복합 지시사항 입력값이 유지되지 않았습니다."
        )
        self.assert_instructions_error_hidden(page)
        self.show_step(page, 3, "한글 / 영문 대소문자 / 숫자 / 특수문자 / 띄어쓰기 지시사항 입력 확인")

        valid_instructions = multiline_text("테스트", MAX_INSTRUCTIONS_LENGTH)
        page.enter_instructions(valid_instructions)
        actual_length = len(page.get_instructions_value())
        assert actual_length == MAX_INSTRUCTIONS_LENGTH, (
            "지시사항 2000자 입력값 길이가 다릅니다. "
            f"expected={MAX_INSTRUCTIONS_LENGTH}, actual={actual_length}"
        )
        self.assert_instructions_error_hidden(page)
        self.show_step(page, 4, "줄바꿈 포함 지시사항 2000자 입력값 확인")

        over_limit_instructions = multiline_text("테스트", OVER_INSTRUCTIONS_LENGTH)
        page.enter_instructions(over_limit_instructions)
        page.blur_active_element()
        error_message = self.assert_instructions_error_visible(page)
        self.assert_error_message_equals(
            error_message,
            INSTRUCTIONS_LENGTH_ERROR_MESSAGE,
            "지시사항 2001자",
        )
        self.show_step(page, 5, "지시사항 2001자 에러 메시지 확인")
        logger.info(f"[{scenario}] 지시사항 2001자 에러 메시지: {error_message}")

    @pytest.mark.detail
    @pytest.mark.parametrize(
        "slides_count, expected_error, field_name",
        [
            pytest.param(MIN_SLIDES_COUNT, "", "슬라이드 수 최소 경계값", id="min_valid_3"),
            pytest.param(MAX_SLIDES_COUNT, "", "슬라이드 수 최대 경계값", id="max_valid_50"),
            pytest.param("1", SLIDES_COUNT_RANGE_ERROR_MESSAGE, "슬라이드 수 1", id="below_min_1"),
            pytest.param("51", SLIDES_COUNT_RANGE_ERROR_MESSAGE, "슬라이드 수 51", id="above_max_51"),
        ],
    )
    def test_ppt_slide_count_validation(
        self,
        logged_in_driver,
        slides_count,
        expected_error,
        field_name,
    ):
        """
        PPT 슬라이드 수 입력값 검증 시나리오

        커버 TC: TC_063, TC_064, TC_065

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 파라미터 슬라이드 수 입력
        Step 4. 정상값은 에러 메시지 미노출, 범위 밖 값은 에러 메시지 출력 확인
        """
        scenario = f"슬라이드 수 입력값 검증 - {field_name}"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_slides_count(slides_count)
        page.blur_active_element()
        assert page.get_slides_count_value() == slides_count, (
            f"{field_name} 입력값이 유지되지 않았습니다."
        )
        self.show_step(page, 3, f"{field_name} 입력 확인")

        actual_error = page.get_slides_count_error_text()
        if expected_error:
            self.assert_range_error_message(actual_error, field_name)
            self.show_step(page, 4, f"{field_name} 에러 메시지 확인")
            logger.info(f"[{scenario}] {field_name} 에러 메시지: {actual_error}")
        else:
            self.assert_count_error_hidden(actual_error, field_name)
            self.show_step(page, 4, f"{field_name} 정상 입력 확인")

    @pytest.mark.detail
    @pytest.mark.parametrize(
        "section_count, expected_error, field_name",
        [
            pytest.param(MIN_SECTION_COUNT, "", "섹션 수 최소 경계값", id="min_valid_1"),
            pytest.param(MAX_SECTION_COUNT, "", "섹션 수 최대 경계값", id="max_valid_8"),
            pytest.param("9", SECTION_COUNT_RANGE_ERROR_MESSAGE, "섹션 수 9", id="above_max_9"),
        ],
    )
    def test_ppt_section_count_boundary_validation(
        self,
        logged_in_driver,
        section_count,
        expected_error,
        field_name,
    ):
        """
        PPT 섹션 수 경계값 검증 시나리오

        커버 TC: TC_076, TC_078

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 파라미터 섹션 수 입력
        Step 4. 정상값은 에러 메시지 미노출, 범위 밖 값은 에러 메시지 출력 확인
        """
        scenario = f"섹션 수 경계값 검증 - {field_name}"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_section_count(section_count)
        page.blur_active_element()
        assert page.get_section_count_value() == section_count, (
            f"{field_name} 입력값이 유지되지 않았습니다."
        )
        self.show_step(page, 3, f"{field_name} 입력 확인")

        actual_error = page.get_section_count_error_text()
        if expected_error:
            self.assert_section_range_error_message(actual_error, field_name)
            self.show_step(page, 4, f"{field_name} 에러 메시지 확인")
            logger.info(f"[{scenario}] {field_name} 에러 메시지: {actual_error}")
        else:
            self.assert_count_error_hidden(actual_error, field_name)
            self.show_step(page, 4, f"{field_name} 정상 입력 확인")

    @pytest.mark.detail
    @pytest.mark.parametrize(
        "enter_method_name, get_method_name, field_name",
        [
            pytest.param(
                "enter_slides_count",
                "get_slides_count_value",
                "슬라이드 수",
                id="slides_count",
            ),
            pytest.param(
                "enter_section_count",
                "get_section_count_value",
                "섹션 수",
                id="section_count",
            ),
        ],
    )
    def test_ppt_slide_and_section_count_reject_zero_input(
        self,
        logged_in_driver,
        enter_method_name,
        get_method_name,
        field_name,
    ):
        """
        PPT 슬라이드, 섹션 수 0 입력 차단 검증 시나리오

        커버 TC: TC_077, 슬라이드 수 0 입력 차단 추가 자동화 시나리오

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 슬라이드 수 또는 섹션 수 0 입력 불가 확인
        """
        scenario = f"슬라이드, 섹션 수 0 입력 차단 검증 - {field_name}"
        page = self.setup_page(logged_in_driver, scenario)

        enter_method = getattr(page, enter_method_name)
        get_method = getattr(page, get_method_name)

        enter_method("0")
        page.blur_active_element()
        assert get_method() == "", f"{field_name} 0 입력값이 차단되지 않았습니다."
        self.show_step(page, 3, f"{field_name} 0 입력 불가 확인")
        logger.info(f"[{scenario}] {field_name} 0 입력 불가 확인 완료")

    @pytest.mark.detail
    @pytest.mark.parametrize(
        "enter_method_name, get_method_name, field_name",
        [
            pytest.param(
                "enter_slides_count",
                "get_slides_count_value",
                "슬라이드 수",
                id="slides_count",
            ),
            pytest.param(
                "enter_section_count",
                "get_section_count_value",
                "섹션 수",
                id="section_count",
            ),
        ],
    )
    def test_ppt_numeric_fields_reject_text(
        self,
        logged_in_driver,
        enter_method_name,
        get_method_name,
        field_name,
    ):
        """
        PPT 슬라이드, 섹션 수 문자 포함 입력값 검증 시나리오

        커버 TC: TC_074 일부, 섹션 수 문자 입력 추가 자동화 시나리오

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 슬라이드 수 또는 섹션 수에 문자 포함 값 입력
        Step 4. 숫자만 추출되어 반영되는지 확인
        """
        scenario = f"슬라이드, 섹션 수 문자 포함 입력값 검증 - {field_name}"
        page = self.setup_page(logged_in_driver, scenario)

        enter_method = getattr(page, enter_method_name)
        get_method = getattr(page, get_method_name)

        enter_method(INVALID_NUMERIC_TEXT)
        assert get_method() == NUMERIC_TEXT_EXTRACTED_VALUE, (
            f"{field_name} 필드가 문자 포함 입력에서 숫자만 반영하지 않았습니다."
        )
        self.show_step(page, 3, f"{field_name} 필드 문자 포함 입력 시 숫자만 반영 확인")
        logger.info(f"[{scenario}] {field_name} 문자 포함 입력값 검증 완료")

    @pytest.mark.detail
    @pytest.mark.xfail(
        reason="Known issue: 숫자 입력 필드의 긴 숫자 입력값이 지수 표기/Infinity로 변환됨",
        strict=True,
    )
    @pytest.mark.parametrize(
        "enter_method_name, get_method_name, long_value, field_name, cover_tc",
        LONG_NUMERIC_FIELD_CASES,
    )
    def test_ppt_numeric_field_long_value_cases(
        self,
        logged_in_driver,
        enter_method_name,
        get_method_name,
        long_value,
        field_name,
        cover_tc,
    ):
        """
        PPT 숫자 필드 긴 입력값 변환 검증 시나리오

        커버 TC: TC_066, TC_067, TC_073, TC_079, TC_080 중심

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 숫자 필드에 긴 입력값 입력
        Step 4. 긴 입력값이 지수 표기 / Infinity로 변환되지 않고 원본 유지되는지 확인
        """
        scenario = f"{field_name} 긴 입력값 변환 검증 - {cover_tc}"
        page = self.setup_page(logged_in_driver, scenario)
        enter_method = getattr(page, enter_method_name)
        get_method = getattr(page, get_method_name)

        enter_method(long_value)
        assert get_method() == long_value, (
            f"{field_name} 긴 입력값이 원본 그대로 유지되지 않았습니다. "
            f"expected={long_value}, actual={get_method()}"
        )
        self.show_step(page, 4, f"{field_name} 긴 입력값 원본 유지 확인")

    @pytest.mark.detail
    def test_ppt_generate_button_state(self, logged_in_driver):
        """
        PPT 생성 버튼 상태 검증 시나리오

        커버 TC: TC_083, TC_084, TC_091, TC_098, TC_101 일부

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 미입력 상태 생성 버튼 비활성화 확인
        Step 4. 주제 미입력 / 지시사항 입력 상태 생성 버튼 비활성화 확인
        Step 5. 주제 입력 / 지시사항 미입력 상태 생성 버튼 활성화 확인
        Step 6. 주제만 입력한 상태 생성 버튼 활성화 확인
        Step 7. 전체 입력값 입력 상태 생성 버튼 활성화 확인
        """
        scenario = "생성 버튼 상태 검증"
        page = self.setup_page(logged_in_driver, scenario)

        self.assert_generate_disabled(page)
        self.show_step(page, 3, "주제 미입력 상태 생성 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 주제 미입력 상태 생성 버튼 비활성화 확인 완료")

        page.enter_instructions(VALID_INSTRUCTIONS)
        self.assert_generate_disabled(page)
        self.show_step(page, 4, "주제 미입력 / 지시사항 입력 상태 생성 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 주제 미입력 / 지시사항 입력 상태 생성 버튼 비활성화 확인 완료")

        page.enter_topic(VALID_TOPIC)
        page.enter_instructions("")
        self.assert_generate_enabled(page)
        self.show_step(page, 5, "주제 입력 / 지시사항 미입력 상태 생성 버튼 활성화 확인")
        logger.info(f"[{scenario}] 주제 입력 / 지시사항 미입력 상태 생성 버튼 활성화 확인 완료")

        page.enter_topic(VALID_TOPIC)
        page.enter_slides_count("")
        page.enter_section_count("")
        self.assert_generate_enabled(page)
        self.show_step(page, 6, "주제만 입력한 상태 생성 버튼 활성화 확인")
        logger.info(f"[{scenario}] 주제만 입력한 상태 생성 버튼 활성화 확인 완료")

        page.enter_instructions(VALID_INSTRUCTIONS)
        page.enter_slides_count(VALID_SLIDES_COUNT)
        page.enter_section_count(VALID_SECTION_COUNT)
        self.assert_generate_enabled(page)
        self.show_step(page, 7, "전체 입력값 입력 상태 생성 버튼 활성화 확인")
        logger.info(f"[{scenario}] 전체 입력값 입력 상태 생성 버튼 활성화 확인 완료")

    @pytest.mark.detail
    def test_ppt_topic_delete_disables_generate_button(self, logged_in_driver):
        """
        PPT 주제 삭제 시 다시생성 버튼 상태 검증 시나리오

        커버 TC: TC_057 일부, 주제 삭제 추가 자동화 시나리오

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 정상값 입력 후 다시생성 버튼 활성화 확인
        Step 4. 주제 입력값 삭제 후 다시생성 버튼 비활성화 확인
        """
        scenario = "주제 삭제 시 다시생성 버튼 상태 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic(VALID_TOPIC)
        assert page.get_topic_value() == VALID_TOPIC, "주제 입력값이 유지되지 않았습니다."
        self.assert_generate_enabled(page)
        self.show_step(page, 3, "주제 정상값 입력 후 다시생성 버튼 활성화 확인")
        logger.info(f"[{scenario}] 주제 정상값 입력 후 다시생성 버튼 활성화 확인 완료")

        page.clear_topic()
        page.blur_active_element()
        assert page.get_topic_value() == "", "주제 입력값이 삭제되지 않았습니다."
        self.assert_generate_disabled(page)
        self.show_step(page, 4, "주제 입력값 삭제 후 다시생성 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 주제 입력값 삭제 후 다시생성 버튼 비활성화 확인 완료")

    @pytest.mark.detail
    @pytest.mark.xfail(
        reason="Known issue: 공백만 있는 주제가 유효값으로 처리되어 다시생성 버튼이 활성화됨"
    )
    def test_ppt_blank_topic_disables_generate_button(self, logged_in_driver):
        """
        PPT 공백 주제 입력 시 다시생성 버튼 상태 검증 시나리오

        커버 TC: TC 미등록 - 공백 주제 버그 리포트용

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 공백만 있는 주제 에러 메시지 및 다시생성 버튼 비활성화 확인
        """
        scenario = "공백 주제 입력 시 다시생성 버튼 상태 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.enter_topic(BLANK_TOPIC)
        page.blur_active_element()

        blank_error = self.assert_topic_error_visible(page)
        self.assert_error_message_equals(blank_error, TOPIC_LENGTH_ERROR_MESSAGE, "공백 주제")
        self.assert_generate_disabled(page)
        self.show_step(page, 3, "공백만 있는 주제 에러 메시지 및 다시생성 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 공백 주제 에러 메시지: {blank_error}")

    @pytest.mark.detail
    def test_ppt_create_stop(self, logged_in_driver):
        """
        PPT 생성 중지 시나리오

        커버 TC: TC 미등록 - 생성 중지 추가 자동화 시나리오

        Step 1. 로그인 상태로 PPT 생성 페이지 진입
        Step 2. 입력 필드 초기화
        Step 3. 주제 / 지시사항 / 슬라이드 수 / 섹션 수 입력
        Step 4. 생성 버튼 클릭
        Step 5. 모달 내부 생성 버튼 클릭
        Step 6. 생성 시작 확인
        Step 7. 생성 중지 버튼 클릭
        Step 8. 생성 중지 메시지 출력 확인
        """
        scenario = "생성 중지"
        page = self.setup_page(logged_in_driver, scenario)

        self.enter_valid_inputs(page)
        self.show_step(page, 3, "주제 / 지시사항 / 슬라이드 수 / 섹션 수 입력")

        self.start_generation(page, scenario)

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

