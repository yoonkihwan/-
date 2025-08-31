from __future__ import annotations

from typing import Literal


class ThemeService:
    """ttkbootstrap 테마 + tk 위젯 팔레트 적용 서비스.

    - 기본 라이트: flatly
    - 다크: solar
    - 전역 스케일: 1.30
    - tk 위젯은 option_add + 재귀 순회로 배경/전경을 적용한다.
    """

    LIGHT_THEME = "flatly"
    DARK_THEME = "darkly"

    def __init__(self) -> None:
        self._style = None  # lazy

    def apply(self, root, mode: Literal["light", "dark"] = "light") -> None:
        """루트에 테마와 팔레트를 적용한다."""
        dark = mode == "dark"
        # ttkbootstrap 스타일 초기화/전환
        try:
            import ttkbootstrap as tb

            if self._style is None:
                self._style = tb.Style(theme=self.LIGHT_THEME)
            self._style.theme_use(self.DARK_THEME if dark else self.LIGHT_THEME)
        except Exception:
            # ttkbootstrap 미설치여도 tk 팔레트는 적용
            pass

        # 전역 스케일
        try:
            root.tk.call("tk", "scaling", 1.30)
        except Exception:
            pass

        # tk 위젯 기본 옵션(이후 생성 위젯에 반영)
        try:
            root.option_add("*Font", ("Segoe UI", 10))
        except Exception:
            pass

        palette = self._dark_palette() if dark else self._light_palette()

        # 루트 배경
        try:
            root.configure(bg=palette["bg"])
        except Exception:
            pass

        # 기존 위젯들에 즉시 반영
        self._apply_widget_palette(root, palette)

        # ttk 대비 보정(라벨 등)
        try:
            if self._style is not None and dark:
                for stylename in ("TLabel", "secondary.TLabel"):
                    try:
                        self._style.configure(stylename, foreground="#ffffff")
                    except Exception:
                        pass
        except Exception:
            pass

    # ---- internal helpers ----
    def _light_palette(self):
        return {
            "bg": "#f5f6f8",
            "panel": "#ffffff",
            "fg": "#222222",
            "subfg": "#555555",
            "button": "#f0f0f0",
            "entry": "#ffffff",
            "border": "#e2e2e2",
        }

    def _dark_palette(self):
        return {
            "bg": "#1e1f22",
            "panel": "#2b2d31",
            "fg": "#ffffff",
            "subfg": "#e6e6e6",
            "button": "#3a3d41",
            "entry": "#232428",
            "border": "#3a3d41",
        }

    def _apply_widget_palette(self, widget, pal: dict) -> None:
        """tk 위젯 전반에 배경/전경색을 최대한 적용한다."""
        try:
            import tkinter as tk
        except Exception:
            return

        try:
            if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Toplevel)):
                widget.configure(bg=pal["panel"])  # Frame 류는 panel 배경
            elif isinstance(widget, tk.Label):
                widget.configure(bg=pal["panel"], fg=pal["fg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=pal["button"], fg=pal["fg"], activebackground=pal["border"])
            elif isinstance(widget, (tk.Entry,)):
                widget.configure(bg=pal["entry"], fg=pal["fg"])
                try:
                    widget.configure(insertbackground=pal["fg"])  # 커서 색
                except Exception:
                    pass
            elif isinstance(widget, tk.Text):
                widget.configure(bg=pal["entry"], fg=pal["fg"], insertbackground=pal["fg"])
            elif isinstance(widget, tk.Checkbutton):
                widget.configure(bg=pal["panel"], fg=pal["fg"])  # selectcolor는 기본 유지
        except Exception:
            pass

        # 재귀 적용
        try:
            for child in widget.winfo_children():
                self._apply_widget_palette(child, pal)
        except Exception:
            pass
