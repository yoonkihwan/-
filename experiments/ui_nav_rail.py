"""
Prototype 1: Left Navigation Rail + Content Stack

- Consistent top AppBar (title, clock, theme toggle)
- Left Nav Rail (icons + labels)
- Right Content area swaps frames
- Bottom StatusBar for transient messages

Run: python experiments/ui_nav_rail.py
"""

from __future__ import annotations

import datetime as _dt
import tkinter as tk
from ttkbootstrap import Window, ttk


PAGES = (
    ("home", "🏠 홈"),
    ("todo", "✅ 할 일"),
    ("workspace", "🧭 워크스페이스"),
    ("formatter", "🔀 포맷 변환"),
    ("template", "📝 템플릿"),
    ("clipboard", "📋 클립보드"),
    ("translate", "🌐 번역"),
    ("settings", "⚙️ 설정"),
)


class App(Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("업무 프로그램 — Prototype: Nav Rail")
        self.geometry("1100x700")
        try:
            self.tk.call("tk", "scaling", 1.30)
        except Exception:
            pass

        # state
        self._dark = False
        self._pages: dict[str, tk.Frame] = {}

        # layout: top, center (left nav + content), bottom
        self._build_appbar()
        self._build_body()
        self._build_statusbar()

        # init pages
        for key, label in PAGES:
            self._pages[key] = self._create_page(self.content, key, label)

        # default page
        self.show_page("home")
        self._tick_clock()

    # --- UI builders ---
    def _build_appbar(self):
        bar = ttk.Frame(self, padding=10)
        bar.pack(side=tk.TOP, fill=tk.X)

        self.title_label = ttk.Label(bar, text="업무 프로그램", style="secondary.TLabel")
        self.title_label.pack(side=tk.LEFT)

        # right items
        self.clock_label = ttk.Label(bar, text="--:--:--")
        self.clock_label.pack(side=tk.RIGHT, padx=(8, 0))

        theme_btn = ttk.Button(bar, text="Light/Dark", command=self._toggle_theme, bootstyle="secondary")
        theme_btn.pack(side=tk.RIGHT)

        ttk.Separator(self, orient="horizontal").pack(fill=tk.X)

    def _build_body(self):
        body = ttk.Frame(self, padding=0)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # left nav rail
        nav = ttk.Frame(body, padding=(6, 10))
        nav.pack(side=tk.LEFT, fill=tk.Y)

        self._nav_buttons = {}
        for key, label in PAGES:
            b = ttk.Button(nav, text=label, width=18, command=lambda k=key: self.show_page(k), bootstyle="secondary")
            b.pack(fill=tk.X, pady=4)
            self._nav_buttons[key] = b

        ttk.Separator(body, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=(6, 0))

        # content
        self.content = ttk.Frame(body, padding=12)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _build_statusbar(self):
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X)
        bar = ttk.Frame(self, padding=(10, 6))
        bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(bar, text="준비 완료", style="secondary.TLabel")
        self.status_label.pack(side=tk.LEFT)

    # --- Pages ---
    def _create_page(self, parent: tk.Misc, key: str, label: str) -> tk.Frame:
        f = ttk.Frame(parent)
        header = ttk.Frame(f)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text=label, font=("Malgun Gothic", 12, "bold")).pack(side=tk.LEFT)

        actions = ttk.Frame(header)
        actions.pack(side=tk.RIGHT)
        # example primary/secondary actions
        ttk.Button(actions, text="Primary", bootstyle="primary").pack(side=tk.LEFT, padx=4)
        ttk.Button(actions, text="Secondary", bootstyle="secondary").pack(side=tk.LEFT, padx=4)

        card = ttk.Labelframe(f, text="콘텐츠 영역", padding=12)
        card.pack(fill=tk.BOTH, expand=True)
        ttk.Label(card, text=f"여기에 '{label}' 페이지 콘텐츠를 배치하세요.").pack(anchor=tk.W)
        return f

    # --- Behaviors ---
    def show_page(self, key: str):
        for k, frame in self._pages.items():
            frame.pack_forget()
        frame = self._pages.get(key)
        if frame:
            frame.pack(fill=tk.BOTH, expand=True)
            self._toast(f"{key} 페이지 표시")
        # update nav styles
        try:
            for k, btn in self._nav_buttons.items():
                btn.configure(bootstyle=("primary" if k == key else "secondary"))
        except Exception:
            pass

    def _toggle_theme(self):
        self._dark = not self._dark
        self.style.theme_use("darkly" if self._dark else "flatly")
        self._toast("테마 적용: " + ("Dark" if self._dark else "Light"))

    def _tick_clock(self):
        self.clock_label.configure(text=_dt.datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick_clock)

    def _toast(self, msg: str, ms: int = 3000):
        self.status_label.configure(text=msg)
        self.after(ms, lambda: self.status_label.configure(text=""))


if __name__ == "__main__":
    App().mainloop()
