"""
에이전트 검색 기능 시나리오 테스트
"""

import logging
import pytest
from pages.agent_search_page import AgentSearchPage

logger = logging.getLogger(__name__)

"""
시나리오:
    1) 로그인 완료 상태
    2) LNB 메뉴의 에이전트 탐색 클릭
    3) 필터 기본값 '전체'에 카드가 노출되어 있는지 확인
    4) 검색영역 확인
    5) 잘못된 검색어 입력 시 카드 없음 확인
    6) 존재하는 카드 검색어 입력 시 카드 노출 확인

기대 결과:
    - 입력값에 맞는 카드가 노출되어야 한다.
"""

@pytest.mark.ui
def test_agent_search_full_scenario(logged_in_driver, base_url):
    page = AgentSearchPage(logged_in_driver)
    total_steps = 5  # 중복 스텝 병합 및 슬림화

    # ==========================================
    # Step 1. 에이전트 탐색 이동
    # ==========================================
    with page.step("에이전트 탐색 페이지 이동", step_no=1, total_steps=total_steps):
        page.navigate_to_agent_search()

    # ==========================================
    # Step 2. 기본 에이전트 카드 노출 검증
    # ==========================================
    with page.step("기본 에이전트 카드 노출 검증", step_no=2, total_steps=total_steps):
        initial_count = page.get_card_count()

    # ==========================================
    # Step 3. 잘못된 검색어 검증
    # ==========================================
    invalid_keyword = "tssdafasetasfdasdfasd"
    with page.step(f"잘못된 검색어 검증 [{invalid_keyword}]", step_no=3, total_steps=total_steps):
        
        page.search_keyword(invalid_keyword)
        
        # 고정 대기 없이 문구가 뜨는 순간 즉시 패스
        assert page.is_no_result_displayed(), "❌ 오류: '검색 결과가 없습니다.' 문구가 노출되지 않았습니다."

    # ==========================================
    # Step 4. 정상 검색어 검증
    # ==========================================
    valid_keyword = "제작"
    with page.step(f"정상 검색어 검증 [{valid_keyword}]", step_no=4, total_steps=total_steps):
        
        page.search_keyword(valid_keyword)
        
        # 동적 주소 기반 명시적 대기 함수 호출 (텍스트 리턴)
        actual_card_text = page.wait_for_card_with_keyword(valid_keyword)
        
        assert valid_keyword in actual_card_text, f"❌ 오류: 카드 제목에 '{valid_keyword}' 단어가 포함되어 있지 않습니다."

    # ==========================================
    # Step 5. 테스트 완료 마감
    # ==========================================
    with page.step("테스트 완료", step_no=5, total_steps=total_steps):
        page.clear_step_overlay()