"""
[TS-021] 메시지 전송 E2E 플로우 검증 (버튼 클릭)
포함 TC: TC_007 (새 대화 진입), TC_008 (전송 버튼)

시나리오 흐름:
  Step 1. 사이드바 상단 "새 대화" 버튼 확인 후 클릭              [TC_007]
  Step 2. 빈 대화 화면으로 이동 확인                            [TC_007]
  Step 3. 입력창 초기화 상태 확인                               [TC_007]
  Step 4. 입력창 클릭 후 텍스트 입력                            [TC_008]
  Step 5. 입력창 우측 전송 버튼 클릭                            [TC_008]
  Step 6. 전송 후 입력창 초기화 확인                             [TC_008]
  Step 7. AI 응답 로딩 완료 후 응답 내용 출력 확인               [TC_008]
"""

import logging
import pytest
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestMessageSend:

    @pytest.mark.ui
    def test_send_via_button_e2e_flow(self, logged_in_driver):
        """
        [TC-007] 새 대화 버튼 클릭 후 빈 화면 전환 확인
        [TC-008] 텍스트 입력 후 전송 버튼 클릭 시 입력창 초기화 및 AI 응답 출력 확인
        """
        chat_page = ChatPage(logged_in_driver)

        # Step 1. 사이드바 상단 "새 대화" 버튼 확인 후 클릭  [TC_007]
        chat_page.show_step("Step 1. 새 대화 버튼 클릭")
        chat_page.click(chat_page.NEW_CHAT_BUTTON)
        logger.info("새 대화 버튼 클릭 완료")

        # Step 2. 빈 대화 화면으로 이동 확인  [TC_007]
        chat_page.show_step("Step 2. 빈 대화 화면 확인")
        message_elements = chat_page.driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
        assert len(message_elements) == 0, \
            f"새 대화 화면에 이전 메시지 {len(message_elements)}개가 남아있습니다."

        # Step 3. 입력창 초기화 상태 확인  [TC_007]
        chat_page.show_step("Step 3. 입력창 초기화 확인")
        input_value = chat_page.get_input_value()
        assert input_value == "", \
            f"새 대화 진입 후 입력창이 초기화되지 않았습니다. value: '{input_value}'"
        logger.info("새 대화 진입 확인 완료 — 빈 화면 전환, 입력창 초기화")

        # Step 4. 입력창 클릭 후 텍스트 입력  [TC_008]
        chat_page.show_step("Step 4. 텍스트 입력")
        test_message = "소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘."
        chat_page.enter_text(chat_page.CHAT_INPUT, test_message)

        # Step 5. 입력창 우측 전송 버튼 클릭  [TC_008]
        chat_page.show_step("Step 5. 전송 버튼 클릭")
        chat_page.click(chat_page.SEND_BUTTON)
        logger.info(f"전송 버튼 클릭 완료: '{test_message}'")

        # Step 6. 메시지 인디케이터 표시 및 입력창 초기화 확인  [TC_008]
        chat_page.show_step("Step 6. 전송 후 입력창 초기화 확인")
        input_value = chat_page.get_input_value()
        assert input_value == "", \
            f"메시지 전송 후 입력창이 초기화되지 않았습니다. value: '{input_value}'"
        logger.info("전송 후 입력창 초기화 확인 완료")

        # Step 7. AI 응답 로딩 완료 후 응답 내용 출력 확인  [TC_008]
        chat_page.show_step("Step 7. AI 응답 대기 중...")
        response_text = chat_page.wait_for_ai_response()
        assert response_text, "AI 응답이 출력되지 않았습니다."
        logger.info(f"AI 응답 출력 확인 완료: '{response_text}'")
