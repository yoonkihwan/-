import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sys
import subprocess
from datetime import datetime

from repositories.todo_repository import TodoRepository
from services.todo_service import TodoService
from services.screenshot_service import ScreenshotService
from services.config_service import ConfigService
from services.ocr_service import OCRService
from services.clipboard_service import ClipboardService
from services.launcher_service import LauncherService
from services.formatter_service import FormatterService
from services.template_service import TemplateService
from services.translate_service import TranslateService

from ui.todo_frame import TodoFrame
from ui.clipboard_frame import ClipboardFrame
from ui.launcher_frame import LauncherFrame
from ui.formatter_frame import FormatterFrame
from ui.template_frame import TemplateFrame
from ui.translator_frame import TranslatorFrame
from ui.theme_service import ThemeService

try:
    # 선택적: OS 드래그앤드롭 지원
    from tkinterdnd2 import DND_FILES, DND_TEXT, TkinterDnD
    BaseTk = TkinterDnD.Tk
    _DND_AVAILABLE = True
except Exception:
    BaseTk = tk.Tk
    DND_FILES = None
    DND_TEXT = None
    _DND_AVAILABLE = False

class Application(BaseTk):
    def __init__(self):
        super().__init__()
        # Theme/Scaling: Light Yeti by default
        self.theme_service = ThemeService()
        self._dark_mode = True  # 기본 다크 모드 선호
        try:
            self.theme_service.apply(self, mode="dark")
        except Exception:
            pass
        self.title("업무 프로그램")
        self.geometry("1000x700")
        # Window state variables
        self._last_normal_geometry = None

        # --- Services ---
        self.config_service = ConfigService()
        self.todo_service = TodoService(repository=TodoRepository(db_path="todos.db"))
        self.screenshot_service = ScreenshotService(config_service=self.config_service)
        self.ocr_service = OCRService(tesseract_cmd_path=self.config_service.get('tesseract_cmd_path'))
        self.clipboard_service = ClipboardService(root=self, on_change_callback=None)
        self.launcher_service = LauncherService()
        self.formatter_service = FormatterService()
        self.template_service = TemplateService()
        self.translate_service = TranslateService()

        # Restore window settings (geometry/topmost/fullscreen)
        self._restore_window_settings()

        # --- Main Layout ---
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.clock_label = tk.Label(top_frame, font=('Helvetica', 12))
        self.clock_label.pack(side=tk.LEFT)
        self.update_clock()

        # Light/Dark toggle button (ThemeService)
        tk.Button(top_frame, text="Light/Dark", command=self.toggle_theme).pack(side=tk.RIGHT, padx=(6, 0))
        self.status_label = tk.Label(top_frame, text="", font=('Helvetica', 10))
        self.status_label.pack(side=tk.RIGHT)

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = tk.Frame(bottom_frame, width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(bottom_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Left Widgets ---
        screenshot_frame = tk.LabelFrame(left_frame, text="스크린샷 & OCR")
        screenshot_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Button(screenshot_frame, text="전체 화면 캡처", command=self.capture_fullscreen).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(screenshot_frame, text="영역 선택 캡처", command=self.capture_region).pack(fill=tk.X, padx=5, pady=5)
        tk.Button(screenshot_frame, text="영역 캡처 후 OCR", command=self.capture_and_ocr).pack(fill=tk.X, padx=5, pady=5)

        settings_frame = tk.LabelFrame(left_frame, text="설정")
        settings_frame.pack(fill=tk.X, pady=10)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        tk.Button(settings_frame, text="폴더 변경", command=self.change_screenshot_directory).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        tk.Button(settings_frame, text="폴더 열기", command=self.open_screenshot_directory).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        tk.Button(settings_frame, text="Tesseract 경로 지정", command=self.set_tesseract_path).grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        # Window options: Always on Top / Fullscreen
        self.topmost_var = tk.BooleanVar(value=bool(self.config_service.get('window_topmost') or False))
        self.fullscreen_var = tk.BooleanVar(value=bool(self.config_service.get('window_fullscreen') or False))
        opt_frame = tk.Frame(settings_frame)
        opt_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        tk.Checkbutton(opt_frame, text="항상 위", variable=self.topmost_var, command=self.toggle_topmost).pack(side=tk.LEFT)
        tk.Checkbutton(opt_frame, text="전체화면", variable=self.fullscreen_var, command=self.toggle_fullscreen).pack(side=tk.LEFT, padx=(10, 0))
        # Size presets
        preset_frame = tk.Frame(settings_frame)
        preset_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        tk.Button(preset_frame, text="작게 (800×600)", command=lambda: self.set_geometry_preset(800, 600)).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(preset_frame, text="기본 (1200×800)", command=lambda: self.set_geometry_preset(1200, 800)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        clipboard_history_frame = ClipboardFrame(left_frame, app=self, clipboard_service=self.clipboard_service)
        clipboard_history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # --- Right Widgets (Notebook) ---
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        todo_app_frame = TodoFrame(notebook, self.todo_service)
        self.todo_frame = todo_app_frame
        launcher_app_frame = LauncherFrame(notebook, self.launcher_service, self)
        formatter_app_frame = FormatterFrame(notebook, self.formatter_service, self)
        template_app_frame = TemplateFrame(notebook, self.template_service, self)
        translator_app_frame = TranslatorFrame(notebook, self.translate_service, self)

        notebook.add(todo_app_frame, text="할 일")
        notebook.add(launcher_app_frame, text="작업 공간")
        notebook.add(formatter_app_frame, text="형식 변환")
        notebook.add(template_app_frame, text="템플릿")
        notebook.add(translator_app_frame, text="번역")
        # Keep reference for tab change handling
        self.notebook = notebook
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

        # Apply theme again after all widgets are created (ensures tk palette applied)
        try:
            if hasattr(self, "theme_service") and self.theme_service:
                self.theme_service.apply(self, mode="dark" if getattr(self, "_dark_mode", False) else "light")
        except Exception:
            pass

        # Start background services
        self.clipboard_service.start_monitoring()

        # Enable Drag-and-Drop if available
        if _DND_AVAILABLE:
            self._enable_dnd()
        else:
            # 가용 시 설치 안내는 상태표시로만 제공
            self.update_status("Drag&Drop 비활성: pip install tkinterdnd2")

    # --- Helpers ---
    def update_clock(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def update_status(self, text: str):
        self.status_label.config(text=str(text))
        self.after(5000, lambda: self.status_label.config(text=""))

    def toggle_theme(self):
        """라이트/다크 테마 전환."""
        try:
            self._dark_mode = not getattr(self, "_dark_mode", False)
            mode = "dark" if self._dark_mode else "light"
            if hasattr(self, "theme_service") and self.theme_service:
                self.theme_service.apply(self, mode=mode)
        except Exception:
            pass

    # --- Screenshot & OCR ---
    def capture_fullscreen(self):
        try:
            filepath = self.screenshot_service.capture_fullscreen()
            self.update_status(f"스크린샷 저장: {filepath}")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")

    def capture_region(self):
        try:
            filepath = self.screenshot_service.capture_region()
            if filepath:
                self.update_status(f"스크린샷 저장: {filepath}")
            else:
                self.update_status("캡처가 취소되었습니다")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")

    def capture_and_ocr(self):
        try:
            self.wm_state('iconic')
        except Exception:
            pass
        self.after(200, lambda: self._execute_region_capture(ocr_after=True))

    def _execute_region_capture(self, ocr_after=False):
        try:
            filepath = self.screenshot_service.capture_region()
            if filepath:
                self.update_status(f"스크린샷 저장: {filepath}")
                if ocr_after:
                    self.run_ocr(filepath)
            else:
                self.update_status("캡처가 취소되었습니다")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")
        finally:
            try:
                self.wm_state('normal')
            except Exception:
                pass

    def run_ocr(self, filepath):
        self.update_status("문자 인식 중...")
        self.ocr_service = OCRService(tesseract_cmd_path=self.config_service.get('tesseract_cmd_path'))
        extracted_text = self.ocr_service.extract_text_from_image(filepath)
        # 기존 메시지와의 호환을 위해 '오류:' 또는 깨진 '?�류:' 모두 감지
        if (isinstance(extracted_text, str) and (extracted_text.startswith("오류:") or extracted_text.startswith("?�류:"))):
            messagebox.showerror("OCR 실패", extracted_text)
        else:
            self.show_ocr_result(extracted_text)
        self.update_status("OCR 완료")

    def show_ocr_result(self, text):
        result_window = tk.Toplevel(self)
        result_window.title("OCR 결과")
        result_window.geometry("500x380")

        text_widget = tk.Text(result_window, wrap=tk.WORD, font=('Malgun Gothic', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, text)

        btns = tk.Frame(result_window)
        btns.pack(fill=tk.X, pady=5)

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(text_widget.get("1.0", tk.END))
            self.update_status("클립보드로 복사했습니다")

        def add_to_todo():
            content = text_widget.get("1.0", tk.END)
            if not content.strip():
                messagebox.showwarning("추가 실패", "추가할 내용이 없습니다.")
                return
            if hasattr(self.todo_service, 'add_from_text'):
                count = self.todo_service.add_from_text(content)
                messagebox.showinfo("항목 추가", f"{count}개 항목을 추가했습니다.")
            else:
                self.todo_service.add_todo(content.strip())
                messagebox.showinfo("항목 추가", "1개 항목을 추가했습니다.")
            if hasattr(self, 'todo_frame'):
                self.todo_frame.refresh_todos()

        tk.Button(btns, text="클립보드 복사", command=copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="할 일로 추가", command=add_to_todo).pack(side=tk.LEFT, padx=5)

    # --- Settings ---
    def change_screenshot_directory(self):
        new_dir = filedialog.askdirectory(
            title="스크린샷 저장 폴더 선택",
            initialdir=self.config_service.get("screenshot_save_dir")
        )
        if new_dir:
            self.config_service.set("screenshot_save_dir", new_dir)
            self.update_status("스크린샷 저장 폴더가 변경되었습니다")

    def open_screenshot_directory(self):
        path = self.config_service.get("screenshot_save_dir")
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", path], check=True)
        except Exception as e:
            messagebox.showerror("폴더 열기 실패", f"폴더를 열 수 없습니다: {e}")

    def set_tesseract_path(self):
        filepath = filedialog.askopenfilename(
            title="tesseract.exe 파일을 선택하세요",
            filetypes=[("Executable files", "*.exe")]
        )
        if filepath:
            self.config_service.set('tesseract_cmd_path', filepath)
            self.update_status("Tesseract 경로가 지정되었습니다. OCR을 다시 시도하세요.")
            messagebox.showinfo("설정 완료", "Tesseract 경로가 지정되었습니다. OCR 기능을 다시 시도하세요.")
    # --- Window controls ---
    def _restore_window_settings(self):
        try:
            geom = self.config_service.get('window_geometry')
            if geom:
                self.geometry(geom)
                self._last_normal_geometry = geom
            topmost = bool(self.config_service.get('window_topmost') or False)
            self.attributes('-topmost', topmost)
            fullscreen = bool(self.config_service.get('window_fullscreen') or False)
            if fullscreen:
                self.attributes('-fullscreen', True)
        except Exception:
            pass
        # Save on close
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _on_close(self):
        try:
            is_full = bool(self.attributes('-fullscreen')) if hasattr(self, 'attributes') else False
            geom = self._last_normal_geometry if is_full and self._last_normal_geometry else self.geometry()
            self.config_service.set('window_geometry', geom)
            self.config_service.set('window_topmost', bool(self.attributes('-topmost')))
            self.config_service.set('window_fullscreen', is_full)
        except Exception:
            pass
        finally:
            self.destroy()

    def set_geometry_preset(self, w: int, h: int):
        try:
            self.attributes('-fullscreen', False)
            self.fullscreen_var.set(False)
        except Exception:
            pass
        self.geometry(f"{int(w)}x{int(h)}")
        self._last_normal_geometry = self.geometry()
        self.config_service.set('window_geometry', self._last_normal_geometry)

    def toggle_topmost(self):
        val = bool(self.topmost_var.get())
        try:
            self.attributes('-topmost', val)
        except Exception:
            pass
        self.config_service.set('window_topmost', val)

    def toggle_fullscreen(self):
        val = bool(self.fullscreen_var.get())
        try:
            if val:
                self._last_normal_geometry = self.geometry()
            self.attributes('-fullscreen', val)
        except Exception:
            pass
        self.config_service.set('window_fullscreen', val)

    def _on_tab_changed(self, event=None):
        try:
            tab_text = self.notebook.tab(self.notebook.select(), 'text')
        except Exception:
            return
        minsize_map = {
            '할 일': (900, 600),
            '작업 공간': (1000, 700),
            '형식 변환': (900, 600),
            '템플릿': (900, 600),
            '번역': (900, 600),
        }
        w, h = minsize_map.get(tab_text, (800, 600))
        try:
            self.minsize(w, h)
        except Exception:
            pass

    # --- Drag & Drop ---
    def _enable_dnd(self):
        try:
            # 루트에 드롭 등록 (텍스트/파일 모두)
            self.drop_target_register(DND_FILES, DND_TEXT)
            self.dnd_bind('<<Drop>>', self._on_drop_event)
            self.update_status("Drag&Drop 사용 가능: 텍스트/파일 드롭")
        except Exception as e:
            self.update_status(f"DnD 활성화 실패: {e}")

    def _on_drop_event(self, event):
        data = event.data or ''
        text_payload = ''
        paths = []
        try:
            # 파일 드롭 형식: Tcl list → splitlist로 안전 파싱
            if event.pattern == '<<Drop>>' and (data.startswith('{') or os.path.exists(data.split(' ')[0])):
                try:
                    paths = list(self.tk.splitlist(data))
                except Exception:
                    # 공백 포함 경로 등 예외 시 보수적 분리
                    paths = [p.strip('{}') for p in data.split()]
        except Exception:
            pass

        if paths:
            # 파일 내용을 읽어 텍스트로 합치기(텍스트 파일 우선, 실패 시 경로로 대체)
            parts = []
            for p in paths:
                part = self._read_text_best_effort(p)
                if part is None:
                    parts.append(p)  # 텍스트로 못 읽으면 경로를 그대로 사용
                else:
                    parts.append(part)
            text_payload = "\n\n".join(parts)
        else:
            # 순수 텍스트 드롭
            text_payload = str(data)

        text_payload = (text_payload or '').strip()
        if not text_payload:
            self.update_status("드롭된 데이터가 없습니다")
            return

        # 대상 선택: 예(투두) / 아니오(템플릿) / 취소
        choice = messagebox.askyesnocancel(
            "드롭 처리",
            "드롭한 내용을 Todo로 추가할까요?\n아니오를 선택하면 템플릿으로 저장합니다.")
        if choice is None:
            self.update_status("드롭 처리 취소")
            return
        if choice:  # Todo
            count = 0
            if hasattr(self.todo_service, 'add_from_text'):
                count = self.todo_service.add_from_text(text_payload)
            else:
                # 줄 단위로 추가
                lines = [ln.strip() for ln in text_payload.splitlines() if ln.strip()]
                for ln in lines:
                    t = self.todo_service.add_todo(ln)
                    if t:
                        count += 1
            self.update_status(f"Todo {count}개 추가 완료")
            if hasattr(self, 'todo_frame'):
                self.todo_frame.refresh_todos()
        else:  # Template
            title = simpledialog.askstring("템플릿 제목", "템플릿 제목을 입력하세요:", parent=self)
            if not title:
                self.update_status("템플릿 생성 취소")
                return
            new_id = self.template_service.add_template(title, text_payload)
            if not new_id:
                messagebox.showerror("추가 실패", "같은 이름의 템플릿이 이미 존재합니다.")
            else:
                self.update_status("템플릿 추가 완료")

    def _read_text_best_effort(self, path: str):
        try:
            if not os.path.isfile(path):
                return None
            # 텍스트 기반 확장자 우선 처리
            text_exts = {'.txt', '.md', '.csv', '.tsv', '.log', '.json', '.yaml', '.yml'}
            ext = os.path.splitext(path)[1].lower()
            if ext not in text_exts:
                # 비텍스트로 간주
                return None
            for enc in ('utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin-1'):
                try:
                    with open(path, 'r', encoding=enc, errors='strict') as f:
                        return f.read()
                except Exception:
                    continue
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None


if __name__ == "__main__":
    app = Application()
    app.mainloop()
