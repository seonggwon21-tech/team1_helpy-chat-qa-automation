# HelpyChat QA Automation

> 📌 **이 저장소는 엘리스 KDT 5인 팀 프로젝트의 협업 원본입니다.**
> 제가 담당한 영역만 별도로 정리한 **개인 포트폴리오**는 👉 [**helpy-chat-qa-automation**](https://github.com/seonggwon21-tech/helpy-chat-qa-automation) 을 참고해 주세요.
> (담당 역할은 아래 [팀 구성 및 담당 역할](#팀-구성-및-담당-역할) 참고)

HelpyChat 서비스의 주요 사용자 흐름을 검증하는 Python 기반 E2E UI 자동화 프로젝트입니다.
Selenium WebDriver와 Pytest를 사용하며, 화면 조작 로직은 Page Object Model(POM) 구조로 분리되어 있습니다.

## 기술 스택

- Python 3.10 이상
- Pytest
- Selenium WebDriver
- python-dotenv
- requests
- Slack Incoming Webhook
- Jira REST API
- GitLab CI/CD

## 프로젝트 구조

```text
first-project/
├─ config/
│  ├─ __init__.py
│  └─ config.py                 # URL, 계정, 다운로드, Jira, Slack 설정
├─ pages/                       # Page Object Model 클래스
│  ├─ base_page.py              # 공통 클릭, 입력, 대기, step overlay, safe click
│  ├─ login_page.py             # 로그인
│  ├─ signup_page.py            # 최초 약관 동의 처리
│  ├─ chat_page.py              # 채팅 입력, 전송, AI 응답 확인
│  ├─ search_page.py            # 검색 모달
│  ├─ tool_page.py              # 도구 탭 공통 진입
│  ├─ quiz_page.py              # 퀴즈 생성
│  ├─ ppt_page.py               # PPT 생성
│  ├─ lesson_plan_page.py       # 수업 지도안 생성
│  ├─ deep_investigation_page.py
│  ├─ behavior_and_opinions_page.py
│  ├─ detailed_specialty_page.py
│  ├─ agent_add_page.py         # 에이전트 추가
│  ├─ agent_filter_page.py      # 에이전트 필터
│  ├─ agent_myagent_page.py     # 내 에이전트 관리
│  ├─ agent_search_page.py      # 에이전트 검색
│  └─ register_page.py          # 신규 계정 생성 보조
├─ tests/                       # Pytest 테스트 시나리오
├─ test_data/                   # 업로드 테스트용 파일
├─ utils/
│  ├─ slack_notifier.py         # Slack 요약/실패 상세 알림
│  └─ jira_notifier.py          # Jira 버그 이슈 생성 및 스크린샷 첨부
├─ logs/                        # 테스트 로그 및 실패 스크린샷
├─ conftest.py                  # pytest fixture, WebDriver, hook 관리
├─ pytest.ini                   # pytest 경로, 로그, marker 설정
├─ requirements.txt             # Python 의존성
├─ .gitlab-ci.yml               # GitLab CI 테스트 잡
└─ README.md
```

## 주요 파일 역할

| 파일 | 역할 |
|---|---|
| `config/config.py` | `.env` 기반 설정값을 한곳에서 로드합니다. |
| `conftest.py` | WebDriver, 로그인된 브라우저, API 세션, 다운로드 경로, 실패 처리 hook을 관리합니다. |
| `pages/` | 화면별 조작 로직을 Page Object로 관리합니다. |
| `tests/` | 실제 테스트 시나리오와 검증 로직을 관리합니다. |
| `utils/slack_notifier.py` | 테스트 종료 요약과 실패 상세를 Slack으로 전송합니다. |
| `utils/jira_notifier.py` | 실패 시 Jira Bug 이슈를 만들고 스크린샷을 첨부합니다. |
| `pytest.ini` | 테스트 탐색 경로, 로그 파일, CLI 로그, marker를 정의합니다. |
| `.gitlab-ci.yml` | GitLab Runner에서 headless UI 테스트를 실행합니다. |

## 테스트 범위

현재 `pytest --collect-only -q` 기준으로 45개 테스트가 수집됩니다.

- 로그인 및 최초 약관 동의 후 메인 화면 진입
- 새 채팅 생성, 메시지 전송, 기존 대화 유지 확인
- LNB 대화 목록 생성, 새로고침, 선택, 삭제 흐름
- 검색 모달 열기, 검색어 입력, 결과 이동, 재오픈 시 입력값 초기화
- 모델 설정 변경 후 채팅 검증
- 입력창 부가 기능 및 `+` 메뉴 검증
- 파일 업로드, PPT 생성, 웹 검색 메뉴 검증
- 퀴즈 생성, 중단, 입력값 오류, 드롭다운 검증
- PPT 생성, 중단, 다운로드, 입력값 경계값 검증
- 수업 지도안 생성
- 심층 조사 생성, 필수값, 경계값, 중단 흐름 검증
- 우리 반 AI 도구, 행동 특성 및 종합 의견, 세부 능력 특기사항, 에이전트 관련 흐름 검증

## 사전 준비

Chrome 브라우저가 설치되어 있어야 합니다. ChromeDriver는 Selenium Manager가 자동으로 관리합니다.

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux 환경에서는 가상환경 활성화 명령만 아래처럼 사용합니다.

```bash
source venv/bin/activate
```

## 환경 변수

프로젝트 루트에 `.env` 파일을 만들고 필요한 값을 설정합니다. 실제 계정 정보와 토큰은 Git에 커밋하지 않습니다.

```env
BASE_UI_URL=https://qaproject.elice.io
BASE_API_URL=https://dev-v2-community-api.dev.elicer.io

TEST_USER_ID=your_test_user@example.com
TEST_USER_PW=your_password

DOWNLOAD_DIR=C:\Users\user\Downloads
DEFAULT_API_TIMEOUT=10

JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_jira_email@example.com
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=YOUR_PROJECT_KEY

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SLACK_WEBHOOK_FAILURES_URL=https://hooks.slack.com/services/...
```

설정값 기본 동작:

- `BASE_UI_URL` 기본값은 `https://qaproject.elice.io`입니다.
- `BASE_API_URL` 기본값은 `https://dev-v2-community-api.dev.elicer.io`입니다.
- `DOWNLOAD_DIR` 기본값은 사용자 홈의 `Downloads` 폴더입니다.
- `HEADLESS=true`이면 Chrome을 headless 모드로 실행합니다.
- Jira 관련 환경변수가 모두 있을 때만 실패 시 Jira 이슈를 생성합니다.
- Slack Webhook이 없으면 Slack 알림만 생략하고 테스트는 계속 진행합니다.

## 실행 방법

전체 테스트 실행:

```bash
pytest
```

특정 테스트 파일 실행:

```bash
pytest tests/test_search.py
```

특정 marker 실행:

```bash
pytest -m ui
pytest -m slow
pytest -m ui_slow
```

테스트 수집만 확인:

```bash
pytest --collect-only -q
```

CI와 동일하게 headless 모드로 실행:

```bash
$env:HEADLESS="true"
pytest
```

## 로그와 실패 처리

`pytest.ini` 설정에 따라 실행 로그는 `logs/test_run.log`에 기록됩니다.

테스트 실패 시 `conftest.py`의 pytest hook이 다음 처리를 수행합니다.

- 실패 테스트명, 파일 경로, 에러 메시지를 로그에 기록
- WebDriver가 있는 테스트라면 현재 화면 스크린샷 저장
- 스크린샷 저장 경로: `logs/screenshots/`
- `SLACK_WEBHOOK_FAILURES_URL`이 있으면 실패 상세를 Slack으로 전송
- Jira 설정이 모두 있으면 Bug 이슈 생성 후 스크린샷 첨부

테스트 세션 종료 시에는 `SLACK_WEBHOOK_URL`이 설정된 경우 전체 요약을 Slack으로 전송합니다.
단, `pytest --collect-only` 실행 시에는 Slack 요약 알림을 보내지 않습니다.

## GitLab CI/CD

`.gitlab-ci.yml`은 Python 3.12 이미지를 사용해 의존성을 설치하고 `pytest`를 실행합니다.
CI 환경에서는 아래 변수가 기본 설정되어 Chrome이 headless 모드로 실행됩니다.

```yaml
variables:
  HEADLESS: "true"
```

## 작성 규칙

- 화면 조작은 가능한 한 `pages/`의 Page Object 클래스에 둡니다.
- 테스트 파일은 시나리오 흐름과 검증에 집중합니다.
- 공통 클릭, 입력, 대기 처리는 `BasePage`의 메서드를 우선 사용합니다.
- 긴 생성 작업은 충분한 `WebDriverWait` 시간을 둡니다.
- 다운로드 검증이 필요한 테스트는 `DOWNLOAD_DIR` 또는 `temp_download_dir` fixture를 사용합니다.
- 실패 분석에 필요한 정보는 로그, 스크린샷, Slack, Jira 흐름 중 적절한 위치에 남깁니다.

## 현재 상태

| 항목 | 상태 |
|---|---|
| Selenium Page Object 구조 | 적용 |
| Pytest fixture 분리 | 적용 |
| API 인증 세션 fixture | 적용 |
| 실패 스크린샷 자동 저장 | 적용 |
| Jira Bug 이슈 자동 생성 | 환경변수 설정 시 동작 |
| Slack 테스트 요약 알림 | 환경변수 설정 시 동작 |
| Slack 실패 상세 알림 | 환경변수 설정 시 동작 |
| GitLab CI/CD | 기본 테스트 잡 구성 |
| 테스트 수집 검증 | 45 tests collected |

## 팀 구성 및 담당 역할

5인 팀 프로젝트로 진행했습니다. 각 팀원이 기능 영역을 나눠 Page Object와 테스트 코드를 담당했으며, 저(김성권)는 아래 영역을 맡았습니다.

| 담당 영역 | 내용 |
|---|---|
| 프레임워크 설계 | `BasePage` 방어적 클릭 패턴 (visibility → scrollIntoView → element_to_be_clickable → JS fallback 4단계), `conftest.py` fixture 구조 설계 |
| 새 대화 기능 UI 자동화 | `test_new_chat.py` · `test_message_send.py` · `test_lnb_management.py` · `test_plus_menu.py` · `test_input_features.py` |
| SSO 인증 처리 | CDP 쿠키 주입으로 매 테스트 SSO 리다이렉트 5~8초 제거 — TC당 실행 시간 단축, 팀 전체 86 TC 기준 약 7~11분 절감 |
| CI/CD | GitLab Runner 기반 `.gitlab-ci.yml` 구성 |
| 결함 추적 | 미해결 결함 `xfail(strict=True)` 처리로 파이프라인 유지 및 자동 감지 체계 구축 |

## 버전 관리 제외 대상

현재 `.gitignore`에는 다음 항목이 제외되어 있습니다.

```text
.env
__pycache__/
*.pyc
.pytest_cache/
logs/
.DS_Store
venv/
.claude/
local_changes.patch
```

