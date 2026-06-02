"""
에이전트 필터 기능 시나리오 테스트
"""

import pytest
import logging
from pages.agent_filter_page import AgentFilterPage

logger = logging.getLogger(__name__)

"""
시나리오:
    1) 로그인 완료 상태
    2) LNB 메뉴의 에이전트 탐색 클릭
    3) 필터영역 (전체, 교육 지원, 글쓰기, 내부지원, 기타) 존재 확인
    4) 전체 필터부터 -> 기타 필터까지 확인
    5) 필터 초기값이 '전체'인지 확인

기대 결과:
    - 모든 필터의 정상값이 노출 되어야 하고,
      필터의 초기값은 전체가 적용 되어 있어야 한다.
"""

@pytest.mark.ui
def test_agent_filter_scenario(logged_in_driver, base_url):
    page = AgentFilterPage(logged_in_driver)
    total_steps = 7

    logger.info("🔥필터 시나리오 시작")

    # ==========================================
    # Step 1. 에이전트 탐색 이동
    # ==========================================
    with page.step("에이전트 탐색 메뉴 이동", step_no=1, total_steps=total_steps):
        page.navigate_to_agent_search()

    # ==========================================
    # Step 2. 전체 필터 기본 활성화 확인
    # ==========================================
    with page.step("전체 필터 기본 활성화 검증", step_no=2, total_steps=total_steps):
        total_classes = page.click_filter_chip("전체")

        total_card_count = page.get_card_count()

    # ==========================================
    # Step 3 ~ 6. 반복 필터 루프
    # ==========================================
    filters_to_test = [
        {"name": "교육 지원", "step": 3},
        {"name": "글쓰기", "step": 4},
        {"name": "내부 지원", "step": 5},
        {"name": "기타", "step": 6}
    ]

    for filter_info in filters_to_test:
        f_name = filter_info["name"]
        s_no   = filter_info["step"]

        with page.step(f"{f_name} 필터 검증", step_no=s_no, total_steps=total_steps):
            
            chip_classes = page.click_filter_chip(f_name)

            current_card_count = page.get_card_count()
            assert current_card_count <= total_card_count, (
                f"❌ 오류: {f_name} 필터링 후 카드 수가 전체보다 많습니다."
            )

    # ==========================================
    # Step 7. 전체 필터 복귀 검증
    # ==========================================
    with page.step("전체 필터 복귀 검증", step_no=7, total_steps=total_steps):
        page.click_filter_chip("전체")

        final_card_count = page.get_card_count()
        assert final_card_count == total_card_count, (
            "❌ 오류: '전체'로 복귀했으나 처음 카드 개수와 일치하지 않습니다."
        )

    page.clear_step_overlay()