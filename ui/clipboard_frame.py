import tkinter as tk
from services.clipboard_service import ClipboardService


class ClipboardFrame(tk.Frame):
    """
    클립보드 히스토리 UI를 구성하는 패널
    """
    def __init__(self, master, app, clipboard_service: ClipboardService, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app  # 메인 참조
        self.clipboard_service = clipboard_service
        self.clipboard_service.on_change_callback = self.refresh_history

        self._create_widgets()
        self.refresh_history()

    def _create_widgets(self):
        """UI 위젯을 생성하고 배치"""
        self.config(padx=5, pady=5)

        title_label = tk.Label(self, text="클립보드 히스토리", font=('Helvetica', 12, 'bold'))
        title_label.pack(fill=tk.X, pady=(0, 5))

        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.history_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.on_item_select)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)

    def refresh_history(self):
        """클립보드 히스토리 목록을 새로고침"""
        self.history_listbox.delete(0, tk.END)
        history = self.clipboard_service.get_history()
        for item in history:
            # 긴 텍스트는 잘라서 표시
            display_item = (item[:70] + '...') if len(item) > 70 else item
            self.history_listbox.insert(tk.END, display_item.replace('\n', ' '))

    def on_item_select(self, event):
        """리스트에서 항목 선택 시 클립보드로 복사"""
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            return

        selected_index = selected_indices[0]
        history = self.clipboard_service.get_history()
        if 0 <= selected_index < len(history):
            text_to_copy = history[selected_index]
            self.clipboard_service.copy_to_clipboard(text_to_copy)
            self.app.update_status(f"'{self.history_listbox.get(selected_index)}' 복사됨")

