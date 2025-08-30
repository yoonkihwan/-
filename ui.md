UI 가이드 / 디자인 시스템

목적과 범위
- 목적: ttkbootstrap 기반 데스크톱 앱의 UI 수정 시 일관성·가독성·접근성·성능을 보장한다.
- 범위: 테마/액센트/밀도 토큰, 전환 규칙, 컴포넌트 스타일, 접근성·성능 가이드, 코드 조직/체크리스트.
- 관계: 기능/사용 문서는 `WORKSPACE_MANUAL.md`, 개발 지침은 `AGENTS.md`. 본 문서는 UI 설계·구현 규칙의 단일 기준이다.

기술 선택(결정)
- 프레임워크: `tkinter + ttkbootstrap`
- 루트: `ttkbootstrap.Window`를 사용한다.
- 위젯: 가능하면 `ttkbootstrap` 위젯으로 통일한다(혼용 시 스타일 누락 위험).

테마 정책
- 기본 시작 모드: 다크(solar)
- 라이트: `flatly` (화려한 라이트 테마)
- 선택 제공(옵션): `flatly, minty, sandstone, simplex, yeti, cyborg, darkly`
- 다크 테마 집합: `{solar, cyborg, darkly}`

액센트/색상 토큰
- Primary: `#3b82f6`(Blue). 주요 버튼/링크/강조에 사용.
- 라벨 대비: 다크 테마일 때 회색 계열 라벨은 흰색으로 오버라이드한다.

밀도/스케일
- 기본 밀도: 여유(Comfortable)
- 전역 스케일: 1.30(기본) — 실패 시 1.25로 폴백 가능
- 스케일 연동 패딩: 8 → 9(>=1.25) → 10(>=1.30)
- 필요 시 `Treeview` `rowheight`도 함께 상향(예: 26→30)

전환 규칙(라이트/다크/밀도)
- 적용 순서: `theme_use()` → `tk scaling` → (다크 시) 대비 오버라이드 → 액센트 적용.
- 토글 구현: 직접 `theme_use` 호출 대신 “정책 함수(ThemeService.apply)”를 통해 일괄 적용한다(누락 방지).
- 다크 대비 오버라이드 최소 집합:
  - `TLabel`/`secondary.TLabel` 전경색을 흰색으로
  - 필요 시 `Notebook.Tab`/`Treeview.Heading`/`Treeview` 텍스트도 밝게

컴포넌트 가이드
- 상단바: `Frame bootstyle='secondary'`, 패딩 8–10, 우측에 주요 버튼(`bootstyle='primary'`), 라이트/다크 토글 배치
- 사이드바: `Frame bootstyle='secondary'`, 항목 버튼은 `bootstyle='light'`, 라벨은 라이트 `secondary`, 다크 시 `light`
- 카드: `Labelframe bootstyle='info'`, 본문 보조 텍스트는 라이트 `secondary`, 다크 시 `light`
- 테이블: 열 너비 기본 `title:260/prio:100/status:120`, 다크 시 헤더/행 텍스트 명도 보정

접근성
- 대비: 일반 텍스트 WCAG 2.1 AA(4.5:1) 지향
- 포커스: 키보드 포커스 링 가시성 유지
- 최소 타겟: 버튼 높이 28px 이상(스케일 포함)

성능 가이드
- 메인 스레드 블로킹 금지: OCR/스크린샷/파일 I/O는 워커 스레드, UI 업데이트는 `after()` 디스패치
- DB 접근: 단일 스레드 또는 스레드별 커넥션. UI 스레드에서 장시간 쿼리 금지
- 대량 리스트: `Treeview`는 지연 삽입/페이지네이션 고려

코드 조직(권장)
- 루트 초기화: `root = tb.Window(themename='yeti')` → `root.tk.call('tk','scaling',1.30)` (예외 허용)
- 테마 서비스 모듈: `ui/theme_service.py`
  - `apply_policy(window, mode: Literal['light','dark'])`
  - 내부에서: 테마 선택(yeti/darkly) → 스케일 → 다크 대비 오버라이드 → 액센트 반영
  - 옵션: `set_density(window, scale: float)`

체크리스트(머지 전)
- [ ] 라이트/다크 토글 시 레이아웃 튐 없고 모든 텍스트 대비 충분한가
- [ ] 스케일 1.25/1.30 간 전환 시 패딩/행높이 동기화 되었는가
- [ ] 사이드바/상단바/상태바 라벨이 다크에서 흰색으로 보이는가
- [ ] 긴 작업에서 UI 응답성 유지되는가(프리즈 없음)
- [ ] `ttkbootstrap` 위젯으로 통일되었는가(혼용 제거)

수정 절차
- 1) UI 변경 전: 이 문서의 토큰/전환 규칙 확인
- 2) 변경: `theme_service` 경유 호출로 적용
- 3) 테스트: 라이트↔다크/스케일 전환, 주요 화면 3가지 이상 수동 확인
- 4) 문서: 의미 있는 규칙 변경 시 본 문서 업데이트, 사용자 기능 변경은 `WORKSPACE_MANUAL.md`의 변경 로그 갱신

테스트 시나리오(수동)
- 라이트↔다크 10회 토글: 텍스트/아이콘 대비 유지 여부
- 스케일 1.25↔1.30 전환: 겹침/잘림 여부
- 사이드바 메뉴/상단바 라벨: 다크에서 흰색 표시
- 테이블/탭: 헤더·탭 텍스트 명도 정상

참고
- 샘플: `experiments/ttkbootstrap_mini.py` (Light Yeti 기본, 다크 대비 보정 예시)
