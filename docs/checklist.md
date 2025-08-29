# 업무용 PC 앱 개발 체크리스트

이 체크리스트는 프로젝트의 모든 단계를 순차적으로 정의합니다. 각 단계가 완료되면 체크 표시(`[x]`)합니다.

---

### **Phase 1: 프로젝트 초기 설정**

- [x] 1. Git 저장소 초기화 (`git init`)
- [x] 2. `.gitignore` 파일 생성 (Python, venv, IDE 관련 설정 추가)
- [x] 3. 제안된 프로젝트 디렉터리 구조 생성
- [x] 4. `project_log.md`에 초기 설정 완료 기록

---

### **Phase 2: 핵심 기능 1 - 투두리스트 (SQLite 연동)**

- [x] 1. **데이터 모델 정의**: `models/todo.py`
- [x] 2. **데이터베이스 저장소 구현**: `repositories/todo_repository.py`
- [x] 3. **비즈니스 로직 구현**: `services/todo_service.py`
- [x] 4. **UI 구현 및 통합**: `ui/todo_frame.py`, `main.py`

---

### **Phase 3: 핵심 기능 2 - 날짜 및 시간 표시**

- [x] 1. **UI 및 로직 구현**: `main.py`에 실시간 시간 라벨 추가

---

### **Phase 4: 핵심 기능 3 - 스크린샷**

- [x] 1. **서비스 구현**: `services/screenshot_service.py`
- [x] 2. **UI 구현 및 연동**: `main.py`에 관련 버튼 추가

---

### **Phase 5: 핵심 기능 4 - OCR**

- [x] 1. **서비스 구현**: `services/ocr_service.py`
- [x] 2. **UI 연동**: `main.py`에 OCR 실행 버튼 및 결과 창 추가

---

### **Phase 6: 핵심 기능 5 - 클립보드 히스토리**

- [x] 1. **서비스 구현**: `services/clipboard_service.py`
- [x] 2. **UI 구현 및 통합**: `ui/clipboard_frame.py`, `main.py`

---

### **Phase 7: 핵심 기능 6 - 작업 공간 (Workspace)**

- [x] 1. **기능 확장**: '빠른 실행'을 '작업 공간' 개념으로 확장
- [x] 2. **DB 스키마 변경**: `workspaces` 테이블 추가 및 `launcher_items` 테이블 수정
- [x] 3. **서비스 로직 확장**: URL 실행 및 그룹 실행 기능 추가
- [x] 4. **UI 전면 개편**: 작업 공간 관리 UI로 변경 (`ui/launcher_frame.py`)

---

### **Phase 8: 핵심 기능 7 - 텍스트 서식 변환기**

- [x] 1. **서비스 구현**: `services/formatter_service.py`
- [x] 2. **UI 구현 및 통합**: `ui/formatter_frame.py`, `main.py`

---

### **Phase 9: 핵심 기능 8 - 이메일 템플릿 관리자**

- [x] 1. **데이터 모델 정의**: `models/template.py`
- [x] 2. **데이터베이스 저장소 구현**: `repositories/template_repository.py`
- [x] 3. **비즈니스 로직 구현**: `services/template_service.py`
- [x] 4. **UI 구현 및 통합**: `ui/template_frame.py`, `main.py`

---

### **Phase 10: UI/UX 개선 및 버그 수정**

- [x] 1. **편의성 개선**: 스크린샷 저장 폴더 열기 버튼 추가
- [x] 2. **버그 수정**: 클립보드 히스토리 `AttributeError` 해결
- [x] 3. **버그 수정**: 작업 공간 `sqlite3.IntegrityError` 해결 (DB 자동 마이그레이션)
- [x] 4. **버그 수정**: 작업 공간 `IndentationError` 및 이벤트 핸들러 오류 해결

---

### **Phase 11: 최종 문서화**

- [x] 1. `README.md` 파일 업데이트
- [x] 2. `project_log.md` 파일 업데이트
- [x] 3. `checklist.md` 파일 최종 정리