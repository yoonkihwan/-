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
from ui.floating_bar import FloatingBar

# Optional: ttkbootstrap for colored buttons/styles
try:
    import ttkbootstrap as _tb
    from ttkbootstrap import ttk as _bttk
except Exception:
    _tb = None
    _bttk = None

try:
    # ?좏깮?? OS ?쒕옒洹몄븻?쒕∼ 吏??
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
        self.title("?낅Т ?꾨줈洹몃옩")
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

        # --- Nav Rail + Content Stack Layout ---
        # Top AppBar
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=6)
        tk.Label(top_frame, text="?낅Т ?꾨줈洹몃옩", font=('Malgun Gothic', 12, 'bold')).pack(side=tk.LEFT)
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

        content = tk.Frame(middle)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)
        self._content = content

        # Build pages (frames)
        self.page_frames = {}

        # Home page: move former left widgets here
        home = tk.Frame(content)
        # Quick actions
        screenshot_frame = tk.LabelFrame(home, text="?ㅽ겕由곗꺑 & OCR")
        screenshot_frame.pack(fill=tk.X, pady=(0, 10))
        self._btn(screenshot_frame, "?꾩껜 ?붾㈃ 罹≪쿂", self.capture_fullscreen, style="info").pack(fill=tk.X, padx=5, pady=5)
        self._btn(screenshot_frame, "?곸뿭 ?좏깮 罹≪쿂", self.capture_region, style="secondary").pack(fill=tk.X, padx=5, pady=5)
        self._btn(screenshot_frame, "?곸뿭 罹≪쿂 ??OCR", self.capture_and_ocr, style="primary").pack(fill=tk.X, padx=5, pady=5)

        settings_frame = tk.LabelFrame(home, text="?ㅼ젙")
        settings_frame.pack(fill=tk.X, pady=10)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        self._btn(settings_frame, "?대뜑 蹂寃?, self.change_screenshot_directory, style="secondary").grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self._btn(settings_frame, "?대뜑 ?닿린", self.open_screenshot_directory, style="secondary").grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self._btn(settings_frame, "Tesseract 寃쎈줈 吏??, self.set_tesseract_path, style="warning").grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        # Window options: Always on Top / Fullscreen
        self.topmost_var = tk.BooleanVar(value=bool(self.config_service.get('window_topmost') or False))
        self.fullscreen_var = tk.BooleanVar(value=bool(self.config_service.get('window_fullscreen') or False))
        opt_frame = tk.Frame(settings_frame)
        opt_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        tk.Checkbutton(opt_frame, text="??긽 ??, variable=self.topmost_var, command=self.toggle_topmost).pack(side=tk.LEFT)
        tk.Checkbutton(opt_frame, text="?꾩껜?붾㈃", variable=self.fullscreen_var, command=self.toggle_fullscreen).pack(side=tk.LEFT, padx=(10, 0))
        # Size presets
        preset_frame = tk.Frame(settings_frame)
        preset_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=(0, 5))
        tk.Button(preset_frame, text="?묎쾶 (800횞600)", command=lambda: self.set_geometry_preset(800, 600)).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(preset_frame, text="湲곕낯 (1200횞800)", command=lambda: self.set_geometry_preset(1200, 800)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        # Clipboard history
        clipboard_history_frame = ClipboardFrame(home, app=self, clipboard_service=self.clipboard_service)
        clipboard_history_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

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

        # Nav Rail buttons
        nav_items = [
            ('home', '?룧 ??),
            ('todo', '??????),
            ('workspace', '?㎛ ?묒뾽 怨듦컙'),
            ('formatter', '?? ?뺤떇 蹂??),
            ('template', '?뱷 ?쒗뵆由?),
            ('translate', '?뙋 踰덉뿭'),
        ]
        self._nav_buttons = {}
        for key, label in nav_items:
            if _bttk is not None:
                btn = _bttk.Button(nav, text=label, command=lambda k=key: self.show_page(k), bootstyle="secondary")
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
        # Initialize floating bar after UI is ready
        try:
            self.after(0, self._init_floating_bar)
        except Exception:
            pass

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
            # 媛?????ㅼ튂 ?덈궡???곹깭?쒖떆濡쒕쭔 ?쒓났
            self.update_status("Drag&Drop 鍮꾪솢?? pip install tkinterdnd2")

    def show_page(self, key: str):
        """醫뚯륫 ?ㅻ퉬濡??좏깮???섏씠吏瑜??쒖떆?쒕떎."""
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

    # --- Floating Bar integration ---
    def _init_floating_bar(self):
        try:
            actions = {
                "capture_fullscreen": {"label": "전체 캡처", "command": self.capture_fullscreen, "style": "info"},
                "capture_region": {"label": "영역 캡처", "command": self.capture_region, "style": "secondary"},
                "capture_and_ocr": {"label": "캡처+OCR", "command": self.capture_and_ocr, "style": "primary"},
                "toggle_theme": {"label": "Light/Dark", "command": self.toggle_theme, "style": "secondary"},
                "open_todo": {"label": "할 일", "command": lambda: self.show_page('todo'), "style": "secondary"},
                "open_workspace": {"label": "작업 공간", "command": lambda: self.show_page('workspace'), "style": "secondary"},
            }
            selected = self.config_service.get("floating_bar_actions") or [
                "capture_fullscreen", "capture_region", "capture_and_ocr", "toggle_theme", "open_todo"
            ]
            geom = self.config_service.get("floating_bar_geometry")
            self._floating_bar = FloatingBar(
                self,
                actions_registry=actions,
                selected_actions=selected,
                geometry=geom,
                on_close=lambda g, a: self._save_floating_bar_prefs(g, a),
            )
            # Shortcut
            self.bind_all('<Control-Shift-space>', lambda e: self.toggle_floating_bar())
        except Exception:
            pass

    def _save_floating_bar_prefs(self, geometry: str, actions: list[str]):
        try:
            self.config_service.set("floating_bar_geometry", geometry)
            self.config_service.set("floating_bar_actions", list(actions))
        except Exception:
            pass

    def toggle_floating_bar(self):
        try:
            if getattr(self, '_floating_bar', None) and self._floating_bar.winfo_exists():
                self._floating_bar.withdraw() if self._floating_bar.state() == 'normal' else self._floating_bar.deiconify()
            else:
                self._init_floating_bar()
        except Exception:
            pass

    # --- Helpers ---
    def update_clock(self):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.clock_label.config(text=now)
        self.after(1000, self.update_clock)

    def update_status(self, text: str):
        self.status_label.config(text=str(text))
        self.after(5000, lambda: self.status_label.config(text=""))

    def toggle_theme(self):
        """?쇱씠???ㅽ겕 ?뚮쭏 ?꾪솚."""
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
            self.update_status(f"?ㅽ겕由곗꺑 ??? {filepath}")
        except Exception as e:
            messagebox.showerror("罹≪쿂 ?ㅽ뙣", f"?ㅻ쪟 諛쒖깮: {e}")

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
                self.update_status(f"?ㅽ겕由곗꺑 ??? {filepath}")
            else:
                self.update_status("罹≪쿂媛 痍⑥냼?섏뿀?듬땲??)
        except Exception as e:
            messagebox.showerror("罹≪쿂 ?ㅽ뙣", f"?ㅻ쪟 諛쒖깮: {e}")

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
                self.update_status(f"?ㅽ겕由곗꺑 ??? {filepath}")
                if ocr_after:
                    self.run_ocr(filepath)
            else:
                self.update_status("罹≪쿂媛 痍⑥냼?섏뿀?듬땲??)
        except Exception as e:
            messagebox.showerror("罹≪쿂 ?ㅽ뙣", f"?ㅻ쪟 諛쒖깮: {e}")
        finally:
            try:
                self.wm_state('normal')
            except Exception:
                pass

    def _execute_fullscreen_capture(self):
        try:
            filepath = self.screenshot_service.capture_fullscreen()
            self.update_status(f"?ㅽ겕由곗꺑 ?꾨즺: {filepath}")
        except Exception as e:
            messagebox.showerror("罹≪쿂 ?ㅽ뙣", f"?ㅻ쪟 諛쒖깮: {e}")
        finally:
            try:
                self.wm_state('normal')
            except Exception:
                pass

    def run_ocr(self, filepath):
        self.update_status("臾몄옄 ?몄떇 以?..")
        self.ocr_service = OCRService(tesseract_cmd_path=self.config_service.get('tesseract_cmd_path'))
        extracted_text = self.ocr_service.extract_text_from_image(filepath)
        # 湲곗〈 硫붿떆吏????명솚???꾪빐 '?ㅻ쪟:' ?먮뒗 源⑥쭊 '?占쎈쪟:' 紐⑤몢 媛먯?
        if (isinstance(extracted_text, str) and (extracted_text.startswith("?ㅻ쪟:") or extracted_text.startswith("?占쎈쪟:"))):
            messagebox.showerror("OCR ?ㅽ뙣", extracted_text)
        else:
            self.show_ocr_result(extracted_text)
        self.update_status("OCR ?꾨즺")

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
            self.update_status("?대┰蹂대뱶濡?蹂듭궗?덉뒿?덈떎")

        def add_to_todo():
            content = text_widget.get("1.0", tk.END)
            if not content.strip():
                messagebox.showwarning("異붽? ?ㅽ뙣", "異붽????댁슜???놁뒿?덈떎.")
                return
            if hasattr(self.todo_service, 'add_from_text'):
                count = self.todo_service.add_from_text(content)
                messagebox.showinfo("??ぉ 異붽?", f"{count}媛???ぉ??異붽??덉뒿?덈떎.")
            else:
                self.todo_service.add_todo(content.strip())
                messagebox.showinfo("??ぉ 異붽?", "1媛???ぉ??異붽??덉뒿?덈떎.")
            if hasattr(self, 'todo_frame'):
                self.todo_frame.refresh_todos()

        tk.Button(btns, text="?대┰蹂대뱶 蹂듭궗", command=copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        tk.Button(btns, text="???쇰줈 異붽?", command=add_to_todo).pack(side=tk.LEFT, padx=5)

    # --- Settings ---
    def change_screenshot_directory(self):
        new_dir = filedialog.askdirectory(
            title="?ㅽ겕由곗꺑 ????대뜑 ?좏깮",
            initialdir=self.config_service.get("screenshot_save_dir")
        )
        if new_dir:
            self.config_service.set("screenshot_save_dir", new_dir)
            self.update_status("?ㅽ겕由곗꺑 ????대뜑媛 蹂寃쎈릺?덉뒿?덈떎")

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
            messagebox.showerror("?대뜑 ?닿린 ?ㅽ뙣", f"?대뜑瑜??????놁뒿?덈떎: {e}")

    def set_tesseract_path(self):
        filepath = filedialog.askopenfilename(
            title="tesseract.exe ?뚯씪???좏깮?섏꽭??,
            filetypes=[("Executable files", "*.exe")]
        )
        if filepath:
            self.config_service.set('tesseract_cmd_path', filepath)
            self.update_status("Tesseract 寃쎈줈媛 吏?뺣릺?덉뒿?덈떎. OCR???ㅼ떆 ?쒕룄?섏꽭??")
            messagebox.showinfo("?ㅼ젙 ?꾨즺", "Tesseract 寃쎈줈媛 吏?뺣릺?덉뒿?덈떎. OCR 湲곕뒫???ㅼ떆 ?쒕룄?섏꽭??")
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
            '????: (900, 600),
            '?묒뾽 怨듦컙': (1000, 700),
            '?뺤떇 蹂??: (900, 600),
            '?쒗뵆由?: (900, 600),
            '踰덉뿭': (900, 600),
        }
        w, h = minsize_map.get(tab_text, (800, 600))
        try:
            self.minsize(w, h)
        except Exception:
            pass

    # --- Drag & Drop ---
    def _enable_dnd(self):
        try:
            # 猷⑦듃???쒕∼ ?깅줉 (?띿뒪???뚯씪 紐⑤몢)
            self.drop_target_register(DND_FILES, DND_TEXT)
            self.dnd_bind('<<Drop>>', self._on_drop_event)
            self.update_status("Drag&Drop ?ъ슜 媛?? ?띿뒪???뚯씪 ?쒕∼")
        except Exception as e:
            self.update_status(f"DnD ?쒖꽦???ㅽ뙣: {e}")

    def _on_drop_event(self, event):
        data = event.data or ''
        text_payload = ''
        paths = []
        try:
            # ?뚯씪 ?쒕∼ ?뺤떇: Tcl list ??splitlist濡??덉쟾 ?뚯떛
            if event.pattern == '<<Drop>>' and (data.startswith('{') or os.path.exists(data.split(' ')[0])):
                try:
                    paths = list(self.tk.splitlist(data))
                except Exception:
                    # 怨듬갚 ?ы븿 寃쎈줈 ???덉쇅 ??蹂댁닔??遺꾨━
                    paths = [p.strip('{}') for p in data.split()]
        except Exception:
            pass

        if paths:
            # ?뚯씪 ?댁슜???쎌뼱 ?띿뒪?몃줈 ?⑹튂湲??띿뒪???뚯씪 ?곗꽑, ?ㅽ뙣 ??寃쎈줈濡??泥?
            parts = []
            for p in paths:
                part = self._read_text_best_effort(p)
                if part is None:
                    parts.append(p)  # ?띿뒪?몃줈 紐??쎌쑝硫?寃쎈줈瑜?洹몃?濡??ъ슜
                else:
                    parts.append(part)
            text_payload = "\n\n".join(parts)
        else:
            # ?쒖닔 ?띿뒪???쒕∼
            text_payload = str(data)

        text_payload = (text_payload or '').strip()
        if not text_payload:
            self.update_status("?쒕∼???곗씠?곌? ?놁뒿?덈떎")
            return

        # ????좏깮: ???щ몢) / ?꾨땲???쒗뵆由? / 痍⑥냼
        choice = messagebox.askyesnocancel(
            "?쒕∼ 泥섎━",
            "?쒕∼???댁슜??Todo濡?異붽??좉퉴??\n?꾨땲?ㅻ? ?좏깮?섎㈃ ?쒗뵆由우쑝濡???ν빀?덈떎.")
        if choice is None:
            self.update_status("?쒕∼ 泥섎━ 痍⑥냼")
            return
        if choice:  # Todo
            count = 0
            if hasattr(self.todo_service, 'add_from_text'):
                count = self.todo_service.add_from_text(text_payload)
            else:
                # 以??⑥쐞濡?異붽?
                lines = [ln.strip() for ln in text_payload.splitlines() if ln.strip()]
                for ln in lines:
                    t = self.todo_service.add_todo(ln)
                    if t:
                        count += 1
            self.update_status(f"Todo {count}媛?異붽? ?꾨즺")
            if hasattr(self, 'todo_frame'):
                self.todo_frame.refresh_todos()
        else:  # Template
            title = simpledialog.askstring("?쒗뵆由??쒕ぉ", "?쒗뵆由??쒕ぉ???낅젰?섏꽭??", parent=self)
            if not title:
                self.update_status("?쒗뵆由??앹꽦 痍⑥냼")
                return
            new_id = self.template_service.add_template(title, text_payload)
            if not new_id:
                messagebox.showerror("異붽? ?ㅽ뙣", "媛숈? ?대쫫???쒗뵆由우씠 ?대? 議댁옱?⑸땲??")
            else:
                self.update_status("?쒗뵆由?異붽? ?꾨즺")

    def _read_text_best_effort(self, path: str):
        try:
            if not os.path.isfile(path):
                return None
            # ?띿뒪??湲곕컲 ?뺤옣???곗꽑 泥섎━
            text_exts = {'.txt', '.md', '.csv', '.tsv', '.log', '.json', '.yaml', '.yml'}
            ext = os.path.splitext(path)[1].lower()
            if ext not in text_exts:
                # 鍮꾪뀓?ㅽ듃濡?媛꾩＜
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
