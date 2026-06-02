"""
헬피챗 에이전트 탐색 -> 마이 에이전트
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage

class MyAgentPage(BasePage):
    # =======================================================================
    # 1. 고정 로케이터 정의
    # =======================================================================
    HAMBURGER_BUTTON = (By.XPATH, "//button[.//svg[@data-testid='barsIcon']]")
    AGENT_SEARCH_TAB = (By.XPATH, "//a[contains(@href, '/ai-helpy-chat/agents')]")
    MY_AGENT_MENU_BTN = (By.XPATH, "//a[contains(@href, '/ai-helpy-chat/agents/mine') and contains(., '내 에이전트')]")
    CREATE_MODE_BTN = (By.XPATH, "//a[contains(@href, '/agents/builder')]")
    
    # 에이전트 카드 및 입력 폼
    TARGET_CARD = (By.XPATH, "//a[contains(@href, '/ai-helpy-chat/agents/') and contains(@href, '/builder')]")
    AGENT_NAME_INPUT = (By.XPATH, "(//input[contains(@placeholder, '이름')])[1]")
    AGENT_DESC_INPUT = (By.XPATH, "(//input[contains(@placeholder, '설명')])[1]")
    AGENT_PROMPT_INPUT = (By.XPATH, "(//textarea[contains(@placeholder, '용도') or contains(@placeholder, '제한 사항')])[1]")
    
    # 저장 및 모달
    SUBMIT_CREATE_BTN = (By.XPATH, "//button[@type='button' and (contains(., '만들기') or contains(., '업데이트') or contains(., '완료'))]")    
    MODAL_SAVE_BTN = (By.XPATH, "//button[contains(., '저장')]")
    MODAL_CONTAINER = (By.CLASS_NAME, "MuiDialog-container")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # 2. 에이전트 탐색 -> 내 에이전트 메뉴로 순차 이동
    def navigate_to_my_agents(self):
        try:
            WebDriverWait(self.driver, 0.5).until(EC.element_to_be_clickable(self.HAMBURGER_BUTTON)).click()
        except Exception:
            pass
        self.click(self.AGENT_SEARCH_TAB)
        self.wait.until(EC.url_contains("/ai-helpy-chat/agents"))
        
        self.click(self.MY_AGENT_MENU_BTN)
        self.wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))

    # 3. 카드 유무 판단 및 분기 방어 행동
    def ensure_agent_card_exists_and_click(self):
        cards = []
        try:
            # 카드가 그리는 순간을 3초간 명시적 대기 후 수집
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(self.TARGET_CARD))
            cards = self.driver.find_elements(*self.TARGET_CARD)
        except Exception:
            pass

        if len(cards) > 0:
            my_card = self.wait.until(EC.element_to_be_clickable(self.TARGET_CARD))
            my_card.click()
        else:
            self.click(self.CREATE_MODE_BTN)
            
            # 임시 에이전트 필수 값 입력 플로우
            self.modify_agent_form_fields("자동화_테스트_에이전트", "자동화_테스트_에이전트 입니다..", "자동화_테스트_에이전트 규칙 입니다.")
            self.click(self.SUBMIT_CREATE_BTN)
            
            # 명시적 대기
            my_card = self.wait.until(EC.element_to_be_clickable(self.TARGET_CARD))
            my_card.click()

    # 4. 입력창 타이핑 모듈
    def modify_agent_form_fields(self, name: str, desc: str, prompt: str):
        # 1. 이름 필드 클리어 후 입력
        name_el = self.wait.until(EC.visibility_of_element_located(self.AGENT_NAME_INPUT))
        name_el.click()
        name_el.send_keys(Keys.CONTROL + "a")
        name_el.send_keys(Keys.BACKSPACE)
        name_el.send_keys(name)
        name_el.send_keys(Keys.TAB)

        # 2. 설명 필드 클리어 후 입력
        desc_el = self.wait.until(EC.visibility_of_element_located(self.AGENT_DESC_INPUT))
        desc_el.click()
        desc_el.send_keys(Keys.CONTROL + "a")
        desc_el.send_keys(Keys.BACKSPACE)
        desc_el.send_keys(desc)
        desc_el.send_keys(Keys.TAB)

        # 3. 규칙(프롬프트) 필드 클리어 후 입력
        prompt_el = self.wait.until(EC.visibility_of_element_located(self.AGENT_PROMPT_INPUT))
        prompt_el.click()
        prompt_el.send_keys(Keys.CONTROL + "a")
        prompt_el.send_keys(Keys.BACKSPACE)
        prompt_el.send_keys(prompt)
        prompt_el.send_keys(Keys.ESCAPE)

    # 5. 최종 만들기 버튼 클릭 및 리액트 비동기 마감 처리
    def submit_and_handle_modal(self):
        # 최종 보라색 버튼 클릭 가능 상태 잡기
        submit_btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_CREATE_BTN))
        submit_btn.click()
        
        # 2차 공개 설정 모달창 클로저 대기
        save_btn = self.wait.until(EC.element_to_be_clickable(self.MODAL_SAVE_BTN))
        save_btn.click()
        
        # 배경레이어가 걷힐 때까지 명시적 대기
        self.wait.until(EC.invisibility_of_element_located(self.MODAL_CONTAINER))