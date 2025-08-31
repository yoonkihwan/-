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
from ui.screenshot_frame import ScreenshotFrame
from ui.settings_frame import SettingsFrame
from ui.home_frame import HomeFrame

# Optional: ttkbootstrap for colored buttons/styles
try:
    import ttkbootstrap as _tb
    from ttkbootstrap import ttk as _bttk
except Exception:
    _tb = None
    _bttk = None

try:
    # 선택적 OS 드래그앤드롭 지원
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
        self._dark_mode = True  # 湲곕낯 ?ㅽ겕 紐⑤뱶 ?좏샇
        try:
            self.theme_service.apply(self, mode="dark")
        except Exception:
            pass
        self.title("업무 도움 프로그램")
        self.geometry("1200x800")
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
        # If no saved geometry, center the window at default size
        try:
            if not self.config_service.get('window_geometry'):
                sw = self.winfo_screenwidth()
                sh = self.winfo_screenheight()
                w, h = 1200, 800
                x = max(0, int((sw - w) / 2))
                y = max(0, int((sh - h) / 2))
                self.geometry(f"{w}x{h}+{x}+{y}")
                self._last_normal_geometry = self.geometry()
        except Exception:
            pass
        # Window/Startup option variables used by Settings UI
        try:
            self.topmost_var = tk.BooleanVar(value=bool(self.config_service.get('window_topmost') or False))
            self.fullscreen_var = tk.BooleanVar(value=bool(self.config_service.get('window_fullscreen') or False))
            self.autostart_var = tk.BooleanVar(value=bool(self.config_service.get('auto_start') or False))
        except Exception:
            self.topmost_var = tk.BooleanVar(value=False)
            self.fullscreen_var = tk.BooleanVar(value=False)
            self.autostart_var = tk.BooleanVar(value=False)

        # --- Nav Rail + Content Stack Layout ---
        # Top AppBar
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)
        tk.Label(top_frame, text="업무 도움 프로그램", font=('Malgun Gothic', 12, 'bold')).pack(side=tk.LEFT)
        self.clock_label = tk.Label(top_frame, font=('Helvetica', 12))
        self.clock_label.pack(side=tk.RIGHT)
        if _bttk is not None:
            _bttk.Button(top_frame, text="Light/Dark", command=self.toggle_theme, bootstyle="secondary").pack(side=tk.RIGHT, padx=(8, 10))
        else:
            tk.Button(top_frame, text="Light/Dark", command=self.toggle_theme).pack(side=tk.RIGHT, padx=(8, 10))
        self.update_clock()
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X)

        # Middle: Left Nav + Right Content
        middle = tk.Frame(self)
        middle.pack(fill=tk.BOTH, expand=True)

        nav = tk.Frame(middle, width=200)
        nav.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 6), pady=10)
        nav.pack_propagate(False)

        # Scrollable content area (adapts to window size)
        content_wrap = tk.Frame(middle)
        content_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        content_canvas = tk.Canvas(content_wrap, highlightthickness=0)
        vscroll = ttk.Scrollbar(content_wrap, orient=tk.VERTICAL, command=content_canvas.yview)
        content_canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content = tk.Frame(content_canvas)
        # create window and keep refs for resize handling
        self._content_window = content_canvas.create_window((0, 0), window=content, anchor="nw")
        self._content_canvas = content_canvas
        self._content = content
        # update scrollregion when content changes
        def _on_frame_configure(_event=None):
            try:
                bbox = content_canvas.bbox("all")
                if bbox:
                    content_canvas.configure(scrollregion=bbox)
            except Exception:
                pass
        content.bind("<Configure>", _on_frame_configure)
        # match inner width to canvas width
        def _on_canvas_configure(event):
            try:
                content_canvas.itemconfig(self._content_window, width=event.width)
            except Exception:
                pass
        content_canvas.bind("<Configure>", _on_canvas_configure)
        # mouse wheel scrolling
        try:
            from ui.scroll_util import bind_mousewheel
            bind_mousewheel(content_canvas, containers=[content_canvas, content])
        except Exception:
            pass

        # Build pages (frames)
        self.page_frames = {}

        # Home page: dynamic by settings
        home = HomeFrame(content, app=self)
        self.home_frame = home
        try:
            home.set_sections(self.get_home_sections())
        except Exception:
            pass
        self.page_frames['home'] = home

        # Domain pages reuse existing frames
        todo_app_frame = TodoFrame(content, self.todo_service)
        self.todo_frame = todo_app_frame
        self.page_frames['todo'] = todo_app_frame

        launcher_app_frame = LauncherFrame(content, self.launcher_service, self)
        self.page_frames['workspace'] = launcher_app_frame

        formatter_app_frame = FormatterFrame(content, self.formatter_service, self)
        self.page_frames['formatter'] = formatter_app_frame

        template_app_frame = TemplateFrame(content, self.template_service, self)
        self.page_frames['template'] = template_app_frame

        translator_app_frame = TranslatorFrame(content, self.translate_service, self)
        self.page_frames['translate'] = translator_app_frame

        # New tabs
        screenshot_app_frame = ScreenshotFrame(content, app=self)
        self.page_frames['screenshot'] = screenshot_app_frame

        settings_app_frame = SettingsFrame(content, app=self)
        self.page_frames['settings'] = settings_app_frame

        # Clipboard tab
        clipboard_app_frame = ClipboardFrame(content, app=self, clipboard_service=self.clipboard_service)
        self.page_frames['clipboard'] = clipboard_app_frame
        # Nav Rail buttons
        nav_items = [
            ('home', '홈'),
            ('clipboard', '클립보드'),
            ('todo', '할 일'),
            ('workspace', '작업 공간'),
            ('formatter', '포맷 변환'),
            ('template', '템플릿'),
            ('translate', '번역'),
            ('screenshot', '스크린샷'),
            ('settings', '설정'),
        ]
        self._nav_buttons = {}
        for key, label in nav_items:
            if _bttk is not None:
                btn = _bttk.Button(nav, text=label, command=lambda k=key: self.show_page(k), bootstyle='secondary')
            else:
                btn = tk.Button(nav, text=label, command=lambda k=key: self.show_page(k))
            btn.pack(fill=tk.X, pady=4)
            self._nav_buttons[key] = btn
# Bottom StatusBar
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X)
        status_bar = tk.Frame(self)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(4, 8))
        self.status_label = tk.Label(status_bar, text="", font=('Helvetica', 10))
        self.status_label.pack(side=tk.LEFT)

        # Default page
        self.show_page('home')
        # Floating bar does not auto-initialize; it is launched explicitly from UI

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
            # 가용하지 않은 경우 상태표시로만 공지
            self.update_status("Drag&Drop 비활성: pip install tkinterdnd2")

    def show_page(self, key: str):
        """좌측 네비로 선택된 페이지를 표시한다."""
        try:
            for k, f in getattr(self, 'page_frames', {}).items():
                try:
                    f.pack_forget()
                except Exception:
                    pass
            frame = self.page_frames.get(key) if hasattr(self, 'page_frames') else None
            if frame:
                frame.pack(in_=self._content, fill=tk.BOTH, expand=True)
            # update nav button styles
            try:
                for k, btn in getattr(self, '_nav_buttons', {}).items():
                    if _bttk is not None:
                        btn.configure(bootstyle=("primary" if k == key else "secondary"))
            except Exception:
                pass
        except Exception:
            pass

    # Helper to create a button with optional ttkbootstrap style
    def _btn(self, parent, text, command, style: str = "secondary"):
        if _bttk is not None:
            return _bttk.Button(parent, text=text, command=command, bootstyle=style)
        return tk.Button(parent, text=text, command=command)

# --- Helpers ---
    def update_clock(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def update_status(self, text: str):
        self.status_label.config(text=str(text))
        self.after(5000, lambda: self.status_label.config(text=""))

    def toggle_theme(self):
        """테마 라이트/다크 전환."""
        try:
            self._dark_mode = not getattr(self, "_dark_mode", False)
            mode = "dark" if self._dark_mode else "light"
            if hasattr(self, "theme_service") and self.theme_service:
                self.theme_service.apply(self, mode=mode)
            # Notify frames that depend on theme colors
            try:
                if hasattr(self, 'todo_frame') and self.todo_frame:
                    self.todo_frame.apply_theme_update()
            except Exception:
                pass
        except Exception:
            pass

    # --- Home configuration ---
    def get_home_sections(self) -> list:
        try:
            sections = self.config_service.get('home_sections')
            # None이면만 기본값을 채우고, 빈 리스트([])는 사용자가 의도한 값으로 존중
            if sections is None:
                sections = ['clipboard', 'screenshot']
        except Exception:
            sections = ['clipboard']
        return list(sections)

    def set_home_sections(self, sections: list[str]):
        try:
            self.config_service.set('home_sections', list(sections))
        except Exception:
            pass
        try:
            if hasattr(self, 'home_frame') and self.home_frame:
                self.home_frame.set_sections(list(sections))
        except Exception:
            pass

    # --- Screenshot & OCR ---
    def capture_fullscreen(self):
        try:
            self.wm_state('iconic')
        except Exception:
            pass
        self.after(200, self._execute_fullscreen_capture)
        return
        try:
            filepath = self.screenshot_service.capture_fullscreen()
            self.update_status(f"스크린샷 저장: {filepath}")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")

    def capture_region(self):
        try:
            self.wm_state('iconic')
        except Exception:
            pass
        self.after(200, lambda: self._execute_region_capture(ocr_after=False))
        return
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

    def _execute_fullscreen_capture(self):
        try:
            filepath = self.screenshot_service.capture_fullscreen()
            self.update_status(f"스크린샷 완료: {filepath}")
        except Exception as e:
            messagebox.showerror("캡처 실패", f"오류 발생: {e}")
        finally:
            try:
                self.wm_state('normal')
            except Exception:
                pass

    def run_ocr(self, filepath):
        self.update_status("OCR 실행 중...")
        self.ocr_service = OCRService(tesseract_cmd_path=self.config_service.get('tesseract_cmd_path'))
        extracted_text = self.ocr_service.extract_text_from_image(filepath)
        # 기존 메시지 호환: "오류:" 접두어면 실패로 간주
        if isinstance(extracted_text, str) and extracted_text.strip().lower().startswith("오류:"):
            messagebox.showerror("OCR 실패", extracted_text)
        else:
            self.show_ocr_result(extracted_text)
        self.update_status("OCR 완료")

    def show_ocr_result(self, text):
        result_window = tk.Toplevel(self)
        result_window.title("OCR 寃곌낵")
        result_window.geometry("500x380")

        text_widget = tk.Text(result_window, wrap=tk.WORD, font=('Malgun Gothic', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, text)

        btns = tk.Frame(result_window)
        btns.pack(fill=tk.X, pady=5)

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(text_widget.get("1.0", tk.END))
            self.update_status("클립보드에 복사했습니다")

        def add_to_todo():
            content = text_widget.get("1.0", tk.END)
            if not content.strip():
                messagebox.showwarning("추가 실패", "추가할 내용이 없습니다.")
                return
            if hasattr(self.todo_service, 'add_from_text'):
                count = self.todo_service.add_from_text(content)
                messagebox.showinfo("TODO 추가", f"{count}건 추가했습니다.")
            else:
                self.todo_service.add_todo(content.strip())
                messagebox.showinfo("TODO 추가", "1건 추가했습니다.")
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
            messagebox.showerror("폴더 열기 실패", f"폴더를 열지 못했습니다: {e}")

    def set_tesseract_path(self):
        filepath = filedialog.askopenfilename(
            title="tesseract.exe 파일을 선택하세요",
            filetypes=[("Executable files", "*.exe")]
        )
        if filepath:
            self.config_service.set('tesseract_cmd_path', filepath)
            self.update_status("Tesseract 경로가 지정되었습니다. OCR 기능을 사용해보세요")
            messagebox.showinfo("설정 완료", "Tesseract 경로가 지정되었습니다. OCR 기능을 사용해보세요")
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

    # Startup (Windows) auto-run
    def toggle_autostart(self):
        enable = bool(self.autostart_var.get())
        try:
            self._set_windows_autostart(enable)
        except Exception:
            # non-Windows or registry access failed; keep config only
            pass
        try:
            self.config_service.set('auto_start', enable)
        except Exception:
            pass

    def _set_windows_autostart(self, enable: bool):
        try:
            if sys.platform != 'win32':
                return
            import winreg
            run_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "WorkspaceApp"
            exe = sys.executable
            script = os.path.abspath(sys.argv[0])
            cmd = f'"{exe}" "{script}"'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
        except Exception:
            raise

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
            # 파일 드롭 형식: Tcl list splitlist로 변환 처리
            if event.pattern == '<<Drop>>' and (data.startswith('{') or os.path.exists(data.split(' ')[0])):
                try:
                    paths = list(self.tk.splitlist(data))
                except Exception:
                    # 공백 포함 경로 예외 보수: 분리
                    paths = [p.strip('{}') for p in data.split()]
        except Exception:
            pass

        if paths:
            # 파일 내용이거나 경로 문자열로 파츠 구성
            parts = []
            for p in paths:
                part = self._read_text_best_effort(p)
                if part is None:
                    parts.append(p)  # 경로 그대로 사용
                else:
                    parts.append(part)
            text_payload = "\n\n".join(parts)
        else:
            # 텍스트 드롭
            text_payload = str(data)

        text_payload = (text_payload or '').strip()
        if not text_payload:
            self.update_status("드롭한 데이터가 비어 있습니다")
            return

        # 처리 선택: 예(할 일) / 아니오(템플릿) / 취소
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
                # 한 줄씩 추가
                lines = [ln.strip() for ln in text_payload.splitlines() if ln.strip()]
                for ln in lines:
                    t = self.todo_service.add_todo(ln)
                    if t:
                        count += 1
            self.update_status(f"Todo {count}건 추가 완료")
            if hasattr(self, 'todo_frame'):
                self.todo_frame.refresh_todos()
        else:  # Template
            title = simpledialog.askstring("템플릿 제목", "템플릿 제목을 입력하세요", parent=self)
            if not title:
                self.update_status("템플릿 생성 취소")
                return
            new_id = self.template_service.add_template(title, text_payload)
            if not new_id:
                messagebox.showerror("추가 실패", "같은 이름의 템플릿이 이미 존재합니다")
            else:
                self.update_status("템플릿 추가 완료")

    def _read_text_best_effort(self, path: str):
        try:
            if not os.path.isfile(path):
                return None
            # 텍스트 기반 저장 우선 처리
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
        except Exception:
            return None

    # --- OCR automation helpers ---
    def _ocr_extract_text(self, filepath) -> str | None:
        try:
            svc = OCRService(tesseract_cmd_path=self.config_service.get('tesseract_cmd_path'))
            text = svc.extract_text_from_image(filepath)
            try:
                chk = (text or '').strip().lower()
                if chk.startswith("오류:") or chk.startswith("error:"):
                    messagebox.showerror("OCR 오류", str(text))
                    return None
            except Exception:
                pass
            return text or ''
        except Exception as e:
            messagebox.showerror("OCR 오류", f"처리 실패: {e}")
            return None

    def capture_region_ocr_copy(self):
        try:
            self.wm_state('iconic')
        except Exception:
            pass
        def _task():
            try:
                path = self.screenshot_service.capture_region()
                if not path:
                    self.update_status("캡처가 취소되었습니다")
                    return
                text = self._ocr_extract_text(path)
                if text is None:
                    return
                try:
                    self.clipboard_clear()
                    self.clipboard_append(text)
                    self.update_status("OCR 결과를 클립보드에 복사했습니다")
                except Exception:
                    pass
            finally:
                try:
                    self.wm_state('normal')
                except Exception:
                    pass
        self.after(200, _task)

    def capture_region_ocr_todo(self):
        try:
            self.wm_state('iconic')
        except Exception:
            pass
        def _task():
            try:
                path = self.screenshot_service.capture_region()
                if not path:
                    self.update_status("캡처가 취소되었습니다")
                    return
                text = self._ocr_extract_text(path)
                if text is None or not text.strip():
                    return
                try:
                    if hasattr(self.todo_service, 'add_from_text'):
                        count = self.todo_service.add_from_text(text)
                        self.update_status(f"TODO {count}개 추가")
                    else:
                        self.todo_service.add_todo(text.strip())
                        self.update_status("TODO 1개 추가")
                    if hasattr(self, 'todo_frame'):
                        self.todo_frame.refresh_todos()
                except Exception as e:
                    messagebox.showerror("TODO 추가", f"실패: {e}")
            finally:
                try:
                    self.wm_state('normal')
                except Exception:
                    pass
        self.after(200, _task)
if __name__ == "__main__":
    app = Application()
    app.mainloop()







