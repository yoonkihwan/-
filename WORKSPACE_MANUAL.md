# 업무 프로그램 통합 매뉴얼 (WORKSPACE_MANUAL)

- 목적: 저장소의 모든 사용자/운영 문서를 단일 기준(SSOT)으로 통합하고, 운영·개발·유지보수에 필요한 정보를 한 곳에 제공합니다.
- 개요: 개인 업무 생산성 데스크톱 애플리케이션 (Python, tkinter)
- 핵심 기능: 템플릿/문구 관리, 포맷 변환, 작업 공간(Workspace) 일괄 실행, Todo 관리(SQLite), 스크린샷, OCR(Tesseract), 클립보드 히스토리, 번역, 설정, 미니 플로팅바

---

## 설치 및 실행

- 요구 사항: Python 3.9+, pip, Windows 권장
- 의존성 설치: `pip install -r requirements.txt`
- 실행: `python main.py`
- OCR 사전 준비(Tesseract):
  - 다운로드: https://github.com/UB-Mannheim/tesseract/wiki (Windows 설치 프로그램)
  - 설치 시 Additional language data에서 Korean, English 선택
  - PATH 등록 또는 설정에서 `tesseract_cmd_path` 지정
  - 드래그앤드롭(DnD): `tkinterdnd2` 설치 시 활용 가능(미설치여도 실행되며 DnD는 비활성화 안내)

---

## 폴더 및 파일 구조(요약)

- `main.py`: 엔트리 포인트. 서비스 초기화 및 UI 조립
- `models/`: 데이터 모델 (`todo.py`, `workspace.py`, `launcher_item.py`, `template.py`)
- `repositories/`: SQLite CRUD 및 마이그레이션 (`todo_repository.py`, `launcher_repository.py`, `template_repository.py`)
- `services/` 비즈니스 로직
  - `todo_service.py`, `screenshot_service.py`, `ocr_service.py`, `clipboard_service.py`,
    `launcher_service.py`, `formatter_service.py`, `template_service.py`, `translate_service.py`, `config_service.py`
- `ui/`: tkinter UI 컴포넌트 (Todo/Workspace/Formatter/Template/Clipboard/Translator/Theme)
  - 기본 레이아웃: 좌측 네비게이션 레일 + 우측 콘텐츠 스택
  - 상단 AppBar(타이틀/시계/Light-Dark), 하단 StatusBar(토스트)
  - 미니 플로팅바: 항상 위 퀵바(드래그 이동, 선택 액션 실행)
- `config.json`: 앱 환경 설정(JSON)
- 데이터베이스(SQLite)
  - `todos.db`: Todo 데이터(테이블 `todos`)
  - `config.db`: 워크스페이스/런처/템플릿 데이터(테이블 `workspaces`, `launcher_items`, `templates`)
- `screenshots/`: 캡처 파일 저장 기본 폴더 (없으면 자동 생성)

참고: 상세한 레이어 원칙과 개발 지침은 `AGENTS.md`를 따릅니다(중복 서술 최소화).

---

## 설정 (config.json)

- `screenshot_save_dir`: 스크린샷 저장 폴더 경로 (기본 `screenshots`)
- `tesseract_cmd_path`: Tesseract 실행 파일 경로(선택). 미설치 시 PATH 사용
- `window_fullscreen`, `window_topmost`, `window_geometry`: 창 상태/위치 복원 관련 옵션
- `floating_bar_geometry`: 플로팅바 위치/크기 지오메트리 문자열
- `floating_bar_actions`: 플로팅바 버튼 구성(예: `["capture_fullscreen","capture_region","capture_and_ocr","toggle_theme","open_todo"]`)

---

## 기능 요약 및 사용법

- 스크린샷 & OCR
  - 전체 화면 캡처, 영역 선택 캡처, 영역 캡처 후 즉시 OCR
  - 결과 표시, 클립보드 복사 또는 Todo 전송
- Todo 리스트
  - 더블 클릭 완료/미완료 전환, 체크박스 상태 표시, 완료 취소/회귀
  - 멀티 선택 Space/Delete, 드래그 정렬, 부모-자식 구성, 기간 경과 자동 보관
- 작업 공간(Workspace)
  - 파일/폴더/URL을 그룹으로 묶어 한 번에 실행
  - `launcher_items.item_type`은 `file|folder|url`
- 포맷 변환
  - 공백/줄바꿈 리스트 ↔ CSV/Markdown 상호 변환
  - Excel 붙여넣기 보정(공백→줄바꿈) 옵션 제공
- 템플릿/문구 관리
  - 자주 쓰는 문구 저장/삽입
- 번역(googletrans)
  - 입력 언어 자동 감지 및 타깃 선택 후 번역, 결과 복사 지원
- 클립보드 히스토리
  - 백그라운드 모니터링, 최근 항목 빠른 선택/붙여넣기/복사
- 간단 시계 & 상태 표시
- 미니 플로팅바
  - Ctrl+Shift+Space로 표시/숨김
  - 버튼 구성/순서는 설정값으로 지속(`floating_bar_actions`)

---

## 데이터베이스 상세

- `todos.db`: `todos(id, content, status, created_at, sort_order, parent_id, archived_at)`
  - 정렬/계층/보관 컬럼까지 마이그레이션 포함
- `config.db`
  - `workspaces(id, name)`
  - `launcher_items(id, name, path, item_type CHECK in ('file','folder','url'), workspace_id)`
  - `templates(id, title UNIQUE, content)`

마이그레이션 지침은 `AGENTS.md` 6)항을 참고하세요(`repositories/todo_repository.py#_migrate`, `repositories/launcher_repository.py` 등).

---

## 개발 원칙 요약(SOLID/DRY/KISS)

- 레이어 분리와 의존성 역전 지향(`AGENTS.md` 참조)
- 중복 제거(DRY), 단순화(KISS)
- 변경 시 명확한 커밋 메시지와 요약 기록

---

## 변경 로그(요약)

변경 로그 원칙: 본 섹션은 사용자 관점 변경 사항의 단일 출처(SSOT)입니다. `CHANGELOG.md`는 접근성 향상을 위한 요약 미러이며, 상세 설명과 사유는 본 섹션을 우선합니다.

### 최근 변경(YYYY-MM-DD)
- Nav Rail 채택: 좌측 네비 + 우측 콘텐츠 스택
- 미니 플로팅바 도입: 퀵 액션, 위치/구성 지속
- 인코딩/EOL 정책: UTF-8 + LF 일원화(.editorconfig/.gitattributes)

---

## 문제 해결 가이드

일반 이슈와 해결책은 `TROUBLESHOOTING.md`를 참고하세요.

---

## 문서 정책(중요)

- 본 파일(`WORKSPACE_MANUAL.md`)은 문서의 단일 출처(SSOT)입니다.
- 중복 문서는 제거하고, 개발 지침은 `AGENTS.md`에만 유지합니다.
- `README.md`는 진입점 링크와 빠른 시작만 제공합니다.

---

## 자주 쓰는 명령

- 의존성 설치: `pip install -r requirements.txt`
- 실행: `python main.py`
- 포맷 변환/템플릿/워크스페이스/스크린샷/OCR/클립보드는 좌측 네비게이션에서 선택하여 사용

---

## UI 변경 사항(중요)

- 홈 탭 제거: 기본 진입 탭은 ‘클립보드’로 변경되었습니다.
- 탭 구조 정리: 스크린샷과 설정을 각각 독립 탭으로 분리했습니다.
  - 클립보드, 할 일, 작업 공간, 포맷 변환, 템플릿, 번역, 스크린샷, 설정 탭 구성
- 미니 플로팅바 동작 변경:
  - 실행: 앱 시작 시 자동 실행하지 않음. ‘설정’ 탭의 “미니 플로팅바 실행” 버튼으로 시작
  - 메인 최소화: 플로팅바 실행 시 메인 창은 작업표시줄 최소화(iconify)
  - 복귀: 플로팅바의 “메인앱 복귀” 버튼으로 메인 창 복귀 + 플로팅바 자동 종료
  - 안전장치: 플로팅바가 닫혀도 메인이 숨김이면 자동 복귀

---

## 변경 로그(요약)

변경 로그 정책: 이 섹션은 사용자 관점의 변경 사항을 간단 미러하며, 상세 설명/사유는 `CHANGELOG.md`를 우선합니다.

### 최근 변경(2025-08-31)
- 홈 탭 제거 및 클립보드 탭 기본화
- 스크린샷/설정 탭 분리 추가
- 미니 플로팅바: 수동 실행, 실행 시 메인 최소화, 복귀 시 자동 종료, 안전 복귀

---

## 최신 UI/설정 변경 요약 (2025-08-31)

- 시작 탭: 앱 실행 시 ‘홈’ 탭에서 시작 (설정 유지)
- 홈 탭 구성: 설정 탭의 “홈 탭 구성”에서 표시 섹션 선택/저장
  - 선택 가능: 클립보드, 스크린샷, 미니 플로팅바 버튼, 할 일, 작업 공간, 포맷 변환, 템플릿, 번역
  - 섹션 미선택 시 홈에서 구성 안내와 “설정 열기” 버튼 표시
- 설정 탭: 하단의 “설정 전체 적용” 버튼으로 일괄 저장/적용
  - 홈 탭 구성(home_sections), 항상 위(window_topmost), 자동 실행(auto_start)을 한 번에 적용
- 자동 실행: Windows 시작 시 자동 실행 옵션 제공(HKCU Run), 경로 변경 시 재설정 권장
- 항상 위: 기본 해제, 설정 탭에서 토글 가능
- 스크롤 가능한 콘텐츠 영역: 작은 창 크기에서도 모든 탭 내용 접근 가능

---

## 2025-08-31 ���� ���
- Ȩ �ǿ��� ����. ������ ��Ȩ �� ������ ����/����
- ��ũ���� �ڵ� ó��: ���� ĸó �� OCR �� ���� / Todo �߰�
- ���� �ڵ� ó�� ��ư ȭ�鿡�� ����(��û �ݿ�)
- �÷��� �� ��� ����
- ���� �ϴ� ������ ��ü ���롯 ��ư���� �ϰ� ����(Ȩ/�׻� ��/�ڵ� ����)
- ���� â������ ��� �� ���� �����ϵ��� ��ũ�� ���� ����

