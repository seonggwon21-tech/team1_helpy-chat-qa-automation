from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from .tool_page import ToolPage


class QuizPage(ToolPage):
    QUIZ_GENERATE_MENU = (
        By.CSS_SELECTOR,
        "a[href='/ai-helpy-chat/tools/98b00265-c2fb-43cc-8785-5330e18f8c28']",
    )

    QUIZ_TYPE_DROPDOWN = (
        By.XPATH,
        "//div[@role='combobox' and contains(@id,'option_type')]",
    )
    QUIZ_DIFFICULTY_DROPDOWN = (
        By.XPATH,
        "//div[@role='combobox' and contains(@id,'difficulty')]",
    )
    QUIZ_TYPE_SELECTED_VALUE = (
        By.CSS_SELECTOR,
        "div[role='combobox'][id='mui-component-select-quiz_configs.0.option_type']",
    )
    QUIZ_DIFFICULTY_SELECTED_VALUE = (
        By.CSS_SELECTOR,
        "div[role='combobox'][id='mui-component-select-quiz_configs.0.difficulty']",
    )
    DROPDOWN_LIST = (By.CSS_SELECTOR, "ul[role='listbox']")

    TOPIC_INPUT = (By.CSS_SELECTOR, "textarea[name='content']")

    QUIZ_SUBMIT_BUTTON = (
        By.CSS_SELECTOR,
        "button[form='tool-factory-create_quiz_from_context']",
    )
    MODAL_REGENERATE_BUTTON = (
        By.CSS_SELECTOR,
        "[role='dialog'] button[form='tool-factory-create_quiz_from_context']",
    )
    REGENERATE_MODAL = (By.CSS_SELECTOR, "[role='dialog']")

    STOP_BUTTON = (
        By.CSS_SELECTOR,
        "button:has(svg[data-testid='stopIcon'])",
    )
    STOP_MESSAGE = (By.CSS_SELECTOR, ".MuiAlertTitle-root")

    ERROR_MESSAGE = (
        By.CSS_SELECTOR,
        ".MuiFormHelperText-root.Mui-error",
    )
    OUTPUT_PANEL = (
        By.CSS_SELECTOR,
        "div[role='tabpanel'][data-panel='output'][aria-hidden='false']",
    )
    RESULT_SUCCESS_MESSAGE = (
        By.XPATH,
        "//div[@role='tabpanel' and @data-panel='output']"
        "//*[contains(text(), '입력하신 내용 기반으로 퀴즈를 생성했습니다.')]",
    )
    RESULT_QUESTION = (
        By.CSS_SELECTOR,
        "div[role='tabpanel'][data-panel='output'] li .elice-aichat__markdown",
    )
    RESULT_ANSWER = (
        By.CSS_SELECTOR,
        "div[role='tabpanel'][data-panel='output'] [data-answer='true']",
    )

    def navigate_to_quiz_page(self):
        self.setup_tool_tab()
        self.click(self.QUIZ_GENERATE_MENU)
        self.wait.until(
            lambda driver: "98b00265-c2fb-43cc-8785-5330e18f8c28"
            in driver.current_url
        )

    def verify_quiz_page_url(self):
        current_url = self.driver.current_url
        assert "98b00265-c2fb-43cc-8785-5330e18f8c28" in current_url, (
            f"퀴즈 생성 페이지 URL이 아닙니다. actual={current_url}"
        )

    def click_quiz_type_dropdown(self):
        dropdown = self.wait.until(
            EC.element_to_be_clickable(self.QUIZ_TYPE_DROPDOWN)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            dropdown,
        )
        dropdown.click()

    def click_quiz_difficulty_dropdown(self):
        dropdown = self.wait.until(
            EC.element_to_be_clickable(self.QUIZ_DIFFICULTY_DROPDOWN)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            dropdown,
        )
        dropdown.click()

    def is_dropdown_displayed(self) -> bool:
        dropdown = self.wait.until(EC.visibility_of_element_located(self.DROPDOWN_LIST))
        return dropdown.is_displayed()

    def get_quiz_type_selected_text(self) -> str:
        element = self.wait.until(
            EC.visibility_of_element_located(self.QUIZ_TYPE_SELECTED_VALUE)
        )
        return element.text.strip()

    def get_quiz_difficulty_selected_text(self) -> str:
        element = self.wait.until(
            EC.visibility_of_element_located(self.QUIZ_DIFFICULTY_SELECTED_VALUE)
        )
        return element.text.strip()

    def is_dropdown_option_displayed(self, option_value: str) -> bool:
        option = self.wait.until(
            EC.visibility_of_element_located(self._dropdown_option(option_value))
        )
        return option.is_displayed()

    def select_dropdown_option_only(self, option_value: str):
        option = self.wait.until(
            EC.element_to_be_clickable(self._dropdown_option(option_value))
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            option,
        )
        option.click()

    def select_mui_dropdown(self, dropdown_locator: tuple, option_value: str):
        dropdown = self.wait.until(EC.element_to_be_clickable(dropdown_locator))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            dropdown,
        )
        dropdown.click()

        self.select_dropdown_option_only(option_value)
        self.wait_until_invisible(self.DROPDOWN_LIST)

    def _dropdown_option(self, option_value: str):
        return (
            By.XPATH,
            f"//li[@role='option' and @data-value='{option_value}']",
        )

    def enter_topic(self, topic: str):
        element = self.wait.until(EC.visibility_of_element_located(self.TOPIC_INPUT))
        element.send_keys(topic)

    def clear_topic_input(self):
        element = self.wait.until(EC.visibility_of_element_located(self.TOPIC_INPUT))
        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        self.wait.until(lambda driver: (element.get_attribute("value") or "") == "")

    def blur_active_element(self):
        self.driver.execute_script("document.activeElement && document.activeElement.blur();")

    def get_topic_value(self) -> str:
        element = self.wait.until(EC.presence_of_element_located(self.TOPIC_INPUT))
        return element.get_attribute("value") or ""

    def click_quiz_submit_button(self):
        button = self.wait.until(lambda driver: self._get_clickable_quiz_submit_button())
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button,
        )
        button.click()

    def click_modal_regenerate_button(self):
        button = self.wait.until(
            EC.element_to_be_clickable(self.MODAL_REGENERATE_BUTTON)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            button,
        )
        button.click()

    def is_quiz_submit_button_enabled(self) -> bool:
        button = self._get_quiz_submit_button()
        return button.is_enabled()

    def is_quiz_submit_button_disabled(self) -> bool:
        return not self.is_quiz_submit_button_enabled()

    def wait_until_submit_button_disabled(self, wait):
        def is_disabled(driver):
            try:
                button = self._get_quiz_submit_button()
                return not button.is_enabled()
            except StaleElementReferenceException:
                return False

        wait.until(is_disabled)

    def wait_until_submit_button_enabled(self, wait):
        def is_enabled(driver):
            try:
                button = self._get_quiz_submit_button()
                return button.is_enabled()
            except StaleElementReferenceException:
                return False

        wait.until(is_enabled)

    def _get_quiz_submit_button(self):
        topic_input = self.wait.until(EC.presence_of_element_located(self.TOPIC_INPUT))
        form = self.driver.execute_script(
            "return arguments[0].closest('form');",
            topic_input,
        )
        if form is not None:
            for button in form.find_elements(By.CSS_SELECTOR, "button[type='submit']"):
                if button.is_displayed():
                    return button

        return self.wait.until(EC.presence_of_element_located(self.QUIZ_SUBMIT_BUTTON))

    def _get_clickable_quiz_submit_button(self):
        button = self._get_quiz_submit_button()
        if button.is_displayed() and button.is_enabled():
            return button
        return False

    def is_regenerate_modal_visible(self) -> bool:
        return self.wait.until(
            EC.visibility_of_element_located(self.REGENERATE_MODAL)
        ).is_displayed()

    def click_stop_button(self):
        self.wait.until(EC.element_to_be_clickable(self.STOP_BUTTON)).click()

    def get_stop_message_text(self) -> str:
        element = self.wait.until(EC.visibility_of_element_located(self.STOP_MESSAGE))
        return element.text.strip()

    def get_error_message_text(self) -> str:
        element = self.wait.until(EC.visibility_of_element_located(self.ERROR_MESSAGE))
        return element.text.strip()

    def has_visible_error_message(self) -> bool:
        return any(
            element.is_displayed()
            for element in self.driver.find_elements(*self.ERROR_MESSAGE)
        )

    def is_quiz_result_visible(self) -> bool:
        panel = self.wait.until(EC.visibility_of_element_located(self.OUTPUT_PANEL))
        success_message = self.wait.until(
            EC.visibility_of_element_located(self.RESULT_SUCCESS_MESSAGE)
        )
        question = self.wait.until(EC.visibility_of_element_located(self.RESULT_QUESTION))
        answer = self.wait.until(EC.visibility_of_element_located(self.RESULT_ANSWER))

        return all(
            (
                panel.is_displayed(),
                success_message.is_displayed(),
                bool(question.text.strip()),
                answer.is_displayed(),
            )
        )
