from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Any

try:
    import ttkbootstrap as tb  # type: ignore
    from ttkbootstrap import ttk as bttk  # type: ignore
except Exception:  # pragma: no cover
    tb = None
    bttk = None


class FloatingBar(tk.Toplevel):
    """
    Mini floating toolbar (always-on-top) with configurable actions.

    - Drag to move, position is persisted by the host via on_close callback.
    - Optional ttkbootstrap button colors if available.
    """

    def __init__(
        self,
        master: tk.Misc,
        actions_registry: Dict[str, Dict[str, Any]],
        selected_actions: list[str],
        geometry: str | None = None,
        on_close: Callable[[str, list[str]], None] | None = None,
    ) -> None:
        super().__init__(master)
        self.master = master
        self.actions_registry = actions_registry
        self.selected_actions = [k for k in selected_actions if k in actions_registry] or list(actions_registry.keys())[:5]
        self.on_close = on_close

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.wm_attributes("-alpha", 0.95)
        except Exception:
            pass
        # Background panel
        self.configure(bg="#2b2d31")

        if geometry:
            try:
                self.geometry(geometry)
            except Exception:
                self.geometry("420x52+120+120")
        else:
            self.geometry("420x52+120+120")

        # Drag state
        self._drag_start: tuple[int, int] | None = None

        outer = tk.Frame(self, bg="#383a40", bd=1, relief=tk.RIDGE)
        outer.pack(fill=tk.BOTH, expand=True)
        bar = tk.Frame(outer, bg="#2b2d31")
        bar.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Drag handlers on background
        bar.bind("<Button-1>", self._on_drag_start)
        bar.bind("<B1-Motion>", self._on_drag_move)

        # Action buttons
        self._btns: dict[str, tk.Widget] = {}
        for key in self.selected_actions:
            meta = self.actions_registry.get(key)
            if not meta:
                continue
            text = meta.get("label", key)
            cmd = meta.get("command")
            style = meta.get("style", "secondary")
            w = self._btn(bar, text, cmd, style)
            w.pack(side=tk.LEFT, padx=4, pady=2)
            self._btns[key] = w

        # gear to open customizer (host should bind)
        tk.Frame(bar, width=6, bg="#2b2d31").pack(side=tk.LEFT)
        self._gear = self._btn(bar, "⚙", getattr(self, "open_customizer", None), "secondary")
        self._gear.pack(side=tk.LEFT, padx=(2, 2), pady=2)

        # Idle transparency
        self._idle_after = None
        self._schedule_idle()
        self.bind("<Enter>", lambda e: self._set_alpha(0.98))
        self.bind("<Leave>", lambda e: self._schedule_idle())

        # Persist position/actions on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---- helpers ----
    def _btn(self, parent, text, command, style="secondary"):
        if bttk is not None and command is not None:
            return bttk.Button(parent, text=text, command=command, bootstyle=style)
        return ttk.Button(parent, text=text, command=command)

    def _on_drag_start(self, e):
        self._drag_start = (e.x_root, e.y_root)

    def _on_drag_move(self, e):
        if not self._drag_start:
            return
        sx, sy = self._drag_start
        dx = e.x_root - sx
        dy = e.y_root - sy
        try:
            x = self.winfo_x() + dx
            y = self.winfo_y() + dy
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{x}+{y}")
            self._drag_start = (e.x_root, e.y_root)
        except Exception:
            pass

    def _schedule_idle(self):
        if self._idle_after:
            try:
                self.after_cancel(self._idle_after)
            except Exception:
                pass
        self._idle_after = self.after(1500, lambda: self._set_alpha(0.6))

    def _set_alpha(self, a: float):
        try:
            self.wm_attributes("-alpha", a)
        except Exception:
            pass

    def _on_close(self):
        if callable(self.on_close):
            try:
                self.on_close(self.geometry(), list(self.selected_actions))
            except Exception:
                pass
        self.destroy()

