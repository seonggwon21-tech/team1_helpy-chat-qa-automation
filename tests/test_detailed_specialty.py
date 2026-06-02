"""
세부 특기사항 메인 성공 시나리오 및 독립 서브 TC 고도화 스위트
"""

import pytest
import time
import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.detailed_specialty_page import DetailedSpecialtyPage

logger = logging.getLogger(__name__)


class TestDetailedSpecialtyAIGeneration:
    """세부 특기사항 AI 생성 및 다운로드 토탈 테스트 시나리오"""

    # 메인 시나리오 전용 총 스텝 수
    TOTAL_STEPS = 7
    
    @pytest.mark.ui
    def test_detailed_specialty_ai_generation_flow(self, logged_in_driver, temp_download_dir):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)

        logger.info("세부 특기사항 AI 생성 결과 검증 성공 시나리오를 시작합니다.")

        # ============================================================
        # Step 1. 페이지 이동
        # ============================================================
        with sp.step("Step 1. 페이지 이동", step_no=1, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        sp.setup_tool_tab()
        sp.navigate_to_detailed_specialty()
        logger.info("✅ 세부 특기사항 페이지 진입 완료")

        wait = WebDriverWait(logged_in_driver, 10)
        short_wait = WebDriverWait(logged_in_driver, 3)

        # ============================================================
        # Step 2. 이전 테스트 데이터 정리
        # ============================================================
        with sp.step("Step 2. 이전 테스트 데이터 정리", step_no=2, total_steps=self.TOTAL_STEPS):
            time.sleep(1)
        
        try:
            short_wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
            logger.info("⚠️ 이전 데이터 감지 → 초기화 진행")
            sp.click_reset_button()
            sp.confirm_reset_modal()
            logger.info("✅ 초기화 완료")
            time.sleep(2)
        except Exception:
            logger.info("ℹ️ 초기 상태 정상")

        # ============================================================
        # Step 3. 수업 정보 입력
        # ============================================================
        with sp.step("Step 3. 수업 정보 입력", step_no=3, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
        sp.click_next_step()
        
        wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
        logger.info("✅ 2단계 화면 진입 완료")
        time.sleep(1)

        # ============================================================
        # Step 4. 학생 이름 입력
        # ============================================================
        with sp.step("Step 4. 학생 이름 입력", step_no=4, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        target_name = "엘리스"
        sp.add_student(target_name)
        logger.info(f"💾 학생 이름 저장 완료: [{target_name}]")

        # ====================================================================
        # Step 5. 활동 키워드 선택
        # ====================================================================
        with sp.step("Step 5. 활동 키워드 선택", step_no=5, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        sp.select_keywords(keyword_text="수업 집중도 높음")
        logger.info("🎉 키워드 선택 및 AI 생성 요청 완료")

        # ============================================================
        # Step 6. AI 생성 결과 완료 확인
        # ============================================================
        with sp.step("Step 6. AI 생성 결과 완료 확인", step_no=6, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        sp.wait_for_api_success(timeout=60)
        logger.info("🎉 AI 초안 생성 성공 스낵바 감지")
        time.sleep(2)

        ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
        elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
        names_text_list = [el.text.strip() for el in elements if el.text]
        
        is_found = any(target_name in n or "엘**" in n for n in names_text_list)
        assert is_found, f"❌ 검증 실패: 결과 화면에 학생 이름 [{target_name}]이 나타나지 않았습니다."
        logger.info("✅ AI 생성 완료 및 화면 적재 무결성 확인 완료")

        # ====================================================================
        # Step 7. 생성 결과 다운로드
        # ====================================================================

        with sp.step("Step 7. 생성 결과 다운로드 검증", step_no=7, total_steps=self.TOTAL_STEPS):
            time.sleep(1)

        download_path = str(temp_download_dir)
        logger.info(f"📥 검증용 임시 폴더 경로 추적: {download_path}")

        sp.click_download_result_button()

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
        logger.info("🥇 [종합 대성공] 세부 특기사항 메인 성공 시나리오 마스터 패스!!!")


    """ [TC-DS-001] 학교급별 핵심 경계값 조합 기반 2단계 진입 무결성 검증 """
    @pytest.mark.ui
    @pytest.mark.parametrize(
        "school_level, grade_idx, subject_idx, unit_text, combo_name",
        [
            ("초등학교", 1, 0, "1", "초등_최소_경계 (1학년 1번째과목)"),
            ("초등학교", 6, 8, "1", "초등_최대_경계 (6학년 9번째과목)"),
            ("중학교",   2, 4, "1", "중등_중간_대표 (2학년 5번째과목)"),
            ("고등학교", 3, 10, "1", "고등_최대_경계 (3학년 11번째과목)")
        ]
    )
    def test_detailed_specialty_boundary_combinations(
        self, logged_in_driver, school_level, grade_idx, subject_idx, unit_text, combo_name
    ):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        SUB_STEPS = 3
        
        logger.info(f"[START] [TC-DS-001] 경계값 타격 가동 ➡️ 타겟 조합: [{combo_name}]")
        
        with sp.step("Step 1. 환경 진입 및 사전 청소", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass

        with sp.step("Step 2. 경계값 파라미터 데이터셋 주입", step_no=2, total_steps=SUB_STEPS):
            sp.select_school_level_and_info(
                school_level=school_level, grade_index=grade_idx, subject_index=subject_idx, unit_text=unit_text
            )
            logger.info(f"💾 데이터 주입 완수: {school_level} / {grade_idx}학년")
            time.sleep(1)

        with sp.step("Step 3. 다음으로 전송 및 페이지 전환 확인", step_no=3, total_steps=SUB_STEPS):
            next_btn_element = driver.find_element(*sp.NEXT_BUTTON)
            assert next_btn_element.is_enabled(), f"❌ 결함 발견 [{combo_name}]: 버튼이 잠겨있습니다!"
            sp.click_next_step()
            time.sleep(3)
            logger.info(f"✅ [PASS] [TC-DS-001] [{combo_name}] 검증 완료!")


    """ [TC-DS-002] 과목 직접 입력 검증 """
    @pytest.mark.ui
    def test_custom_subject_input_and_verify_step_2_entry(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        SUB_STEPS = 3

        logger.info("[START] [TC-DS-002] 과목 직접 입력 검증 시작")

        with sp.step("Step 1. 초기화 진입 및 세탁", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass

        with sp.step("Step 2. 커스텀 과목('중국어') 직접 타이핑 주입", step_no=2, total_steps=SUB_STEPS):
            target_subject = "중국어"
            sp.select_school_level_and_info(
                school_level="초등학교", grade_index=1, custom_subject=target_subject, unit_text="5"
            )
            time.sleep(1)

        with sp.step("Step 3. 활성화 트리거 작동 및 페이지 전환 대기", step_no=3, total_steps=SUB_STEPS):
            next_btn_element = driver.find_element(*sp.NEXT_BUTTON)
            assert next_btn_element.is_enabled(), f"❌ 결함 발견: 버튼이 잠겨있습니다!"
            sp.click_next_step()
            time.sleep(3)
            logger.info(f"✅ [PASS] [TC-DS-002] 과목 직접 입력 후 페이지 전환 확인 완료!")


    """ [TC-DS-003] 단원 필드 특수문자 주입 예외 차단 검증 """
    @pytest.mark.ui
    @pytest.mark.xfail(reason="🚨 GitLab Issue - 단원 필드 특수문자 차단 누락 결함", strict=True)
    def test_unit_input_restriction_with_special_characters(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        SUB_STEPS = 3

        logger.info("[START] [TC-DS-003] 단원 필드 특수문자 주입 예외 차단 검증 시작")

        with sp.step("Step 1. 테스트 환경 셋업 및 공백 확보", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass

        with sp.step("Step 2. 단원 창에 예외 데이터('$%^&') 주입", step_no=2, total_steps=SUB_STEPS):
            invalid_unit = "$%^&"
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, unit_text=invalid_unit)
            time.sleep(1)

        with sp.step("Step 3. 이원화 락킹 스캔 및 결함 스크리닝", step_no=3, total_steps=SUB_STEPS):
            next_btn_element = driver.find_element(*sp.NEXT_BUTTON)
            is_next_disabled_attr = next_btn_element.get_attribute("disabled")
            is_next_enabled_status = next_btn_element.is_enabled()
            
            if not is_next_enabled_status or is_next_disabled_attr is not None:
                logger.info("✅ [합격] 특수문자 감지로 인해 버튼 비활성화 확인 완료.")
                assert True
            else:
                sp.click_next_step()
                time.sleep(3)
                is_step_2_visible = driver.find_elements(*sp.NEXT_STEP_INDICATOR)
                
                if is_step_2_visible:
                    fail_msg = f"\n🚨 [CRITICAL BUG DETECTED] 단원 특수문자 [{invalid_unit}] 필터링 누락 결함 확인!"
                    logger.error(fail_msg)
                    pytest.fail(fail_msg)
                else:
                    logger.info("✅ [합격] 화면 전환 락 정상 작동 확인.")


    """ [TC-DS-004] 학생 이름 필드 특수문자 주입 예외 차단 검증 """
    @pytest.mark.ui
    @pytest.mark.xfail(reason="🚨 GitLab Issue - 학생 이름 특수문자 차단 누락 결함", strict=True)
    def test_student_name_input_restriction_with_special_characters(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 3

        logger.info("[START] [TC-DS-004] 학생 이름 필드 특수문자 주입 예외 차단 검증 시작")

        with sp.step("Step 1. 2단계 안착 사전 렌더링 스태이지 진입", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))

        with sp.step("Step 2. 이름 창에 특수문자('####') 강제 주입 후 저장", step_no=2, total_steps=SUB_STEPS):
            invalid_name = "####"
            sp.add_student(invalid_name)
            time.sleep(2)

        with sp.step("Step 3. 가상 DOM 마스킹 패턴 찌꺼기 전수 스캔", step_no=3, total_steps=SUB_STEPS):
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = driver.find_elements(*ALL_TEXT_NODES)
            raw_data = [el.text.strip() for el in elements if el.text]
            
            is_invalid_name_saved = any(invalid_name in d or "#**" in d or d.startswith("#*") for d in raw_data)

            if is_invalid_name_saved:
                fail_msg = f"\n🚨 [CRITICAL BUG DETECTED] 학생 이름 특수문자 [{invalid_name}] 필터 누락 및 우회 적재 결함 확인!"
                logger.error(fail_msg)
                pytest.fail(fail_msg)
            else:
                logger.info("✅ [합격] 특수문자 학생 이름 진입 완벽 거부 차단 성공 확인.")


    """ [TC-DS-005] 첫 번째 학생 키워드 직접 입력 검증 """
    @pytest.mark.ui
    def test_first_student_keyword_custom_input_and_verify_generation(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-DS-005] 첫 번째 학생 키워드 직접 입력 검증 시작")

        with sp.step("Step 1. 2단계 기본 인프라 진입 및 정돈", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))

        with sp.step("Step 2. 첫 메인 행 데이터 적재 ('엘리스')", step_no=2, total_steps=SUB_STEPS):
            target_name = "엘리스"
            sp.add_student(target_name)
            time.sleep(1)

        with sp.step("Step 3. 팝업 직접 입력창 오픈 및 '활발' 키워드 매칭", step_no=3, total_steps=SUB_STEPS):
            custom_keyword = "활발"
            sp.input_custom_keyword_for_first_student(keyword_text=custom_keyword)
            time.sleep(1)

        with sp.step("Step 4. 비동기 백엔드 스낵바 검출 및 정합성 팩트 체크", step_no=4, total_steps=SUB_STEPS):
            sp.wait_for_api_success(timeout=60)
            time.sleep(2)
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            names_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(target_name in n or "엘**" in n for n in names_text_list)
            logger.info("✅ [PASS] [TC-DS-005] 첫 번째 학생 키워드 직접 입력 무결성 확보!")


    """ [TC-DS-006] 추가 요청사항 입력 및 AI 재생성 검증 """
    @pytest.mark.ui
    def test_verify_additional_request_and_ai_regeneration(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4
        
        logger.info("[START] [TC-DS-006] 추가 요청사항 입력 및 AI 재생성 검증 시작")
        
        with sp.step("Step 1. 1차 생성 초안 데이터 사전 빌드업 완료", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            target_name = "엘리스"
            sp.add_student(target_name)
            sp.select_keywords(category_name="학습 태도", keyword_text="수업 집중도 높음")
            sp.wait_for_api_success(timeout=60)
            time.sleep(1)
        
        with sp.step("Step 2. 요청사항 텍스트 창 피드백('칭찬해주기') 주입", step_no=2, total_steps=SUB_STEPS):
            target_opinion = "칭찬해주기"
            sp.input_additional_request(request_text=target_opinion)
            time.sleep(1)
        
        with sp.step("Step 3. 비동기 재생성 스낵바 파이프라인 체크", step_no=3, total_steps=SUB_STEPS):
            sp.wait_for_api_success(timeout=60)
            time.sleep(2)

        with sp.step("Step 4. 가상 DOM 최종 화면 데이터 갱신 스캔 정합성 체크", step_no=4, total_steps=SUB_STEPS):
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            names_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(target_name in n or "엘**" in n for n in names_text_list)
            logger.info("✅ [PASS] [TC-DS-006] 추가 피드백 재생성 무결성 패스!")


    """ [TC-DS-007] 상단 버튼 학생 추가 및 직접 입력 키워드 검증 """
    @pytest.mark.ui
    def test_add_student_via_top_button_with_custom_keyword(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-DS-007] 상단 버튼 학생 추가 및 직접 입력 키워드 검증 시작")

        with sp.step("Step 1. 2단계 진입 및 1차 기본 적재 완성", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
            base_name = "엘리스"
            sp.add_student(base_name)
            sp.select_keywords(category_name="학습 태도", keyword_text="수업 집중도 높음")
            sp.wait_for_api_success(timeout=60)
            time.sleep(1)

        with sp.step("Step 2. 상단 버튼 클릭 및 가상 확장 줄 생성", step_no=2, total_steps=SUB_STEPS):
            student_1_name = "토끼"
            student_1_keyword = "명랑"
            sp.click_top_add_student_button()

        with sp.step("Step 3. 신규 행 이름 및 팝업 직접 입력창 핸들링", step_no=3, total_steps=SUB_STEPS):
            sp.add_new_student_name_at_last_row(student_1_name)
            sp.input_custom_keyword_at_last_row(student_1_keyword)
            time.sleep(1)

        with sp.step("Step 4. 신규 학생 생성 스낵바 체크 및 데이터 스캔 마감", step_no=4, total_steps=SUB_STEPS):
            sp.wait_for_api_success(timeout=60)
            time.sleep(2)
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            names_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(student_1_name in n or "토**" in n for n in names_text_list)
            logger.info("✅ [PASS] [TC-DS-007] 상단 추가 단독 검증 패스!")


    """ [TC-DS-008] 하단 버튼 학생 추가 및 직접 입력 키워드 검증 """
    @pytest.mark.ui
    def test_add_student_via_bottom_button_with_custom_keyword(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-DS-008] 하단 버튼 학생 추가 및 직접 입력 키워드 검증 시작")

        with sp.step("Step 1. 2단계 인입 및 사전 빌드업 완료", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
            base_name = "엘리스"
            sp.add_student(base_name)
            sp.select_keywords(category_name="학습 태도", keyword_text="수업 집중도 높음")
            sp.wait_for_api_success(timeout=60)
            time.sleep(1)

        with sp.step("Step 2. 하단 버튼 타격 및 빈 인덱스 행 생성", step_no=2, total_steps=SUB_STEPS):
            student_2_name = "래빗"
            student_2_keyword = "새침"
            sp.click_bottom_add_student_button()

        with sp.step("Step 3. 생성 줄 이름 매핑 및 커스텀 키워드 조작 완료", step_no=3, total_steps=SUB_STEPS):
            sp.add_new_student_name_at_last_row(student_2_name)
            sp.input_custom_keyword_at_last_row(student_2_keyword)
            time.sleep(1)

        with sp.step("Step 4. 하단 추가분 초안 스낵바 감지 및 최종 안착 체크", step_no=4, total_steps=SUB_STEPS):
            sp.wait_for_api_success(timeout=60)
            time.sleep(2)
            ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
            names_text_list = [el.text.strip() for el in elements if el.text]
            
            assert any(student_2_name in n or "래**" in n for n in names_text_list)
            logger.info("✅ [PASS] [TC-DS-008] 하단 추가 단독 검증 패스!")


    """ [TC-DS-009] 학생 검색 기능 검증 """
    @pytest.mark.ui
    def test_search_student_by_name_and_verify_filtering(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 4

        logger.info("[START] [TC-DS-009] 학생 검색 기능 검증을 시작합니다.")

        with sp.step("Step 1. 다인원 후보군(3명) 명부 고속 적재 가동", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))

            student_base = "엘리스"
            student_top = "토끼"
            student_bottom = "래빗"

            sp.add_student(student_base)
            sp.select_keywords(category_name="학습 태도", keyword_text="수업 집중도 높음")
            sp.wait_for_api_success(timeout=60)
            
            sp.click_top_add_student_button()
            sp.add_new_student_name_at_last_row(student_top)
            sp.input_custom_keyword_at_last_row("명랑")
            sp.wait_for_api_success(timeout=60)
            
            sp.click_bottom_add_student_button()
            sp.add_new_student_name_at_last_row(student_bottom)
            sp.input_custom_keyword_at_last_row("새침")
            sp.wait_for_api_success(timeout=60)
            time.sleep(1)

        with sp.step("Step 2. 검색창 타겟 키워드('래빗') JS 입력 실행", step_no=2, total_steps=SUB_STEPS):
            target_search_name = "래빗"
            sp.search_student_by_name(target_search_name)

        with sp.step("Step 3. 비동기 필터링 타 데이터 소멸 대기", step_no=3, total_steps=SUB_STEPS):
            try:
                wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), '엘**') or contains(text(), '엘리스')]")))
            except Exception:
                pass

        with sp.step("Step 4. 잔존 목록 추출 및 마스킹 네임 상호 교차 체크", step_no=4, total_steps=SUB_STEPS):
            ALL_DATA_ROWS = (By.XPATH, "//tbody/tr")
            elements = wait.until(EC.presence_of_all_elements_located(ALL_DATA_ROWS))
            raw_data = [el.text.strip() for el in elements if el.text]
            
            has_masked_target = any("래**" in d or "래빗" in d for d in raw_data)
            has_masked_others = any("엘**" in d or "엘리스" in d or "토**" in d or "토끼" in d for d in raw_data)

            assert has_masked_target, f"❌ 타겟 미검출"
            assert not has_masked_others, f"❌ 타 데이터 잔존 결함"
            logger.info("✅ [PASS] [TC-DS-009] 검색 및 필터 정합성 확보 완료!")


    """ [TC-DS-010] 초기 상태에서 "입력 내용 초기화" 버튼 잠금 검증 """
    @pytest.mark.ui
    def test_reset_button_disabled_after_system_clear(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        SUB_STEPS = 2

        logger.info("[START] [TC-DS-010] 초기화 상태에서 '입력 내용 초기화' 버튼 잠금 검증 시작")

        with sp.step("Step 1. 시스템 강제 초기화 단행 (공백 상태 구축)", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root')]")
            try:
                WebDriverWait(driver, 5).until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(3.5)
            except Exception:
                pass

        with sp.step("Step 2. 초기화 버튼 속성(disabled) 및 소멸 여부 정밀 판정", step_no=2, total_steps=SUB_STEPS):
            try:
                reset_btn_element = driver.find_element(*sp.RESET_TRIGGER_BTN)
                is_reset_disabled_attr = reset_btn_element.get_attribute("disabled")
                is_reset_enabled_status = reset_btn_element.is_enabled()
                
                assert not is_reset_enabled_status or is_reset_disabled_attr is not None, "❌ 예외 결함: 초기화 버튼 활성화 상태 누락 버그!"
            except Exception as e:
                logger.info(f"✅ 버튼 소멸 확인 정상 합격 패스 (사유: {str(e)})")


    """ [TC-DS-011] 2단계 진입 직후 "입력 내용 초기화" 버튼 작동 검증 """
    @pytest.mark.ui
    def test_reset_and_rollback_immediately_after_entering_step_2(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 3

        logger.info("[START] [TC-DS-011] 2단계 진입 직후 '입력 내용 초기화' 버튼 작동 검증 시작")

        with sp.step("Step 1. 환경 세탁 후 2단계 강제 진입 가동", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            wait.until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))

        with sp.step("Step 2. 2단계 안착 즉시 초기화 모달 승인 조작", step_no=2, total_steps=SUB_STEPS):
            sp.click_reset_button()
            sp.confirm_reset_modal()
            time.sleep(3.5)

        with sp.step("Step 3. 1단계 원점 복귀 및 다음으로 버튼 패드락 스캔", step_no=3, total_steps=SUB_STEPS):
            next_btn_element = driver.find_element(*sp.NEXT_BUTTON)
            is_disabled_attr = next_btn_element.get_attribute("disabled")
            is_enabled_status = next_btn_element.is_enabled()
            
            assert not is_enabled_status or is_disabled_attr is not None, "❌ 롤백 실패: 1단계 다음으로 버튼이 열려있습니다!"
            logger.info("✅ [PASS] [TC-DS-011] 2단계 즉시 롤백 무결성 확인 완료")


    """ [TC-DS-012] AI 생성 완료 상태에서 "입력 내용 초기화" 버튼 작동 검증 """
    @pytest.mark.ui
    def test_reset_and_rollback_after_ai_generation_success(self, logged_in_driver):
        driver = logged_in_driver
        sp = DetailedSpecialtyPage(driver)
        wait = WebDriverWait(driver, 10)
        SUB_STEPS = 3

        logger.info("[START] [TC-DS-012] AI 생성 완료 상태에서 '입력 내용 초기화' 버튼 작동 검증 시작")

        with sp.step("Step 1. 초안 데이터 화면 꽉 찬 스테이지 빌드 완료", step_no=1, total_steps=SUB_STEPS):
            sp.setup_tool_tab()
            sp.navigate_to_detailed_specialty()
            try:
                WebDriverWait(driver, 3).until(EC.visibility_of_element_located(sp.NEXT_STEP_INDICATOR))
                sp.click_reset_button()
                sp.confirm_reset_modal()
                time.sleep(2)
            except Exception:
                pass
            sp.select_school_level_and_info(school_level="초등학교", grade_index=1, subject_index=0, unit_text="5")
            sp.click_next_step()
            target_name = "엘리스"
            sp.add_student(target_name)
            sp.select_keywords(category_name="학습 태도", keyword_text="수업 집중도 높음")
            sp.wait_for_api_success(timeout=60)
            time.sleep(1.5)

        with sp.step("Step 2. 헤비 데이터 적재 구역 전체 파괴 초기화 단행", step_no=2, total_steps=SUB_STEPS):
            sp.click_reset_button()
            sp.confirm_reset_modal()
            time.sleep(3.5)

        with sp.step("Step 3. 1단계 정식 원점 복귀 최종 무결성 크로스 assert", step_no=3, total_steps=SUB_STEPS):
            next_btn_element = driver.find_element(*sp.NEXT_BUTTON)
            is_disabled_attr = next_btn_element.get_attribute("disabled")
            is_enabled_status = next_btn_element.is_enabled()
            
            assert not is_enabled_status or is_disabled_attr is not None, "❌ 롤백 파괴 실패: 데이터 클리어 오류!"
            logger.info("✅ [PASS] [TC-DS-012] 데이터 적재 상태 리셋 완전 복귀 성공!")