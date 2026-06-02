"""
검색 모달 테스트
"""

import logging

import pytest

from selenium.common.exceptions import TimeoutException

from pages.search_page import SearchPage

logger = logging.getLogger(__name__)

SEARCH_KEYWORD_EXIST = "테스트"
SEARCH_KEYWORD_RANDOM = "testtesttest"


class TestSearchModal:
    """검색 모달 기능 테스트"""

    TOTAL_STEPS = 5

    @pytest.mark.ui
    def test_search_result_click_navigates_to_chat(self, logged_in_driver):
        search_page = SearchPage(logged_in_driver)

        logger.info("[START] TC-TOOL-001 검색 결과 클릭 후 대화 이동 테스트 시작")

        self._open_search_modal(search_page, 1, "[PASS] 검색 모달 오픈 완료")
        self._enter_search_keyword(search_page, SEARCH_KEYWORD_EXIST, 2)
        self._verify_result_list(search_page, 3)
        self._click_first_result(search_page, 4)

        with search_page.step("대화 화면 이동 확인", step_no=5, total_steps=self.TOTAL_STEPS):
            self._verify_chat_detail_open(search_page, logged_in_driver)
            self._verify_search_modal_closed(search_page)
            logger.info("[PASS] 검색 결과 클릭 후 대화 화면 이동 및 모달 닫힘 확인 완료")
            search_page.clear_step_overlay()

    @pytest.mark.xfail(
        reason="검색 모달 재오픈 시 이전 검색어가 유지되는 현재 서비스 이슈",
        strict=False
    )
    @pytest.mark.ui
    def test_search_input_cleared_after_modal_reopen(self, logged_in_driver):
        search_page = SearchPage(logged_in_driver)

        logger.info("[START] TC-TOOL-002 검색 입력값 초기화 테스트 시작")

        self._open_search_modal(search_page, 1, "[PASS] 검색 모달 오픈 완료")
        self._enter_search_keyword(search_page, SEARCH_KEYWORD_RANDOM, 2)

        with search_page.step("검색 모달 닫기", step_no=3, total_steps=self.TOTAL_STEPS):
            try:
                search_page.click_close_button()
            except TimeoutException:
                pytest.fail("X 버튼(닫기 버튼)이 보이지 않습니다.")

            self._verify_search_modal_closed(search_page)
            logger.info("[PASS] 검색 모달 닫힘 확인 완료")

        self._open_search_modal(search_page, 4, "[PASS] 검색 모달 재오픈 완료")

        with search_page.step("입력값 초기화 여부 확인", step_no=5, total_steps=self.TOTAL_STEPS):
            actual_value = search_page.get_search_input_value()
            assert actual_value == "", (
                f"[이슈] 모달 재오픈 후 이전 검색어 '{SEARCH_KEYWORD_RANDOM}' 가 "
                f"남아 있습니다. (현재 값: '{actual_value}')"
            )
            logger.info("[PASS] 모달 재오픈 시 검색 입력값 초기화 확인 완료")
            search_page.clear_step_overlay()

    @pytest.mark.ui
    def test_delete_first_lnb_chat_item(self, logged_in_driver):
        total_steps = 6
        search_page = SearchPage(logged_in_driver)

        logger.info("[START] TC-TOOL-003 LNB 첫 번째 항목 삭제 테스트 시작")

        self._run_search_and_open_first_result(search_page, logged_in_driver, 1, total_steps)

        with search_page.step("LNB 첫 번째 항목 노출 확인", step_no=2, total_steps=total_steps):
            if not search_page.is_first_lnb_chat_visible():
                pytest.fail("LNB 대화 목록 첫 번째 항목이 보이지 않습니다.")
            logger.info("[PASS] LNB 첫 번째 항목 노출 확인 완료")

        with search_page.step("LNB 첫 번째 항목 3dot 버튼 클릭", step_no=3, total_steps=total_steps):
            try:
                search_page.click_first_lnb_chat_more_button()
            except TimeoutException:
                pytest.fail("LNB 첫 번째 항목의 3dot 버튼이 보이지 않거나 클릭할 수 없습니다.")
            logger.info("[PASS] LNB 첫 번째 항목 3dot 버튼 클릭 완료")

        with search_page.step("컨텍스트 메뉴 삭제 버튼 클릭", step_no=4, total_steps=total_steps):
            try:
                search_page.click_context_delete_button()
            except TimeoutException:
                pytest.fail("컨텍스트 메뉴의 삭제 버튼이 보이지 않거나 클릭할 수 없습니다.")
            logger.info("[PASS] 컨텍스트 메뉴 삭제 버튼 클릭 완료")

        with search_page.step("삭제 확인 다이얼로그 삭제 버튼 클릭", step_no=5, total_steps=total_steps):
            try:
                search_page.click_confirm_delete_button()
            except TimeoutException:
                pytest.fail("삭제 확인 다이얼로그의 삭제 버튼이 보이지 않거나 클릭할 수 없습니다.")
            logger.info("[PASS] 삭제 확인 다이얼로그 삭제 버튼 클릭 완료")

        with search_page.step("삭제 완료 알림 노출 확인", step_no=6, total_steps=total_steps):
            if not search_page.is_delete_success_alert_visible():
                pytest.fail("'대화가 삭제되었습니다!' 알림이 노출되지 않았습니다.")
            logger.info("[PASS] 삭제 완료 알림 노출 확인 완료")
            search_page.clear_step_overlay()

    def _run_search_and_open_first_result(self, search_page, driver, step_no, total_steps):
        with search_page.step(
            "TC-TOOL-001 사전 조건 수행 (검색 → 결과 클릭 → 대화 화면 이동)",
            step_no=step_no,
            total_steps=total_steps
        ):
            search_page.open_search_modal()
            self._enter_keyword_without_step(search_page, SEARCH_KEYWORD_EXIST)
            self._assert_result_list_visible(search_page)
            search_page.click_first_result()
            self._verify_chat_detail_open(search_page, driver)
            self._verify_search_modal_closed(search_page)

    def _open_search_modal(self, search_page, step_no, success_message):
        with search_page.step("검색 모달 열기", step_no=step_no, total_steps=self.TOTAL_STEPS):
            try:
                search_page.open_search_modal()
            except TimeoutException:
                pytest.fail("LNB 검색 버튼이 보이지 않습니다.")

            assert search_page.is_modal_open(), "검색 모달이 열리지 않았습니다."
            logger.info(success_message)

    def _enter_search_keyword(self, search_page, keyword, step_no):
        with search_page.step(f"검색어 입력: {keyword}", step_no=step_no, total_steps=self.TOTAL_STEPS):
            self._enter_keyword_without_step(search_page, keyword)
            logger.info(f"[PASS] 검색어 입력 완료: {keyword}")

    @staticmethod
    def _enter_keyword_without_step(search_page, keyword):
        try:
            search_page.enter_search_keyword(keyword)
        except TimeoutException:
            pytest.fail("검색 입력창이 보이지 않아 키워드를 입력할 수 없습니다.")

    def _verify_result_list(self, search_page, step_no):
        with search_page.step("검색 결과 리스트 확인", step_no=step_no, total_steps=self.TOTAL_STEPS):
            self._assert_result_list_visible(search_page)
            logger.info("[PASS] 검색 결과 리스트 노출 확인 완료")

    @staticmethod
    def _assert_result_list_visible(search_page):
        assert search_page.is_result_list_visible(), (
            f"검색어 '{SEARCH_KEYWORD_EXIST}' 입력 후 검색 결과가 노출되지 않습니다."
        )

    def _click_first_result(self, search_page, step_no):
        with search_page.step("첫 번째 검색 결과 클릭", step_no=step_no, total_steps=self.TOTAL_STEPS):
            try:
                search_page.click_first_result()
            except TimeoutException:
                pytest.fail("첫 번째 검색 결과 항목을 클릭할 수 없습니다.")
            logger.info("[PASS] 첫 번째 검색 결과 클릭 완료")

    @staticmethod
    def _verify_chat_detail_open(search_page, driver):
        if not search_page.is_chat_detail_open():
            pytest.fail(f"검색 결과 클릭 후 대화 상세 화면으로 이동되지 않았습니다. actual={driver.current_url}")

    @staticmethod
    def _verify_search_modal_closed(search_page):
        if not search_page.is_modal_closed():
            pytest.fail("대화 화면 이동 후에도 검색 모달이 닫히지 않았습니다.")
