"""
새로운 에이전트 생성
"""

import pytest
import logging

from pages.agent_add_page import AgentAddPage

logger = logging.getLogger(__name__)


class TestAgentAdd:
    """새 에이전트 생성 기능 테스트"""

    TOTAL_STEPS = 7

    AGENT_NAME = "자동화_테스트_에이전트"
    AGENT_DESCRIPTION = "자동화_테스트_에이전트 입니다.."
    AGENT_PROMPT = "자동화_테스트_에이전트 규칙 입니다."

    @pytest.mark.ui
    def test_create_new_agent_scenario(self, logged_in_driver):
        page = AgentAddPage(logged_in_driver)

        logger.info("[START] 새 에이전트 생성 자동화 테스트를 시작합니다.")

        with page.step("에이전트 탐색 메뉴 진입", step_no=1, total_steps=self.TOTAL_STEPS):
            page.navigate_to_agents()
            logger.info("[PASS] 에이전트 탐색 영역 진입 성공")

        with page.step("새 에이전트 만들기 화면 진입", step_no=2, total_steps=self.TOTAL_STEPS):
            page.open_builder()
            logger.info("[PASS] 새 에이전트 만들기 화면 진입 확인")

        with page.step("에이전트 정보 입력", step_no=3, total_steps=self.TOTAL_STEPS):
            page.fill_agent_form(
                name=self.AGENT_NAME,
                description=self.AGENT_DESCRIPTION,
                prompt=self.AGENT_PROMPT,
            )
            logger.info("[PASS] 에이전트 이름, 한줄 소개, 규칙 입력 완료")

        with page.step("만들기 버튼 클릭", step_no=4, total_steps=self.TOTAL_STEPS):
            page.click_create_button()
            logger.info("[PASS] 만들기 버튼 클릭 완료")

        with page.step("공개 설정 저장", step_no=5, total_steps=self.TOTAL_STEPS):
            page.save_visibility_settings()
            page.wait_until_visibility_modal_closed()
            logger.info("[PASS] 공개 설정 저장 완료")

        with page.step("내 에이전트 탭 진입", step_no=6, total_steps=self.TOTAL_STEPS):
            page.navigate_to_my_agents()
            logger.info("[PASS] 내 에이전트 탭 진입 성공")

        with page.step("생성된 에이전트 카드 확인", step_no=7, total_steps=self.TOTAL_STEPS):
            assert page.is_created_agent_card_visible(), (
                "내 에이전트 목록에서 생성된 에이전트 카드를 찾을 수 없습니다."
            )

            logger.info("[PASS] 목록에 새 에이전트 카드가 정상적으로 노출됩니다.")
            page.clear_step_overlay()
