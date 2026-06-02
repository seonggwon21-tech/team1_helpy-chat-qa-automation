"""
헬피챗 에이전트 탐색 -> 검색영역
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage

class AgentSearchPage(BasePage):
    # =======================================================================
    # 1. 고정 로케이터 정의 
    # =======================================================================
    HAMBURGER_BUTTON = (By.XPATH, "//button[.//svg[@data-testid='barsIcon']]")
    AGENT_SEARCH_MENU = (By.XPATH, "//*[text()='에이전트 탐색']")
    AGENT_CARD = (By.XPATH, "//div[contains(@class, 'MuiCard-root') or contains(@class, 'agent-card')]")
    SEARCH_INPUT = (By.XPATH, "//input[@placeholder='AI 에이전트 검색']")
    NO_RESULT_TEXT = (By.XPATH, "//*[text()='검색 결과가 없습니다.']")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    # 에이전트 탐색 메뉴 이동 (반응형 햄버거 대응 포함)
    def navigate_to_agent_search(self):
        try:
            self.wait.until(EC.element_to_be_clickable(self.HAMBURGER_BUTTON)).click()
        except Exception:
            pass
        self.click(self.AGENT_SEARCH_MENU)
        self.wait.until(EC.url_contains("/agents"))

    # 화면에 로드된 전체 카드 개수 반환
    def get_card_count(self) -> int:
        try:
            cards = self.wait.until(EC.visibility_of_all_elements_located(self.AGENT_CARD))
            return len(cards)
        except Exception:
            return 0

    # 🎯 [time.sleep 박멸] 기존 입력값을 지우고 한 글자씩 타이핑 후 인풋 마감 대기
    def search_keyword(self, keyword: str):
        search_el = self.wait.until(EC.visibility_of_element_located(self.SEARCH_INPUT))
        search_el.click()
        
        # 글자 싹 지우기 (Human Typing 기반)
        search_el.send_keys(Keys.CONTROL + "a")
        search_el.send_keys(Keys.BACKSPACE)
        
        # 키워드 주입
        search_el.send_keys(keyword)
        search_el.send_keys(Keys.ENTER)

    # 🎯 [명시적 대기] "검색 결과 없음" 문구가 화면에 뜰 때까지 대기
    def is_no_result_displayed(self) -> bool:
        try:
            return self.wait.until(EC.visibility_of_element_located(self.NO_RESULT_TEXT)).is_displayed()
        except Exception:
            return False

    # 🎯 [동적 셀렉터 & 명시적 대기] 내가 검색한 단어가 포함된 카드가 렌더링될 때까지 대기
    def wait_for_card_with_keyword(self, keyword: str) -> str:
        # 두 개의 완성된 XPath 경로를 파이프(|) 기호로 연결해 주어야 브라우저가 정상 인식합니다.
        dynamic_card_title_xpath = (
            By.XPATH,
            f"//*[contains(@class, 'title') and contains(text(), '{keyword}')] "
            f"| //*[contains(@class, 'MuiCard-root') or contains(@class, 'agent-card')]//*[contains(text(), '{keyword}')]"
        )
        # 해당 타이틀을 가진 카드가 노출되는 순간 즉시 낚아챕니다.
        card_title_el = self.wait.until(EC.visibility_of_element_located(dynamic_card_title_xpath))
        return card_title_el.text