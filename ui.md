UI 가이드 / 디자이너스 가이드

목적·범위
- 목적: ttkbootstrap 기반 데스크톱 앱의 UI 일관성·가독성·접근성·성능을 보장한다.
- 범위: 테마/스케일(밀도), 전환 규칙, 컴포넌트 배치, 접근성 가이드, 코드 조직/체크리스트
- 관련 문서: 기능/사용은 `WORKSPACE_MANUAL.md`, 개발 지침은 `AGENTS.md`. 본 문서는 UI 설계·구현 규칙의 단일 기준이다.

기술 스택(결정)
- 프레임워크: `tkinter + ttkbootstrap`
- 루트: `ttkbootstrap.Window` 사용
- 위젯: 가급적 `ttkbootstrap` 위젯으로 통일(혼용 최소화)

테마 정책
- 기본 라이트: `flatly`
- 다크: `darkly`
- 선택 제공(옵션): `flatly, minty, sandstone, simplex, yeti, cyborg, darkly`
- 다크 테마 집합: `{solar, cyborg, darkly}` 중 정책상 `darkly` 채택

색상·명도 정책
- Primary: `#3b82f6` (주요 버튼/링크/강조)
- 레이블·테이블 헤더는 테마별로 충분한 대비 확보

밀도(스케일)
- 기본 스케일: 1.30(권장), 1.25 보완
- 스케일별 패딩: 8(기본) / 9(>=1.25) / 10(>=1.30)
- `Treeview` `rowheight`는 스케일에 맞춰 26~30 권장

레이아웃 정책(채택)
- 기본 레이아웃: 좌측 네비게이션 레일 + 우측 콘텐츠 스택
- 상단 AppBar(타이틀/시계/토글) + 하단 StatusBar(토스트 메시지)
- 홈(Home) 화면: 스크린샷/OCR/설정/클립보드의 빠른 작업 카드 배치

전환 규칙(라이트/다크/밀도)
- 진입점: `ThemeService.apply(window, mode: Literal['light','dark'])`
- 구현: 직접 `theme_use` 호출 대신 `ui/theme_service.py`의 API를 통해 일괄 적용(누락 방지)
- 최소 오버라이드:
  - `TLabel`/`secondary.TLabel` 배경 대비 확보
  - `Notebook.Tab`/`Treeview.Heading`/`Treeview`의 명도 보정

컴포넌트 가이드
- 상단바: `Frame bootstyle='secondary'`, 패딩 8~10, 오른쪽 주요 버튼은 `bootstyle='primary'`
- 사이드바: `Frame bootstyle='secondary'`, 보조 버튼은 `bootstyle='light'`
- 카드: `Labelframe bootstyle='info'`, 본문 보조 텍스트는 `secondary`, 표는 `light`
- 컬럼 폭(예시): `title:260 / prio:100 / status:120`, 테마에 맞춰 헤더/본문 명도 보정

접근성
- 텍스트 대비 WCAG 2.1 AA(4.5:1) 준수 권장
- 포커스 표시 및 키보드 탐색 가능성 확보
- 최소 터치/클릭 타겟 28px 이상

성능 가이드
- 메인 스레드 블로킹 금지: OCR/스크린샷/파일 I/O 등은 작업 스레드 + UI 업데이트는 `after()` 사용
- DB 접근: UI 스레드에서 직접 커넥션 금지(서비스 계층 통해 호출)
- 대용량 `Treeview`는 가상 스크롤/페이징 고려

코드 조직(권장)
- 루트 초기화: `root = tb.Window(themename='flatly'); root.tk.call('tk','scaling',1.30)`
- 테마 서비스 모듈: `ui/theme_service.py`
  - `apply(window, mode: Literal['light','dark'])`
  - `set_density(window, scale: float)`

체크리스트(머지 전)
- [ ] 라이트/다크 전환 시 레이아웃 붕괴 없음
- [ ] 1.25/1.30 스케일 전환 시 패딩/행높이 정상
- [ ] 사이드바/상단바/상태바 대비 충분
- [ ] 긴 목록/대량 항목에서 UI 응답성 유지
- [ ] `ttkbootstrap` 위젯 통일 사용

검증 시나리오(자동/수동)
- 라이트↔다크 10회 전환: 깜빡임/누락 없는지 확인
- 1.25↔1.30 스케일 전환: 겹침/흘러내림 없는지 확인
- 사이드바·상단바·상태바: 다크에서 대비 확인
- 표 헤더·본문 명도: 가독성 확인
