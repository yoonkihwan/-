# 업무 프로그램 통합 매뉴얼 (WORKSPACE_MANUAL)

- 목적: 이 저장소의 모든 문서를 단일 기준으로 통합하고, 운영·개발·유지보수에 필요한 정보를 한 곳에서 제공합니다.
- 앱 개요: 개인 업무 생산성 데스크톱 애플리케이션 (Python, tkinter)
- 핵심 기능: 템플릿/문구 관리, 텍스트 형식 변환, 작업 공간(Workspace) 일괄 실행, Todo 관리(SQLite), 스크린샷, OCR(Tesseract), 클립보드 히스토리, 시계, 환경설정

---

## 설치 및 실행

- 요구 사항: Python 3.9+, pip, Windows 권장
- 의존성 설치: `pip install -r requirements.txt`
- 실행: `python main.py`
- OCR 사전 준비(Tesseract):
  - 다운로드: https://github.com/UB-Mannheim/tesseract/wiki (Windows 인스톨러)
  - 설치 시 Additional language data에서 Korean, English 선택
  - PATH 등록을 못 했다면 앱 내 [설정]에서 `tesseract.exe` 경로를 지정하세요
  - DnD(선택): `tkinterdnd2` 설치 시 드래그앤드롭 활성화 (미설치 시 앱은 정상 실행되며 상태표시로 비활성화 안내)

---

## 폴더 및 파일 구조

- `main.py`: 앱 엔트리포인트. 서비스 초기화와 UI 탭 조립
- `models/`: 데이터 모델 (`todo.py`, `workspace.py`, `launcher_item.py`, `template.py`)
- `repositories/`: SQLite CRUD 레이어 (`todo_repository.py`, `launcher_repository.py`, `template_repository.py`)
- `services/`: 비즈니스 로직과 기능 서비스
  - `todo_service.py`: Todo 처리
  - `screenshot_service.py`: 전체/영역 캡처
  - `ocr_service.py`: Tesseract 기반 OCR
  - `clipboard_service.py`: 클립보드 히스토리
  - `launcher_service.py`: 파일/폴더/URL 실행 및 워크스페이스 일괄 실행
  - `formatter_service.py`: CSV/Markdown/리스트 변환 등 텍스트 포맷팅
  - `template_service.py`: 템플릿 CRUD
- `ui/`: tkinter UI 컴포넌트 (Todo/Workspace/Formatter/Template/Clipboard)
- `config.json`: 앱 환경설정(JSON)
- 데이터베이스(SQLite)
  - `todos.db`: Todo 데이터 (테이블 `todos`)
  - `config.db`: 런처/워크스페이스 및 템플릿 데이터 (테이블 `workspaces`, `launcher_items`, `templates`)
  - `inventory.db`: 현재 코드 경로에서 직접 사용하지 않음(보존)
- `screenshots/`: 캡처 파일 저장 기본 폴더 (없으면 자동 생성)

---

## 설정 (config.json)

- `screenshot_save_dir`: 스크린샷 저장 폴더 경로 (기본 `screenshots`)
- `tesseract_cmd_path`: Tesseract 실행 파일 경로(선택). 미설정 시 PATH 사용 시도
- 앱 내 [설정] 탭에서 스크린샷 폴더 변경/열기, Tesseract 경로 지정 가능

---

## 기능 요약 및 사용법

- 스크린샷 & OCR
  - 전체 화면 캡처, 영역 선택 캡처, 영역 캡처 후 즉시 OCR
  - OCR 결과는 별도 창에 표시, 클립보드 복사 또는 Todo로 전송 가능
- Todo 리스트
  - 더블클릭으로 완료/미완료 토글, 체크박스로 상태 표시, 완료 시 취소선·회색 표시
  - 고급: 다중 선택 후 Space(토글)/Delete(일괄 삭제), 드래그로 정렬, 부모-하위(서브태스크) 구성, 일정 기간 경과 시 자동 보관(archived)
- 작업 공간(Workspace)
  - 파일/폴더/URL을 그룹으로 묶어 한 번에 실행
  - 스키마: `launcher_items.item_type`은 `file|folder|url` 지원
- 텍스트 포맷 변환
  - 탭/공백 구분 텍스트 → CSV/Markdown 테이블/리스트 변환
  - “공백→줄바꿈(Excel 붙여넣기 보정)” 변환 지원
- 템플릿/문구 관리
  - 자주 쓰는 문구 저장/삽입
- 클립보드 히스토리
  - 백그라운드 모니터링, 최근 항목 선택 후 즉시 붙여넣기/복사
- 상단 시계 & 상태표시

---

## 데이터베이스 상세

- `todos.db`: `todos(id, content, status, created_at, sort_order, parent_id, archived_at)`
  - 정렬/계층/보관 컬럼까지 마이그레이션 포함
- `config.db`
  - `workspaces(id, name)`
  - `launcher_items(id, name, path, item_type CHECK in ('file','folder','url'), workspace_id)`
  - `templates(id, title UNIQUE, content)`

---

## 개발 원칙 요약(SOLID/DRY/KISS)

- SRP/OCP/ISP/DIP 등 계층 분리 및 확장 용이성 준수
- 중복 제거(DRY), 단순성 유지(KISS)
- 변경은 명확한 커뮤니케이션·로그 기록(아래 변경 로그 참고)

---

## 변경 로그(요약)

- Phase 1: 초기 세팅(.gitignore, 기본 구조)
- Phase 2: Todo 기능(SQLite) 모델/레포/서비스/UI
- Phase 3: 날짜/시간 표시 추가
- Phase 4: 스크린샷(전체/영역) 기능
- Phase 5: OCR(Tesseract) 연동 및 경로 설정 기능
- Phase 6: 클립보드 히스토리
- Phase 7: ‘빠른 실행’ → ‘작업 공간’ 확장(모델/레포/서비스/UI)
- Phase 8: 작업 공간 관련 버그 수정 및 마이그레이션
- Phase 9: 텍스트 포맷 변환기(서비스/UI)
- Phase 10: 템플릿/문구 관리자
- Phase 11: 문서 정비

---

## 문제 해결 가이드

- OCR 오류: Tesseract 미설치/경로 미설정 → `tesseract_cmd_path` 지정 또는 PATH 확인
- 스크린샷 실패: 권한/다중 모니터 이슈 → 관리자 권한 또는 전체화면 캡처 테스트
- DB 잠김: 다른 프로세스 점유 → 앱 종료 후 재시도, 백업 후 재실행

---

## 문서 정책(중요)

- 본 파일(`WORKSPACE_MANUAL.md`)을 문서의 단일 출처(SSOT)로 사용합니다.
- 기존 `docs/*.md`는 본 통합 문서로 병합되었으며, 중복 문서는 정리·삭제되었습니다.
- README는 본 문서를 참조하도록 최소화되었습니다.

---

## 자주 쓰는 명령

- 의존성 설치: `pip install -r requirements.txt`
- 실행: `python main.py`
- 포맷 변환/템플릿/워크스페이스/스크린샷/OCR/클립보드는 앱 UI 탭에서 사용
