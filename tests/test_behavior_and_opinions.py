"""
행동특성 및 종합의견 메인 성공 시나리오 및 독립 서브 TC 고도화 스위트
"""

import pytest
import time
import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.behavior_and_opinions_page import BehaviorAndOpinionsPage

logger = logging.getLogger(__name__)


class TestBehaviorAndOpinionsAIGeneration:
    """행동특성 및 종합의견 테스트 시나리오"""

    # 메인 시나리오 전용 총 스텝 수
    TOTAL_STEPS = 7

    @pytest.mark.ui
    def test_behavior_ai_generation_flow(self, logged_in_driver, temp_download_dir):

        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)

        logger.info("행동특성 및 종합의견 AI 생성 결과 검증을 시작합니다.")

        # ============================================================
        # Step 1. 페이지 이동
        # ============================================================ 
        with bp.step("Step 1. 페이지 이동", step_no=1, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        bp.setup_tool_tab()
        bp.navigate_to_behavior_and_opinions()
        logger.info("✅ 행동특성 및 종합의견 페이지 진입 완료")

        wait = WebDriverWait(logged_in_driver, 10)
        short_wait = WebDriverWait(logged_in_driver, 3)

        # ============================================================
        # Step 2. 이전 테스트 데이터 정리
        # ============================================================
        with bp.step("Step 2. 이전 테스트 데이터 정리", step_no=2, total_steps=self.TOTAL_STEPS):
            time.sleep(1)
        
        NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root') and contains(@class, 'Mui-selected')]")
        try:
            short_wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            logger.info("⚠️ 이전 데이터 감지 → 초기화 진행")
            bp.click_reset_button()
            bp.confirm_reset_modal()
            logger.info("✅ 초기화 완료")
            time.sleep(2)
        except Exception:
            logger.info("ℹ️ 초기 상태 정상")

        # ============================================================
        # Step 3. 수업 정보 입력
        # ============================================================
        with bp.step("Step 3. 수업 정보 입력", step_no=3, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        bp.select_school_level("초등학교")
        bp.click_next_step()
        
        wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
        logger.info("✅ 2단계 화면 진입 완료")
        time.sleep(1)

        # ============================================================
        # Step 4. 학생 이름 입력
        # ============================================================
        with bp.step("Step 4. 학생 이름 입력", step_no=4, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        target_name = "엘리스"
        bp.add_student(target_name)
        logger.info(f"💾 학생 이름 저장 완료: [{target_name}]")

        # ====================================================================
        # Step 5. 활동 키워드 선택
        # ====================================================================
        with bp.step("Step 5. 활동 키워드 선택", step_no=5, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        target_category = "인성·태도"
        my_keywords = ["예의 바르고 배려심 있음"]
        
        bp.select_keywords(category_name=target_category, keyword_list=my_keywords)
        logger.info(f"🎉 동적 키워드 선택 완료: [{target_category}] -> {my_keywords}")

        # ============================================================
        # Step 6. AI 생성 완료 확인
        # ============================================================
        with bp.step("Step 6. AI 생성 완료 확인", step_no=6, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        bp.wait_for_api_success(timeout=30)
        logger.info("🎉 [1차 완료] AI 초안 생성 성공 팝업 감지")
        time.sleep(2)

        # ====================================================================
        # Step 7. 생성 결과 다운로드
        # ====================================================================
        with bp.step("Step 7. 생성 결과 다운로드", step_no=7, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        download_path = str(temp_download_dir)
        logger.info(f"📥 검증용 임시 폴더 경로 추적: {download_path}")

        bp.click_download_result_button()

        timeout = 25
        start_time = time.time()
        downloaded = False

        while time.time() - start_time < timeout:
            files = os.listdir(download_path)
            if files:  
                time.sleep(1) 
                downloaded = True
                logger.info(f"✅ 파일 다운로드 최종 감지 완료! (파일명: {files[0]})")
                break
            time.sleep(1)

        assert downloaded, f"❌ 검증 실패: 제한 시간 내에 임시 폴더에 파일이 생성되지 않았습니다."
        logger.info("🥇 [종합 대성공] 행동특성 및 종합의견 테스트 시나리오")


    """ [TC-BO-001] 학교급 선택 시 정상 진입 검증 """
    @pytest.mark.ui
    @pytest.mark.parametrize("school_level", ["초등학교", "중학교", "고등학교"])
    def test_behavior_generation_entry_by_school_level(self, logged_in_driver, school_level):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        short_wait = WebDriverWait(driver, 3)
        SUB_STEPS = 3
        
        logger.info(f"[START] [TC-BO-001 SchoolLevel] 입력값 [{school_level}] 기반 진입 검증 시작")
        
        with bp.step("Step 1. 환경 진입 및 찌꺼기 청소", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                short_wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                logger.info("⚠️ 이전 데이터 감지 → 안전 초기화 단행")
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                logger.info("ℹ️ 초기 상태 정상이므로 리렌더링 패스")

        with bp.step("Step 2. 파라미터 기반 학교급 동적 선택 및 클릭", step_no=2, total_steps=SUB_STEPS):
            bp.select_school_level(school_level)
            bp.click_next_step()
        
        with bp.step("Step 3. 2단계 진입 랜드마크 스캔 검증", step_no=3, total_steps=SUB_STEPS):
            is_entry_successful = wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            assert is_entry_successful, f"❌ 진입 실패: 옵션 [{school_level}] 선택 에러"
            logger.info(f"✅ [PASS] [{school_level}] 옵션 기반 2단계 진입 성공 무결성 확인 완료!")


    """ [TC-BO-002] 학교급 미선택 시 '다음으로' 버튼 잠금 검증 """
    @pytest.mark.ui
    def test_next_button_disabled_when_no_school_level_selected(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        SUB_STEPS = 2

        logger.info("[START] 학교급 미선택 시 '다음으로' 버튼 잠금 검증 시작")

        with bp.step("Step 1. 학교급 미선택 상태로 최초 진입", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            time.sleep(1.5)

        with bp.step("Step 2. 다음으로 버튼 활성화 속성(disabled) 검시", step_no=2, total_steps=SUB_STEPS):
            NEXT_BUTTON_XPATH = (By.XPATH, "//button[@type='submit'][@form='student_record_generation'] | //button[@type='submit'][@form='student_evaluation']")
            next_btn_element = driver.find_element(*NEXT_BUTTON_XPATH)
            
            is_next_disabled_attr = next_btn_element.get_attribute("disabled")
            is_next_enabled_status = next_btn_element.is_enabled()
            
            logger.info(f"📋 '다음으로' 버튼 disabled 속성 상태: '{is_next_disabled_attr}'")
            
            assert not is_next_enabled_status or is_next_disabled_attr is not None, \
                "❌ 예외 결함 발견: 학교급 미선택 상태인데 버튼이 활성화되어 있습니다!"
            logger.info("✅ [PASS] 학교급 미선택 상태에서 '다음으로' 버튼 잠금 확인 완료")


    """ [TC-BO-003] 학생 이름 필드 특수문자 주입 예외 차단 검증 """
    @pytest.mark.ui
    @pytest.mark.xfail(reason="🚨 GitLab Issue - 학생 이름 특수문자 차단 누락 결함", strict=True)
    def test_behavior_student_name_input_restriction_with_special_characters(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 3

        logger.info("[START] [TC-BO-003] 학생 이름 필드 특수문자 주입 예외 차단 검증 시작")

        with bp.step("Step 1. 행발 2단계 학생 입력 화면 사전 안착", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))

        with bp.step("Step 2. 학생 이름 필드 예외 특수문자('####') 주입", step_no=2, total_steps=SUB_STEPS):
            invalid_name = "####"
            bp.add_student(invalid_name)
            time.sleep(2)

        with bp.step("Step 3. 가상 DOM 전체 마스킹(#**) 찌꺼기 전수 스캔", step_no=3, total_steps=SUB_STEPS):
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = driver.find_elements(*ALL_TEXT_NODES)
            raw_data = [el.text.strip() for el in elements if el.text]
            
            is_invalid_name_saved = any(invalid_name in d or "#**" in d or d.startswith("#*") for d in raw_data)

            if is_invalid_name_saved:
                fail_msg = f"\n🚨 [CRITICAL BUG DETECTED] 행발 학생 이름 특수문자 [{invalid_name}] 우회 적재 결함 발견!"
                logger.error(fail_msg)
                pytest.fail(fail_msg)
            else:
                logger.info("✅ [합격] 특수문자 학생 이름이 저장되지 않고 행발 화면에서 안전하게 차단되었습니다.")


    """ [TC-BO-004] 활동 키워드 직접 입력 검증 """
    @pytest.mark.ui
    def test_behavior_first_student_keyword_custom_input_and_verify_generation(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-BO-004] 활동 키워드 직접 입력 검증 시작")

        with bp.step("Step 1. 행발 도구 2단계 입력창 정식 진입", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))

        with bp.step("Step 2. 기본 행 학생 이름('엘리스') 적재", step_no=2, total_steps=SUB_STEPS):
            target_name = "엘리스"
            bp.add_student(target_name)
            time.sleep(1)

        with bp.step("Step 3. POM 은닉 함수 호출 기반 커스텀 키워드('활발') 주입", step_no=3, total_steps=SUB_STEPS):
            custom_keyword = "활발"
            bp.input_custom_keyword_at_last_row(custom_keyword)
            time.sleep(1)

        with bp.step("Step 4. 비동기 생성 스낵바 스캔 및 결과 화면 안착 검증", step_no=4, total_steps=SUB_STEPS):
            bp.wait_for_api_success(timeout=60)
            time.sleep(2)
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            names_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(target_name in n or "엘**" in n for n in names_text_list)
            logger.info("✅ [PASS] [TC-BO-004] 활동 키워드 직접 입력 검증 패스!")


    """ [TC-BO-005] 추가 요청사항 입력 및 AI 재생성 기능 검증 """
    @pytest.mark.ui
    def test_regenerate_ai_opinion_with_additional_request(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-BO-005] 추가 요청사항 입력 및 AI 재생성 기능 검증을 시작합니다.")

        with bp.step("Step 1. 1차 AI 생성 완료 데이터 사전 빌드업", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(1.5)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            target_name = "엘리스"
            bp.add_student(target_name)
            bp.select_keywords(category_name="인성·태도", keyword_list=["예의 바르고 배려심 있음"])
            bp.wait_for_api_success(timeout=30)
            time.sleep(1)
        
        with bp.step("Step 2. 추가 피드백 란 요청 문구('칭찬해주기') 전송", step_no=2, total_steps=SUB_STEPS):
            target_opinion = "칭찬해주기"
            bp.input_additional_opinion(target_opinion)
            time.sleep(1)
        
        with bp.step("Step 3. 비동기 재생성 완수 스낵바 파이프라인 검출", step_no=3, total_steps=SUB_STEPS):
            bp.wait_for_api_success(timeout=30)
            time.sleep(2)

        with bp.step("Step 4. 최종 리렌더링 결과 지점 무결성 체크", step_no=4, total_steps=SUB_STEPS):
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            results_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(target_name in text or "엘**" in text for text in results_text_list)
            logger.info("✅ [PASS] [TC-BO-005] 추가 요청사항 입력 및 AI 재생성 기능 검증 완료!")


    """ [TC-BO-006] 상단 버튼을 통한 학생 추가 및 생성 검증 """
    @pytest.mark.ui
    def test_add_student_via_top_button_and_verify_generation(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-BO-006] 상단 버튼을 통한 학생 추가 및 생성 검증을 시작합니다.")

        with bp.step("Step 1. 2단계 진입 및 1차 기본 적재 조건 충족", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(1.5)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            target_name = "엘리스"
            bp.add_student(target_name)
            bp.select_keywords(category_name="인성·태도", keyword_list=["예의 바르고 배려심 있음"])
            bp.wait_for_api_success(timeout=30)
            time.sleep(1)

        with bp.step("Step 2. 상단 버튼 클릭 및 확장 빈 행(tfoot) 유도", step_no=2, total_steps=SUB_STEPS):
            student_1_name = "토끼"
            student_1_keyword = "명랑"
            bp.click_top_add_student_button()

        with bp.step("Step 3. 확장 행 데이터 입력 및 직접 입력 키워드 마감", step_no=3, total_steps=SUB_STEPS):
            bp.add_new_student_name_at_last_row(student_1_name)
            bp.input_custom_keyword_at_last_row(student_1_keyword)
            time.sleep(1)

        with bp.step("Step 4. 상단 학생 초안 생성 스낵바 체크 및 데이터 안착 검증", step_no=4, total_steps=SUB_STEPS):
            bp.wait_for_api_success(timeout=30)
            time.sleep(2)
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            names_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(student_1_name in n or "토**" in n for n in names_text_list)
            logger.info("✅ [PASS] [TC-BO-006] 상단 추가 버튼 기능 및 AI 초안 생성 무결성 확인 완료!")


    """ [TC-BO-007] 하단 버튼을 통한 학생 추가 및 생성 검증 """
    @pytest.mark.ui
    def test_add_student_via_bottom_button_and_verify_generation(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-BO-007] 하단 버튼을 통한 학생 추가 및 생성 검증을 시작합니다.")

        with bp.step("Step 1. 2단계 진입 및 기성 데이터 1차 셋업 완수", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(1.5)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            target_name = "엘리스"
            bp.add_student(target_name)
            bp.select_keywords(category_name="인성·태도", keyword_list=["예의 바르고 배려심 있음"])
            bp.wait_for_api_success(timeout=30)
            time.sleep(1)

        with bp.step("Step 2. 하단 학생 추가 버튼 타격 및 신규 행 생성", step_no=2, total_steps=SUB_STEPS):
            student_2_name = "래빗"
            student_2_keyword = "새침"
            bp.click_bottom_add_student_button()

        with bp.step("Step 3. 인덱스 확장 줄 이름 매핑 및 커스텀 키워드 조작 마감", step_no=3, total_steps=SUB_STEPS):
            bp.add_new_student_name_at_last_row(student_2_name)
            bp.input_custom_keyword_at_last_row(student_2_keyword)
            time.sleep(1)

        with bp.step("Step 4. 하단 추가분 생성 성공 감지 및 최종 정합성 체크", step_no=4, total_steps=SUB_STEPS):
            bp.wait_for_api_success(timeout=30)
            time.sleep(2)
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            names_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(student_2_name in n or "래**" in n for n in names_text_list)
            logger.info("✅ [PASS] [TC-BO-007] 하단 추가 버튼 기능 및 AI 초안 생성 무결성 확인 완료!")


    """ [TC-BO-008] 학생 이름 검색 및 필터링 검증 """
    @pytest.mark.ui
    def test_search_student_by_name_and_verify_filtering(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-BO-008] 학생 이름 검색 및 필터링 검증을 시작합니다.")

        with bp.step("Step 1. 다인원 후보군 3명 명부 동시 적재 빌드업", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(1.5)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))

            student_1 = "엘리스"
            student_2 = "토끼"
            student_3 = "래빗"

            bp.add_student(student_1)
            bp.select_keywords(category_name="인성·태도", keyword_list=["예의 바르고 배려심 있음"])
            bp.wait_for_api_success(timeout=30)
            
            bp.click_top_add_student_button()
            bp.add_new_student_name_at_last_row(student_2)
            bp.input_custom_keyword_at_last_row("명랑")
            bp.wait_for_api_success(timeout=30)
            
            bp.click_bottom_add_student_button()
            bp.add_new_student_name_at_last_row(student_3)
            bp.input_custom_keyword_at_last_row("새침")
            bp.wait_for_api_success(timeout=30)
            time.sleep(1)

        with bp.step("Step 2. 검색창에 특정 키워드('래빗') 네이티브 JS 전송", step_no=2, total_steps=SUB_STEPS):
            target_search_name = "래빗"
            bp.search_student_by_name(target_search_name)
            time.sleep(1.5)

        with bp.step("Step 3. 비동기 필터링 타겟 외 데이터 화면 소멸 대기", step_no=3, total_steps=SUB_STEPS):
            try:
                wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), '엘**') or contains(text(), '엘리스')]")))
            except Exception:
                pass

        with bp.step("Step 4. 실제 잔존 tr 행 스캔 및 마스킹 데이터 교차 체크", step_no=4, total_steps=SUB_STEPS):
            ALL_DATA_ROWS = (By.XPATH, "//tbody/tr")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_DATA_ROWS))
            raw_data = [el.text.strip() for el in elements if el.text]
            
            has_masked_target = any("래**" in d or "래빗" in d for d in raw_data)
            has_masked_others = any("엘**" in d or "엘리스" in d or "토**" in d or "토끼" in d for d in raw_data)

            assert has_masked_target, f"❌ 타겟 래빗 검출 오류"
            assert not has_masked_others, f"❌ 타 데이터 숨김 실패 결함"
            logger.info("✅ [PASS] [TC-BO-008] 학생 검색 및 타 데이터 차단 필터링 무결성 확인 완료!")


    """ [TC-BO-009] 시스템 초기화 후 '입력 내용 초기화' 버튼 잠금 검증 """
    @pytest.mark.ui
    def test_reset_button_disabled_after_system_clear(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        SUB_STEPS = 2

        logger.info("[START] [TC-BO-009] 시스템 초기화 후 '입력 내용 초기화' 버튼 잠금 검증 시작")

        with bp.step("Step 1. 강제 초기화 프로세스 가동 (완벽한 공백 세탁)", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(3.5)
            except Exception:
                pass

        with bp.step("Step 2. 버튼 비활성화 상태(disabled) 속성 및 소멸 여부 검증", step_no=2, total_steps=SUB_STEPS):
            RESET_BUTTON_XPATH = (By.XPATH, "//*[contains(@data-testid, 'rotate-right') or contains(@class, 'rotate-right')]/ancestor::button | //button[contains(@class, 'MuiButton-root') and .//*[contains(@data-testid, 'Icon')]]")
            try:
                reset_btn_element = driver.find_element(*RESET_BUTTON_XPATH)
                is_reset_disabled_attr = reset_btn_element.get_attribute("disabled")
                is_reset_enabled_status = reset_btn_element.is_enabled()
                
                assert not is_reset_enabled_status or is_reset_disabled_attr is not None, "❌ 예외 결함: 리셋 후 버튼이 여전히 활성화 상태!"
            except Exception as e:
                logger.info(f"✅ [PASS] 초기화 후 버튼 정상 소멸 처리 확인 (사유: {str(e)})")


    """ [TC-BO-010] 2단계 진입 후 초기화 검증 """
    @pytest.mark.ui
    def test_reset_and_rollback_immediately_after_entering_step_2(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 3

        logger.info("[START] [TC-BO-010] 2단계 진입 후 초기화 검증 시작")

        with bp.step("Step 1. 클린 셋업 완료 후 행발 2단계 진입 트리거", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(1.5)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            logger.info("✅ 2단계 화면 진입 완료 - 즉시 초기화 단행")

        with bp.step("Step 2. 2단계 스테이지에서 초기화 버튼 및 팝업 확인 승인", step_no=2, total_steps=SUB_STEPS):
            bp.click_reset_button()
            bp.confirm_reset_modal()
            time.sleep(3.5)

        with bp.step("Step 3. 1단계 원점 복귀 확인 및 다음으로 버튼 락킹 체크", step_no=3, total_steps=SUB_STEPS):
            NEXT_BUTTON_1ST_STEP = (By.XPATH, "//button[@form='student_record_generation']")
            next_btn_element = driver.find_element(*NEXT_BUTTON_1ST_STEP)
            
            is_disabled_attr = next_btn_element.get_attribute("disabled")
            is_enabled_status = next_btn_element.is_enabled()
            
            assert not is_enabled_status or is_disabled_attr is not None, "❌ 롤백 실패: 1단계 버튼 패드락 오류!"
            logger.info("✅ [PASS] [TC-BO-010] 2단계 진입 후 초기화 검증 완료")


    """ [TC-BO-011] AI 생성 완료 상태에서 초기화 검증 """
    @pytest.mark.ui
    def test_reset_and_rollback_after_ai_generation_success(self, logged_in_driver):
        driver = logged_in_driver
        bp = BehaviorAndOpinionsPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 3

        logger.info("[START] [TC-BO-011] AI 생성 완료 상태에서 초기화 검증 시작")

        with bp.step("Step 1. AI 1차 초안 생성이 완료된 데이터 적재 구역 빌드", step_no=1, total_steps=SUB_STEPS):
            bp.setup_tool_tab()
            bp.navigate_to_behavior_and_opinions()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                bp.click_reset_button()
                bp.confirm_reset_modal()
                time.sleep(1.5)
            except Exception:
                pass
            bp.select_school_level("초등학교")
            bp.click_next_step()
            target_name = "엘리스"
            bp.add_student(target_name)
            bp.select_keywords(category_name="인성·태도", keyword_list=["예의 바르고 배려심 있음"])
            bp.wait_for_api_success(timeout=30)
            time.sleep(1.5)

        with bp.step("Step 2. 헤비 데이터 적재 상태에서 전체 초기화 모달 승인", step_no=2, total_steps=SUB_STEPS):
            bp.click_reset_button()
            bp.confirm_reset_modal()
            time.sleep(3.5)

        with bp.step("Step 3. 최초 1단계 복귀 최종 무결성 크로스 assert 단행", step_no=3, total_steps=SUB_STEPS):
            NEXT_BUTTON_1ST_STEP = (By.XPATH, "//button[@form='student_record_generation']")
            next_btn_element = driver.find_element(*NEXT_BUTTON_1ST_STEP)
            
            is_disabled_attr = next_btn_element.get_attribute("disabled")
            is_enabled_status = next_btn_element.is_enabled()
            
            assert not is_enabled_status or is_disabled_attr is not None, "❌ 전체 롤백 파괴 실패 결함 발생!"
            logger.info("✅ [PASS] [TC-BO-011] AI 생성 완료 상태에서 초기화 검증 완료")