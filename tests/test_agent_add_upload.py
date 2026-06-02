"""
새로운 에이전트 생성
"""

import pytest
import time
import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  # MUI 입력창 청소용
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

@pytest.mark.ui
def test_create_new_agent_scenario(logged_in_driver, base_url):
    base = BasePage(logged_in_driver)
    
    logger.info("🔥 [시나리오 시작] 새 에이전트 생성 자동화 테스트를 시작합니다.")

    # ==========================================
    # [Locator] 로케이터 정의 구역
    # ==========================================
    # 1. 탐색 및 진입 관련 (다국어 방어 href 주소 기반)
    agent_search_tab_xpath = (By.XPATH, "//a[contains(@href, '/ai-helpy-chat/agents')]")
    create_mode_btn_xpath = (By.XPATH, "//a[contains(@href, '/ai-helpy-chat/agents/builder')]") 
    
    # 2. 빌더 입력창 관련 
    agent_name_input_xpath = (By.XPATH, "(//input[contains(@placeholder, '이름')])[1]")
    agent_desc_input_xpath = (By.XPATH, "(//input[contains(@placeholder, '설명')])[1]")
    agent_prompt_input_xpath = (By.XPATH, "(//textarea[contains(@placeholder, '용도') or contains(@placeholder, '제한 사항')])[1]")
    
    # 3. 우측 상단 만들기 버튼 
    submit_create_btn_xpath = (By.XPATH, "//button[@type='button' and contains(., '만들기')]")    
    
    # 4. 만들기 버튼 후 최종 모달  
    modal_save_btn_xpath = (By.XPATH, "//button[contains(., '저장')]")

    # ==========================================
    # 타이핑 정의
    # ==========================================

    def human_typing(element, text):
        element.click()
        time.sleep(0.2)
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        time.sleep(0.2)
        for char in text:
            element.send_keys(char)
            time.sleep(0.06)
        element.send_keys(Keys.TAB)
        time.sleep(0.2)

    # ==========================================
    # Step 1. LNB 메뉴에서 에이전트 탐색 클릭
    # ==========================================
    logger.info("✅ 에이전트 탐색 LNB 메뉴에서 에이전트 탐색 클릭")

    # 반응형 햄버거 버튼 분기 대응 (있으면 누르고 없으면 패스)
    try:
        hamburger_xpath = "//button[.//svg[@data-testid='barsIcon']]"
        base.wait.until(EC.element_to_be_clickable((By.XPATH, hamburger_xpath))).click()
    except Exception:
        pass

    base.wait.until(EC.element_to_be_clickable(agent_search_tab_xpath)).click()
    base.wait.until(EC.url_contains("/agents"))
    logger.info("✅ 에이전트 탐색 영역 진입 성공")

    # ==========================================
    # Step 2. 우측 상단 +만들기 버튼 클릭
    # ==========================================
    logger.info("🖱️ '+만들기 버튼 클릭")

    base.wait.until(EC.element_to_be_clickable(create_mode_btn_xpath)).click()
    base.wait.until(EC.visibility_of_element_located(agent_name_input_xpath)) 

    logger.info("✅ 새 에이전트 만들기(add) 화면 진입 확인")

    # ==========================================
    # Step 3. 각 항목에 값 입력
    # ==========================================
    # 1. 에이전트 이름 입력
    name_el = base.wait.until(EC.visibility_of_element_located(agent_name_input_xpath))
    human_typing(name_el, "자동화_테스트_에이전트")
    logger.info("✍️ 에이전트 이름 입력 완료")

    # 2. 에이전트 한줄 소개 입력
    desc_el = base.wait.until(EC.visibility_of_element_located(agent_desc_input_xpath))
    human_typing(desc_el, "자동화_테스트_에이전트 입니다..")
    logger.info("✍️ 에이전트 한줄 소개 입력 완료")

    # 3. 규칙(프롬프트) 입력
    prompt_el = base.wait.until(EC.visibility_of_element_located(agent_prompt_input_xpath))
    human_typing(prompt_el, "자동화_테스트_에이전트 규칙 입니다.")
    
    # 규칙 창은 textarea이므로 TAB 대신 확실하게 ESCAPE로 커서를 완전히 빼줍니다.
    prompt_el.send_keys(Keys.ESCAPE)
    logger.info("✍️ 에이전트 규칙 입력 및 포커스 탈출 완료")

    # ==========================================
    # Step 3.5. 파일 업로드 검증    
    # ==========================================
    logger.info("📁 에이전트 생성 내 더미 파일 업로드 테스트 시작")

    # 1. 절대 경로 변환
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    project_root = os.path.dirname(current_dir)       
    
    dummy_file_path = os.path.join(project_root, "test_data", "test_upload2.pdf")
    
    logger.info(f"📄 계산된 더미 파일 경로: {dummy_file_path}")

    # 파일이 위치하는지 확인
    if not os.path.exists(dummy_file_path):
        raise FileNotFoundError(f"❌ 지정된 위치에 더미 파일이 없습니다: {dummy_file_path}")

    # 2. 숨겨진 input[type='file'] 태그 조준 (HTML 구조 기반)
    file_input_xpath = (By.XPATH, "//label[contains(., '파일 업로드')]//input[@type='file']")
    
    # 3. DOM에 존재하면 바로 잡아서 파일 경로 주입!
    file_input_el = base.wait.until(EC.presence_of_element_located(file_input_xpath))
    file_input_el.send_keys(dummy_file_path)
    
    logger.info("✅ test_upload2.pdf 더미 파일 업로드 완료")
    time.sleep(1.5)  # 파일이 업로드되어 UI에 파일 칩이나 리스트가 반영될 시간을 줍니다.

    # ==========================================
    # Step 4. 우측 상단 만들기 버튼 활성화 확인 및 클릭!
    # ==========================================
    logger.info("⏳ 입력 완료 후 최종 버튼 활성화 및 상태 안정화 대기 중...")
    time.sleep(1) 
    
    submit_button = base.wait.until(EC.element_to_be_clickable(submit_create_btn_xpath))
    submit_button.click()
    logger.info("✅ 만들기 버튼 클릭 완료")

    # 최종 모달 확인 (나만보기/기관 내 공유)
    logger.info("🔐 2차 '공개 설정' 모달 선택")
    save_button = base.wait.until(EC.element_to_be_clickable(modal_save_btn_xpath))
    save_button.click()
    logger.info("✅ 공개 설정 [저장] 버튼 최종 클릭")
    
    # 모달이 사라질 때까지 대기
    base.wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "MuiDialog-container")))
    time.sleep(1)

    # ==========================================
    # 검증 시작
    # ==========================================
    logger.info("🔄 [검증 시작] 내 에이전에서 생성 검증")
    time.sleep(1) #화면이 갱신되는데 필요한 최소 시간

    # 1. LNB 메뉴에서 '에이전트 탐색' 클릭
    base.wait.until(EC.element_to_be_clickable(agent_search_tab_xpath)).click()
    base.wait.until(EC.url_contains("/ai-helpy-chat/agents"))
    logger.info("✅ LNB 에이전트 탐색 클릭 및 이동 확인")
    
    # 2. 신규 로케이터 선언
    myagent_mode_btn_xpath = (By.XPATH, "//a[contains(@href, '/ai-helpy-chat/agents/mine') and contains(., '내 에이전트')]")
    
    # 3. 우측 상단 '내 에이전트' 탭 버튼 클릭
    base.wait.until(EC.element_to_be_clickable(myagent_mode_btn_xpath)).click()
    base.wait.until(EC.url_contains("/ai-helpy-chat/agents/mine"))
    logger.info("✅ 내 에이전트 탭 진입 성공!")
    
    # 4.내가 만든 카드가 목록에 있는지 최종 확인!
    # 이름 불문, 주소 규칙을 가진 카드가 화면에 보일 때까지 명시적 대기
    target_card_xpath = (By.XPATH, "//a[contains(@href, '/ai-helpy-chat/agents/') and contains(@href, '/builder')]")
    base.wait.until(EC.presence_of_element_located(target_card_xpath))
    
    logger.info("🎯 목록에 새 에이전트 카드가 정상적으로 노출되는 것을 확인")
    
    # ==========================================
    # 테스트 완료
    # ==========================================
    logger.info("🎉 에이전트 생성 기능 시나리오 테스트 완료")