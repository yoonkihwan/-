# 프로젝트 로그

이 파일은 Gemini와의 모든 수정, 개발, 논의 사항을 기록합니다.

**[2025-08-28] Phase 1: 프로젝트 초기 설정 완료**
- Git 저장소 초기화
- .gitignore 파일 생성
- 프로젝트 폴더 구조(models, repositories, services, ui) 생성

**[2025-08-28] Phase 2: 투두리스트 기능 개발 완료**
- `models/todo.py` 데이터 모델 정의
- `repositories/todo_repository.py` SQLite 연동 CRUD 구현
- `services/todo_service.py` 비즈니스 로직 구현
- `ui/todo_frame.py` 및 `main.py`를 통한 UI 구현 및 통합
- 버그 수정: `delete_todo` 메서드 호출 오류 해결

**[2025-08-28] Phase 3: 날짜/시간 표시 기능 개발 완료**
- `main.py`에 실시간으로 업데이트되는 날짜/시간 라벨 추가

**[2025-08-28] Phase 4: 스크린샷 기능 개발 완료**
- `services/screenshot_service.py`에 전체/부분 화면 캡처 로직 구현
- `main.py`에 관련 UI 버튼 추가 및 서비스 연동

**[2025-08-28] 추가 요청사항 처리**
- `docs` 폴더를 생성하여 모든 `.md` 문서 파일 정리
- `config.json`과 `ConfigService`를 구현하여 스크린샷 저장 폴더를 설정하는 기능 추가

**[2025-08-28] Phase 5: OCR 기능 개발 완료**
- `services/ocr_service.py`에 Tesseract를 이용한 텍스트 추출 로직 구현
- `main.py`에 '캡처 후 OCR' 버튼 및 결과 창 UI 추가
- 버그 수정: Tesseract 경로를 앱 내에서 설정하는 기능 추가

**[2025-08-28] Phase 6: 클립보드 히스토리 기능 개발 완료**
- `services/clipboard_service.py`에 클립보드 모니터링 및 히스토리 관리 로직 구현
- `ui/clipboard_frame.py` UI 컴포넌트 구현
- `main.py`에 클립보드 히스토리 기능 통합

**[2025-08-29] Phase 7: '작업 공간' 기능으로 업그레이드**
- 기존 '빠른 실행' 기능을 '작업 공간'으로 확장
- `models/workspace.py` 데이터 모델 추가
- `repositories/launcher_repository.py`를 작업 공간 지원하도록 DB 스키마 변경 및 자동 마이그레이션 로직 추가
- `services/launcher_service.py`에 URL 실행 및 작업 공간 일괄 실행 로직 추가
- `ui/launcher_frame.py` UI를 작업 공간 관리 형태로 전면 개편

**[2025-08-29] Phase 8: '작업 공간' 기능 버그 수정**
- `repositories/launcher_repository.py`: 'url' 타입을 허용하도록 DB 제약 조건 오류 수정
- `ui/launcher_frame.py`: URL 추가 시 이름 입력 창이 두 번 뜨는 오류 수정
- `ui/launcher_frame.py`: 이벤트 핸들러 로직 오류로 인한 `IndentationError` 수정

**[2025-08-29] Phase 9: 텍스트 서식 변환기 기능 개발**
- `services/formatter_service.py`에 텍스트 변환 로직 구현
- `ui/formatter_frame.py` UI 컴포넌트 구현
- `main.py`에 '텍스트 변환기' 탭 추가 및 기능 통합
- '공백→줄바꿈(Excel)' 변환 기능 추가

**[2025-08-29] Phase 10: 이메일 템플릿 관리자 기능 개발**
- `models/template.py` 데이터 모델 정의
- `repositories/template_repository.py` DB 연동 CRUD 구현
- `services/template_service.py` 비즈니스 로직 구현
- `ui/template_frame.py` UI 컴포넌트 구현
- `main.py`에 '이메일 템플릿' 탭 추가 및 기능 통합

**[2025-08-29] Phase 11: 최종 문서화**
- `README.md`, `project_log.md`, `checklist.md` 등 문서 최신화 작업
- 프로젝트 개발 완료
