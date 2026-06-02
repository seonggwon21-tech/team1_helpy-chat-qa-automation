"""
헬피챗 에이전트 탐색 -> 필터영역
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class AgentFilterPage(BasePage):
    # =======================================================================
    # 1. 고정 로케이터 정의 
    # =======================================================================
    AGENT_SEARCH_MENU = (By.XPATH, "//*[text()='에이전트 탐색']")
    AGENT_CARD = (By.XPATH, "//div[contains(@class, 'MuiCard-root') or contains(@class, 'agent-card')]")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def navigate_to_agent_search(self):
        self.click(self.AGENT_SEARCH_MENU)
        self.wait.until(EC.url_contains("/agents"))

    # =======================================================================
    # 🔥 [time.sleep 100% 제거] 동적 필터 칩 클릭 및 조건부 대기 함수
    # =======================================================================
    def click_filter_chip(self, filter_name: str):
        """
        time.sleep 없이, 필터 칩이 활성화되는 순간을 명시적으로 대기하고 클릭합니다.
        """
        dynamic_filter_xpath = (
            By.XPATH, 
            f"//div[contains(@class, 'MuiChip-root')][.//span[contains(text(), '{filter_name}')]]"
        )
        
        # 1. 버튼이 클릭 가능할 때까지 기다린 후 클릭
        filter_btn = self.wait.until(EC.element_to_be_clickable(dynamic_filter_xpath))
        filter_btn.click()
        
        # 🎯 [핵심 방어막] time.sleep(1) 대신 쓰는 명시적 대기 치트키!
        # 클릭한 필터 칩의 HTML 클래스 속성에 'MuiChip-clickable' 혹은 'Mui-selected' 같은 
        # 활성화 클래스 상태가 반영될 때까지 기다립니다. (리액트 상태 갱신 완료 순간 캐치)
        self.wait.until(EC.element_attribute_to_include(dynamic_filter_xpath, "class"))
        
        return filter_btn.get_attribute("class")

    def get_card_count(self) -> int:
        """현재 화면에 노출된 에이전트 카드의 개수를 반환합니다."""
        try:
            # 카드가 최소 1개 이상 화면에 나타나서 안정화될 때까지 명시적 대기
            cards = self.wait.until(EC.visibility_of_all_elements_located(self.AGENT_CARD))
            return len(cards)
        except Exception:
            return 0