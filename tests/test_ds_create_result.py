"""
세부 특기사항 - 학생 정보 입력 및 AI 생성 결과 검증 UI 시나리오 테스트.
"""

import pytest
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.detailed_specialty_page import DetailedSpecialtyPage

logger = logging.getLogger(__name__)


class TestDetailedSpecialtyStudentInput:
    """행동특성 및 종합의견 AI 결과 생성 검증 테스트 스위트"""

    TOTAL_STEPS = 8

    @pytest.mark.ui
    def test_student_name_input_successful(self, logged_in_driver):

        driver = logged_in_driver

        detailed_specialty_page = DetailedSpecialtyPage(driver)

        logger.info("세부 특기사항 AI 생성 결과 검증을 시작합니다.")

        # ============================================================
        # 페이지 초기화
        # ============================================================

        with detailed_specialty_page.step(
            "Step 1. 페이지 이동",
            step_no=1,
            total_steps=self.TOTAL_STEPS
        ):
            
            time.sleep(1)  

        specialty_page = DetailedSpecialtyPage(logged_in_driver)
        specialty_page.setup_tool_tab()
        specialty_page.navigate_to_detailed_specialty()

        logger.info("✅ 세부 특기사항 페이지 진입 완료")

        wait = WebDriverWait(logged_in_driver, 10)
        short_wait = WebDriverWait(logged_in_driver, 3)

        # ============================================================
        # 이전 테스트 찌꺼기 제거
        # ============================================================

        with detailed_specialty_page.step(
            "Step 2. 이전 테스트 데이터 정리",
            step_no=2,
            total_steps=self.TOTAL_STEPS
        ):
            
            time.sleep(1)  
        
        NEXT_STEP_INDICATOR = (By.XPATH, "//button[@role='tab'][1] " "| //button[contains(@class, 'MuiTab-root') and contains(@class, 'Mui-selected')]")
        RESET_TRIGGER_BTN = (By.XPATH, "//*[contains(@data-testid, 'rotate-right') or contains(@class, 'rotate-right')]/ancestor::button " "| //button[contains(@class, 'MuiButton-root') and .//*[contains(@data-testid, 'Icon')]]")

        try:
            short_wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
            logger.info("⚠️ 이전 데이터 감지 → 초기화 진행")
            
            specialty_page.safe_click(RESET_TRIGGER_BTN)
            time.sleep(1)
            
            MODAL_CONFIRM_BTN = (
            By.XPATH, 
            "//div[contains(@class, 'MuiDialogActions-root')]//button[contains(@class, 'MuiButton-containedError')]"
            )

            specialty_page.safe_click(MODAL_CONFIRM_BTN)
            logger.info("✅ 초기화 완료")
            time.sleep(2)
            
        except Exception:
            logger.info("ℹ️ 초기 상태 정상")

        # ============================================================
        # 수업 정보 입력
        # ============================================================

        with detailed_specialty_page.step(
            "Step 3. 수업 정보 입력",
            step_no=3,
            total_steps=self.TOTAL_STEPS
        ):
            
            time.sleep(1)  


        # 학교급 콤보박스 클릭해서 열기
        SCHOOL_LEVEL_COMBO = (By.XPATH, "//div[@role='combobox'][@aria-haspopup='listbox'] " "| //div[contains(@class, 'MuiSelect-select')]")
        specialty_page.safe_click(SCHOOL_LEVEL_COMBO)
        time.sleep(1)
        
        ELEMENT_SCHOOL = (By.XPATH, "(//li[@role='option'])[1] | (//*[contains(@class, 'MuiMenuItem-root')])[1]")
        specialty_page.safe_click(ELEMENT_SCHOOL)
        time.sleep(1)

        # 학년: 1학년
        GRADE_COMBO = (By.XPATH, "//input[@name='grade']/parent::div")
        specialty_page.safe_click(GRADE_COMBO)
        time.sleep(1)

        ELEMENT_FIRST_GRADE = (By.XPATH, "(//li[@role='option'])[1]")
        specialty_page.safe_click(ELEMENT_FIRST_GRADE)
        time.sleep(1)

        # 과목: 국어
        SUBJECT_COMBO = (By.XPATH, "//input[@role='combobox'][contains(@class, 'MuiAutocomplete-input')]")
        specialty_page.safe_click(SUBJECT_COMBO)
        time.sleep(1)

        ELEMENT_KOREAN = (By.XPATH, "//li[@role='option'][@data-option-index='0']")
        specialty_page.safe_click(ELEMENT_KOREAN)
        time.sleep(1)

        # 단원: 5
        UNIT_INPUT = (By.CSS_SELECTOR, "input[name='unit']")
        unit_field = wait.until(EC.element_to_be_clickable(UNIT_INPUT))
        unit_field.click()
        unit_field.clear()
        unit_field.send_keys("5")
        time.sleep(1)

        # '다음으로' 버튼 클릭하여 2단계 정식 진입
        NEXT_BUTTON = (By.XPATH, "//button[@type='submit'][@form='student_evaluation']")
        specialty_page.safe_click(NEXT_BUTTON)
        time.sleep(1)
        
        wait.until(EC.visibility_of_element_located(NEXT_STEP_INDICATOR))
        logger.info("✅ 2단계 화면 진입 완료")
        time.sleep(1)

        # ============================================================
        # 학생 이름 입력
        # ============================================================

        with detailed_specialty_page.step(
            "Step 4. 학생 이름 입력",
            step_no=4,
            total_steps=self.TOTAL_STEPS
        ):
            
            time.sleep(1)  

        STUDENT_NAME_TRIGGER = (By.XPATH,
            "//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']")
        specialty_page.safe_click(STUDENT_NAME_TRIGGER)
        logger.info("🖱️ '이름을 입력해주세요.' 영역 클릭 활성화")
        time.sleep(1)

        target_name = "엘리스"
        actions = ActionChains(logged_in_driver)
        for char in target_name:
            actions.send_keys(char)
        actions.perform()
        logger.info(f"⌨️ 커서 위치에 [{target_name}] 주입 완료")
        time.sleep(1)

        SAVE_BUTTON = (By.XPATH, "//td[contains(@class, 'MuiTableCell-footer')]//div[contains(@class, 'MuiStack-root')]//button[1]")
        specialty_page.safe_click(SAVE_BUTTON)
        logger.info("💾 학생 저장 완료")
        time.sleep(2)

        # ====================================================================
        # 활동 키워드 선택
        # ====================================================================

        with detailed_specialty_page.step(
            "Step 5. 학생 이름 입력",
            step_no=5,
            total_steps=self.TOTAL_STEPS
        ):
            
            time.sleep(1)  

        KEYWORD_TARGET_TEXT = (By.XPATH, "//tfoot//tr[last()]//td[3]//button")
        specialty_page.safe_click(KEYWORD_TARGET_TEXT)
        logger.info("🖱️ 키워드 팝업 오픈")
        time.sleep(1.5)

        # 첫 번째 줄 '인성·태도' 아코디언의 우측 아래 화살표(chevron-down) 클릭
        FIRST_ACCORDION_ARROW = (
            By.XPATH, 
            "//div[@role='dialog']//*[contains(@data-testid, 'chevron-downIcon')][1]"
        )
        specialty_page.safe_click(FIRST_ACCORDION_ARROW)
        logger.info("🖱️ 첫 번째 키워드 카테고리(인성·태도) 아코디언 전개 완료")
        time.sleep(1) # 아코디언이 스르륵 열리는 애니메이션 대기 시간

        # 펼쳐진 칩 목록 중에서 첫 번째인 "수업 집중도 높음" 칩 선택
        FIRST_KEYWORD_CHIP = (
            By.XPATH, 
            "//div[@role='dialog']//div[contains(@class, 'MuiCollapse-entered')]//div[contains(@class, 'MuiChip-root')][1]"
        )
        specialty_page.safe_click(FIRST_KEYWORD_CHIP)
        logger.info("🖱️ 첫 번째 키워드 칩 ['수업 집중도 높음'] 선택 완료")
        time.sleep(1)

        # 활성화된 팝업 내부의 최종 "저장" 버튼 클릭
        SAVE_POPUP_BUTTON = (
            By.XPATH, 
            "//div[@role='dialog']//div[contains(@class, 'MuiDialogActions-root')]//button[@type='submit']"
        )
        specialty_page.safe_click(SAVE_POPUP_BUTTON)
        logger.info("🖱️ 키워드 선택 완료 및 AI 생성 요청 피니시")
        time.sleep(2)

        # ============================================================
        # AI 생성 완료 확인
        # ============================================================

        with detailed_specialty_page.step(
            "Step 6. 1차 AI 초안 생성 완료 확인",
            step_no=6,
            total_steps=self.TOTAL_STEPS
        ):
            time.sleep(1)

        SUCCESS_SNACKBAR_1ST = (
            By.XPATH, 
            "//*[@id='notistack-snackbar']//*[contains(@data-testid, 'circle-checkIcon')]"
        )
        
        # 성공 팝업 아이콘이 노출될 때까지 최대 20초간 스마트 대기
        wait.until(EC.presence_of_element_located(SUCCESS_SNACKBAR_1ST))
        logger.info("🎉 [1차 완료] AI 초안 생성 성공 팝업 감지")
        time.sleep(2)

        # ====================================================================
        # 추가 요청사항 내용 입력
        # ====================================================================
        
        with detailed_specialty_page.step(
            "Step 7. 추가 요청사항 내용 입력",
            step_no=7,
            total_steps=self.TOTAL_STEPS
        ):

            time.sleep(1)

        # 추가 요청사항 영역 클릭 활성화
        OPINION_REQUEST_TRIGGER = (
            By.XPATH, 
            "//tbody//tr[last()]//td[.//textarea[@maxlength='200']]//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']"
        )
        specialty_page.safe_click(OPINION_REQUEST_TRIGGER)
        logger.info("🖱️ '요청사항을 입력해주세요.' 영역 클릭 활성화 완료")
        time.sleep(1)

        # 활성화된 폼에 "칭찬해주기" 텍스트 주입
        target_opinion = "칭찬해주기"
        actions = ActionChains(logged_in_driver)
        for char in target_opinion:
            actions.send_keys(char)
        actions.perform()
        logger.info(f"⌨️ 추가 요청사항 입력 완료: [{target_opinion}]")
        time.sleep(1)

        # "저장" 버튼 클릭
        OPINION_SAVE_BUTTON = (
            By.XPATH, 
            "//tbody//tr[last()]//td[.//textarea[@maxlength='200']]//div[contains(@class, 'MuiStack-root')]//button[1]"
        )
        specialty_page.safe_click(OPINION_SAVE_BUTTON)
        logger.info("💾 추가 요청사항 저장 완료")
        time.sleep(2)

        # ============================================================
        # AI 재생성 완료 확인
        # ============================================================

        with detailed_specialty_page.step(
            "Step 8. AI 재생성 결과 대기",
            step_no=8,
            total_steps=self.TOTAL_STEPS
        ):

            time.sleep(1)

        SUCCESS_SNACKBAR_2ND = (
            By.XPATH, 
            "//*[@id='notistack-snackbar']//*[contains(@data-testid, 'circle-checkIcon')]"
        )
        WebDriverWait(logged_in_driver, 20).until(EC.presence_of_element_located(SUCCESS_SNACKBAR_2ND))
        logger.info("🎉 AI 생성 완료")
        time.sleep(2)

        # 화면 내 텍스트 전체 스캔 검증
        ALL_TEXT_NODES = (By.XPATH, "//*[self::p or self::span or self::td or self::div][text()]")
        elements = wait.until(EC.presence_of_all_elements_located(ALL_TEXT_NODES))
        names_text_list = [el.text.strip() for el in elements if el.text]
        
        is_found = any(target_name in n or "엘**" in n for n in names_text_list)
        assert is_found, f"❌ 검증 실패: 결과 화면에 학생 이름 [{target_name}]이 나타나지 않았습니다."
        
        logger.info("🎉 [테스트 최종 성공] 세부 특기사항 AI 생성 결과 시나리오가 완벽히 통과되었습니다!")