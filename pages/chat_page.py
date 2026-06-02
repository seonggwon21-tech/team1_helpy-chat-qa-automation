"""
헬피챗 메인 채팅 화면의 UI 요소와 액션을 정의한 Page Object Model 클래스.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from .base_page import BasePage


class ChatPage(BasePage):
    """헬피챗 메시지 전송 및 응답 확인 클래스"""

    # 채팅 관련 Locators
    CHAT_INPUT      = (By.CSS_SELECTOR, "textarea[name='input']")
    SEND_BUTTON     = (By.CSS_SELECTOR, "button:has(svg[data-testid='arrow-upIcon'])")
    NEW_CHAT_BUTTON = (By.XPATH, "//a[contains(@href, 'ai-helpy-chat') and .//span[text()='새 대화']]")  # 텍스트 조건 필요 — CSS 변환 불가

    # AI 응답 관련 Locators
    AI_MESSAGE_CONTENT    = (By.CSS_SELECTOR, "div.elice-aichat__markdown[data-status='complete']")
    CHAT_MESSAGE_ELEMENTS = (By.CSS_SELECTOR, "div.elice-aichat__markdown")

    # + 버튼 및 하위 메뉴 Locators (TC-012~016)
    PLUS_BUTTON       = (By.CSS_SELECTOR, "button:has([data-testid='plusIcon'])")
    PLUS_MENU_POPOVER = (By.CSS_SELECTOR, "div.MuiPopover-root.MuiMenu-root")
    MENU_FILE_UPLOAD  = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='paperclipIcon'])")
    MENU_IMAGE_CREATE = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='imageIcon'])")
    MENU_PPT_CREATE   = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='presentation-screenIcon'])")
    MENU_WEB_SEARCH   = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='magnifying-glassIcon'])")

    # 파일 업로드 Locators (TC-013)
    FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    FILE_CHIP  = (By.XPATH, "//*[contains(text(),'test_upload') or contains(@title,'test_upload') or contains(@aria-label,'test_upload') or contains(@data-name,'test_upload')]")  # 텍스트 조건 필요 — CSS 변환 불가

    # 이미지 응답 Locators (TC-014)
    IMAGE_IN_RESPONSE     = (By.CSS_SELECTOR, "div.elice-aichat__markdown img")
    RESPONSE_DOWNLOAD_BTN = (By.CSS_SELECTOR, "div[data-variant='assistant'] button:has(svg[data-testid='downloadIcon'])")

    # PPT 결과 Locators (TC-015)
    PPT_RESULT       = (By.XPATH, "//button[contains(., '생성 결과 받기') or contains(., '생성 결과 다운받기')]")  # 버튼 텍스트 기반 — CSS 변환 불가
    PPT_DOWNLOAD_BTN = PPT_RESULT
    PPT_MODE_CHIP    = (By.XPATH, "//*[normalize-space(text())='PPT 생성']")                                      # 텍스트 일치 조건 — CSS 변환 불가

    # LNB 항목 조작 Locators (TC-019~021)
    # LNB_CHAT_ITEMS 는 BasePage에서 상속
    LNB_MORE_BUTTON    = (By.CSS_SELECTOR, "button:has([data-testid='ellipsis-verticalIcon'])")
    LNB_DELETE_BUTTON  = (By.CSS_SELECTOR, "li[role='menuitem']:has([data-testid='trashIcon'])")
    CONFIRM_DELETE_BTN = (By.CSS_SELECTOR, "div.MuiDialogActions-root button.MuiButton-colorError")

    # -----------------------------------------------------------------------
    # 입력창 / 전송 버튼
    # -----------------------------------------------------------------------

    def get_input_value(self):
        """입력창의 현재 value 속성을 반환합니다."""
        return self.wait_for_visible(self.CHAT_INPUT).get_attribute("value")

    def is_send_button_disabled(self):
        """전송 버튼의 disabled 속성 여부를 반환합니다."""
        btn = self.wait.until(EC.presence_of_element_located(self.SEND_BUTTON))
        return btn.get_attribute("disabled") is not None

    def send_message(self, message):
        """텍스트 영역에 메시지를 입력하고 전송 버튼을 클릭합니다."""
        self.enter_text(self.CHAT_INPUT, message)
        self.click(self.SEND_BUTTON)

    # -----------------------------------------------------------------------
    # 새 대화 / LNB
    # -----------------------------------------------------------------------

    def go_to_new_chat(self):
        """새 대화 버튼을 클릭하고 URL이 변경될 때까지 대기합니다."""
        current_url = self.driver.current_url
        self.click(self.NEW_CHAT_BUTTON)
        self.wait.until(EC.url_changes(current_url))

    def wait_for_lnb_loaded(self, timeout=30):
        """LNB 대화 목록이 완전히 로드될 때까지 대기합니다 (항목 수 안정화 기준)."""
        self.wait.until(EC.presence_of_element_located(self.LNB_CHAT_ITEMS))

        # 항목 수가 연속 2회 동일할 때까지 대기 (브라우저별 로딩 속도 차이 대응)
        prev_count = -1
        for _ in range(20):
            try:
                count = len(self.driver.find_elements(*self.LNB_CHAT_ITEMS))
                if count == prev_count:
                    return
                prev_count = count
            except StaleElementReferenceException:
                pass
            time.sleep(0.5)

    def get_lnb_items(self):
        """현재 LNB 대화 목록 요소를 리스트로 반환합니다."""
        return self.driver.find_elements(*self.LNB_CHAT_ITEMS)

    def get_lnb_hrefs(self):
        """현재 LNB 대화 목록의 href 집합(set)을 반환합니다."""
        for _ in range(3):
            try:
                return {el.get_attribute("href") for el in self.get_lnb_items()}
            except StaleElementReferenceException:
                time.sleep(0.3)
        return {el.get_attribute("href") for el in self.get_lnb_items()}

    def wait_for_new_lnb_item(self, initial_hrefs, timeout=60):
        """
        initial_hrefs에 없는 신규 LNB 항목이 나타날 때까지 대기합니다.
        StaleElementReferenceException을 내부에서 방어합니다.

        Returns:
            신규 항목 href 집합 (set)
        """
        lnb_wait = WebDriverWait(self.driver, timeout)

        def new_item_appeared(d):
            try:
                current = {el.get_attribute("href") for el in d.find_elements(*self.LNB_CHAT_ITEMS)}
                return current - initial_hrefs or False
            except StaleElementReferenceException:
                return False

        return lnb_wait.until(new_item_appeared)

    def delete_lnb_item(self, item_element):
        """LNB 항목 위로 hover 후 더보기 → 삭제 → 삭제 확인 순서로 항목을 삭제합니다."""
        self.hover(item_element)
        self.click(self.LNB_MORE_BUTTON)
        self.click(self.LNB_DELETE_BUTTON)
        self.click(self.CONFIRM_DELETE_BTN)

    def wait_for_lnb_item_removed(self, target_href):
        """
        특정 href를 가진 LNB 항목이 목록에서 사라질 때까지 대기합니다.
        StaleElementReferenceException을 내부에서 방어합니다.
        """
        def item_was_deleted(d):
            try:
                return not any(
                    el.get_attribute("href") == target_href
                    for el in d.find_elements(*self.LNB_CHAT_ITEMS)
                )
            except StaleElementReferenceException:
                return False

        self.wait.until(item_was_deleted)

    # -----------------------------------------------------------------------
    # + 버튼 메뉴
    # -----------------------------------------------------------------------

    def open_plus_menu(self):
        """입력창 옆 + 버튼을 클릭해 하위 메뉴를 펼칩니다."""
        self.click(self.PLUS_BUTTON)

    def select_plus_menu_item(self, menu_locator):
        """+ 버튼 클릭 후 지정된 메뉴 항목을 선택합니다."""
        self.open_plus_menu()
        self.click(menu_locator)
        self.wait_until_invisible(self.PLUS_MENU_POPOVER)

    # -----------------------------------------------------------------------
    # 마우스 동작
    # -----------------------------------------------------------------------

    def hover(self, element):
        """지정 요소 위로 마우스 포인터를 이동합니다 (hover overlay 활성화 등)."""
        ActionChains(self.driver).move_to_element(element).perform()

    # -----------------------------------------------------------------------
    # AI 응답 대기
    # -----------------------------------------------------------------------

    def wait_for_ai_response(self, timeout=30):
        """
        AI의 응답이 화면에 완전히 노출될 때까지 대기하고, 해당 텍스트를 반환합니다.
        스트리밍 생성이 완료된(data-status='complete') 메시지를 타겟팅합니다.

        Args:
            timeout: 최대 대기 시간(초). 기본값 30초.
                     이미지/PPT 등 오래 걸리는 응답은 호출 측에서 늘려서 사용.
        """
        ai_wait = WebDriverWait(self.driver, timeout)
        response_element = ai_wait.until(EC.visibility_of_element_located(self.AI_MESSAGE_CONTENT))
        return response_element.text

    def wait_for_image_response(self, timeout=120):
        """
        이미지 생성 응답의 <img> 요소가 노출될 때까지 대기하고 element를 반환합니다.

        Args:
            timeout: 최대 대기 시간(초). 기본값 120초.
        """
        image_wait = WebDriverWait(self.driver, timeout)
        return image_wait.until(EC.visibility_of_element_located(self.IMAGE_IN_RESPONSE))

    def wait_for_ppt_result(self, timeout=600):
        """
        PPT 생성 결과 다운로드 버튼이 노출되고 클릭 가능해질 때까지 대기하고 element를 반환합니다.

        Args:
            timeout: 최대 대기 시간(초). 기본값 600초.
        """
        ppt_wait = WebDriverWait(self.driver, timeout)
        ppt_wait.until(EC.visibility_of_element_located(self.PPT_RESULT))
        return ppt_wait.until(EC.element_to_be_clickable(self.PPT_DOWNLOAD_BTN))

    # -----------------------------------------------------------------------
    # 다운로드
    # -----------------------------------------------------------------------

    @staticmethod
    def wait_for_download(download_dir, suffix=None, timeout=60):
        """
        다운로드 완료까지 폴링 대기 후 완료된 파일 목록을 반환합니다.
        파일 시스템 상태는 Selenium 명시적 대기로 감지 불가 — 1초 간격 폴링 사용.

        Args:
            download_dir: 다운로드 경로 (Path 객체)
            suffix: 확인할 파일 확장자 (예: ".pptx"). None이면 모든 파일 대상.
            timeout: 최대 대기 시간(초). 기본값 60초.

        Returns:
            다운로드된 파일 목록 (list). 타임아웃 시 빈 리스트 반환.
        """
        for _ in range(timeout):
            files = [
                f for f in download_dir.iterdir()
                if suffix is None or f.suffix == suffix
            ]
            downloading = any(
                f.name.endswith((".crdownload", ".part"))  # Chrome: .crdownload / Firefox: .part
                for f in download_dir.iterdir()
            )
            if files and not downloading:
                return files
            time.sleep(1)  # 파일 시스템 상태 — Selenium 명시적 대기 감지 불가, 1초 간격 폴링
        return []
