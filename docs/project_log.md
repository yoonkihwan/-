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
