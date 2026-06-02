"""
모델 변경 테스트
"""

import logging

import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from pages.chat_page import ChatPage
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class TestModelChange:
    """모델 설정 후 변경 및 대화 검증"""

    TOTAL_STEPS = 6
    TARGET_MODEL_NAME = "GPT-5.1"
    QUESTION = "오늘의 날씨는 어때?"

    MODEL_BUTTON = (By.XPATH, "//button[.//p[contains(@class, 'MuiTypography-noWrap')]]")
    MODEL_DROPDOWN = (By.XPATH, "//ul[@role='menu']")
    MODEL_LIST_ITEMS = (
        By.XPATH,
        "//li[contains(@class, 'MuiListItem-root') "
        "and .//span[contains(@class, 'MuiListItemText-primary')]]"
    )
    MODEL_SETTINGS_BTN = (
        By.CSS_SELECTOR,
        "a[role='menuitem'][href='/ai-helpy-chat/admin/models']"
    )
    MODEL_SETTINGS_TITLE = (
        By.CSS_SELECTOR,
        "a[href='/ai-helpy-chat/admin/models'][aria-current='page']"
    )

    @pytest.mark.ui
    def test_enable_model_in_settings_change_model_and_chat(self, logged_in_driver):
        driver = logged_in_driver
        chat_page = ChatPage(driver)
        wait = WebDriverWait(driver, 10)
        long_wait = WebDriverWait(driver, 60)
        model_name = self.TARGET_MODEL_NAME

        logger.info("[START] 모델 변경 및 AI 대화 테스트 시작")

        with chat_page.step("모델 드롭다운 열기", step_no=1, total_steps=self.TOTAL_STEPS):
            self._open_model_dropdown(chat_page, wait)

        with chat_page.step("모델 설정 페이지 이동", step_no=2, total_steps=self.TOTAL_STEPS):
            self._go_to_model_settings(driver, chat_page, wait)

        with chat_page.step(f"{model_name} 모델 활성화", step_no=3, total_steps=self.TOTAL_STEPS):
            self._ensure_model_enabled(driver, chat_page, wait, model_name)

        with chat_page.step("새 대화 화면 이동", step_no=4, total_steps=self.TOTAL_STEPS):
            self._open_new_chat(driver, chat_page, wait)

        with chat_page.step(f"{model_name} 모델 선택", step_no=5, total_steps=self.TOTAL_STEPS):
            self._select_model(chat_page, wait, model_name)

        with chat_page.step("AI 질문 전송 및 응답 확인", step_no=6, total_steps=self.TOTAL_STEPS):
            previous_count = len(self._visible_complete_ai_messages(driver, chat_page))
            chat_page.send_message(self.QUESTION)
            logger.info(f"질문 전송 완료: {self.QUESTION}")
            logger.info(f"질문 전 완료된 AI 응답 수: {previous_count}")

            try:
                response_el = long_wait.until(
                    lambda d: self._new_complete_ai_message(d, chat_page, previous_count)
                )
            except TimeoutException:
                pytest.fail("AI 응답이 제한 시간 내 노출되지 않았습니다.")

            response_text = response_el.text.strip()
            assert response_text, "AI 응답 텍스트가 비어 있습니다."
            logger.info(f"AI 응답 확인 완료: {response_text}")

            chat_page.clear_step_overlay()
            logger.info("[PASS] 모델 변경 및 AI 대화 테스트 성공")

    def _open_model_dropdown(self, chat_page, wait):
        try:
            current_btn = wait.until(EC.element_to_be_clickable(self.MODEL_BUTTON))
            logger.info(f"현재 선택된 모델: {current_btn.text.strip()}")
            chat_page.click(self.MODEL_BUTTON)
            wait.until(EC.visibility_of_element_located(self.MODEL_DROPDOWN))
        except TimeoutException:
            pytest.fail("모델 버튼 또는 드롭다운이 노출되지 않았습니다.")

    def _go_to_model_settings(self, driver, chat_page, wait):
        try:
            settings_btn = wait.until(EC.presence_of_element_located(self.MODEL_SETTINGS_BTN))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", settings_btn)
            chat_page.click(self.MODEL_SETTINGS_BTN)
            wait.until(EC.url_contains("/ai-helpy-chat/admin/models"))
            wait.until(EC.visibility_of_element_located(self.MODEL_SETTINGS_TITLE))
        except TimeoutException:
            pytest.fail("모델 설정 페이지 이동 실패 또는 탭이 활성화되지 않았습니다.")

    def _ensure_model_enabled(self, driver, chat_page, wait, model_name):
        try:
            items = wait.until(EC.visibility_of_any_elements_located(self.MODEL_LIST_ITEMS))
        except TimeoutException:
            pytest.fail("모델 설정 페이지에서 AI 모델 목록이 노출되지 않았습니다.")

        try:
            target_item = wait.until(EC.visibility_of_element_located(self._model_item(model_name)))
        except TimeoutException:
            available_models = [item.text.strip() for item in items if item.text.strip()]
            pytest.fail(f"대상 모델을 찾을 수 없습니다. model={model_name}, available={available_models}")

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target_item)
        checkbox = wait.until(EC.presence_of_element_located(self._model_checkbox(model_name)))

        if checkbox.is_selected():
            logger.info(f"대상 모델은 이미 활성화되어 있습니다: {model_name}")
            return

        try:
            chat_page.click(self._model_switch(model_name))
            wait.until(lambda d: d.find_element(*self._model_checkbox(model_name)).is_selected())
        except TimeoutException:
            pytest.fail(f"대상 모델 토글 활성화 실패. model={model_name}")

    def _open_new_chat(self, driver, chat_page, wait):
        previous_url = driver.current_url
        try:
            chat_page.click(chat_page.NEW_CHAT_BUTTON)
            wait.until(
                lambda d: d.current_url != previous_url
                or d.find_element(*chat_page.CHAT_INPUT).is_displayed()
            )
            wait.until(EC.visibility_of_element_located(chat_page.CHAT_INPUT))
        except TimeoutException:
            pytest.fail("'새 대화' 클릭 후 새 대화 화면으로 이동하지 않았습니다.")

    def _select_model(self, chat_page, wait, model_name):
        try:
            chat_page.click(self.MODEL_BUTTON)
            wait.until(EC.visibility_of_element_located(self.MODEL_DROPDOWN))
            chat_page.click(self._model_menu_item(model_name))
            wait.until(lambda d: model_name in d.find_element(*self.MODEL_BUTTON).text)
        except TimeoutException:
            pytest.fail(f"모델 선택 실패 또는 버튼에 모델명이 반영되지 않았습니다. model={model_name}")

        changed = chat_page.driver.find_element(*self.MODEL_BUTTON).text.strip()
        assert model_name in changed, f"모델 변경 미반영. expected={model_name}, actual={changed}"
        logger.info(f"AI 모델 변경 확인 완료: {changed}")

    def _model_item(self, model_name):
        name = BasePage.xpath_literal(model_name)
        return (
            By.XPATH,
            "//li[contains(@class,'MuiListItem-root') "
            "and .//span[contains(@class,'MuiListItemText-primary') "
            f"and normalize-space()={name}]]"
        )

    def _model_checkbox(self, model_name):
        return (By.XPATH, f"{self._model_item(model_name)[1]}//input[@type='checkbox']")

    def _model_switch(self, model_name):
        return (
            By.XPATH,
            f"{self._model_item(model_name)[1]}//span[contains(@class,'MuiSwitch-switchBase')]"
        )

    def _model_menu_item(self, model_name):
        name = BasePage.xpath_literal(model_name)
        return (
            By.XPATH,
            f"//li[@role='menuitem' and (normalize-space()={name} or .//*[normalize-space()={name}])]"
        )

    @staticmethod
    def _visible_complete_ai_messages(driver, chat_page):
        messages = []
        for element in driver.find_elements(*chat_page.AI_MESSAGE_CONTENT):
            try:
                if element.is_displayed() and element.text.strip():
                    messages.append(element)
            except StaleElementReferenceException:
                continue
        return messages

    def _new_complete_ai_message(self, driver, chat_page, previous_count):
        messages = self._visible_complete_ai_messages(driver, chat_page)
        if len(messages) > previous_count:
            return messages[-1]
        return False
