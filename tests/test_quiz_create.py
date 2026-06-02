import logging

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.quiz_page import QuizPage


logger = logging.getLogger(__name__)

VALID_TOPIC = "한글을 만든 사람은?"
SUBJECTIVE_TOPIC = "넌센스"
COMPLEX_TOPIC = '가것ABab01!"'
BLANK_TOPIC = "   "
LONG_TOPIC_LENGTH = 5000
QUIZ_TYPE_SINGLE_CHOICE = "0"
QUIZ_TYPE_SUBJECTIVE = "3"
QUIZ_TYPE_SINGLE_CHOICE_TEXT = "객관식 (단일 선택)"
QUIZ_TYPE_SUBJECTIVE_TEXT = "주관식"
QUIZ_DIFFICULTY_LOW = "Level1"
QUIZ_DIFFICULTY_MEDIUM = "Level2"
QUIZ_DIFFICULTY_HIGH = "Level3"
QUIZ_DIFFICULTY_LOW_TEXT = "하"
GENERATION_TIMEOUT_SECONDS = 600
QUIZ_TOPIC_REQUIRED_ERROR_MESSAGE = "1자 이상 입력해주세요."
QUIZ_STOP_MESSAGE_TITLE = "요청에 의해 답변 생성을 중지했습니다."


class TestQuizCreate:
    def setup_quiz_page(self, logged_in_driver):
        self.driver = logged_in_driver
        self.long_wait = WebDriverWait(self.driver, GENERATION_TIMEOUT_SECONDS)
        self.quiz_page = QuizPage(self.driver)

    def show_step(self, page, step_no, message):
        page.show_step(f"Step.{step_no} {message}")

    def assert_error_message_equals(self, actual_message, expected_message, field_name):
        assert actual_message == expected_message, (
            f"{field_name} 에러 메시지가 한국어 기준 문구와 일치하지 않습니다. "
            f"expected={expected_message}, actual={actual_message}"
        )

    def setup_page(self, logged_in_driver, scenario):
        self.setup_quiz_page(logged_in_driver)
        page = self.quiz_page

        page.navigate_to_quiz_page()
        page.verify_quiz_page_url()
        self.show_step(page, 1, f"퀴즈 생성 페이지 진입 - {scenario}")
        logger.info(f"[{scenario}] 퀴즈 생성 페이지 이동 완료")

        return page

    def select_default_options(self, page, scenario):
        page.select_mui_dropdown(
            page.QUIZ_TYPE_DROPDOWN,
            option_value=QUIZ_TYPE_SINGLE_CHOICE,
        )
        self.show_step(page, 2, "유형 드롭다운 선택")
        logger.info(f"[{scenario}] 유형 선택 완료: {QUIZ_TYPE_SINGLE_CHOICE}")

        page.select_mui_dropdown(
            page.QUIZ_DIFFICULTY_DROPDOWN,
            option_value=QUIZ_DIFFICULTY_LOW,
        )
        self.show_step(page, 3, "난이도 드롭다운 선택")
        logger.info(f"[{scenario}] 난이도 선택 완료: {QUIZ_DIFFICULTY_LOW}")

    def enter_valid_topic(self, page, scenario):
        page.clear_topic_input()
        page.enter_topic(VALID_TOPIC)

        assert page.get_topic_value() == VALID_TOPIC, "주제 입력값이 유지되지 않았습니다."
        self.show_step(page, 4, "주제 입력값 확인")
        logger.info(f"[{scenario}] 주제 입력 완료")

    def start_generation(self, page, scenario):
        assert page.is_quiz_submit_button_enabled(), (
            "퀴즈 생성 버튼이 활성화되지 않았습니다."
        )

        page.click_quiz_submit_button()
        self.show_step(page, 5, "다시 생성 버튼 클릭")
        logger.info(f"[{scenario}] 다시 생성 버튼 클릭 완료")

        assert page.is_regenerate_modal_visible(), (
            "다시 생성 확인 모달이 표시되지 않았습니다."
        )
        page.click_modal_regenerate_button()
        self.show_step(page, 6, "모달 내부 다시 생성 버튼 클릭")
        logger.info(f"[{scenario}] 모달 내부 다시 생성 버튼 클릭 완료")

        self.show_step(page, 7, "생성 시작 확인")
        page.wait_until_submit_button_disabled(self.long_wait)
        logger.info(f"[{scenario}] 생성 시작 확인 완료")

    @pytest.mark.ui
    def test_quiz_create(self, logged_in_driver):
        """
        퀴즈 객관식 생성 시나리오

        커버 TC: TC_103, TC_121, TC_123, TC_124

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 유형 드롭다운에서 객관식 단일 선택
        Step 3. 난이도 드롭다운에서 하 선택
        Step 4. 주제 입력값 확인
        Step 5. 다시 생성 버튼 클릭
        Step 6. 모달 내부 다시 생성 버튼 클릭
        Step 7. 생성 시작 확인
        Step 8. 생성 완료 및 퀴즈 결과 노출 확인
        """
        scenario = "퀴즈 생성"
        page = self.setup_page(logged_in_driver, scenario)

        self.select_default_options(page, scenario)
        self.enter_valid_topic(page, scenario)
        self.start_generation(page, scenario)

        self.show_step(page, 8, "생성 완료 확인")
        page.wait_until_submit_button_enabled(self.long_wait)
        assert page.is_quiz_result_visible(), "퀴즈 생성 결과가 표시되지 않았습니다."
        logger.info(f"[{scenario}] 생성 완료 확인")

    @pytest.mark.ui
    def test_quiz_create_subjective_type(self, logged_in_driver):
        """
        퀴즈 주관식 생성 시나리오

        커버 TC: TC_103, TC_105, TC_107, TC_108, TC_122

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 유형 드롭다운에서 주관식 선택
        Step 3. 난이도 드롭다운에서 하 선택
        Step 4. 주제 입력값 확인
        Step 5. 다시 생성 버튼 클릭
        Step 6. 모달 내부 다시 생성 버튼 클릭
        Step 7. 생성 시작 확인
        Step 8. 생성 완료 및 주관식 퀴즈 결과 노출 확인
        """
        scenario = "주관식 퀴즈 생성"
        page = self.setup_page(logged_in_driver, scenario)

        page.select_mui_dropdown(
            page.QUIZ_TYPE_DROPDOWN,
            option_value=QUIZ_TYPE_SUBJECTIVE,
        )
        self.show_step(page, 2, "주관식 유형 선택")
        logger.info(f"[{scenario}] 유형 선택 완료: {QUIZ_TYPE_SUBJECTIVE}")

        page.select_mui_dropdown(
            page.QUIZ_DIFFICULTY_DROPDOWN,
            option_value=QUIZ_DIFFICULTY_LOW,
        )
        self.show_step(page, 3, "하 난이도 선택")
        logger.info(f"[{scenario}] 난이도 선택 완료: {QUIZ_DIFFICULTY_LOW}")

        page.clear_topic_input()
        page.enter_topic(SUBJECTIVE_TOPIC)
        assert page.get_topic_value() == SUBJECTIVE_TOPIC, "주관식 생성 주제 입력값이 유지되지 않았습니다."
        self.show_step(page, 4, "주제 입력")
        logger.info(f"[{scenario}] 주제 입력 완료")

        self.start_generation(page, scenario)

        self.show_step(page, 8, "생성 완료 확인")
        page.wait_until_submit_button_enabled(self.long_wait)
        assert page.is_quiz_result_visible(), "주관식 퀴즈 생성 결과가 표시되지 않았습니다."
        logger.info(f"[{scenario}] 생성 완료 확인")
    
    @pytest.mark.detail
    def test_quiz_topic_input_validation(self, logged_in_driver):
        """
        퀴즈 주제 입력값 검증 시나리오

        커버 TC: TC_111, TC_112

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 주제 0자 에러 메시지 및 버튼 비활성화 확인
        Step 3. 한글 / 영문 대소문자 / 숫자 / 특수문자 주제 입력값 확인
        Step 4. 5000자 주제 입력값 길이 및 버튼 활성화 확인
        """
        scenario = "주제 입력값 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.clear_topic_input()
        page.blur_active_element()
        error_message = page.get_error_message_text()
        self.assert_error_message_equals(
            error_message,
            QUIZ_TOPIC_REQUIRED_ERROR_MESSAGE,
            "퀴즈 주제 필수값",
        )
        assert page.is_quiz_submit_button_disabled(), (
            "주제 0자 입력 후 다시 생성 버튼이 비활성화되지 않았습니다."
        )
        self.show_step(page, 2, "주제 0자 에러 메시지 및 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 주제 0자 에러 메시지: {error_message}")

        page.enter_topic(COMPLEX_TOPIC)
        assert page.get_topic_value() == COMPLEX_TOPIC, (
            "복합 문자열 주제 입력값이 유지되지 않았습니다."
        )
        assert not page.has_visible_error_message(), (
            "복합 문자열 주제 입력 후 에러 메시지가 표시되었습니다."
        )
        self.show_step(page, 3, "복합 문자열 주제 입력값 확인")
        logger.info(f"[{scenario}] 복합 문자열 입력 확인 완료")

        long_topic = "가" * LONG_TOPIC_LENGTH
        page.clear_topic_input()
        page.enter_topic(long_topic)
        assert len(page.get_topic_value()) == LONG_TOPIC_LENGTH, (
            f"5000자 주제 입력값 길이가 다릅니다. actual={len(page.get_topic_value())}"
        )
        assert not page.has_visible_error_message(), (
            "5000자 주제 입력 후 에러 메시지가 표시되었습니다."
        )
        assert page.is_quiz_submit_button_enabled(), (
            "5000자 주제 입력 후 다시 생성 버튼이 활성화되지 않았습니다."
        )
        self.show_step(page, 4, "5000자 주제 입력값 확인")
        logger.info(f"[{scenario}] 5000자 입력 확인 완료")

    @pytest.mark.detail
    def test_quiz_type_dropdown(self, logged_in_driver):
        """
        퀴즈 유형 드롭다운 시나리오

        커버 TC: TC_105, TC_107

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 유형 드롭다운 클릭
        Step 3. 드롭다운 목록 및 객관식 단일 선택 옵션 표시 확인
        Step 4. 객관식 단일 선택값 반영 및 드롭다운 닫힘 확인
        """
        scenario = "퀴즈 유형 드롭다운"
        page = self.setup_page(logged_in_driver, scenario)

        page.click_quiz_type_dropdown()
        self.show_step(page, 2, "유형 드롭다운 클릭")
        logger.info(f"[{scenario}] 유형 드롭다운 클릭 완료")

        assert page.is_dropdown_displayed(), "드롭다운 목록이 표시되지 않았습니다."
        assert page.is_dropdown_option_displayed(QUIZ_TYPE_SINGLE_CHOICE), (
            "단일 선택 유형 옵션이 표시되지 않았습니다."
        )
        self.show_step(page, 3, "드롭다운 목록 및 옵션 표시 확인")

        page.select_dropdown_option_only(QUIZ_TYPE_SINGLE_CHOICE)
        page.wait_until_invisible(page.DROPDOWN_LIST)
        assert page.get_quiz_type_selected_text() == QUIZ_TYPE_SINGLE_CHOICE_TEXT, (
            "유형 선택값이 입력 필드에 반영되지 않았습니다."
        )
        self.show_step(page, 4, "유형 선택값 반영 및 드롭다운 닫힘 확인")
        logger.info(f"[{scenario}] 유형 선택 및 드롭다운 닫힘 확인")

    @pytest.mark.detail
    def test_quiz_difficulty_dropdown(self, logged_in_driver):
        """
        퀴즈 난이도 드롭다운 시나리오

        커버 TC: TC_108, TC_109 일부

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 난이도 드롭다운 클릭
        Step 3. 상 / 중 / 하 난이도 옵션 표시 확인
        Step 4. 하 난이도 선택값 반영 및 드롭다운 닫힘 확인
        """
        scenario = "퀴즈 난이도 드롭다운"
        page = self.setup_page(logged_in_driver, scenario)

        page.click_quiz_difficulty_dropdown()
        self.show_step(page, 2, "난이도 드롭다운 클릭")
        logger.info(f"[{scenario}] 난이도 드롭다운 클릭 완료")

        assert page.is_dropdown_displayed(), "드롭다운 목록이 표시되지 않았습니다."
        assert page.is_dropdown_option_displayed(QUIZ_DIFFICULTY_HIGH), (
            "상 난이도 옵션이 표시되지 않았습니다."
        )
        assert page.is_dropdown_option_displayed(QUIZ_DIFFICULTY_MEDIUM), (
            "중 난이도 옵션이 표시되지 않았습니다."
        )
        assert page.is_dropdown_option_displayed(QUIZ_DIFFICULTY_LOW), (
            "하 난이도 옵션이 표시되지 않았습니다."
        )
        self.show_step(page, 3, "난이도 옵션 표시 확인")

        page.select_dropdown_option_only(QUIZ_DIFFICULTY_LOW)
        page.wait_until_invisible(page.DROPDOWN_LIST)
        assert page.get_quiz_difficulty_selected_text() == QUIZ_DIFFICULTY_LOW_TEXT, (
            "난이도 선택값이 입력 필드에 반영되지 않았습니다."
        )
        self.show_step(page, 4, "하 난이도 선택값 반영 및 드롭다운 닫힘 확인")
        logger.info(f"[{scenario}] 하 난이도 선택 및 드롭다운 닫힘 확인")

    @pytest.mark.detail
    def test_quiz_topic_delete_disables_submit_button(self, logged_in_driver):
        """
        퀴즈 주제 삭제 시 다시 생성 버튼 상태 검증 시나리오

        커버 TC: TC_113, TC_114, TC_120

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 주제 입력 후 입력값 삭제
        Step 3. 다시 생성 버튼 비활성화 확인
        Step 4. 주제 재입력 후 다시 생성 버튼 활성화 확인
        """
        scenario = "주제 삭제 시 다시 생성 버튼 상태 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.clear_topic_input()
        page.enter_topic(VALID_TOPIC)
        assert page.get_topic_value() == VALID_TOPIC, "주제 입력값이 유지되지 않았습니다."

        page.clear_topic_input()
        page.blur_active_element()
        self.show_step(page, 2, "주제 입력값 삭제")
        logger.info(f"[{scenario}] 주제 입력값 삭제 완료")

        assert page.is_quiz_submit_button_disabled(), (
            "주제 삭제 후 다시 생성 버튼이 비활성화되지 않았습니다."
        )
        self.show_step(page, 3, "주제 삭제 후 다시 생성 버튼 비활성화 확인")
        logger.info(f"[{scenario}] 주제 삭제 후 다시 생성 버튼 비활성화 확인 완료")

        page.enter_topic(VALID_TOPIC)
        assert page.get_topic_value() == VALID_TOPIC, "주제 입력값이 유지되지 않았습니다."
        assert page.is_quiz_submit_button_enabled(), (
            "주제 입력 후 다시 생성 버튼이 활성화되지 않았습니다."
        )
        self.show_step(page, 4, "주제 입력 후 다시 생성 버튼 활성화 확인")
        logger.info(f"[{scenario}] 주제 재입력 후 다시 생성 버튼 활성화 확인 완료")

    @pytest.mark.detail
    def test_quiz_blank_topic_disables_submit_button(self, logged_in_driver):
        """
        퀴즈 공백 주제 입력 시 다시 생성 버튼 상태 검증 시나리오

        커버 TC: TC 미등록 - TC_113 확장 케이스

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 공백만 있는 주제 입력
        Step 3. 다시 생성 버튼 비활성화 확인
        Step 4. 주제 필수 에러 메시지 확인
        """
        scenario = "공백 주제 입력 시 다시 생성 버튼 상태 검증"
        page = self.setup_page(logged_in_driver, scenario)

        page.clear_topic_input()
        page.enter_topic(BLANK_TOPIC)
        page.blur_active_element()

        assert page.is_quiz_submit_button_disabled(), (
            "공백만 입력한 주제에서 다시 생성 버튼이 비활성화되지 않았습니다."
        )
        error_message = page.get_error_message_text()
        self.assert_error_message_equals(
            error_message,
            QUIZ_TOPIC_REQUIRED_ERROR_MESSAGE,
            "퀴즈 공백 주제",
        )
        self.show_step(page, 3, "공백 주제 입력 시 다시 생성 버튼 비활성화 확인")
        self.show_step(page, 4, "공백 주제 필수 에러 메시지 확인")
        logger.info(f"[{scenario}] 공백 주제 에러 메시지: {error_message}")

    @pytest.mark.detail
    def test_quiz_create_stop(self, logged_in_driver):
        """
        퀴즈 생성 중지 시나리오

        커버 TC: TC 미등록 - 생성 중지 추가 자동화 시나리오

        Step 1. 로그인 상태로 퀴즈 생성 페이지 진입
        Step 2. 유형 드롭다운에서 객관식 단일 선택
        Step 3. 난이도 드롭다운에서 하 선택
        Step 4. 주제 입력값 확인
        Step 5. 다시 생성 버튼 클릭
        Step 6. 모달 내부 다시 생성 버튼 클릭
        Step 7. 생성 시작 확인
        Step 8. 생성 중지 버튼 클릭
        Step 9. 생성 중지 메시지 출력 확인
        """
        scenario = "퀴즈 생성 중지"
        page = self.setup_page(logged_in_driver, scenario)

        self.select_default_options(page, scenario)
        self.enter_valid_topic(page, scenario)
        self.start_generation(page, scenario)

        page.click_stop_button()
        self.show_step(page, 8, "생성 중지 버튼 클릭")
        logger.info(f"[{scenario}] 생성 중지 버튼 클릭 완료")

        stop_message = page.get_stop_message_text()
        self.assert_error_message_equals(
            stop_message,
            QUIZ_STOP_MESSAGE_TITLE,
            "퀴즈 생성 중지",
        )
        self.show_step(page, 9, "생성 중지 메시지 확인")
        logger.info(f"[{scenario}] 생성 중지 메시지: {stop_message}")

