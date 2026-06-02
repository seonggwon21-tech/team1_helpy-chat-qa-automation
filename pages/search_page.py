"""
search modal page object.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage


class SearchPage(BasePage):
    """검색 모달 조작 및 검증 Page Object"""

    MENU_SEARCH = (
        By.XPATH,
        "//*[@data-testid='magnifying-glassIcon']/ancestor::*[@role='button']"
    )
    SEARCH_INPUT = (
        By.CSS_SELECTOR,
        "div[role='dialog'] input.MuiInputBase-input.MuiInputBase-inputAdornedEnd"
    )
    CLOSE_BUTTON = (
        By.XPATH,
        "//div[@role='dialog']//button[.//*[@data-testid='xmark-largeIcon']]"
    )
    SEARCH_RESULT_ITEM = (
        By.CSS_SELECTOR,
        "div[role='dialog'] "
        "a.MuiListItemButton-root[href*='/ai-helpy-chat/chats/']"
    )

    LNB_FIRST_CHAT_ITEM = (
        By.CSS_SELECTOR,
        "ul[data-testid='virtuoso-item-list'] "
        "a.MuiListItemButton-root[href*='/ai-helpy-chat/chats/'][data-index='0']"
    )
    LNB_FIRST_CHAT_MORE_BUTTON = (
        By.XPATH,
        "("
        "//ul[@data-testid='virtuoso-item-list']"
        "//a[contains(@class, 'MuiListItemButton-root') "
        "and contains(@href, '/ai-helpy-chat/chats/') "
        "and @data-index='0']"
        "//button[contains(@class, 'MuiIconButton-root')]"
        ")[last()]"
    )
    CONTEXT_DELETE_BUTTON = (
        By.XPATH,
        "//li[@role='menuitem' and .//*[@data-testid='trashIcon']]"
    )
    CONFIRM_DELETE_BUTTON = (By.CSS_SELECTOR, "button.MuiButton-containedError")
    DELETE_SUCCESS_ALERT = (
        By.XPATH,
        "//div[@role='alert' "
        "and contains(@class, 'notistack-MuiContent-success') "
        "and contains(., '대화가 삭제되었습니다!')]"
    )
    DELETE_SUCCESS_ALERT_TEXT = (
        By.XPATH,
        "//*[@role='alert' and contains(., '대화가 삭제되었습니다!')]"
    )

    def open_search_modal(self):
        """LNB 검색 버튼 클릭 후 검색 입력창 노출까지 대기합니다."""
        self.click(self.MENU_SEARCH)
        self.wait_for_visible(self.SEARCH_INPUT)

    def enter_search_keyword(self, keyword: str):
        """검색어 입력 후 입력값 반영까지 대기합니다."""
        self.enter_text(self.SEARCH_INPUT, keyword)
        self.wait.until(lambda driver: self.get_search_input_value() == keyword)

    def click_close_button(self):
        """검색 모달 닫기 버튼 클릭 후 입력창이 사라질 때까지 대기합니다."""
        self.click(self.CLOSE_BUTTON)
        self.wait_until_invisible(self.SEARCH_INPUT)

    def click_first_result(self):
        """첫 번째 검색 결과 클릭 후 대화 상세 URL 이동까지 대기합니다."""
        self.click(self.SEARCH_RESULT_ITEM)
        self.wait_for_url_contains("/ai-helpy-chat/chats/")

    def click_first_lnb_chat_more_button(self):
        """LNB 첫 번째 대화 항목의 3dot 메뉴를 엽니다."""
        first_item = self.wait.until(
            EC.visibility_of_element_located(self.LNB_FIRST_CHAT_ITEM)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            first_item
        )
        ActionChains(self.driver).move_to_element(first_item).perform()

        self.click(self.LNB_FIRST_CHAT_MORE_BUTTON)
        self.wait_for_visible(self.CONTEXT_DELETE_BUTTON)

    def click_context_delete_button(self):
        """컨텍스트 메뉴 삭제 버튼 클릭 후 확인 다이얼로그를 기다립니다."""
        self.click(self.CONTEXT_DELETE_BUTTON)
        self.wait_for_visible(self.CONFIRM_DELETE_BUTTON)

    def click_confirm_delete_button(self):
        """삭제 확인 다이얼로그의 삭제 버튼을 클릭하고 성공 알림을 즉시 대기합니다."""
        self.click(self.CONFIRM_DELETE_BUTTON)
        self._delete_success_alert_seen = self._wait_for_delete_success_alert(
            timeout=20
        )

    def get_search_input_value(self) -> str:
        """현재 검색 입력창 값을 반환합니다."""
        element = self.wait_for_visible(self.SEARCH_INPUT)
        return element.get_attribute("value") or ""

    def is_modal_open(self) -> bool:
        return self._visible(self.SEARCH_INPUT)

    def is_modal_closed(self) -> bool:
        try:
            self.wait.until(EC.invisibility_of_element_located(self.SEARCH_INPUT))
            return True
        except TimeoutException:
            return False

    def is_result_list_visible(self) -> bool:
        return self._visible(self.SEARCH_RESULT_ITEM)

    def is_chat_detail_open(self) -> bool:
        try:
            self.wait.until(EC.url_contains("/ai-helpy-chat/chats/"))
            return True
        except TimeoutException:
            return False

    def is_first_lnb_chat_visible(self) -> bool:
        return self._present(self.LNB_FIRST_CHAT_ITEM)

    def is_delete_success_alert_visible(self) -> bool:
        if getattr(self, "_delete_success_alert_seen", False):
            return True

        self._delete_success_alert_seen = self._wait_for_delete_success_alert(
            timeout=20
        )
        return self._delete_success_alert_seen

    def _wait_for_delete_success_alert(self, timeout: int = 20) -> bool:
        wait = WebDriverWait(
            self.driver,
            timeout,
            poll_frequency=0.2
        )

        def success_alert_is_visible(_driver):
            for locator in (
                self.DELETE_SUCCESS_ALERT,
                self.DELETE_SUCCESS_ALERT_TEXT,
            ):
                elements = self.driver.find_elements(*locator)
                if any(element.is_displayed() for element in elements):
                    return True
            return False

        try:
            wait.until(success_alert_is_visible)
            return True
        except TimeoutException:
            return False

    def _visible(self, locator: tuple) -> bool:
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def _present(self, locator: tuple) -> bool:
        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False
