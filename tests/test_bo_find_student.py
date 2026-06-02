"""
행동특성 및 종합의견 - 학생 검색 결과 검증 시나리오 테스트
"""

import pytest
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.behavior_and_opinions_page import BehaviorAndOpinionsPage

logger = logging.getLogger(__name__)


class TestBehaviorAndOpinionsAIGeneration:
    """학생 검색 결과 검증 시나리오 테스트"""

    TOTAL_STEPS = 11

    @pytest.mark.ui
    def test_behavior_ai_generation_flow(self, logged_in_driver):

        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)

        logger.info("행동특성 및 종합의견 AI 생성 결과 검증을 시작합니다.")

        # ============================================================
        # Step 1. 페이지 이동
        # ============================================================ 
               
        with bp.step(
            "Step 1. 페이지 이동",
            step_no=1,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        bp.setup_tool_tab()
        bp.navigate_to_behavior_and_opinions()
        logger.info("✅ 행동특성 및 종합의견 페이지 진입 완료")

        wait = WebDriverWait(logged_in_driver, 10)
        short_wait = WebDriverWait(logged_in_driver, 3)

        # ============================================================
        # Step 2. 이전 테스트 데이터 정리
        # ============================================================

        with bp.step(
            "Step 2. 이전 테스트 데이터 정리",
            step_no=2,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)
        
        NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root') and contains(@class, 'Mui-selected')]")
        try:
            short_wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            logger.info("⚠️ 이전 데이터 감지 → 초기화 진행")
            
            # 리셋 함수
            bp.click_reset_button()
            bp.confirm_reset_modal()
            logger.info("✅ 초기화 완료")
            time.sleep(2)
            
        except Exception:
            logger.info("ℹ️ 초기 상태 정상")

        # ============================================================
        # Step 3. 수업 정보 입력
        # ============================================================

        with bp.step(
            "Step 3. 수업 정보 입력",
            step_no=3,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 페이지에 만들어 둔 학교급 선택 함수와 다음 버튼 함수 호출!
        bp.select_school_level("초등학교")
        bp.click_next_step()
        
        # 2단계 화면 진입 상태 체크 (검증 레이어)
        wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
        logger.info("✅ 2단계 화면 진입 완료")
        time.sleep(1)

        # ============================================================
        # Step 4. 학생 이름 입력
        # ============================================================

        with bp.step(
            "Step 4. 학생 이름 입력",
            step_no=4,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 페이지에 만들어 둔 함수로 이름 주입 끝! (ActionChains 청소 완료)
        target_name = "엘리스"
        bp.add_student(target_name)
        logger.info(f"💾 학생 이름 저장 완료: [{target_name}]")

        # ====================================================================
        # Step 5. 활동 키워드 선택
        # ====================================================================

        with bp.step(
            "Step 5. 활동 키워드 선택",
            step_no=5,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 카테고리와 원하는 키워드를 리스트로 유연하게 던집니다.
        # 인성·태도 안의 '예의 바르고 배려심 있음'을 저격 조작!
        target_category = "인성·태도"
        my_keywords = ["예의 바르고 배려심 있음"]
        
        bp.select_keywords(category_name=target_category, keyword_list=my_keywords)
        logger.info(f"🎉 동적 키워드 선택 완료: [{target_category}] -> {my_keywords}")

        # ============================================================
        # Step 6. AI 생성 완료 확인
        # ============================================================

        with bp.step(
            "Step 6. 1차 AI 초안 생성 완료 확인",
            step_no=6,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 페이지의 스마트 대기 함수 호출 (Xpath 감추기 완료)
        bp.wait_for_api_success(timeout=30)
        logger.info("🎉 [1차 완료] AI 초안 생성 성공 팝업 감지")
        time.sleep(2)

        # ====================================================================
        # Step 7. 추가 요청사항 내용 입력
        # ====================================================================

        with bp.step(
            "Step 7. 추가 요청사항 내용 입력",
            step_no=7,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 페이지 함수로 깔끔하게 추가 요청 사항 입력
        target_opinion = "칭찬해주기"
        bp.input_additional_opinion(target_opinion)
        logger.info(f"💾 추가 요청사항 저장 완료: [{target_opinion}]")

        # ============================================================
        # Step 8. AI 재생성 완료 확인
        # ============================================================

        with bp.step(
            "Step 8. AI 재생성 결과 대기",
            step_no=8,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 재생성 완료 스낵바도 공통 함수로 똑같이 대기합니다.
        bp.wait_for_api_success(timeout=30)
        logger.info("🎉 AI 생성 완료")
        time.sleep(2)

        # ====================================================================
        # Step 9. 상단 버튼으로 첫 번째 학생 추가 및 생성
        # ====================================================================

        with bp.step(
            "Step 9. 상단 버튼으로 첫 번째 학생 추가 및 생성",
            step_no=9,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        student_1_name = "토끼"
        student_1_keyword = "명랑"

        bp.click_top_add_student_button()                    # 상단 버튼 클릭
        bp.add_new_student_name_at_last_row(student_1_name)     # 이름 입력 및 저장
        bp.input_custom_keyword_at_last_row(student_1_keyword) # 직접 입력 키워드 추가 및 최종 팝업 저장
        logger.info(f"🖱️ 상단 버튼 이용: [{student_1_name}] 학생 생성 및 AI 초안 요청 완료")

        # 공통 스마트 대기 함수로 스낵바 체크
        bp.wait_for_api_success(timeout=30)
        logger.info(f"🎉 [{student_1_name}] 학생 AI 초안 생성 스낵바 감지 완료")
        time.sleep(1)

        # ====================================================================
        # Step 10. 하단 버튼으로 두 번째 학생 추가 및 생성
        # ====================================================================

        with bp.step(
            "Step 10. 하단 버튼으로 두 번째 학생 추가 및 생성",
            step_no=10,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 동일한 last row 제어 함수를 인자값만 바꿔서 완벽하게 재사용!
        student_2_name = "래빗"
        student_2_keyword = "새침"

        bp.click_bottom_add_student_button()                 # 하단 버튼 클릭
        bp.add_new_student_name_at_last_row(student_2_name)     # 이름 입력 및 저장
        bp.input_custom_keyword_at_last_row(student_2_keyword) # 직접 입력 키워드 추가 및 최종 팝업 저장
        logger.info(f"🖱️ 하단 버튼 이용: [{student_2_name}] 학생 생성 및 AI 초안 요청 완료")

        # 공통 스마트 대기 함수 재사용
        bp.wait_for_api_success(timeout=30)
        logger.info(f"🎉 [{student_2_name}] 학생 AI 초안 생성 스낵바 감지 완료")
        time.sleep(1)

        # ====================================================================
        # Step 11. 학생 이름 검색
        # ====================================================================

        with bp.step(
            "Step 11. 학생 이름 검색",
            step_no=11,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        target_search_name = "래빗"
        bp.search_student_by_name(target_search_name)

        # ====================================================================
        # Step 12. 데이터 검증
        # ====================================================================

        with bp.step(
            "Step 12. 데이터 검증",
            step_no=12,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        logger.info("🔎 최종 무결성 검증: 필터링 완료까지 안정적으로 대기합니다.")

        # 타겟 외 다른 데이터(엘리스)가 사라질 때까지 방어용 스마트 대기
        try:
            wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), '엘**')]")))
        except Exception:
            logger.info("ℹ️ 엘리스 데이터가 이미 필터링되었습니다.")

        # 🎯 [검증 레이어] 화면에 남은 실제 데이터를 확보하여 팩트 체크를 진행합니다 (assert 존치)
        ALL_DATA_ROWS = (By.XPATH, "//tbody/tr")
        elements = wait.until(EC.presence_of_all_elements_located(ALL_DATA_ROWS))
        raw_data = [el.text.strip() for el in elements if el.text]
        
        logger.info(f"📋 화면에 남은 데이터들: {raw_data}")

        has_masked_target = any("래**" in d for d in raw_data)
        has_masked_others = any("엘**" in d or "토**" in d for d in raw_data)

        # 족집게 최종 검증 검사 단행
        assert has_masked_target, "❌ 검증 실패: 검색 대상 데이터가 화면에서 검출되지 않습니다."
        assert not has_masked_others, f"❌ 검증 실패: 필터링되지 않은 다른 데이터가 화면에 남아있습니다: {raw_data}"
        
        logger.info(f"🥇 [종합 대성공] 검색 결과 확인 및 다른 데이터 필터링 무결성까지 {self.TOTAL_STEPS}단계 대장정 최종 패스!!!")