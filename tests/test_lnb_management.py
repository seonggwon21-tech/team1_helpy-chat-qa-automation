"""
[TS-025] LNB 대화 목록 관리 검증
포함 TC: TC_019 (항목 추가), TC_020 (새로고침 유지), TC_021 (LNB 삭제)

시나리오 흐름:
  Step 1. 메시지 전송 후 LNB에 새 대화 항목이 추가되는지 확인    [TC_019]
  Step 2. 페이지 새로고침 후에도 기존 대화 목록이 유지되는지 확인  [TC_020]
  Step 3. LNB 항목 삭제 버튼 클릭 후 목록에서 제거되는지 확인    [TC_021]
"""

import logging
import pytest
from pages.chat_page import ChatPage

logger = logging.getLogger(__name__)


class TestLnbManagement:

    @pytest.mark.ui
    def test_lnb_lifecycle(self, logged_in_driver):
        """
        [TC-019] 메시지 전송 후 LNB에 새 대화 항목이 추가되는지 확인
        [TC-020] 페이지 새로고침 후 LNB 목록이 유지되는지 확인
        [TC-021] LNB 항목 삭제 버튼 클릭 후 목록에서 제거되는지 확인
        """
        chat_page = ChatPage(logged_in_driver)

        initial_hrefs = chat_page.get_lnb_hrefs()
        logger.info(f"초기 LNB 항목 수: {len(initial_hrefs)}")

        # [TC_019] 메시지 전송 후 LNB에 새 항목 추가 확인
        chat_page.show_step("[TC_019] 메시지 전송 후 LNB 항목 추가 확인")
        chat_page.send_message("LNB 목록 관리 검증용 테스트 메시지입니다.")

        new_hrefs = chat_page.wait_for_new_lnb_item(initial_hrefs, timeout=60)
        chat_page.wait_for_ai_response(timeout=60)

        assert len(new_hrefs) == 1, \
            f"LNB에 새 항목이 정확히 1개 추가되지 않았습니다. 추가된 항목: {new_hrefs}"
        logger.info(f"LNB 신규 항목 추가 확인 완료: {new_hrefs}")

        # [TC_020] 페이지 새로고침 후 LNB 목록 유지 확인
        chat_page.show_step("[TC_020] 새로고침 후 LNB 목록 유지 확인")
        before_refresh_hrefs = chat_page.get_lnb_hrefs()
        chat_page.driver.refresh()
        chat_page.wait_for_lnb_loaded()

        after_refresh_hrefs = chat_page.get_lnb_hrefs()
        assert before_refresh_hrefs == after_refresh_hrefs, (
            f"새로고침 후 LNB 목록이 변경되었습니다.\n"
            f"이전: {before_refresh_hrefs}\n이후: {after_refresh_hrefs}"
        )
        logger.info("새로고침 후 LNB 목록 유지 확인 완료")

        # [TC_021] LNB 첫 번째 항목 삭제 후 목록에서 제거 확인
        chat_page.show_step("[TC_021] LNB 항목 삭제 확인")
        current_items = chat_page.get_lnb_items()
        target_href = current_items[0].get_attribute("href")

        chat_page.delete_lnb_item(current_items[0])
        chat_page.wait_for_lnb_item_removed(target_href)
        logger.info(f"LNB 대화 삭제 확인 완료: {target_href}")
