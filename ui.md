UI 가이드 / 디자이너스 가이드

목적·범위
- 목적: ttkbootstrap 기반 데스크톱 앱의 UI 일관성·가독성·접근성·성능을 보장한다.
- 범위: 테마/스케일(밀도), 전환 규칙, 컴포넌트 배치, 접근성 가이드, 코드 조직/체크리스트
- 관련 문서: 기능/사용은 `WORKSPACE_MANUAL.md`, 개발 지침은 `AGENTS.md`.

기술 스택(결정)
- 프레임워크: `tkinter + ttkbootstrap`
- 루트: `ttkbootstrap.Window` 사용
- 위젯: 가급적 `ttkbootstrap` 위젯으로 통일(혼용 최소화)

테마 정책
- 라이트: `flatly`
- 다크: `darkly`
- 선택 제공(옵션): `flatly, minty, sandstone, simplex, yeti, cyborg, darkly`

색상·명도 정책
- Primary: `#3b82f6` (주요 버튼/링크/강조)
- 레이블·테이블 헤더는 테마별로 충분한 대비 확보

밀도(스케일)
- 기본 스케일: 1.30(권장), 1.25 보완
- 패딩 기준: 8(기본) / 9(>=1.25) / 10(>=1.30)
- `Treeview` `rowheight`: 26~30 권장

레이아웃 정책(채택)
- 좌측 네비게이션 레일 + 우측 콘텐츠 스택
- 상단 AppBar(타이틀/시계/Light-Dark) + 하단 StatusBar(토스트)
- 홈: 스크린샷/OCR/설정/클립보드 빠른 작업 카드
- 미니 플로팅바: 항상 위 소형 퀵바(드래그 이동, 선택 액션 실행)

전환 규칙(라이트/다크/밀도)
- 진입점: `ThemeService.apply(window, mode: Literal['light','dark'])`
- 구현: 직접 `theme_use` 호출 대신 `ui/theme_service.py` API 경유 적용
- 최소 오버라이드: `TLabel`/`secondary.TLabel` 대비, `Notebook.Tab`/`Treeview.Heading`/`Treeview` 명도 보정

컴포넌트 가이드
- 상단바: `Frame bootstyle='secondary'`, 패딩 8~10, 주요 버튼 `primary`
- 사이드바: `Frame bootstyle='secondary'`, 보조 버튼 `light`
- 카드: `Labelframe bootstyle='info'`, 본문 보조 텍스트 `secondary`, 표는 `light`
- 컬럼 폭(예): `title:260 / prio:100 / status:120`

접근성
- 텍스트 대비 WCAG 2.1 AA(4.5:1) 지향
- 포커스 가시성/키보드 접근성 확보
- 최소 터치/클릭 타겟 28px 이상

성능 가이드
- 메인 스레드 블로킹 금지: OCR/스크린샷/파일 I/O는 워커 + `after()` 업데이트
- DB 접근: UI 스레드 직접 커넥션 금지(서비스 계층 호출)
- 대용량 `Treeview`: 가상 스크롤/페이징 고려

코드 조직(권장)
- 루트 초기화: `root = tb.Window(themename='flatly'); root.tk.call('tk','scaling',1.30)`
- 테마 서비스: `ui/theme_service.py`
  - `apply(window, mode: Literal['light','dark'])`
  - `set_density(window, scale: float)`

체크리스트(머지 전)
- [ ] 라이트/다크 전환 시 레이아웃 붕괴 없음
- [ ] 1.25/1.30 스케일 전환 시 패딩/행높이 정상
- [ ] 사이드바/상단바/상태바 대비 충분
- [ ] 긴 목록/대량 항목에서 UI 응답성 유지
- [ ] `ttkbootstrap` 위젯 통일 사용

미니 플로팅바(Floating Bar)
- 개요: 항상 위 `Toplevel` 퀵바. 드래그 이동, 아이들 시 반투명, 호버 시 복원.
- 액션: 전체 캡처(info), 영역 캡처(secondary), 캡처+OCR(primary), 테마 토글(secondary), 페이지 열기 등.
- 스타일: `ttkbootstrap` 사용 시 `bootstyle` 적용(primary/secondary/info/warning 등).
- 단축키: `Ctrl+Shift+Space` 표시/숨김 토글.
- 지속성: 위치(`floating_bar_geometry`), 버튼 구성(`floating_bar_actions`)을 `config.json`에 저장.
