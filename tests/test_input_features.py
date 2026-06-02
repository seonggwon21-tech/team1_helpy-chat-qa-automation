"""
[TS-023] 메시지 입력 기능 검증
포함 TC: TC_011 (전송 버튼 비활성화), TC_010 (Enter 전송), TC_018 (Shift+Enter 줄바꿈)
제외 TC: TC_017 (최대 글자수 — N/T)

시나리오 흐름:
  Step 1. 빈 입력창 상태에서 전송 버튼 비활성화 확인              [TC_011]
  Step 2. 텍스트 입력 후 Shift+Enter 입력                       [TC_018]
  Step 3. 줄바꿈만 적용되고 전송이 동작하지 않음을 확인           [TC_018]
  Step 4. 새 텍스트 입력 후 Enter 키 전송                       [TC_010]
  Step 5. AI 응답이 정상 출력되는지 확인                        [TC_010]

미구현 항목 (자동화 제외):
  - TC_017: 최대 글자수 초과 입력 시 제한 동작 및 경고 노출 확인  N/T
"""

import logging
import pytest
from selenium.webdriver.common.keys import Keys
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestInputFeatures:

    @pytest.mark.ui
    def test_input_features_scenario(self, logged_in_driver):
        """
        [TC-011] 빈 입력창에서 전송 버튼 비활성화 확인
        [TC-018] Shift+Enter 입력 시 줄바꿈만 적용되고 전송 미동작 확인
        [TC-010] 텍스트 입력 후 Enter 키로 전송 및 AI 응답 출력 확인
        """
        chat_page = ChatPage(logged_in_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)
        logger.info("새 대화 화면 진입")

        # [TC_011] 빈 입력창에서 전송 버튼 비활성화 확인
        chat_page.show_step("[TC_011] 빈 입력창 전송 버튼 비활성화 확인")
        assert chat_page.is_send_button_disabled(), \
            "전송 버튼이 활성화 상태입니다. 빈 입력창에서는 disabled 속성이 있어야 합니다."
        logger.info("전송 버튼 비활성화 확인 완료")

        # [TC_018] Shift+Enter 입력 시 줄바꿈만 적용, 전송 미동작 확인
        chat_page.show_step("[TC_018] Shift+Enter 줄바꿈 확인")
        input_element = chat_page.enter_text(chat_page.CHAT_INPUT, "줄바꿈 테스트")
        input_element.send_keys(Keys.SHIFT, Keys.ENTER)

        input_value = input_element.get_attribute("value")
        assert "\n" in input_value, \
            f"Shift+Enter 입력 후 줄바꿈이 적용되지 않았습니다. value: '{input_value}'"

        ai_messages = chat_page.driver.find_elements(*chat_page.CHAT_MESSAGE_ELEMENTS)
        assert len(ai_messages) == 0, \
            f"Shift+Enter 입력 후 메시지가 전송되었습니다. AI 응답 요소 수: {len(ai_messages)}"
        logger.info("Shift+Enter 줄바꿈 적용 및 전송 미동작 확인 완료")

        # [TC_010] Enter 키 전송 후 AI 응답 출력 확인
        chat_page.show_step("[TC_010] Enter 키 전송 및 AI 응답 확인")
        input_element = chat_page.enter_text(
            chat_page.CHAT_INPUT, "소프트웨어 QA에 대해 10글자 이내로 짧게 설명해줘."
        )
        input_element.send_keys(Keys.ENTER)
        logger.info("Enter 키 전송 완료")

        response_text = chat_page.wait_for_ai_response()
        assert response_text, "AI 응답이 출력되지 않았습니다."
        logger.info(f"AI 응답 출력 확인 완료: '{response_text}'")
