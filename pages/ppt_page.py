"""
ToolPage를 상속받아 도구 메뉴의 하위 기능인
'PPT 생성' 페이지 이동 및 입력 제어를 담당하는 클래스.
"""

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from .tool_page import ToolPage


class PptPage(ToolPage):

    # =========================
    # Locators
    # =========================
    PPT_GENERATE_MENU = (
        By.CSS_SELECTOR,
        "a[href='/ai-helpy-chat/tools/b11ea464-c1bc-45e0-8140-85e38f5ec1e1']",
    )
    PPT_TOOL_PATH = "/ai-helpy-chat/tools/b11ea464-c1bc-45e0-8140-85e38f5ec1e1"

    TOPIC_INPUT = (By.CSS_SELECTOR, "input[name='topic']")
    INSTRUCTIONS_TEXTAREA = (By.CSS_SELECTOR, "textarea[name='instructions']")
    SLIDES_COUNT_INPUT = (By.CSS_SELECTOR, "input[name='slides_count']")
    SECTION_COUNT_INPUT = (By.CSS_SELECTOR, "input[name='section_count']")

    GENERATE_BUTTON = (
        By.CSS_SELECTOR,
        "button[form='tool-factory-create_pptx'][type='submit']",
    )
    MODAL_GENERATE_BUTTON = (
        By.CSS_SELECTOR,
        "[role='dialog'] button[form='tool-factory-create_pptx'][type='submit']",
    )
    STOP_BUTTON = (By.CSS_SELECTOR, "button:has(svg[data-testid='stopIcon'])")
    STOP_MESSAGE = (By.CSS_SELECTOR, ".MuiAlertTitle-root")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".MuiFormHelperText-root.Mui-error")
    DOWNLOAD_BUTTON = (
        By.CSS_SELECTOR,
        "div[role='tabpanel'][data-panel='output'] "
        "a[target='_blank'][rel='noopener noreferrer'][href*='blob.core.windows.net']",
    )

    # =========================
    # Navigation
    # =========================
    def navigate(self):
        self.setup_tool_tab()
        try:
            self.click(self.PPT_GENERATE_MENU)
        except TimeoutException:
            origin = self.driver.execute_script("return window.location.origin;")
            self.driver.get(f"{origin}{self.PPT_TOOL_PATH}")
        self.wait.until(
            lambda driver: "b11ea464-c1bc-45e0-8140-85e38f5ec1e1"
            in driver.current_url
        )

    def navigate_to_ppt_page(self):
        self.navigate()

    def verify_ppt_page_url(self):
        current_url = self.driver.current_url
        assert "b11ea464-c1bc-45e0-8140-85e38f5ec1e1" in current_url, (
            f"PPT 생성 페이지 URL이 아닙니다. actual={current_url}"
        )

    # =========================
    # Clear
    # =========================
    def _clear_field(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        self.wait.until(lambda driver: (element.get_attribute("value") or "") == "")
        return element

    def clear_topic(self):
        self._clear_field(self.TOPIC_INPUT)

    def clear_topic_input(self):
        self.clear_topic()

    def clear_instructions(self):
        self._clear_field(self.INSTRUCTIONS_TEXTAREA)

    def clear_instructions_input(self):
        self.clear_instructions()

    def clear_slides_count(self):
        self._clear_field(self.SLIDES_COUNT_INPUT)

    def clear_slides_count_input(self):
        self.clear_slides_count()

    def clear_section_count(self):
        self._clear_field(self.SECTION_COUNT_INPUT)

    def clear_section_count_input(self):
        self.clear_section_count()

    def clear_inputs(self):
        self.clear_topic()
        self.clear_instructions()
        self.clear_slides_count()
        self.clear_section_count()

    def clear_all_fields(self):
        self.clear_inputs()

    def blur_active_element(self):
        self.driver.execute_script("document.activeElement && document.activeElement.blur();")

    # =========================
    # Input
    # =========================
    def enter_topic(self, topic: str):
        element = self._clear_field(self.TOPIC_INPUT)
        element.send_keys(topic)

    def enter_instructions(self, instructions: str):
        element = self._clear_field(self.INSTRUCTIONS_TEXTAREA)
        element.send_keys(instructions)

    def enter_slides_count(self, count: str):
        element = self._clear_field(self.SLIDES_COUNT_INPUT)
        element.send_keys(count)

    def enter_section_count(self, count: str):
        element = self._clear_field(self.SECTION_COUNT_INPUT)
        element.send_keys(count)

    # =========================
    # Value Getters
    # =========================
    def get_topic_value(self) -> str:
        element = self.wait.until(EC.presence_of_element_located(self.TOPIC_INPUT))
        return element.get_attribute("value") or ""

    def get_instructions_value(self) -> str:
        element = self.wait.until(
            EC.presence_of_element_located(self.INSTRUCTIONS_TEXTAREA)
        )
        return element.get_attribute("value") or ""

    def get_slides_count_value(self) -> str:
        element = self.wait.until(
            EC.presence_of_element_located(self.SLIDES_COUNT_INPUT)
        )
        return element.get_attribute("value") or ""

    def get_section_count_value(self) -> str:
        element = self.wait.until(
            EC.presence_of_element_located(self.SECTION_COUNT_INPUT)
        )
        return element.get_attribute("value") or ""

    # =========================
    # Button State
    # =========================
    def is_generate_enabled(self) -> bool:
        return self.is_generate_button_enabled()

    def is_generate_button_enabled(self) -> bool:
        button = self._get_generate_button()
        return button.is_enabled()

    def is_generate_button_disabled(self) -> bool:
        return not self.is_generate_button_enabled()

    def click_generate_button(self):
        button = self.wait.until(lambda driver: self._get_clickable_generate_button())
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button,
        )
        button.click()

    def click_modal_generate_button(self):
        button = self.wait.until(lambda driver: self._get_clickable_modal_generate_button())
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button,
        )
        button.click()

    def click_stop_button(self):
        self.wait.until(EC.element_to_be_clickable(self.STOP_BUTTON)).click()

    def wait_until_generation_starts(self, wait):
        self.wait_until_generate_button_disabled(wait)

    def wait_until_generation_completes(self, wait):
        self.wait_until_generate_button_enabled(wait)

    def wait_until_generate_button_disabled(self, wait):
        def is_disabled(driver):
            try:
                button = self._get_generate_button()
                return not button.is_enabled()
            except StaleElementReferenceException:
                return False

        wait.until(is_disabled)

    def wait_until_generate_button_enabled(self, wait):
        def is_enabled(driver):
            try:
                button = self._get_generate_button()
                return button.is_enabled()
            except StaleElementReferenceException:
                return False

        wait.until(is_enabled)

    def _get_generate_button(self):
        topic_input = self.wait.until(EC.presence_of_element_located(self.TOPIC_INPUT))
        form = self.driver.execute_script(
            "return arguments[0].closest('form');",
            topic_input,
        )
        if form is not None:
            for button in form.find_elements(By.CSS_SELECTOR, "button[type='submit']"):
                if button.is_displayed():
                    return button

        return self.wait.until(EC.presence_of_element_located(self.GENERATE_BUTTON))

    def _get_clickable_generate_button(self):
        button = self._get_generate_button()
        if button.is_displayed() and button.is_enabled():
            return button
        return False

    def _get_clickable_modal_generate_button(self):
        button = self.driver.find_element(*self.MODAL_GENERATE_BUTTON)
        if button.is_displayed() and button.is_enabled():
            return button
        return False

    # =========================
    # Result
    # =========================
    def is_result_download_button_visible(self) -> bool:
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.DOWNLOAD_BUTTON)
            ).is_displayed()
        except TimeoutException:
            return False

    def click_download_button(self):
        button = self.wait.until(EC.element_to_be_clickable(self.DOWNLOAD_BUTTON))
        button.click()

    # =========================
    # Stop
    # =========================
    def get_stop_message_text(self) -> str:
        element = self.wait.until(EC.visibility_of_element_located(self.STOP_MESSAGE))
        return element.text.strip()

    # =========================
    # Error Messages
    # =========================
    def _get_field_error_element(self, field_locator):
        field = self.wait.until(EC.presence_of_element_located(field_locator))

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

        for helper in form_control.find_elements(By.CSS_SELECTOR, ".MuiFormHelperText-root.Mui-error"):
            if helper.is_displayed():
                return helper

        raise AssertionError("표시된 에러 메시지를 찾지 못했습니다.")

    def get_topic_error_text(self) -> str:
        try:
            return self._get_field_error_element(self.TOPIC_INPUT).text.strip()
        except AssertionError:
            return ""

    def get_instructions_error_text(self) -> str:
        try:
            return self._get_field_error_element(self.INSTRUCTIONS_TEXTAREA).text.strip()
        except AssertionError:
            return ""

    def get_slides_count_error_text(self) -> str:
        try:
            return self._get_field_error_element(self.SLIDES_COUNT_INPUT).text.strip()
        except AssertionError:
            return ""

    def get_section_count_error_text(self) -> str:
        try:
            return self._get_field_error_element(self.SECTION_COUNT_INPUT).text.strip()
        except AssertionError:
            return ""

    def get_error_message_text(self) -> str:
        element = self.wait.until(EC.visibility_of_element_located(self.ERROR_MESSAGE))
        return element.text.strip()
