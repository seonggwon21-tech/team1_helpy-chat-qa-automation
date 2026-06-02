"""
ToolPage를 상속받아 도구 메뉴의 하위 기능인
'심층 조사' 페이지 이동 및 입력 제어를 담당하는 클래스.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.support import expected_conditions as EC

from .tool_page import ToolPage


class DeepInvestigationPage(ToolPage):

    # =========================
    # Locators
    # =========================
    DEEP_INVESTIGATION_MENU = (
        By.CSS_SELECTOR,
        "a:has(svg[data-ai-tool-ident='do_deep_research'])",
    )

    TOPIC_INPUT = (By.CSS_SELECTOR, "input[name='topic'], textarea[name='topic']")
    INSTRUCTIONS_TEXTAREA = (By.CSS_SELECTOR, "textarea[name='instructions']")

    REGENERATE_BUTTON = (
        By.CSS_SELECTOR,
        "button[form='tool-factory-do_deep_research'][type='submit']",
    )

    MODAL_REGENERATE_BUTTON = (
        By.CSS_SELECTOR,
        "[role='dialog'] button[form='tool-factory-do_deep_research'][type='submit']",
    )

    REGENERATE_MODAL = (By.CSS_SELECTOR, "[role='dialog']")
    STOP_BUTTON = (By.CSS_SELECTOR, "button:has(svg[data-testid='stopIcon'])")
    STOP_MESSAGE = (By.CSS_SELECTOR, "[role='alert'] .MuiAlertTitle-root")

    RESULT_PANEL = (
        By.CSS_SELECTOR,
        "div[role='tabpanel'][data-panel='output'][aria-hidden='false']",
    )
    RESULT_SUCCESS_MESSAGE = (
        By.XPATH,
        "//div[@role='tabpanel' and @data-panel='output']"
        "//*[contains(normalize-space(.), '입력하신 내용 기반으로 심층조사 결과를 생성했습니다.')]",
    )
    RESULT_MARKDOWN = (
        By.CSS_SELECTOR,
        "div[role='tabpanel'][data-panel='output'] .elice-aichat__markdown",
    )
    RESULT_DOWNLOAD_BUTTON = (
        By.XPATH,
        "//div[@role='tabpanel' and @data-panel='output']//button[.//*[@data-testid='caret-downIcon']]",
    )
    DOWNLOAD_MENU = (
        By.CSS_SELECTOR,
        "[role='menu'], ul[role='listbox']",
    )
    MARKDOWN_DOWNLOAD_OPTION = (
        By.XPATH,
        "//*[@role='menuitem' or @role='option' or self::button or self::a]"
        "[contains(normalize-space(.), '마크다운') "
        "or contains(normalize-space(.), 'Markdown') "
        "or contains(normalize-space(.), 'markdown') "
        "or contains(normalize-space(.), 'MD') "
        "or contains(normalize-space(.), 'md')]",
    )

    # =========================
    # Navigation
    # =========================
    def navigate(self):
        self.setup_tool_tab()
        element = self.wait.until(
            EC.element_to_be_clickable(self.DEEP_INVESTIGATION_MENU)
        )
        element.click()

    def navigate_to_deep_investigation_page(self):
        self.navigate()

    # =========================
    # Clear (명시적 유지 - 중요)
    # =========================
    def _clear_field(self, locator):
        element = self.wait.until(
            EC.element_to_be_clickable(locator)
        )
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        self.wait.until(
            lambda driver: (element.get_attribute("value") or "") == ""
        )
        return element

    def clear_topic(self):
        self._clear_field(self.TOPIC_INPUT)

    def clear_topic_input(self):
        self.clear_topic()

    def clear_instructions(self):
        self._clear_field(self.INSTRUCTIONS_TEXTAREA)

    def clear_instructions_input(self):
        self.clear_instructions()

    def clear_inputs(self):
        self.clear_topic()
        self.clear_instructions()

    # =========================
    # Input
    # =========================
    def enter_topic(self, text: str):
        element = self._clear_field(self.TOPIC_INPUT)
        element.send_keys(text)

    def enter_instructions(self, text: str):
        element = self._clear_field(self.INSTRUCTIONS_TEXTAREA)
        element.send_keys(text)

    # =========================
    # Value Getters
    # =========================
    def get_topic_value(self) -> str:
        el = self.wait.until(
            EC.presence_of_element_located(self.TOPIC_INPUT)
        )
        return el.get_attribute("value") or ""

    def get_instructions_value(self) -> str:
        el = self.wait.until(
            EC.presence_of_element_located(self.INSTRUCTIONS_TEXTAREA)
        )
        return el.get_attribute("value") or ""

    # =========================
    # Button State
    # =========================
    def is_regenerate_enabled(self) -> bool:
        button = self._get_regenerate_button()
        return button.is_enabled()

    def click_regenerate(self):
        button = self.wait.until(lambda driver: self._get_clickable_regenerate_button())
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button,
        )
        button.click()

    def click_regenerate_button(self):
        self.click_regenerate()

    def click_modal_regenerate_button(self):
        el = self.wait.until(
            EC.element_to_be_clickable(self.MODAL_REGENERATE_BUTTON)
        )
        el.click()

    def is_regenerate_modal_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.REGENERATE_MODAL)
            ).is_displayed()
        except TimeoutException:
            return False

    def wait_until_regenerate_button_disabled(self, wait):
        def is_disabled(driver):
            try:
                button = self._get_regenerate_button()
                return not button.is_enabled()
            except StaleElementReferenceException:
                return False

        wait.until(is_disabled)

    def wait_until_regenerate_button_enabled(self, wait):
        def is_enabled(driver):
            try:
                button = self._get_regenerate_button()
                return button.is_enabled()
            except StaleElementReferenceException:
                return False

        wait.until(is_enabled)

    def _get_regenerate_button(self):
        topic_input = self.wait.until(EC.presence_of_element_located(self.TOPIC_INPUT))
        form = self.driver.execute_script(
            "return arguments[0].closest('form');",
            topic_input,
        )
        if form is not None:
            for button in form.find_elements(By.CSS_SELECTOR, "button[type='submit']"):
                if button.is_displayed():
                    return button

        return self.wait.until(EC.presence_of_element_located(self.REGENERATE_BUTTON))

    def _get_clickable_regenerate_button(self):
        button = self._get_regenerate_button()
        if button.is_displayed() and button.is_enabled():
            return button
        return False

    # =========================
    # Stop
    # =========================
    def click_stop_button(self):
        self.wait.until(EC.element_to_be_clickable(self.STOP_BUTTON)).click()

    def get_stop_message_text(self) -> str:
        element = self.wait.until(EC.visibility_of_element_located(self.STOP_MESSAGE))
        return element.text.strip()

    # =========================
    # Result
    # =========================
    def is_result_panel_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.RESULT_PANEL)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_result_success_message_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.RESULT_SUCCESS_MESSAGE)
            ).is_displayed()
        except TimeoutException:
            return False

    def is_result_download_button_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.RESULT_DOWNLOAD_BUTTON)
            ).is_displayed()
        except TimeoutException:
            return False

    def click_download_button(self):
        button = self.wait.until(
            EC.element_to_be_clickable(self.RESULT_DOWNLOAD_BUTTON)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button,
        )
        button.click()
        self.wait.until(EC.visibility_of_element_located(self.DOWNLOAD_MENU))

    def click_markdown_download_option(self):
        option = self.wait.until(
            EC.element_to_be_clickable(self.MARKDOWN_DOWNLOAD_OPTION)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            option,
        )
        option.click()

    def get_result_markdown_text(self) -> str:
        try:
            element = self.wait.until(
                EC.visibility_of_element_located(self.RESULT_MARKDOWN)
            )
            return element.text.strip()
        except TimeoutException:
            return ""

    # =========================
    # Error Messages
    # =========================
    def _get_field_error_element(self, field_locator):
        field = self.wait.until(
            EC.presence_of_element_located(field_locator)
        )

        field_has_error = field.get_attribute("aria-invalid") == "true"
        described_by = field.get_attribute("aria-describedby") or ""
        for helper_id in described_by.split():
            try:
                helper = self.driver.find_element(By.ID, helper_id)
                helper_class = helper.get_attribute("class") or ""
                if helper.is_displayed() and (field_has_error or "Mui-error" in helper_class):
                    return helper
            except NoSuchElementException:
                continue

        form_control = self.driver.execute_script(
            "return arguments[0].closest('.MuiFormControl-root');",
            field,
        )
        assert form_control is not None, "입력 필드의 에러 메시지 영역을 찾지 못했습니다."

        helper_texts = form_control.find_elements(
            By.CSS_SELECTOR,
            ".MuiFormHelperText-root.Mui-error",
        )
        for helper in helper_texts:
            if helper.is_displayed():
                return helper

        raise AssertionError("표시된 에러 메시지를 찾지 못했습니다.")

    def get_topic_error(self):
        el = self._get_field_error_element(self.TOPIC_INPUT)
        return el.text

    def get_topic_error_text(self):
        try:
            return self.get_topic_error().strip()
        except AssertionError:
            return ""

    def get_instructions_error(self):
        el = self._get_field_error_element(self.INSTRUCTIONS_TEXTAREA)
        return el.text

    def get_instructions_error_text(self):
        try:
            return self.get_instructions_error().strip()
        except AssertionError:
            return ""

    def get_error_message(self):
        errors = []
        for locator in (self.TOPIC_INPUT, self.INSTRUCTIONS_TEXTAREA):
            try:
                errors.append(self._get_field_error_element(locator).text)
            except AssertionError:
                continue

        return "\n".join(error for error in errors if error)
