import tkinter as tk
from tkinter import ttk, messagebox


class TranslatorFrame(tk.Frame):
    def __init__(self, parent, translate_service, app):
        super().__init__(parent)
        self.translate_service = translate_service
        self.app = app

        self._build_widgets()

    def _build_widgets(self):
        # Controls (language selectors)
        ctrl = tk.Frame(self, pady=5)
        ctrl.pack(fill=tk.X)

        # Language choices
        langs = self.translate_service.languages()  # code -> english name
        # Build sorted list (by name)
        items = sorted([(code, name.title()) for code, name in langs.items()], key=lambda x: x[1])
        # Source(lang) with auto
        self.src_var = tk.StringVar(value='auto')
        self.dest_var = tk.StringVar(value='ko')

        tk.Label(ctrl, text='원문 언어').pack(side=tk.LEFT)
        self.src_combo = ttk.Combobox(ctrl, state='readonly', width=18,
                                      values=['auto (Auto Detect)'] + [f"{c} — {n}" for c, n in items])
        self.src_combo.current(0)
        self.src_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.src_combo.bind('<<ComboboxSelected>>', self._on_src_changed)

        tk.Label(ctrl, text='대상 언어').pack(side=tk.LEFT)
        self.dest_combo = ttk.Combobox(ctrl, state='readonly', width=18,
                                       values=[f"{c} — {n}" for c, n in items])
        # Default to Korean if present
        try:
            idx = [i for i, s in enumerate(self.dest_combo['values']) if s.startswith('ko')][0]
            self.dest_combo.current(idx)
        except Exception:
            self.dest_combo.current(0)
        self.dest_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.dest_combo.bind('<<ComboboxSelected>>', self._on_dest_changed)

        tk.Button(ctrl, text='번역', command=self.translate_now).pack(side=tk.LEFT)
        tk.Button(ctrl, text='서로 바꾸기', command=self.swap_languages).pack(side=tk.LEFT, padx=(5, 0))
        tk.Button(ctrl, text='결과 복사', command=self.copy_output).pack(side=tk.RIGHT)

        # IO panes
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(pane, padding=5)
        tk.Label(left, text='입력', font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)
        self.input_text = tk.Text(left, wrap=tk.WORD, height=12)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        pane.add(left, weight=1)

        right = ttk.Frame(pane, padding=5)
        tk.Label(right, text='결과', font=('Helvetica', 10, 'bold')).pack(anchor=tk.W)
        self.output_text = tk.Text(right, wrap=tk.WORD, height=12)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        pane.add(right, weight=1)

        # Detected label
        self.detect_label = tk.Label(self, text='', fg='#666')
        self.detect_label.pack(anchor=tk.W, padx=8, pady=2)

    # Helpers
    def _parse_code(self, combo_value: str, allow_auto=True) -> str:
        if allow_auto and combo_value.startswith('auto'):
            return 'auto'
        return (combo_value.split('—')[0].strip() if '—' in combo_value else combo_value.split()[0].strip())

    def _on_src_changed(self, _):
        val = self.src_combo.get()
        self.src_var.set(self._parse_code(val, allow_auto=True))

    def _on_dest_changed(self, _):
        val = self.dest_combo.get()
        self.dest_var.set(self._parse_code(val, allow_auto=False))

    def translate_now(self):
        text = self.input_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning('입력 없음', '번역할 텍스트를 입력하세요.')
            return
        src = self.src_var.get() or 'auto'
        src_param = None if src == 'auto' else src
        dest = self.dest_var.get() or 'ko'
        self.app.update_status('번역 중...')
        result = self.translate_service.translate(text, src=src_param, dest=dest)
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert(tk.END, result)
        detected = self.translate_service.detect(text)
        if detected:
            self.detect_label.config(text=f'감지된 원문 언어: {detected}')
        else:
            self.detect_label.config(text='')
        self.app.update_status('번역 완료')

    def copy_output(self):
        out = self.output_text.get('1.0', tk.END).strip()
        if not out:
            return
        self.app.clipboard_clear()
        self.app.clipboard_append(out)
        self.app.update_status('결과가 클립보드로 복사되었습니다')

    def swap_languages(self):
        # swap only if src is not auto
        src = self.src_var.get()
        dest = self.dest_var.get()
        if src and src != 'auto':
            self.src_var.set(dest)
            self.dest_var.set(src)
            # update combobox selections visually
            def set_combo_value(combo, code):
                vals = list(combo['values'])
                idx = next((i for i, s in enumerate(vals) if s.startswith(code)), None)
                if idx is not None:
                    combo.current(idx)
            set_combo_value(self.src_combo, self.src_var.get())
            set_combo_value(self.dest_combo, self.dest_var.get())
        # move output to input for immediate reverse translation
        out = self.output_text.get('1.0', tk.END)
        if out.strip():
            self.input_text.delete('1.0', tk.END)
            self.input_text.insert(tk.END, out)

