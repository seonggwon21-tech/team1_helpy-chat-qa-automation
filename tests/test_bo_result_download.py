"""
행동특성 및 종합의견 - AI 생성 결과 다운로드 시나리오 테스트
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
    """AI 생성 결과 다운로드 시나리오 테스트"""

    TOTAL_STEPS = 11

    @pytest.mark.ui
    def test_behavior_ai_generation_flow(self, logged_in_driver, temp_download_dir):
        
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)

        logger.info("행동특성 및 종합의견 AI 생성 결과 다운로드 검증을 시작합니다.")

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
        # Step 11. 생성 결과 다운로드 검증
        # ====================================================================
        with bp.step(
            "Step 11. 생성 결과 다운로드 검증",
            step_no=11,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        # 🎯 1. 로컬 시스템 인프라 및 경로 확보 (테스트 파일의 본분)
        # pytest fixture 등으로 정의된 temp_download_dir와 os 모듈을 사용합니다.
        import os
        download_path = str(temp_download_dir)
        logger.info(f"📥 검증용 임시 폴더 경로 추적: {download_path}")

        # 🎯 2. 다운로드 버튼 조작은 페이지 함수 단 1줄로 격리 호출!
        bp.click_download_result_button()

        # 🎯 3. 로컬 폴더에 파일이 실제로 들어오는지 파일 시스템 감시 및 검증(assert) 수행
        timeout = 25
        start_time = time.time()
        downloaded = False

        while time.time() - start_time < timeout:
            files = os.listdir(download_path)
            if files:  # 빈 임시 폴더에 파일이 감지되는 순간 즉시 조기 종료 처리
                time.sleep(1) # 다운로드 중 생성되는 크롬 임시 파일(.crdownload 등) 안정화 대기
                downloaded = True
                logger.info(f"✅ 파일 다운로드 최종 감지 완료! (파일명: {files[0]})")
                break
            time.sleep(1)

        # 최종 무결성 팩트 체크
        assert downloaded, f"❌ 검증 실패: 제한 시간({timeout}초) 내에 임시 폴더에 파일이 생성되지 않았습니다."
        logger.info("🥇 [종합 대성공] 임시 폴더 기반 다운로드 로컬 파일 무결성 최종 검증 완료!")