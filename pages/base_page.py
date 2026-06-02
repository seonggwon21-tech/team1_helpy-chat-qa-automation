"""
모든 Page Object가 상속받는 최상위 부모 클래스.
공통 동작(클릭, 입력 등)과 명시적 대기를 래핑합니다.
"""

import time
import logging

from contextlib import contextmanager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)

logger = logging.getLogger(__name__)


class BasePage:
    """모든 페이지 객체의 부모 클래스"""

    # =======================================================================
    # LNB-메뉴 경로 추가
    # =======================================================================
    LNB_CHAT_ITEMS = (
        By.CSS_SELECTOR,
        "a[href*='/ai-helpy-chat/chats/']"
    )

    def __init__(self, driver):

        self.driver = driver

        # 명시적 대기(Explicit Wait)
        self.wait = WebDriverWait(driver, 10)

    # =======================================================================
    # Step Overlay UI
    # =======================================================================

    def show_step(
        self,
        message,
        step_no=None,
        total_steps=None
    ):
        """
        테스트 진행 단계를 브라우저 우측 상단 Overlay로 표시합니다.
        """

        title = message

        if (
            step_no is not None and
            total_steps is not None
        ):
            title = (
                f"[ STEP {step_no}/{total_steps} ]\n"
                f"{message}"
            )

        script = """
        let old = document.getElementById('test-step-overlay');

        if (old) {
            old.remove();
        }

        let div = document.createElement('div');

        div.id = 'test-step-overlay';

        div.innerText = arguments[0];

        div.style.position = 'fixed';
        div.style.top = '88px';
        div.style.right = '20px';

        div.style.zIndex = '999999';

        div.style.background = 'rgba(0, 0, 0, 0.85)';
        div.style.color = '#ffffff';

        div.style.padding = '16px 20px';

        div.style.fontSize = '16px';
        div.style.fontWeight = '600';
        div.style.lineHeight = '1.5';

        div.style.borderRadius = '12px';

        div.style.boxShadow =
            '0 4px 12px rgba(0,0,0,0.3)';

        div.style.whiteSpace = 'pre-line';

        div.style.pointerEvents = 'none';

        div.style.transition =
            'all 0.2s ease-in-out';

        div.style.maxWidth = '320px';

        document.body.appendChild(div);
        """

        self.driver.execute_script(script, title)

    def clear_step_overlay(self):
        """
        화면에 표시된 Step Overlay를 제거합니다.
        """

        self.driver.execute_script("""
            let old = document.getElementById(
                'test-step-overlay'
            );

            if (old) {
                old.remove();
            }
        """)

    @contextmanager
    def step(
        self,
        message,
        step_no=None,
        total_steps=None
    ):
        """
        테스트 Step 시작/종료를 자동 관리합니다.

        사용 예시:

        with self.step(
            "로그인 진행",
            step_no=1,
            total_steps=5
        ):
            ...
        """

        self.show_step(
            message,
            step_no,
            total_steps
        )

        logger.info(
            f"▶ STEP 시작: {message}"
        )

        start_time = time.time()

        try:

            yield

            elapsed = round(
                time.time() - start_time,
                2
            )

            logger.info(
                f"✅ STEP 완료: "
                f"{message} "
                f"({elapsed}초)"
            )

        except Exception:

            logger.exception(
                f"❌ STEP 실패: {message}"
            )

            raise

    # =======================================================================
    # 공통 동작
    # =======================================================================

    def click(self, locator, timeout=10):
        """
        프로젝트 표준 클릭 함수.

        요소가 클릭 가능해질 때까지 대기한 뒤 클릭합니다.
        React/MUI 환경에서 발생하는 tooltip, popper, animation,
        rerender, intercept 문제를 방어하고 마지막에는 JS click으로 재시도합니다.
        """

        wait = WebDriverWait(
            self.driver,
            timeout
        )

        element = wait.until(
            EC.presence_of_element_located(locator)
        )

        # 요소를 화면 중앙으로 스크롤
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element
        )

        self._wait_for_element_rect_stable(element, timeout=timeout)

        try:

            element = wait.until(
                EC.element_to_be_clickable(locator)
            )

            element.click()

        except (
            ElementClickInterceptedException,
            StaleElementReferenceException,
            TimeoutException
        ):

            logger.warning(
                f"일반 클릭 실패, "
                f"방해 요소 정리 후 JS click으로 재시도합니다. "
                f"locator={locator}"
            )

            # MUI Tooltip/Popover가 클릭을 가로막는 경우 숨김 처리
            self._hide_click_blockers()

            # React rerender 대비 재조회
            element = wait.until(
                EC.presence_of_element_located(locator)
            )

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                element
            )

            wait.until(
                lambda driver: self._is_element_js_clickable(
                    driver.find_element(*locator)
                )
            )

            # JS click fallback
            self.driver.execute_script(
                "arguments[0].click();",
                element
            )

    def enter_text(self, locator, text):
        """
        요소가 화면에 보일 때까지 대기 후 텍스트를 입력합니다.
        """

        element = self.wait.until(
            EC.visibility_of_element_located(locator)
        )

        # 입력창 중앙 정렬
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element
        )

        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        element.clear()

        element.send_keys(text)

        try:
            self.wait.until(
                lambda driver: self._get_element_value(
                    driver.find_element(*locator)
                ) == text
            )
        except TimeoutException:
            element = self.wait.until(
                EC.visibility_of_element_located(locator)
            )
            self._set_input_value(element, text)
            self.wait.until(
                lambda driver: self._get_element_value(
                    driver.find_element(*locator)
                ) == text
            )

        return element

    def get_text(self, locator: tuple) -> str:
        """
        요소가 화면에 보일 때까지 대기 후 텍스트를 반환합니다.
        """

        element = self.wait_for_visible(locator)

        return element.text

    def wait_until_invisible(
        self,
        locator: tuple,
        timeout: int = 10
    ):
        """
        요소가 화면에서 완전히 사라질 때까지 대기합니다.
        """

        custom_wait = WebDriverWait(
            self.driver,
            timeout
        )

        custom_wait.until(
            EC.invisibility_of_element_located(locator)
        )

    def wait_for_url_contains(self, text: str):
        """
        현재 브라우저 URL에 특정 문자열이 포함될 때까지 대기합니다.
        """

        self.wait.until(
            EC.url_contains(text)
        )

    def wait_for_visible(self, locator: tuple):
        """
        요소가 화면에 렌더링되어 시각적으로 보일 때까지 대기합니다.
        """

        return self.wait.until(
            EC.visibility_of_element_located(locator)
        )

    def safe_click(self, locator, timeout=10):
        """
        이전 테스트 코드와의 호환을 위한 alias.
        신규 Page Object에서는 click()을 표준으로 사용합니다.
        """

        return self.click(locator, timeout=timeout)

    def _hide_click_blockers(self):
        """
        MUI Tooltip/Popover처럼 클릭을 가로막는 임시 레이어를 비활성화합니다.
        """

        self.driver.execute_script("""
            const blockers = document.querySelectorAll(
                '[role="tooltip"], .MuiTooltip-popper, .MuiPopper-root'
            );

            blockers.forEach(el => {
                el.style.display = 'none';
                el.style.pointerEvents = 'none';
            });
        """)

    def _is_element_js_clickable(self, element) -> bool:
        """
        JS click fallback 전에 최소한 실제 클릭 가능한 상태인지 확인합니다.
        """

        class_name = element.get_attribute("class") or ""
        disabled = element.get_attribute("disabled")
        aria_disabled = element.get_attribute("aria-disabled")

        return (
            element.is_displayed()
            and element.is_enabled()
            and disabled is None
            and aria_disabled != "true"
            and "Mui-disabled" not in class_name
        )

    def _wait_for_element_rect_stable(self, element, timeout=10):
        """
        애니메이션 중인 요소의 위치/크기가 잠시 안정될 때까지 기다립니다.
        """

        wait = WebDriverWait(
            self.driver,
            timeout,
            poll_frequency=0.1
        )

        last_rect = {"value": None, "same_count": 0}

        def rect_is_stable(_driver):
            try:
                rect = element.rect
            except StaleElementReferenceException:
                return True

            current_rect = (
                round(rect.get("x", 0), 1),
                round(rect.get("y", 0), 1),
                round(rect.get("width", 0), 1),
                round(rect.get("height", 0), 1)
            )

            if current_rect == last_rect["value"]:
                last_rect["same_count"] += 1
            else:
                last_rect["value"] = current_rect
                last_rect["same_count"] = 1

            return last_rect["same_count"] >= 2

        try:
            wait.until(rect_is_stable)
        except TimeoutException:
            logger.debug("요소 위치 안정화 대기 시간 초과, 클릭을 계속 진행합니다.")

    def _set_input_value(self, element, value: str):
        """
        React가 입력값 변경을 감지하도록 native setter와 이벤트를 함께 사용합니다.
        """

        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];
            const tagName = element.tagName.toLowerCase();
            const prototype = tagName === 'textarea'
                ? window.HTMLTextAreaElement.prototype
                : window.HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(
                prototype,
                'value'
            ).set;

            setter.call(element, value);
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element,
            value
        )

    def _get_element_value(self, element) -> str:
        """input/textarea 요소의 현재 값을 문자열로 반환합니다."""

        return element.get_attribute("value") or ""

    @staticmethod
    def xpath_literal(text: str) -> str:
        """
        XPath 문자열 리터럴을 안전하게 생성합니다.
        """

        if "'" not in text:
            return f"'{text}'"

        if '"' not in text:
            return f'"{text}"'

        parts = text.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"
