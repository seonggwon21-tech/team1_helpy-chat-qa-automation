"""
생성되어 있는 내 에이전트 확인 및 편집 삭제
"""

import logging
import pytest
from pages.agent_myagent_page import MyAgentPage

logger = logging.getLogger(__name__)

"""
시나리오:
    1) 로그인 완료 상태
    2) LNB 메뉴의 에이전트 탐색 클릭
    3) 필터 기본값 '전체'에 카드가 노출되어 있는지 확인
    4) 내 에이전트 진입
    5) 생성되어 있는 에이전트 카드 편집
    6) 저장

기대 결과:
    - 생성되어 있는 에이전트 카드에 진입 후 편집이 가능해야 합니다.
"""

@pytest.mark.ui
def test_viewer_my_agent_scenario(logged_in_driver, base_url):
    # 1.  페이지 오브젝트 초기화
    page = MyAgentPage(logged_in_driver)
    total_steps = 4

    # ==========================================
    # Step 1. 내 에이전트 메뉴 진입
    # ==========================================
    with page.step("내 에이전트 화면 메뉴 이동", step_no=1, total_steps=total_steps):
        page.navigate_to_my_agents()

    # ==========================================
    # Step 2. 카드 유무 판별 및 카드 클릭 진입
    # ==========================================
    with page.step("내 에이전트 카드 확보 및 편집창 진입", step_no=2, total_steps=total_steps):
        # 분기 처리와 데이터 주입이 비동기로 완벽하게 연동됩니다.
        page.ensure_agent_card_exists_and_click()

    # ==========================================
    # Step 3. 정보 수정 및 필드 주입
    # ==========================================
    with page.step("에이전트 필수 항목 수정값 타이핑", step_no=3, total_steps=total_steps):
        page.modify_agent_form_fields(
            name="자동화_테스트_에이전트_수정본",
            desc="자동화_테스트_에이전트 수정본 설명입니다.",
            prompt="자동화_테스트_에이전트 수정본 규칙입니다."
        )

    # ==========================================
    # Step 4. 변경 내용 업데이트 및 최종 모달 저장
    # ==========================================
    with page.step("수정 사항 최종 저장 및 모달 클로징", step_no=4, total_steps=total_steps):
        page.submit_and_handle_modal()
        page.clear_step_overlay()