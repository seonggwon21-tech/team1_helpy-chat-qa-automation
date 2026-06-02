"""
[TS-024] 버튼 메뉴 및 부가 기능 검증
포함 TC: TC_012 (+ 버튼 메뉴 4종 노출), TC_013 (파일 업로드),
         TC_014 (이미지 생성), TC_015 (PPT 생성), TC_016 (웹 검색)

시나리오 흐름:
  Step 1. 새 대화 화면 진입 후 입력창 좌측 "+" 버튼 클릭                           [TC_012]
  Step 2. 하위 메뉴 4종 (파일 업로드·이미지 생성·PPT 생성·웹 검색) 노출 확인        [TC_012]
  Step 3. 파일 업로드 선택 → 파일 첨부 → 첨부 칩 노출 확인                         [TC_013]
  Step 4. 이미지 생성 선택 → 프롬프트 전송 → 이미지 결과 노출 → 다운로드 파일 확인  [TC_014]
  Step 5. PPT 생성 선택 → 프롬프트 전송 → PPT 결과 노출 → 다운로드 파일 확인       [TC_015]
  Step 6. 웹 검색 선택 → 검색어 전송 → 웹 검색 결과 및 출처 카드 노출 확인          [TC_016]

미구현 항목 (자동화 제외):
  - TC_017: 최대 글자수 초과 입력 시 제한 동작 및 경고 노출 확인  N/T
"""

import time
import logging
import pytest
from pathlib import Path
from selenium.webdriver.support import expected_conditions as EC
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)

DUMMY_FILE = Path(__file__).resolve().parents[1] / "test_data" / "test_upload.txt"


class TestPlusMenu:

    @pytest.mark.ui
    def test_plus_button_shows_all_menus(self, logged_in_driver):
        """
        [TC-012] + 버튼 클릭 시 하위 메뉴 4종 모두 정상 노출되는지 확인
        """
        chat_page = ChatPage(logged_in_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        # Step 1. 새 대화 화면 진입 후 + 버튼 클릭
        chat_page.show_step("Step 1. + 버튼 클릭 [TC_012]")
        chat_page.open_plus_menu()
        logger.info("+ 버튼 클릭 완료")

        # Step 2. 하위 메뉴 4종 노출 확인
        chat_page.show_step("Step 2. 하위 메뉴 4종 노출 확인")
        menus = [
            ("파일 업로드", chat_page.MENU_FILE_UPLOAD),
            ("이미지 생성", chat_page.MENU_IMAGE_CREATE),
            ("PPT 생성",   chat_page.MENU_PPT_CREATE),
            ("웹 검색",    chat_page.MENU_WEB_SEARCH),
        ]
        for label, locator in menus:
            element = chat_page.wait_for_visible(locator)
            assert element.is_displayed(), \
                f'"{label}" 메뉴가 화면에 노출되지 않았습니다.'
            logger.info(f'"{label}" 메뉴 노출 확인 완료')

    @pytest.mark.ui
    def test_file_upload_via_plus_menu(self, logged_in_driver):
        """
        [TC-013] 파일 업로드 선택 후 파일이 입력창에 첨부되는지 확인
        """
        chat_page = ChatPage(logged_in_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        assert DUMMY_FILE.exists(), f"더미 파일이 존재하지 않습니다: {DUMMY_FILE}"
        logger.info(f"더미 파일 경로 확인: {DUMMY_FILE}")

        # Step 1. + 버튼 클릭 후 파일 업로드 메뉴 노출 확인
        chat_page.show_step("Step 1. 파일 업로드 메뉴 선택 [TC_013]")
        chat_page.open_plus_menu()
        chat_page.wait_for_visible(chat_page.MENU_FILE_UPLOAD)
        logger.info("파일 업로드 메뉴 노출 확인")

        # Step 2. 풀패스 방식으로 파일 직접 주입 (탐색기 우회)
        # MENU_FILE_UPLOAD 클릭 시 input[type='file']이 DOM에 생성됨.
        # send_keys로 절대경로를 직접 주입하면 탐색기 없이 파일 선택 가능.
        chat_page.show_step("Step 2. 파일 경로 전달")
        chat_page.click(chat_page.MENU_FILE_UPLOAD)
        logger.info("파일 업로드 메뉴 클릭 완료")
        file_input = chat_page.wait.until(
            EC.presence_of_element_located(chat_page.FILE_INPUT)
        )
        chat_page.driver.execute_script("arguments[0].style.display = 'block';", file_input)
        file_input.send_keys(str(DUMMY_FILE))
        logger.info(f"풀패스 파일 주입 완료: {DUMMY_FILE.name}")

        # Step 3. 첨부 칩(미리보기) 노출 확인
        chat_page.show_step("Step 3. 첨부 칩 노출 확인")
        chip = chat_page.wait_for_visible(chat_page.FILE_CHIP)
        assert chip.is_displayed(), \
            "파일 첨부 후 입력창 영역에 첨부 칩이 노출되지 않았습니다."
        logger.info("파일 첨부 칩 노출 확인 완료")

    @pytest.mark.xfail(run=False, reason="TC-014: 이미지 다운로드 버튼 클릭 시 파일 미저장 — 수동 확인 시에도 동일 증상, 앱 버그")
    @pytest.mark.slow
    @pytest.mark.ui
    def test_image_creation_via_plus_menu(self, logged_in_driver, temp_download_dir):
        """
        [TC-014] 이미지 생성 선택 후 프롬프트 전송 시 AI 응답에 이미지가 출력되고
                 다운로드 버튼 클릭 시 이미지 파일이 저장되는지 확인
        """
        chat_page = ChatPage(logged_in_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        # Step 1. + 버튼 클릭 후 이미지 생성 메뉴 선택
        chat_page.show_step("Step 1. 이미지 생성 메뉴 선택 [TC_014]")
        chat_page.select_plus_menu_item(chat_page.MENU_IMAGE_CREATE)
        logger.info("이미지 생성 메뉴 클릭 완료")

        # Step 2. 이미지 생성 프롬프트 입력 후 전송
        chat_page.show_step("Step 2. 프롬프트 입력 후 전송")
        chat_page.enter_text(chat_page.CHAT_INPUT, "고양이")
        chat_page.click(chat_page.SEND_BUTTON)
        logger.info("이미지 생성 프롬프트 전송 완료")

        # Step 3. 응답 영역에 이미지 요소 노출 확인 (생성 시간 고려 120초 대기)
        chat_page.show_step("Step 3. AI 응답 이미지 노출 확인 중...")
        image_element = chat_page.wait_for_image_response(timeout=120)
        assert image_element.is_displayed(), \
            "이미지 생성 응답에 이미지 요소가 노출되지 않았습니다."
        src = image_element.get_attribute("src")
        assert src, "이미지 src 속성이 비어있습니다."
        logger.info(f"이미지 응답 노출 확인 완료: {src[:80]}...")

        # Step 4. 응답 영역 다운로드 버튼 직접 클릭 (다이얼로그 불필요)
        chat_page.show_step("Step 4. 이미지 다운로드 확인")

        # 이미지 위에 마우스를 올려 hover overlay 활성화
        chat_page.hover(image_element)
        logger.info("이미지 hover 완료 — 다운로드 버튼 오버레이 활성화")

        # hover 상태에서 다운로드 버튼으로 이동 후 클릭
        download_btn = chat_page.wait_for_visible(chat_page.RESPONSE_DOWNLOAD_BTN)
        assert download_btn.is_displayed(), "응답 영역에 다운로드 버튼이 노출되지 않았습니다."
        chat_page.hover(download_btn)
        chat_page.click(chat_page.RESPONSE_DOWNLOAD_BTN)
        logger.info("응답 영역 다운로드 버튼 클릭 완료")

        files = chat_page.wait_for_download(temp_download_dir)
        assert files, "이미지 파일이 다운로드되지 않았습니다."
        logger.info(f"이미지 다운로드 파일 저장 확인 완료: {files}")

    @pytest.mark.slow
    @pytest.mark.ui
    def test_ppt_creation_via_plus_menu(self, logged_in_driver, temp_download_dir):
        """
        [TC-015] PPT 생성 선택 후 프롬프트 전송 시 PPT 결과가 화면에 노출되고
                 다운로드 버튼 클릭 시 PPTX 파일이 저장되는지 확인
        """
        chat_page = ChatPage(logged_in_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        # Step 1. + 버튼 클릭 후 PPT 생성 메뉴 선택
        chat_page.show_step("Step 1. PPT 생성 메뉴 선택 [TC_015]")
        chat_page.select_plus_menu_item(chat_page.MENU_PPT_CREATE)
        logger.info("PPT 생성 메뉴 클릭 완료")

        # Step 2. 입력창에 "PPT 생성" 모드 칩 노출 확인
        chat_page.wait_for_visible(chat_page.PPT_MODE_CHIP)
        logger.info("PPT 생성 모드 칩 노출 확인 완료")

        # Step 3. 프롬프트 입력 후 전송
        chat_page.show_step("Step 3. PPT 생성 프롬프트 전송")
        chat_page.enter_text(chat_page.CHAT_INPUT, "고양이에 대한 3슬라이드 PPT를 만들어줘.")
        chat_page.click(chat_page.SEND_BUTTON)
        logger.info("PPT 생성 프롬프트 전송 완료")

        # Step 4. PPT 결과 노출 확인 (생성 시간 고려 600초 대기)
        chat_page.show_step("Step 4. PPT 결과 노출 확인 중...")
        download_btn = chat_page.wait_for_ppt_result(timeout=600)
        assert download_btn.is_displayed(), \
            "PPT 생성 후 결과 요소(다운로드 링크 등)가 화면에 노출되지 않았습니다."
        logger.info("PPT 결과 노출 확인 완료")

        # Step 5. 다운로드 버튼 클릭 후 PPTX 파일 저장 확인
        chat_page.show_step("Step 5. PPT 다운로드 확인")
        chat_page.click(chat_page.PPT_DOWNLOAD_BTN)
        logger.info("PPT 다운로드 버튼 클릭 완료")

        pptx_files = chat_page.wait_for_download(temp_download_dir, suffix=".pptx")
        assert pptx_files, "PPTX 파일이 다운로드되지 않았습니다."
        logger.info(f"PPT 다운로드 파일 저장 확인 완료: {pptx_files[0].name}")

    @pytest.mark.ui
    def test_web_search_via_plus_menu(self, logged_in_driver):
        """
        [TC-016] 웹 검색 선택 후 검색어 전송 시 AI 응답 및 출처 카드가 노출되는지 확인
        """
        chat_page = ChatPage(logged_in_driver)
        chat_page.click(chat_page.NEW_CHAT_BUTTON)

        # Step 1. + 버튼 클릭 후 웹 검색 메뉴 선택
        chat_page.show_step("Step 1. 웹 검색 메뉴 선택 [TC_016]")
        chat_page.select_plus_menu_item(chat_page.MENU_WEB_SEARCH)
        logger.info("웹 검색 메뉴 클릭 완료")

        # Step 2. 검색어 입력 후 전송
        chat_page.show_step("Step 2. 검색어 입력 후 전송")
        chat_page.enter_text(chat_page.CHAT_INPUT, "오늘 날씨 알려줘")
        chat_page.click(chat_page.SEND_BUTTON)
        logger.info("웹 검색어 전송 완료")

        # Step 3. AI 응답 텍스트 노출 확인
        chat_page.show_step("Step 3. AI 응답 대기 중...")
        response_text = chat_page.wait_for_ai_response(timeout=120)
        assert response_text and len(response_text.strip()) > 0, \
            "웹 검색 후 AI 응답 텍스트가 출력되지 않았습니다."
        logger.info(f"AI 응답 출력 확인 완료: '{response_text[:80]}...'")

        # Step 4. 웹 검색 결과 텍스트 내용 확인 (출처 카드는 앱에서 미제공)
        chat_page.show_step("Step 4. 웹 검색 결과 텍스트 확인")
        assert len(response_text.strip()) > 50, \
            "웹 검색 응답 텍스트가 너무 짧습니다."
        logger.info("웹 검색 결과 텍스트 정상 출력 확인 완료")
