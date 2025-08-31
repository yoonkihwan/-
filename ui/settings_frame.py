import tkinter as tk


class SettingsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build()

    def _build(self):
        # 저장 폴더 / OCR
        paths = tk.LabelFrame(self, text="저장 폴더 / OCR")
        paths.pack(fill=tk.X, padx=5, pady=10)
        paths.columnconfigure(0, weight=1)
        paths.columnconfigure(1, weight=1)
        self._btn(paths, "폴더 변경", self.app.change_screenshot_directory).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self._btn(paths, "폴더 열기", self.app.open_screenshot_directory).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self._btn(paths, "Tesseract 경로 지정", self.app.set_tesseract_path).grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # 창 옵션
        win = tk.LabelFrame(self, text="창 옵션")
        win.pack(fill=tk.X, padx=5, pady=10)
        tk.Checkbutton(win, text="항상 위", variable=self.app.topmost_var, command=self.app.toggle_topmost).pack(anchor=tk.W, padx=6, pady=4)

        # 시작 옵션
        start = tk.LabelFrame(self, text="시작 옵션")
        start.pack(fill=tk.X, padx=5, pady=10)
        tk.Checkbutton(start, text="Windows 시작 시 자동 실행", variable=self.app.autostart_var, command=self.app.toggle_autostart).pack(anchor=tk.W, padx=6, pady=4)

        # 홈 탭 구성
        home = tk.LabelFrame(self, text="홈 탭 구성")
        home.pack(fill=tk.X, padx=5, pady=10)
        current = (self.app.get_home_sections() or [])
        self.var_home_clip = tk.BooleanVar(value=('clipboard' in current))
        self.var_home_shot = tk.BooleanVar(value=('screenshot' in current))
        self.var_home_todo = tk.BooleanVar(value=('todo' in current))
        self.var_home_workspace = tk.BooleanVar(value=('workspace' in current))
        self.var_home_formatter = tk.BooleanVar(value=('formatter' in current))
        self.var_home_template = tk.BooleanVar(value=('template' in current))
        self.var_home_translate = tk.BooleanVar(value=('translate' in current))
        tk.Checkbutton(home, text="클립보드", variable=self.var_home_clip).pack(anchor=tk.W, padx=6, pady=2)
        tk.Checkbutton(home, text="스크린샷", variable=self.var_home_shot).pack(anchor=tk.W, padx=6, pady=2)
        tk.Checkbutton(home, text="할 일", variable=self.var_home_todo).pack(anchor=tk.W, padx=6, pady=2)
        tk.Checkbutton(home, text="작업 공간", variable=self.var_home_workspace).pack(anchor=tk.W, padx=6, pady=2)
        tk.Checkbutton(home, text="포맷 변환", variable=self.var_home_formatter).pack(anchor=tk.W, padx=6, pady=2)
        tk.Checkbutton(home, text="템플릿", variable=self.var_home_template).pack(anchor=tk.W, padx=6, pady=2)
        tk.Checkbutton(home, text="번역", variable=self.var_home_translate).pack(anchor=tk.W, padx=6, pady=2)

        # 설정 전체 적용
        def apply_all():
            sections = []
            if self.var_home_clip.get():
                sections.append('clipboard')
            if self.var_home_shot.get():
                sections.append('screenshot')
            if self.var_home_todo.get():
                sections.append('todo')
            if self.var_home_workspace.get():
                sections.append('workspace')
            if self.var_home_formatter.get():
                sections.append('formatter')
            if self.var_home_template.get():
                sections.append('template')
            if self.var_home_translate.get():
                sections.append('translate')
            try:
                self.app.set_home_sections(sections)
            except Exception:
                pass
            try:
                self.app.toggle_topmost()
            except Exception:
                pass
            try:
                self.app.toggle_autostart()
            except Exception:
                pass
            try:
                self.app.update_status("설정을 저장했습니다")
            except Exception:
                pass

        tk.Button(self, text="설정 전체 적용", command=apply_all).pack(anchor=tk.E, padx=8, pady=8)

    def _btn(self, parent, text, command):
        return tk.Button(parent, text=text, command=command)

