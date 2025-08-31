from __future__ import annotations

import sys
import tkinter as tk
from typing import Iterable, Optional


def bind_mousewheel(target: tk.Widget, containers: Optional[Iterable[tk.Widget]] = None) -> None:
    """
    마우스 휠을 내용 영역에서 직접 작동하도록 바인딩한다.
    - target: yview_scroll을 지원하는 위젯(Text/Listbox/Treeview/Canvas 등)
    - containers: 이벤트를 바인딩할 위젯들(기본: [target])
    """
    if containers is None:
        containers = [target]

    def _yview_scroll(lines: int) -> None:
        try:
            target.yview_scroll(lines, 'units')
        except Exception:
            pass

    # Windows/macOS: <MouseWheel>
    def _on_mousewheel(event):
        delta = event.delta
        # Windows는 120 단위, macOS는 소수/작은 값이 들어올 수 있어 보정
        if sys.platform == 'darwin':
            lines = -1 if delta > 0 else 1
        else:
            lines = -int(delta / 120) if delta else 0
        if lines:
            _yview_scroll(lines)
        return 'break'

    # Linux(X11): Button-4/5
    def _on_button4(_event):
        _yview_scroll(-3)
        return 'break'

    def _on_button5(_event):
        _yview_scroll(3)
        return 'break'

    for c in containers:
        try:
            c.bind('<MouseWheel>', _on_mousewheel, add='+')
            c.bind('<Button-4>', _on_button4, add='+')
            c.bind('<Button-5>', _on_button5, add='+')
        except Exception:
            # 위젯이 파괴되었거나 바인딩 불가한 경우 무시
            pass

