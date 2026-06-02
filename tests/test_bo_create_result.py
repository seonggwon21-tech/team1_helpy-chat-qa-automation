"""
행동특성 및 종합의견 - 학생 정보 입력 및 AI 생성 결과 검증 시나리오 테스트
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
    """행동특성 및 종합의견 AI 결과 생성 검증 테스트"""

    TOTAL_STEPS = 8

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

        # ============================================================
        # 최종 마감 검증
        # ============================================================

        ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
        elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
        names_text_list = [el.text.strip() for el in elements if el.text]
        
        is_found = any(target_name in n or "엘**" in n for n in names_text_list)
        assert is_found, f"❌ 검증 실패: 결과 화면에 학생 이름 [{target_name}]이 나타나지 않았습니다."
        
        logger.info("🎉 [테스트 최종 성공] 행동특성 및 종합의견 AI 생성 결과 확인 시나리오가 완벽히 통과되었습니다!")


    
    """[TC-BO-002] 중학교 옵션 선택 시 정상 진입 검증"""
    @pytest.mark.ui
    def test_behavior_generation_with_middle_school(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        
        bp.setup_tool_tab()
        bp.navigate_to_behavior_and_opinions()
        logger.info("✅ [중학교 검증] 페이지 진입 완료")
        
        wait = WebDriverWait(driver, 10)
        short_wait = WebDriverWait(driver, 3)
        
        NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")

        try:
            short_wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            logger.info("⚠️ 이전 데이터 감지 → 초기화 진행")
            bp.click_reset_button()
            bp.confirm_reset_modal()
            time.sleep(2)
        except Exception:
            logger.info("ℹ️ 초기 상태 정상 및 리렌더링 완료")

        bp.select_school_level("중학교")
        bp.click_next_step()
        
        assert wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR)), "❌ 중학교 2단계 화면 진입 실패"
        logger.info("✅ 중학교 옵션 검증 케이스 패스!")



    """[TC-BO-003] 고등학교 옵션 선택 시 정상 진입 검증"""
    @pytest.mark.ui
    def test_behavior_generation_with_middle_school(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        
        bp.setup_tool_tab()
        bp.navigate_to_behavior_and_opinions()
        logger.info("✅ [고등학교 검증] 페이지 진입 완료")
        
        wait = WebDriverWait(driver, 10)
        short_wait = WebDriverWait(driver, 3)
        
        NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")

        try:
            short_wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            logger.info("⚠️ 이전 데이터 감지 → 초기화 진행")
            bp.click_reset_button()
            bp.confirm_reset_modal()
            time.sleep(2)
        except Exception:
            logger.info("ℹ️ 초기 상태 정상 및 리렌더링 완료")

        bp.select_school_level("고등학교")
        bp.click_next_step()
        
        assert wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR)), "❌ 고등학교 2단계 화면 진입 실패"
        logger.info("✅ 고등학교 옵션 검증 케이스 패스!")