"""
ToolPage를 상속받아 도구 메뉴의 하위 기능인 '세부 특기사항' 페이지 제어를 담당하는 클래스.
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .tool_page import ToolPage  

logger = logging.getLogger(__name__)

class DetailedSpecialtyPage(ToolPage): 
    """세부 특기사항 페이지 조작 및 이동 클래스 (ToolPage 확장)"""

    # 랜드마크 및 메뉴 진입 로케이터
    DETAILED_SPECIALTY_MENU = (
        By.XPATH, 
        "//div[contains(@class, 'css-1wkfo6a')]//p[contains(@class, 'css-to37at')]/ancestor::a "
        "| //div[contains(@class, 'css-1wkfo6a')]//p[contains(@class, 'css-to37at')]"
    )
    
    # 초기화
    NEXT_STEP_INDICATOR = (
        By.XPATH, 
        "//button[@role='tab'][1] | //button[contains(@class, 'MuiTab-root') and contains(@class, 'Mui-selected')]"
    )
    RESET_TRIGGER_BTN = (
        By.XPATH, 
        "//*[contains(@data-testid, 'rotate-right') or contains(@class, 'rotate-right')]/ancestor::button "
        "| //button[contains(@class, 'MuiButton-root') and .//*[contains(@data-testid, 'Icon')]]"
    )
    MODAL_CONFIRM_BTN = (
        By.XPATH, 
        "//div[contains(@class, 'MuiDialogActions-root')]//button[contains(@class, 'MuiButton-containedError')]"
    )

    # 수업 정보 입력 로케이터
    SCHOOL_LEVEL_COMBO = (
        By.XPATH, 
        "//div[@role='combobox'][@aria-haspopup='listbox'] | //div[contains(@class, 'MuiSelect-select')]"
    )
    GRADE_COMBO = (By.XPATH, "//input[@name='grade']/parent::div")
    SUBJECT_COMBO = (By.XPATH, "//input[@role='combobox'][contains(@class, 'MuiAutocomplete-input')]")
    UNIT_INPUT = (By.CSS_SELECTOR, "input[name='unit']")
    NEXT_BUTTON = (By.XPATH, "//button[@type='submit'][@form='student_evaluation']")

    # 학생 입력 로케이터
    STUDENT_NAME_TRIGGER = (
        By.XPATH,
        "//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']"
    )
    SAVE_BUTTON = (
        By.XPATH, 
        "//td[contains(@class, 'MuiTableCell-footer')]//div[contains(@class, 'MuiStack-root')]//button[1]"
    )

    # 키워드 팝업 조작 로케이터
    KEYWORD_POPUP_TRIGGER = (By.XPATH, "//tfoot//tr[last()]//td[3]//button")
    FIRST_ACCORDION_ARROW = (
        By.XPATH, 
        "//div[@role='dialog']//*[contains(@data-testid, 'chevron-downIcon')][1]"
    )
    SAVE_POPUP_BUTTON = (
        By.XPATH, 
        "//div[@role='dialog']//div[contains(@class, 'MuiDialogActions-root')]//button[@type='submit']"
    )

    # API 비동기 성공 스낵바 로케이터
    SUCCESS_SNACKBAR = (
        By.XPATH, 
        "//*[@id='notistack-snackbar']//*[contains(@data-testid, 'circle-checkIcon')]"
    )

    # 다운로드 버튼 로케이터
    DOWNLOAD_BTN = (By.XPATH, "(//button[contains(@class, 'MuiLoadingButton-root')])[last()]")

    # 추가 요청사항 구역
    OPINION_REQUEST_TRIGGER = (
        By.XPATH, 
        "//tbody//tr[last()]//td[.//textarea[@maxlength='200']]//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']"
    )
    OPINION_SAVE_BUTTON = (
        By.XPATH, 
        "//tbody//tr[last()]//td[.//textarea[@maxlength='200']]//div[contains(@class, 'MuiStack-root')]//button[1]"
    )

    # [학생 추가 컴포넌트 관련 로케이터]
    ADD_BTN_TOP = (By.XPATH, "//button[contains(@class, 'css-gboxby') and .//*[contains(@data-testid, 'plusIcon')]]")
    ADD_BTN_BOTTOM = (By.XPATH, "//button[contains(@class, 'css-156kttz') and .//*[contains(@data-testid, 'plusIcon')]]")
    
    # 새로 생성된 맨 아래 행(tfoot) 제어 로케이터
    TFOOT_LAST_NAME_TRIGGER = (By.XPATH, "//tfoot//tr[last()]//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']")
    TFOOT_LAST_NAME_SAVE_BTN = (By.XPATH, "//tfoot//tr[last()]//td[2]//div[contains(@class, 'MuiStack-root')]//button[1]")
    TFOOT_LAST_KEYWORD_TRIGGER = (By.XPATH, "//tfoot//tr[last()]//td[3]//button")

    # 팝업창 내부 직접 입력 전용 로케이터
    DIALOG_CUSTOM_INPUT = (By.XPATH, "//div[@role='dialog']//div[contains(@class, 'MuiInputBase-root')]//input[@type='text']")
    DIALOG_ADD_BTN = (By.XPATH, "//div[@role='dialog']//button[@type='button' and contains(@class, 'MuiButton-containedSecondary')]")

    # [검색 컴포넌트 로케이터] 클래스 상단 배치
    SEARCH_INPUT_FIELD = (By.XPATH, "//div[./div/*[@data-testid='magnifying-glassIcon']]/input")


    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_detailed_specialty(self):
        """도구 메뉴 내부 진입 후, 화면에 보이는 '세부 특기사항' 카드를 클릭하여 최종 이동합니다."""
        self.click(self.DETAILED_SPECIALTY_MENU)

    def click_reset_button(self):
        """'입력 내용 초기화' 회전 화살표 버튼을 안전하게 클릭합니다."""
        self.safe_click(self.RESET_TRIGGER_BTN)

    def confirm_reset_modal(self):
        """초기화 확인 모달의 빨간색 에러성 확정 버튼을 클릭합니다."""
        self.safe_click(self.MODAL_CONFIRM_BTN)

    def select_school_level_and_info(self, school_level="초등학교", grade_index=1, custom_subject=None, subject_index=0, unit_text="5"):
 
        # 1. 학교급 선택 콤보박스 클릭
        self.safe_click(self.SCHOOL_LEVEL_COMBO)
        time.sleep(0.8) # 목록 애니메이션 안정화
        
        # 🎯 [Xpath 교정] 삼항 연산자 다 지우고, 화면에 뜬 텍스트 그대로 조준 사격!
        TARGET_SCHOOL = (
            By.XPATH, 
            f"//li[@role='option'][contains(text(), '{school_level}')] "
            f"| //*[contains(@class, 'MuiMenuItem-root')][contains(text(), '{school_level}')]"
        )
        self.safe_click(TARGET_SCHOOL)
        logger.info(f"🖱️ [POM] 학교급 반영 성공 ➡️ [{school_level}]")
        time.sleep(1.0) # 학교급 변경에 따른 학년/과목 목록 리렌더링 대기 시간 보장!

        # 2. 학년 선택 (이하 형님 원본 코드와 동일)
        self.safe_click(self.GRADE_COMBO)
        time.sleep(0.5)
        TARGET_GRADE = (By.XPATH, f"(//li[@role='option'])[{grade_index}]")
        self.safe_click(TARGET_GRADE)
        time.sleep(0.5)

        # 3. 과목 선택 또는 직접 입력
        wait = WebDriverWait(self.driver, 10)
        subject_field = wait.until(EC.element_to_be_clickable(self.SUBJECT_COMBO))
        subject_field.click()
        time.sleep(0.5)

        if custom_subject:
            subject_field.clear()
            for char in custom_subject:
                subject_field.send_keys(char)
            logger.info(f"⌨️ 과목 직접 입력 완료: [{custom_subject}]")
            time.sleep(0.5)
        else:
            TARGET_SUBJECT = (By.XPATH, f"//li[@role='option' and @data-option-index='{subject_index}']")
            self.safe_click(TARGET_SUBJECT)
            time.sleep(0.5)

        # 4. 단원 입력
        unit_field = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.UNIT_INPUT))
        unit_field.click()
        unit_field.clear()
        unit_field.send_keys(unit_text)
        time.sleep(0.5)

    def click_next_step(self):
        """'다음으로' 버튼을 눌러 정식으로 2단계 화면 진입을 트리거합니다."""
        self.safe_click(self.NEXT_BUTTON)

    def add_student(self, name):
        """'이름을 입력해주세요.' 빈 영역을 찾아 클릭한 뒤 ActionChains를 깨끗하게 청소하며 이름을 주입합니다."""
        self.safe_click(self.STUDENT_NAME_TRIGGER)
        time.sleep(0.5)
        
        actions = ActionChains(self.driver)
        for char in name:
            actions.send_keys(char)
        actions.perform()
        time.sleep(0.5)
        
        self.safe_click(self.SAVE_BUTTON)

    def select_keywords(self, category_name="학습 태도", keyword_text="수업 집중도 높음"):
        """
        [고도화] 키워드 팝업을 열고, 매개변수로 전달된 카테고리의 아코디언을 동적으로 찾아 전개한 뒤,
        해당 카테고리 내부의 특정 키워드 칩을 선택하고 저장 요청을 마감합니다.
        
        Args:
            category_name (str): '학습 태도', '성장·변화', '의사소통·사회성', '문제 해결·탐구 역량', '태도 및 품성'
            keyword_text (str): '수업 집중도 높음', '수업 참여도 높음', '질문 및 의견 제시 적극적' 등 실제 칩 텍스트
        """
        # 1. 키워드 선택 팝업 열기 버튼 클릭
        self.safe_click(self.KEYWORD_POPUP_TRIGGER)
        time.sleep(1.2) # 팝업 창이 뜨는 안정화 대기

        # 2. 🔥 [동적 저격] 카테고리 이름에 매핑된 아코디언 화살표(chevron-down) 찾아서 클릭
        DYNAMIC_ACCORDION_ARROW = (
            By.XPATH,
            f"//div[@role='dialog']//*[text()='{category_name}']/ancestor::div[contains(@class, 'MuiButtonBase-root')]//*[contains(@data-testid, 'chevron-downIcon')] "
            f"| //div[@role='dialog']//*[text()='{category_name}']/following-sibling::*[local-name()='svg' or contains(@class, 'Icon')]"
        )
        self.safe_click(DYNAMIC_ACCORDION_ARROW)
        logger.info(f"🖱️ 동적 카테고리 아코디언 전개 완료: [{category_name}]")
        time.sleep(1) # 아코디언이 열리는 애니메이션 시간 대기

        # 3. 🔥 [동적 저격] 활성화된 영역 내에서 원하는 키워드 칩 글자를 찾아서 클릭
        DYNAMIC_KEYWORD_CHIP = (
            By.XPATH,
            f"//div[@role='dialog']//div[contains(@class, 'MuiChip-root')]//*[text()='{keyword_text}']"
            f"| //div[@role='dialog']//div[contains(@class, 'MuiChip-root') and contains(., '{keyword_text}')]"
        )
        self.safe_click(DYNAMIC_KEYWORD_CHIP)
        logger.info(f"🖱️ 동적 키워드 칩 선택 완료: [{keyword_text}]")
        time.sleep(0.5)

        # 4. 팝업 내부 최종 "저장" 버튼 클릭
        self.safe_click(self.SAVE_POPUP_BUTTON)
        logger.info("💾 키워드 선택 완료 및 AI 팝업 저장 피니시")

    def wait_for_api_success(self, timeout=60):
        """
        AI 초안 및 재생성이 완료되어 상단 비동기 성공 체크 스낵바가 렌더링될 때까지 스마트하게 대기합니다.
        """
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.SUCCESS_SNACKBAR)
        )

    def click_download_result_button(self):
        """가장 뒤쪽에 배치된 최종 로딩 스타일의 '다운로드' 버튼을 안전하게 클릭 유도합니다."""
        btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.DOWNLOAD_BTN))
        self.driver.execute_script("arguments[0].click();", btn)

    def input_additional_request(self, request_text="칭찬해주기"):
        """
        '요청사항을 입력해주세요.' 빈 텍스트 영역을 활성화한 후, 
        ActionChains를 통해 원하는 요청 사항을 주입하고 저장 버튼을 누릅니다.
        """
        # 1. 텍스트 영역 활성화 클릭
        self.safe_click(self.OPINION_REQUEST_TRIGGER)
        time.sleep(1)

        # 2. 텍스트 타이핑 주입
        actions = ActionChains(self.driver)
        for char in request_text:
            actions.send_keys(char)
        actions.perform()
        logger.info(f"⌨️ 추가 요청사항 주입 완료: [{request_text}]")
        time.sleep(0.5)

        # 3. 우측 하단 저장 버튼 클릭
        self.safe_click(self.OPINION_SAVE_BUTTON)
        logger.info("💾 추가 요청사항 저장 처리 트리거")

    def click_top_add_student_button(self):
        """상단 [학생 추가] 버튼을 클릭합니다."""
        self.safe_click(self.ADD_BTN_TOP)
        time.sleep(2) # 빈 입력 줄(tfoot) 렌더링 대기

    def click_bottom_add_student_button(self):
        """하단 [학생 추가] 버튼을 클릭합니다."""
        self.safe_click(self.ADD_BTN_BOTTOM)
        time.sleep(2) # 빈 입력 줄(tfoot) 렌더링 대기

    def add_new_student_name_at_last_row(self, name):
        """새로 생성된 tfoot의 마지막 행에 학생 이름을 주입하고 저장합니다."""
        self.safe_click(self.TFOOT_LAST_NAME_TRIGGER)
        time.sleep(1)
        
        actions = ActionChains(self.driver)
        for char in name:
            actions.send_keys(char)
        actions.perform()
        time.sleep(1)
        
        self.safe_click(self.TFOOT_LAST_NAME_SAVE_BTN)
        time.sleep(2)

    def input_custom_keyword_at_last_row(self, keyword_text):
        """새로 생성된 tfoot의 마지막 행 키워드 팝업을 열고, 직접 입력 칸에 텍스트를 주입한 뒤 추가 및 최종 저장합니다."""
        # 1. 키워드 팝업 오픈
        self.safe_click(self.TFOOT_LAST_KEYWORD_TRIGGER)
        time.sleep(1.5)

        # 2. 직접 입력 인풋 필드 클릭 및 텍스트 타이핑
        wait = WebDriverWait(self.driver, 10)
        input_el = wait.until(EC.visibility_of_element_located(self.DIALOG_CUSTOM_INPUT))
        input_el.click()
        input_el.clear()
        input_el.send_keys(keyword_text)
        time.sleep(1)

        # 3. 우측 [추가] 버튼 클릭
        self.safe_click(self.DIALOG_ADD_BTN)
        time.sleep(1)

        # 4. 우측 하단 최종 팝업 [저장] 버튼 클릭
        self.safe_click(self.SAVE_POPUP_BUTTON)
        time.sleep(2)

    def search_student_by_name(self, student_name):
        """
        검색창에 타겟 학생 이름을 주입하고, 리액트(React) 상태값 가상 DOM이 
        동기화되어 인지할 수 있도록 자바스크립트 네네이티브 이벤트를 강제 트리거합니다.
        """
        wait = WebDriverWait(self.driver, 10)
        search_field = wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT_FIELD))

        # 유저님이 고안하신 명품 리액트 바이패스 JS 스크립트 그대로 이식!
        self.driver.execute_script("""
            var el = arguments[0];
            var targetValue = arguments[1];
            // 1. 네이티브 입력 시뮬레이션 (리액트 내부 밸류 바인딩 우회)
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(el, targetValue);
            
            // 2. 버블링 이벤트 전파 트리거
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
        """, search_field, student_name)
        
        logger.info(f"⌨️ [POM 검색] 리액트 상태 가상 업데이트 완수: [{student_name}]")
        time.sleep(4.0)  # 필터링 렌더링 물리 안정화 대기

    def input_custom_keyword_for_first_student(self, keyword_text="활발"):

        wait = WebDriverWait(self.driver, 10)

        btn = wait.until(EC.element_to_be_clickable(self.KEYWORD_POPUP_TRIGGER))
        btn.click()
        logger.info("Mui 🖱️ [POM] 공통 트리거를 이용해 첫 번째 학생 키워드 팝업 오픈 성공")
        time.sleep(1.5)

        # 2. 팝업창 내부 직접 입력 인풋 필드 활용
        input_el = wait.until(EC.visibility_of_element_located(self.DIALOG_CUSTOM_INPUT))
        input_el.click()
        input_el.clear()
        input_el.send_keys(keyword_text)
        time.sleep(1)

        # 3. 우측 [추가] 버튼 클릭
        self.safe_click(self.DIALOG_ADD_BTN)
        time.sleep(1)

        # 4. 우측 하단 최종 팝업 [저장] 버튼 클릭
        self.safe_click(self.SAVE_POPUP_BUTTON)
        time.sleep(2)