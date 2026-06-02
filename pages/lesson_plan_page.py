"""
lesson plan page object.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage


class LessonplanPage(BasePage):
    """수업지도안 도구 Page Object"""

    MENU_TOOLS = (By.CSS_SELECTOR, "a[href='/ai-helpy-chat/tools']")
    TOOL_LESSON_PLAN = (
        By.CSS_SELECTOR,
        "a[href='/ai-helpy-chat/tools/b641b251-ecad-4cf7-8375-4b87efa281e9']"
    )

    SCHOOL_LEVEL_DROPDOWN = (
        By.XPATH,
        "//input[@name='school_level']/preceding-sibling::div[@role='combobox']"
    )
    GRADE_DROPDOWN = (
        By.XPATH,
        "//input[@name='school_year']/preceding-sibling::div[@role='combobox']"
    )
    SUBJECT_DROPDOWN = (
        By.XPATH,
        "//input[@name='subject']/preceding-sibling::div[@role='combobox']"
    )
    TOPIC_INPUT = (By.CSS_SELECTOR, "input[name='topic']")
    LESSON_NUMBER_DROPDOWN = (
        By.XPATH,
        "//input[@name='lesson_number']/preceding-sibling::div[@role='combobox']"
    )

    GENERATE_BUTTON = (
        By.CSS_SELECTOR,
        "button[form='tool-factory-syllabus_generation'][type='submit']"
    )
    GENERATE_CONFIRM_MODAL = (By.CSS_SELECTOR, "div[role='dialog']")
    MODAL_GENERATE_BUTTON = (
        By.CSS_SELECTOR,
        "div[role='dialog'] "
        "button[form='tool-factory-syllabus_generation'][type='submit']"
    )

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def navigate_to_tool(self):
        """도구 메뉴에서 수업지도안 페이지로 이동합니다."""
        self.click(self.MENU_TOOLS)
        self.click(self.TOOL_LESSON_PLAN)

    def select_mui_dropdown(self, dropdown_locator: tuple, option_text: str):
        """MUI Select 옵션을 텍스트 또는 data-value 기준으로 선택합니다."""
        option_literal = self.xpath_literal(option_text)
        option_locator = (
            By.XPATH,
            (
                f"//li[@role='option' and @data-value={option_literal}]"
                f" | //li[@role='option' and normalize-space()={option_literal}]"
                f" | //*[@role='option' and normalize-space()={option_literal}]"
            )
        )

        self.click(dropdown_locator)
        self.click(option_locator)
        self.wait_until_invisible((By.CSS_SELECTOR, "ul[role='listbox']"))

    def is_generate_confirm_modal_visible(self) -> bool:
        """생성/다시 생성 확인 모달 표시 여부를 반환합니다."""
        try:
            self.wait.until(
                EC.visibility_of_element_located(self.GENERATE_CONFIRM_MODAL)
            )
            return True
        except TimeoutException:
            return False

    def click_modal_generate_button(self):
        """확인 모달 내부의 생성/다시 생성 버튼을 클릭합니다."""
        self.click(self.MODAL_GENERATE_BUTTON)
        self.wait_until_invisible(self.GENERATE_CONFIRM_MODAL)
