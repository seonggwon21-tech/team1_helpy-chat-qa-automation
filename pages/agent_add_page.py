"""
새 에이전트 생성 화면의 UI 요소와 액션을 정의한 Page Object Model 클래스.
"""

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .base_page import BasePage


class AgentAddPage(BasePage):
    """에이전트 생성 및 생성 결과 검증 조작 클래스"""

    # =======================================================================
    # Locators
    # =======================================================================
    HAMBURGER_BUTTON = (By.XPATH, "//button[.//svg[@data-testid='barsIcon']]")

    AGENT_SEARCH_TAB = (
        By.XPATH,
        "//a[contains(@href, '/ai-helpy-chat/agents')]",
    )
    CREATE_MODE_BUTTON = (
        By.XPATH,
        "//a[contains(@href, '/ai-helpy-chat/agents/builder')]",
    )
    MY_AGENT_TAB = (
        By.XPATH,
        "//a[contains(@href, '/ai-helpy-chat/agents/mine') and contains(., '내 에이전트')]",
    )

    AGENT_NAME_INPUT = (By.XPATH, "(//input[contains(@placeholder, '이름')])[1]")
    AGENT_DESC_INPUT = (By.XPATH, "(//input[contains(@placeholder, '설명')])[1]")
    AGENT_PROMPT_INPUT = (
        By.XPATH,
        "(//textarea[contains(@placeholder, '용도') or contains(@placeholder, '제한 사항')])[1]",
    )

    SUBMIT_CREATE_BUTTON = (
        By.XPATH,
        "//button[@type='button' and contains(., '만들기')]",
    )
    MODAL_SAVE_BUTTON = (By.XPATH, "//button[contains(., '저장')]")
    MODAL_CONTAINER = (By.CLASS_NAME, "MuiDialog-container")

    CREATED_AGENT_CARD = (
        By.XPATH,
        "//a[contains(@href, '/ai-helpy-chat/agents/') and contains(@href, '/builder')]",
    )

    def __init__(self, driver):
        super().__init__(driver)

    # -----------------------------------------------------------------------
    # Actions
    # -----------------------------------------------------------------------
    def open_lnb_if_collapsed(self):
        """반응형 화면에서 LNB가 접혀 있으면 햄버거 버튼을 클릭합니다."""
        try:
            WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable(self.HAMBURGER_BUTTON)
            ).click()
        except TimeoutException:
            pass

    def navigate_to_agents(self):
        """LNB 에이전트 탐색 메뉴로 이동합니다."""
        self.open_lnb_if_collapsed()
        self.click(self.AGENT_SEARCH_TAB)
        self.wait_for_url_contains("/agents")

    def open_builder(self):
        """새 에이전트 만들기 화면으로 이동합니다."""
        self.click(self.CREATE_MODE_BUTTON)
        self.wait_for_visible(self.AGENT_NAME_INPUT)

    def fill_agent_form(self, name: str, description: str, prompt: str):
        """에이전트 이름, 한줄 소개, 규칙을 순서대로 입력합니다."""
        self._enter_stable_text(self.AGENT_NAME_INPUT, name)
        self._enter_stable_text(self.AGENT_DESC_INPUT, description)

        prompt_element = self._enter_stable_text(self.AGENT_PROMPT_INPUT, prompt)
        prompt_element.send_keys(Keys.ESCAPE)
        self.wait_until_create_button_enabled()

    def click_create_button(self):
        """우측 상단 만들기 버튼을 클릭합니다."""
        button = self.wait_until_create_button_enabled()
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button,
        )
        button.click()

    def save_visibility_settings(self):
        """공개 설정 모달에서 저장 버튼을 클릭합니다."""
        self.click(self.MODAL_SAVE_BUTTON)

    def wait_until_visibility_modal_closed(self):
        """공개 설정 모달이 사라질 때까지 대기합니다."""
        self.wait_until_invisible(self.MODAL_CONTAINER)

    def navigate_to_my_agents(self):
        """내 에이전트 탭으로 이동합니다."""
        self.click(self.AGENT_SEARCH_TAB)
        self.wait_for_url_contains("/ai-helpy-chat/agents")
        self.click(self.MY_AGENT_TAB)
        self.wait_for_url_contains("/ai-helpy-chat/agents/mine")
        self.wait.until(EC.presence_of_element_located(self.CREATED_AGENT_CARD))

    def wait_until_create_button_enabled(self):
        """만들기 버튼이 활성화될 때까지 대기한 뒤 버튼 요소를 반환합니다."""
        return self.wait.until(self._get_clickable_create_button)

    # -----------------------------------------------------------------------
    # Verification helpers
    # -----------------------------------------------------------------------
    def is_created_agent_card_visible(self) -> bool:
        """생성된 에이전트 카드가 목록에 노출되는지 확인합니다."""
        try:
            self.wait.until(EC.presence_of_element_located(self.CREATED_AGENT_CARD))
            return True
        except TimeoutException:
            return False

    def _enter_stable_text(self, locator: tuple, text: str):
        """MUI 입력창 값을 지우고 입력값 반영까지 명시적으로 확인합니다."""
        element = self._clear_field(locator)
        element.send_keys(text)
        self.wait.until(lambda driver: (element.get_attribute("value") or "") == text)
        self.driver.execute_script("arguments[0].blur();", element)
        return element

    def _clear_field(self, locator: tuple):
        """입력창을 클릭 가능한 상태로 기다린 뒤 값을 완전히 비웁니다."""
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        self.wait.until(lambda driver: (element.get_attribute("value") or "") == "")
        return element

    def _get_clickable_create_button(self, driver):
        try:
            button = driver.find_element(*self.SUBMIT_CREATE_BUTTON)
            disabled = button.get_attribute("disabled")
            aria_disabled = button.get_attribute("aria-disabled")
            class_name = button.get_attribute("class") or ""

            if (
                button.is_displayed()
                and button.is_enabled()
                and disabled is None
                and aria_disabled != "true"
                and "Mui-disabled" not in class_name
            ):
                return button

            return False
        except StaleElementReferenceException:
            return False
