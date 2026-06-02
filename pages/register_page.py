"""
회원가입 페이지의 UI 요소와 액션을 정의한 Page Object Model 클래스.

[페이지 URL]
https://accounts.elice.io/accounts/signup/form?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat&lang=en-US&org=qaproject

[카운터 관리]
- counter.txt 파일로 숫자를 관리하며, 파일이 없으면 1부터 자동 시작합니다.
- 카운터는 회원가입이 완전히 완료된 시점에만 +1 증가합니다.
- 중복 계정 감지 시에는 카운터를 증가시키지 않고, 현재 숫자에서 +1한 임시 번호로만 재시도합니다.
"""

import os
import pytest
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage

logger = logging.getLogger(__name__)

# =========================================================
# 카운터 관리 유틸 함수
# =========================================================
_COUNTER_FILE = "counter.txt"
_MAX_RETRY    = 10  # 중복 계정 감지 시 최대 재시도 횟수 (무한 루프 방지)


def _read_counter() -> int:
    """counter.txt에서 현재 숫자를 읽어서 반환합니다. 파일이 없으면 1을 반환합니다."""
    if os.path.exists(_COUNTER_FILE):
        with open(_COUNTER_FILE, "r") as f:
            return int(f.read().strip())
    return 1  # 파일이 없으면 1부터 시작


def _save_counter(count: int):
    """counter.txt에 숫자를 저장합니다."""
    with open(_COUNTER_FILE, "w") as f:
        f.write(str(count))


def get_next_user_info() -> dict:
    """
    현재 카운터 숫자를 기준으로 테스트용 계정 정보를 생성하여 반환합니다.
    카운터 증가는 하지 않습니다. (증가는 회원가입 완료 후에만 수행)

    Returns:
        dict: { "email": "qa1@test.com", "password": "...", "name": "qa5-01" }
    """
    count = _read_counter()
    user_info = {
        "email"   : f"qa{count}@test.com",
        "password": os.getenv("TEST_REG_PW", os.getenv("TEST_USER_PW", "")),
        "name"    : f"qa5-{count:02d}",
    }
    logger.info(f"신규 계정 정보 생성 → email: {user_info['email']} / name: {user_info['name']}")
    return user_info


# =========================================================
# RegisterPage: 회원가입 화면 조작 클래스
# =========================================================
class RegisterPage(BasePage):
    """회원가입 화면 조작 및 검증 클래스"""

    # 회원가입 페이지 URL (고정)
    SIGNUP_URL = (
        "https://accounts.elice.io/accounts/signup/form"
        "?continue_to=https%3A%2F%2Fqaproject.elice.io%2Fai-helpy-chat"
        "&lang=en-US&org=qaproject"
    )

    # =======================================================================
    # Locators
    # =======================================================================
    EMAIL_INPUT    = (By.CSS_SELECTOR, "input[name='loginId']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[name='password']")
    NAME_INPUT     = (By.CSS_SELECTOR, "input[name='fullname']")

    # 이미 가입된 이메일 입력 시 나타나는 에러 문구
    DUPLICATE_EMAIL_ERROR = (By.XPATH, "//*[contains(text(), 'This is an already registered email address.')]")

    # MUI 체크박스: 일반 클릭이 막혀있으므로 JavaScript Click으로 처리합니다.
    AGREE_ALL_CHECKBOX = (By.CSS_SELECTOR, "input.PrivateSwitchBase-input[type='checkbox']")

    # Create account 버튼: form 속성으로 정확히 특정합니다.
    CREATE_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "button[form='signup-form'][type='submit']")

    def __init__(self, driver: WebDriver):
        super().__init__(driver)

    def open(self):
        """회원가입 페이지로 이동합니다."""
        self.driver.get(self.SIGNUP_URL)
        logger.info("회원가입 페이지로 이동합니다.")

        create_account_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Create account with email']")
            )
        )
        create_account_button.click()

    def fill_email(self, email: str):
        """
        이메일 입력란의 기존 값을 완전히 지운 뒤 새 값을 입력합니다.
        MUI/React input은 DOM value만 바꾸면 React state가 남을 수 있어
        키보드 초기화와 input/change 이벤트를 함께 발생시킵니다.
        """
        element = self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))

        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            element
        )

        element.click()
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)

        self._set_input_value(element, "")
        self.wait.until(
            lambda driver: (
                driver.find_element(*self.EMAIL_INPUT).get_attribute("value") or ""
            ) == ""
        )

        element.send_keys(email)

        try:
            self.wait.until(
                lambda driver: self._get_email_value(driver) == email
            )
        except TimeoutException:
            element = self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))
            self._set_input_value(element, email)
            self.wait.until(
                lambda driver: self._get_email_value(driver) == email
            )

    def is_duplicate_email(self) -> bool:
        """
        이메일 중복 에러 메시지가 화면에 나타나는지 확인합니다.
        에러가 보이면 True(중복), 없으면 False(사용 가능)를 반환합니다.
        """
        try:
            # 에러 메시지가 나타날 때까지 최대 3초 대기
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.DUPLICATE_EMAIL_ERROR)
            )
            return True   # 에러 메시지 보임 → 중복 계정
        except TimeoutException:
            return False  # 에러 없음 → 사용 가능한 계정

    def wait_for_duplicate_email_error_to_clear(self, timeout: int = 2):
        """
        이전 이메일에서 발생한 중복 에러가 새 입력 후 사라질 시간을 짧게 기다립니다.
        같은 에러가 계속 유지되면 다음 중복 검사에서 다시 확인합니다.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.DUPLICATE_EMAIL_ERROR)
            )
        except TimeoutException:
            pass

    def _set_input_value(self, element, value: str):
        """React가 입력값 변경을 감지하도록 native setter와 이벤트를 함께 사용합니다."""
        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype,
                'value'
            ).set;

            setter.call(element, value);
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element,
            value
        )

    def _get_email_value(self, driver) -> str:
        """현재 이메일 입력값을 안전하게 조회합니다."""
        return driver.find_element(*self.EMAIL_INPUT).get_attribute("value") or ""

    def register(self, email: str, password: str, name: str):
        """
        이메일, 비밀번호, 이름을 입력하고 약관에 동의한 뒤 Create account 버튼을 클릭합니다.
        - 중복 계정 감지 시: 카운터를 증가시키지 않고 임시 번호(+1)로 재시도합니다.
        - 회원가입 완료 시: 그 때 딱 한 번 counter.txt를 +1 증가시킵니다.

        Args:
            email    : 가입할 이메일 주소 (예: qa1@test.com)
            password : 비밀번호 (예: qwert12345!)
            name     : 사용자 이름 (예: qa5-01)
        """
        # 현재 카운터 숫자를 기준으로 재시도 번호를 관리합니다.
        # counter.txt는 건드리지 않고, 임시 변수로만 번호를 올립니다.
        base_count  = _read_counter()
        retry_count = base_count  # 재시도 시 사용할 임시 번호 (counter.txt와 무관)

        # -------------------------------------------------------
        # 중복 계정 감지 시 임시 번호만 올리며 재시도하는 루프
        # -------------------------------------------------------
        for attempt in range(_MAX_RETRY):
            # 1. 이메일 입력
            logger.info(f"이메일 입력 (시도 {attempt + 1}회): {email}")
            self.fill_email(email)
            self.wait_for_duplicate_email_error_to_clear()

            # 2. 중복 여부 확인
            if self.is_duplicate_email():
                # 중복 감지 → counter.txt는 그대로, 임시 번호만 +1
                retry_count += 1
                email    = f"qa{retry_count}@test.com"
                name     = f"qa5-{retry_count:02d}"
                logger.warning(f"중복 계정 감지 → 임시 번호 {retry_count}로 재시도합니다. (counter.txt 변경 없음)")
                continue  # 루프 처음으로 돌아가서 새 이메일로 재시도

            # 중복 없음 → 사용 가능한 계정 확인
            logger.info(f"사용 가능한 계정 확인: {email}")
            break

        else:
            # _MAX_RETRY 횟수를 모두 소진한 경우 테스트 강제 종료
            pytest.fail(f"중복되지 않는 계정을 {_MAX_RETRY}회 시도했지만 찾지 못했습니다.")

        # 3. 비밀번호 입력
        logger.info("비밀번호 입력.")
        self.enter_text(self.PASSWORD_INPUT, password)

        # 4. 이름 입력
        logger.info(f"이름 입력: {name}")
        self.enter_text(self.NAME_INPUT, name)

        # 5. Agree All 체크박스 체크 (MUI 특성상 JavaScript Click 사용)
        logger.info("약관 동의 체크박스를 선택합니다.")
        checkbox = self.wait.until(EC.presence_of_element_located(self.AGREE_ALL_CHECKBOX))
        self.driver.execute_script("arguments[0].click();", checkbox)

        # 6. Create account 버튼 클릭
        logger.info("'Create account' 버튼을 클릭합니다.")
        self.click(self.CREATE_ACCOUNT_BUTTON)

        try:
            WebDriverWait(self.driver, 15).until(
                lambda driver: "signup/form" not in driver.current_url
            )
        except TimeoutException:
            pytest.fail("회원가입 제출 후 로그인 화면으로 전환되지 않았습니다.")

        # 7. 회원가입 완료 → 이 시점에 딱 한 번 counter.txt를 +1 증가
        # 다음 테스트 실행 시 새로운 번호로 시작하기 위해 저장합니다.
        _save_counter(retry_count + 1)
        logger.info(f"회원가입 완료 → counter.txt를 {retry_count + 1}로 업데이트했습니다.")

        return {
            "email": email,
            "password": password,
            "name": name,
        }
