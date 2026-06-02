"""
'행동특성 및 종합의견' 페이지 제어를 담당하는 클래스.
"""

import time
import logging
from selenium.webdriver.common.by import By
from .tool_page import ToolPage
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class BehaviorAndOpinionsPage(ToolPage): 
    """행동특성 및 종합의견 페이지 조작 및 이동 클래스"""

    BEHAVIOR_MENU_BUTTON = (
        By.XPATH,
        "(//div[contains(@class, 'css-1wkfo6a')]//p[contains(@class, 'css-to37at')])[2]/ancestor::a "
        "| (//div[contains(@class, 'css-1wkfo6a')]//p[contains(@class, 'css-to37at')])[2]"
    )

    def __init__(self, driver):
        super().__init__(driver)

    def navigate_to_behavior_and_opinions(self):
        """
        도구 메뉴 내부 진입 후, 화면에 보이는 '행동특성 및 종합의견' 카드를 클릭하여 이동
        """

        self.click(self.BEHAVIOR_MENU_BUTTON)

    def click_reset_button(self):
        """상단 바에 있는 '입력 내용 초기화' 버튼을 클릭"""
        RESET_TRIGGER_BTN = (By.XPATH, "//*[contains(@data-testid, 'rotate-right') or contains(@class, 'rotate-right')]/ancestor::button | //button[contains(@class, 'MuiButton-root') and .//*[contains(@data-testid, 'Icon')]]")
        self.safe_click(RESET_TRIGGER_BTN)
        time.sleep(2)

    def confirm_reset_modal(self):
        """초기화 확인 모달 팝업이 뜨면 '확인' 버튼을 클릭"""
        MODAL_CONFIRM_BTN = (By.XPATH, "//div[contains(@class, 'MuiDialogActions-root')]//button[contains(@class, 'MuiButton-containedError')]")
        self.safe_click(MODAL_CONFIRM_BTN)
        time.sleep(2)  # 시스템 전체 롤백 및 리렌더링 대기

    def select_school_level(self, level_name="초등학교"):
        """학교급 콤보박스를 열고 옵션을 선택합니다."""
        SCHOOL_LEVEL_COMBO = (By.XPATH, "//div[@role='combobox'][@aria-haspopup='listbox'] | //div[contains(@class, 'MuiSelect-select')]")
        DYNAMIC_OPTION = (By.XPATH, f"//li[@role='option'][contains(text(), '{level_name}')] | //*[contains(@class, 'MuiMenuItem-root')][contains(text(), '{level_name}')]")
        
        # 1. 콤보박스 클릭해서 열기
        self.safe_click(SCHOOL_LEVEL_COMBO)
        time.sleep(1.5) # 애니메이션 노출 대기
        
        # 2. 동적으로 생성된 학교급 옵션 클릭하기
        self.safe_click(DYNAMIC_OPTION)
        time.sleep(1.5)
        
    def click_next_step(self):
        """'다음으로' 버튼을 클릭하여 2단계 화면으로 이동"""
        NEXT_BUTTON = (By.XPATH, "//button[@type='submit'][@form='student_record_generation'] | //button[@type='submit'][@form='student_evaluation']")
        self.safe_click(NEXT_BUTTON)
        time.sleep(2)

    def add_student(self, student_name="엘리스"):
        """학생 이름 영역을 클릭 활성화하고, 이름을 입력 후 저장합니다."""
        STUDENT_NAME_TRIGGER = (By.XPATH, "//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']")
        SAVE_BUTTON = (By.XPATH, "//td[contains(@class, 'MuiTableCell-footer')]//div[contains(@class, 'MuiStack-root')]//button[1]")
        
        self.safe_click(STUDENT_NAME_TRIGGER)
        time.sleep(1)
        
        actions = ActionChains(self.driver)
        for char in student_name:
            actions.send_keys(char)
        actions.perform()
        time.sleep(1)
        
        self.safe_click(SAVE_BUTTON)
        time.sleep(2)

    def select_keywords(self, category_name="인성·태도", keyword_list=None):
        """
        키워드 팝업을 열고, 원하는 카테고리 아코디언을 동적으로 확장한 뒤, 전달받은 키워드 칩들을 다중 선택하고 저장합니다.
        :param category_name: "인성·태도", "학업·진로", "수업 참여도", "학교 활동" 중 선택
        :param keyword_list: 선택하고자 하는 해당 카테고리 내의 키워드 텍스트 리스트
        """
        if keyword_list is None:
            keyword_list = ["예의 바르고 배려심 있음"]

        KEYWORD_TARGET_TEXT = (By.XPATH, "//tfoot//tr[last()]//td[3]//button")
        SAVE_POPUP_BUTTON = (By.XPATH, "//div[@role='dialog']//div[contains(@class, 'MuiDialogActions-root')]//button[@type='submit']")
        
        DYNAMIC_CATEGORY_ARROW = (
            By.XPATH, 
            f"//div[@role='dialog']//div[contains(@class, 'MuiAccordionSummary-root')][.//p[contains(text(), '{category_name}')]]//*[contains(@data-testid, 'chevron-downIcon')]"
            f"| //div[@role='dialog']//div[contains(@class, 'MuiAccordionSummary-root')][.//p[contains(text(), '{category_name}')]]//svg"
        )

        # 1. 키워드 팝업 오픈
        self.safe_click(KEYWORD_TARGET_TEXT)
        time.sleep(1.5)
        
        # 2. 유저님이 지정한 특정 카테고리 화살표 클릭해서 전개!
        logger.info(f"🖱️ [{category_name}] 카테고리 아코디언 전개 시도")
        self.safe_click(DYNAMIC_CATEGORY_ARROW)
        time.sleep(1.2) # 아코디언 열리는 애니메이션 시간 보장
        
        # 3. 전개된 영역 내부에서 원하는 키워드 칩들을 순회하며 다중 선택
        for keyword in keyword_list:
            # 해당 카테고리 내부(MuiCollapse-entered)에서 원하는 글자가 박힌 칩을 정확히 추적하는 XPATH
            DYNAMIC_CHIP = (
                By.XPATH, 
                f"//div[@role='dialog']//div[contains(@class, 'MuiCollapse-entered')]//div[contains(@class, 'MuiChip-root')]//*[text()='{keyword}']"
                f"| //div[@role='dialog']//div[contains(@class, 'MuiCollapse-entered')]//span[contains(@class, 'MuiChip-label')][text()='{keyword}']"
            )
            logger.info(f"   ↳ 칩 클릭: [{keyword}]")
            self.safe_click(DYNAMIC_CHIP)
            time.sleep(0.5)
            
        # 4. 최종 팝업 저장 버튼 클릭
        self.safe_click(SAVE_POPUP_BUTTON)
        time.sleep(2)

    def input_additional_opinion(self, opinion_text="칭찬해주기"):
        """추가 요청사항 영역을 클릭 활성화하고, 요청 텍스트 입력 후 저장합니다."""
        OPINION_REQUEST_TRIGGER = (By.XPATH, "//tbody//tr[last()]//td[.//textarea[@maxlength='200']]//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']")
        OPINION_SAVE_BUTTON = (By.XPATH, "//tbody//tr[last()]//td[.//textarea[@maxlength='200']]//div[contains(@class, 'MuiStack-root')]//button[1]")
        
        self.safe_click(OPINION_REQUEST_TRIGGER)
        time.sleep(1)
        
        actions = ActionChains(self.driver)
        for char in opinion_text:
            actions.send_keys(char)
        actions.perform()
        time.sleep(1)
        
        self.safe_click(OPINION_SAVE_BUTTON)
        time.sleep(2)

    def wait_for_api_success(self, timeout=30):
        """AI 생성/재생성 완료 스낵바 팝업이 노출될 때까지 스마트 대기합니다."""
        SUCCESS_SNACKBAR = (By.XPATH, "//*[@id='notistack-snackbar']//*[contains(@data-testid, 'circle-checkIcon')]")
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(SUCCESS_SNACKBAR))

    def click_top_add_student_button(self):
        """상단 [학생 추가] 버튼 클릭"""
        ADD_BTN_TOP = (By.XPATH, "//button[contains(@class, 'css-gboxby') and .//*[contains(@data-testid, 'plusIcon')]]")
        self.safe_click(ADD_BTN_TOP)
        time.sleep(1.5) # 빈 입력 줄 렌더링 대기

    def click_bottom_add_student_button(self):
        """하단 [학생 추가] 버튼 클릭"""
        ADD_BTN_BOTTOM = (By.XPATH, "//button[contains(@class, 'css-156kttz') and .//*[contains(@data-testid, 'plusIcon')]]")
        self.safe_click(ADD_BTN_BOTTOM)
        time.sleep(1.5)

    def add_new_student_name_at_last_row(self, student_name):
        """가장 최근에 추가된 빈 줄(tfoot의 last row)에 학생 이름을 입력하고 저장"""
        NAME_TRIGGER = (By.XPATH, "//tfoot//tr[last()]//div[contains(@class,'edit-button')]/preceding-sibling::p[@role='button']")
        SAVE_NAME_BTN = (By.XPATH, "//tfoot//tr[last()]//td[2]//div[contains(@class, 'MuiStack-root')]//button[1]")
        
        # 이름 칸 활성화
        self.safe_click(NAME_TRIGGER)
        time.sleep(0.5)
        
        # 이름 입력 (ActionChains 안정성 확보)
        actions = ActionChains(self.driver)
        for char in student_name:
            actions.send_keys(char)
        actions.perform()
        time.sleep(0.5)
        
        # 저장 버튼 클릭
        self.safe_click(SAVE_NAME_BTN)
        time.sleep(1.5)

    def input_custom_keyword_at_last_row(self, custom_keyword):
        """가장 최근에 추가된 학생 행의 키워드 팝업을 열어 [직접 입력]으로 키워드를 주입하고 저장"""
        KEYWORD_POPUP_BTN = (By.XPATH, "//tfoot//tr[last()]//td[3]//button")
        INPUT_FIELD = (By.XPATH, "//div[@role='dialog']//div[contains(@class, 'MuiInputBase-root')]//input[@type='text']")
        ADD_DIALOG_BTN = (By.XPATH, "//div[@role='dialog']//button[@type='button' and contains(@class, 'MuiButton-containedSecondary')]")
        SAVE_DIALOG_BTN = (By.XPATH, "//div[@role='dialog']//div[contains(@class, 'MuiDialogActions-root')]//button[@type='submit']")
        
        # 1. 팝업 열기
        self.safe_click(KEYWORD_POPUP_BTN)
        time.sleep(1)
        
        # 2. 직접 입력 인풋 필드 글자 주입
        wait = WebDriverWait(self.driver, 5)
        input_el = wait.until(EC.visibility_of_element_located(INPUT_FIELD))
        input_el.click()
        input_el.clear()
        input_el.send_keys(custom_keyword)
        time.sleep(0.5)
        
        # 3. 우측 [추가] 버튼 클릭 후 최종 [저장]
        self.safe_click(ADD_DIALOG_BTN)
        time.sleep(0.5)
        self.safe_click(SAVE_DIALOG_BTN)
        time.sleep(1.5) # AI 초안 생성 요청 처리 대기

    def search_student_by_name(self, search_name="래빗"):
        """검색창을 찾아 입력 값을 주입하고 리액트 이벤트를 강제로 트리거하여 학생을 검색합니다."""
        SEARCH_INPUT_FIELD = (By.XPATH, "//div[./div/*[@data-testid='magnifying-glassIcon']]/input")
        
        # 1. 검색창 요소를 대기 후 확보
        wait = WebDriverWait(self.driver, 10)
        search_field = wait.until(EC.element_to_be_clickable(SEARCH_INPUT_FIELD))
        
        # 2. 껍데기만 입력되는 리액트 버그를 방지하기 위한 자바스크립트 네이티브 주입 제어
        self.driver.execute_script("""
            var el = arguments[0];
            var targetValue = arguments[1];
            
            // 1) 네이티브 입력 시뮬레이션 (리액트가 값을 인지하도록 세터 호출)
            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(el, targetValue);
            
            // 2) 리액트 상태 업데이트를 위한 버블링 이벤트 강제 발생
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            el.dispatchEvent(new Event('blur', { bubbles: true }));
        """, search_field, search_name)
        
        logger.info(f"⌨️ [검색창 주입] 리액트 상태 업데이트 완료: 입력어 [{search_name}]")
        time.sleep(4.0) # 비동기 필터링 결과가 화면에 리렌더링될 때까지 안전 대기    

    def click_download_result_button(self):
        """화면 맨 우측 하단에 위치한 최종 [생성 결과 다운로드] 버튼을 클릭합니다."""
        DOWNLOAD_BTN = (By.XPATH, "(//button[contains(@class, 'MLoadingButton-root') or contains(@class, 'MuiLoadingButton-root')])[last()]")
        
        wait = WebDriverWait(self.driver, 10)
        btn = wait.until(EC.element_to_be_clickable(DOWNLOAD_BTN))
        
        # 브라우저 스크롤 및 요소 가림 방지를 위해 JS click 처리 유지
        self.driver.execute_script("arguments[0].click();", btn)
        logger.info("🖱️ [페이지 액션] 생성 결과 다운로드 버튼 클릭 완료 (JS)")
        time.sleep(2) # 다운로드 프로세스 시작 대기