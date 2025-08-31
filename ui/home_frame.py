import tkinter as tk

from ui.clipboard_frame import ClipboardFrame


class HomeFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.sections: list[str] = []
        self.rebuild()

    def set_sections(self, sections: list[str]):
        self.sections = list(sections or [])
        self.rebuild()

    def rebuild(self):
        for w in list(self.winfo_children()):
            try:
                w.destroy()
            except Exception:
                pass

        if not self.sections:
            box = tk.Frame(self)
            box.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
            msg = (
                "홈에서 보여줄 항목이 없습니다.\n\n"
                "설정 탭의 ‘홈 탭 구성’에서 클립보드/스크린샷/할 일/작업 공간/포맷 변환/템플릿/번역을 선택해 홈에 표시할 수 있습니다."
            )
            tk.Label(box, text=msg, justify=tk.LEFT, anchor='w').pack(fill=tk.X, pady=(0, 12))
            tk.Button(box, text='설정 열기', command=lambda: self.app.show_page('settings')).pack(anchor='w')
            return

        for key in (self.sections or []):
            if key == 'clipboard':
                cf = ClipboardFrame(self, app=self.app, clipboard_service=self.app.clipboard_service)
                cf.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
            elif key == 'screenshot':
                lf = tk.LabelFrame(self, text='스크린샷 & OCR')
                lf.pack(fill=tk.X, pady=(8, 8))
                tk.Button(lf, text='전체 화면 캡처', command=self.app.capture_fullscreen).pack(fill=tk.X, padx=6, pady=4)
                tk.Button(lf, text='영역 선택 캡처', command=self.app.capture_region).pack(fill=tk.X, padx=6, pady=4)
                tk.Button(lf, text='영역 캡처 + OCR', command=self.app.capture_and_ocr).pack(fill=tk.X, padx=6, pady=4)
                # 홈에서도 OCR 자동 처리 제공
                tk.Button(lf, text='영역 캡처 → OCR → 복사', command=self.app.capture_region_ocr_copy).pack(fill=tk.X, padx=6, pady=4)
                tk.Button(lf, text='영역 캡처 → OCR → Todo 추가', command=self.app.capture_region_ocr_todo).pack(fill=tk.X, padx=6, pady=4)
            elif key == 'todo':
                lf = tk.LabelFrame(self, text='할 일')
                lf.pack(fill=tk.X, pady=(8, 8))
                tk.Button(lf, text='할 일 열기', command=lambda: self.app.show_page('todo')).pack(side=tk.LEFT, padx=6, pady=6)
            elif key == 'workspace':
                lf = tk.LabelFrame(self, text='작업 공간')
                lf.pack(fill=tk.X, pady=(8, 8))
                tk.Button(lf, text='작업 공간 열기', command=lambda: self.app.show_page('workspace')).pack(side=tk.LEFT, padx=6, pady=6)
            elif key == 'formatter':
                lf = tk.LabelFrame(self, text='포맷 변환')
                lf.pack(fill=tk.X, pady=(8, 8))
                tk.Button(lf, text='포맷 변환 열기', command=lambda: self.app.show_page('formatter')).pack(side=tk.LEFT, padx=6, pady=6)
            elif key == 'template':
                lf = tk.LabelFrame(self, text='템플릿')
                lf.pack(fill=tk.X, pady=(8, 8))
                tk.Button(lf, text='템플릿 열기', command=lambda: self.app.show_page('template')).pack(side=tk.LEFT, padx=6, pady=6)
            elif key == 'translate':
                lf = tk.LabelFrame(self, text='번역')
                lf.pack(fill=tk.X, pady=(8, 8))
                tk.Button(lf, text='번역 열기', command=lambda: self.app.show_page('translate')).pack(side=tk.LEFT, padx=6, pady=6)
