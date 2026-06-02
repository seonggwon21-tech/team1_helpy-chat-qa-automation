"""
[TS-022] 새 대화 진입 및 기존 대화 보존 검증
포함 TC: TC_007 (새 대화 버튼), TC_009 (기존 대화 복원)

시나리오 흐름:
  [사전 준비] 복원 검증용 대화 1개 생성 후 AI 응답 대기
  Step 1. 사이드바 상단 "새 대화" 버튼 확인                      [TC_007]
  Step 2. 클릭 시 빈 대화 화면으로 이동 확인                     [TC_007]
  Step 3. 입력창 초기화 상태 확인                                [TC_007]
  Step 4. 이전 대화 내용 미표시 확인                             [TC_007]
  Step 5. 기존 대화가 사이드바 목록에 보존되어 있는지 확인         [TC_007]
  Step 6. 사이드바 목록에서 기존 대화 클릭                       [TC_009]
  Step 7. 기존 대화 내용이 화면에 정상 복원되는지 확인            [TC_009]
"""

import logging
import pytest
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestNewChat:

    @pytest.mark.ui
    def test_new_chat_preserves_existing_history(self, logged_in_driver):
        """
        [TC-007] 새 대화 버튼 클릭 후 빈 화면 전환, 입력창 초기화, 이전 메시지 미표시 확인
        [TC-009] LNB에서 기존 대화 클릭 후 내용 복원 확인
        """
        chat_page = ChatPage(logged_in_driver)

        # 사전 준비: 복원 검증용 기존 대화 1개 생성
        chat_page.show_step("사전 준비. 기존 대화 생성 중...")
        chat_page.send_message("대화 보존 검증용 테스트 메시지입니다.")
        chat_page.wait_for_ai_response()
        logger.info("사전 대화 생성 완료")

        # [TC_007] 새 대화 버튼 클릭 후 빈 화면 전환 확인
        chat_page.show_step("Step 1. 새 대화 버튼 클릭 및 화면 전환 확인 [TC_007]")
        chat_page.go_to_new_chat()
        logger.info("새 대화 화면 전환 완료")

        chat_page.show_step("Step 2-4. 입력창 초기화 및 이전 메시지 미표시 확인")
        input_value = chat_page.get_input_value()
        assert input_value == "", \
            f"새 대화 진입 후 입력창이 초기화되지 않았습니다. value: '{input_value}'"

        message_elements = chat_page.driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
        assert len(message_elements) == 0, \
            f"새 대화 화면에 이전 메시지 {len(message_elements)}개가 남아있습니다."
        logger.info("입력창 초기화 및 이전 메시지 미표시 확인 완료")

        # [TC_007] 기존 대화가 LNB 목록에 보존되어 있는지 확인
        chat_page.show_step("Step 5. LNB 기존 대화 보존 확인 [TC_007]")
        chat_page.wait_for_lnb_loaded()
        lnb_items = chat_page.get_lnb_items()
        assert len(lnb_items) > 0, \
            "새 대화 화면 전환 후 LNB 목록에서 기존 대화가 사라졌습니다."
        logger.info(f"LNB 기존 대화 {len(lnb_items)}개 보존 확인 완료")

        # [TC_009] LNB에서 기존 대화 클릭 후 내용 복원 확인
        chat_page.show_step("Step 6-7. LNB에서 기존 대화 클릭 후 복원 확인 [TC_009]")
        chat_page.click(chat_page.LNB_CHAT_ITEMS)
        chat_page.wait_for_ai_response()

        restored_messages = chat_page.driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
        assert len(restored_messages) > 0, \
            "기존 대화 클릭 후 메시지 내용이 화면에 표시되지 않습니다."
        logger.info("기존 대화 내용 복원 확인 완료")
