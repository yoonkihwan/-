# 업무용 PC 앱 개발 체크리스트

이 체크리스트는 프로젝트의 모든 단계를 순차적으로 정의합니다. 각 단계가 완료되면 체크 표시(`[x]`)합니다.

---

### **Phase 1: 프로젝트 초기 설정**

- [ ] 1. Git 저장소 초기화 (`git init`)
- [ ] 2. `.gitignore` 파일 생성 (Python, venv, IDE 관련 설정 추가)
- [ ] 3. 제안된 프로젝트 디렉터리 구조 생성
    - `services/`
    - `repositories/`
    - `models/`
    - `ui/`
- [ ] 4. `project_log.md`에 초기 설정 완료 기록
- [ ] 5. **(Git Push 🚀)**: "Initial project structure" 메시지로 첫 커밋 및 푸시

---

### **Phase 2: 핵심 기능 1 - 투두리스트 (SQLite 연동)**

- [ ] 1. **데이터 모델 정의**: `models/todo.py` 파일에 `Todo` 클래스 작성 (id, content, status, created_at)
- [ ] 2. **데이터베이스 저장소 구현**: `repositories/todo_repository.py` 파일 작성
    - [ ] SQLite 데이터베이스 및 `todos` 테이블 초기화 기능 구현
    - [ ] 할 일 추가 (Create) 기능 구현
    - [ ] 모든 할 일 조회 (Read) 기능 구현
    - [ ] 할 일 상태 업데이트 (Update) 기능 구현
    - [ ] 할 일 삭제 (Delete) 기능 구현
- [ ] 3. **비즈니스 로직 구현**: `services/todo_service.py` 파일 작성
    - `TodoRepository`를 사용하여 각 기능(추가, 조회, 업데이트, 삭제)에 대한 서비스 로직 구현
- [ ] 4. **UI 구현**: `tkinter` 사용
    - [ ] `main.py`에서 메인 애플리케이션 창 생성
    - [ ] `ui/todo_frame.py`에서 투두리스트 위젯(목록, 입력창, 버튼) 생성 및 레이아웃 구성
    - [ ] UI 이벤트를 `TodoService`와 연동하여 기능 활성화
- [ ] 5. `project_log.md`에 투두리스트 기능 개발 완료 기록
- [ ] 6. **(Git Push 🚀)**: "Feature: Implement Todo list with SQLite" 메시지로 커밋 및 푸시

---

### **Phase 3: 핵심 기능 2 - 날짜 및 시간 표시**

- [ ] 1. **UI 구현**: 메인 창에 날짜와 시간을 표시할 라벨 추가
- [ ] 2. **로직 구현**: 1초마다 현재 시간을 가져와 라벨을 업데이트하는 기능 구현
- [ ] 3. `project_log.md`에 날짜/시간 기능 개발 완료 기록
- [ ] 4. **(Git Push 🚀)**: "Feature: Add real-time date and time display" 메시지로 커밋 및 푸시

---

### **Phase 4: 핵심 기능 3 - 스크린샷**

- [ ] 1. **필요 라이브러리 설치 확인**: `Pillow`, `mss` 등 (사용자에게 안내)
- [ ] 2. **서비스 구현**: `services/screenshot_service.py` 파일 작성
    - [ ] 전체 화면 캡처 기능 구현
    - [ ] 부분 영역 캡처 기능 구현 (마우스로 영역을 선택할 수 있는 오버레이 창 필요)
- [ ] 3. **UI 구현**: 메인 창에 '전체 화면 캡처', '영역 선택 캡처' 버튼 추가 및 `ScreenshotService`와 연동
- [ ] 4. `project_log.md`에 스크린샷 기능 개발 완료 기록
- [ ] 5. **(Git Push 🚀)**: "Feature: Implement screen capture (full & partial)" 메시지로 커밋 및 푸시

---

### **Phase 5: 핵심 기능 4 - OCR**

- [ ] 1. **Tesseract 설치 확인**: 사용자에게 Tesseract OCR 엔진 설치 안내
- [ ] 2. **서비스 구현**: `services/ocr_service.py` 파일 작성
    - `pytesseract`를 사용하여 이미지(파일 경로 또는 이미지 객체)에서 텍스트(한/영)를 추출하는 기능 구현
- [ ] 3. **UI 연동**:
    - [ ] 스크린샷 캡처 후 OCR을 실행할 수 있는 버튼 또는 메뉴 추가
    - [ ] OCR 결과를 보여주는 팝업창 또는 텍스트 영역 구현
- [ ] 4. `project_log.md`에 OCR 기능 개발 완료 기록
- [ ] 5. **(Git Push 🚀)**: "Feature: Implement OCR functionality" 메시지로 커밋 및 푸시

---

### **Phase 6: 핵심 기능 5 - 클립보드 히스토리**

- [ ] 1. **필요 라이브러리 설치 확인**: `pyperclip` 등
- [ ] 2. **서비스 구현**: `services/clipboard_service.py` 파일 작성
    - [ ] 백그라운드에서 클립보드 변경을 감지하는 로직 구현 (주기적인 폴링)
    - [ ] 변경된 텍스트 데이터를 리스트에 저장 (히스토리 관리)
- [ ] 3. **UI 구현**:
    - [ ] 클립보드 히스토리를 보여주는 목록 UI 추가
    - [ ] 목록의 항목을 클릭하면 해당 텍스트가 클립보드에 다시 복사되는 기능 구현
- [ ] 4. `project_log.md`에 클립보드 히스토리 기능 개발 완료 기록
- [ ] 5. **(Git Push 🚀)**: "Feature: Implement clipboard history" 메시지로 커밋 및 푸시

---

### **Phase 8: 최종 검토 및 리팩토링**

- [ ] 1. 전체 코드 리뷰 및 클린 코드 원칙에 따른 리팩토링
- [ ] 2. 모든 기능에 대한 예외 처리 및 오류 메시지 보강
- [ ] 3. 주석 추가 및 최종 테스트
- [ ] 4. `README.md` 파일 작성 (프로젝트 설명, 실행 방법, 필요 라이브러리 등)
- [ ] 5. `project_log.md`에 프로젝트 완료 기록
- [ ] 6. **(Git Push 🚀)**: "Finalize and refactor project" 메시지로 최종 커밋 및 푸시
